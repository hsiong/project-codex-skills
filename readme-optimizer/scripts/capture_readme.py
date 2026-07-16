#!/usr/bin/env python3
"""Capture deterministic README screenshots from a running web application."""

from __future__ import annotations

import argparse
import asyncio
import json
import sys
from pathlib import Path
from typing import Any
from urllib.parse import urljoin


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Capture one or more README screenshots from a JSON configuration."
    )
    parser.add_argument("config", type=Path, help="Path to the capture JSON file")
    return parser.parse_args()


def load_config(path: Path) -> dict[str, Any]:
    with path.open(encoding="utf-8") as handle:
        config = json.load(handle)

    if not isinstance(config.get("base_url"), str):
        raise ValueError("base_url must be a string")
    if not isinstance(config.get("shots"), list) or not config["shots"]:
        raise ValueError("shots must be a non-empty list")
    return config


def merged_shot(defaults: dict[str, Any], shot: Any) -> dict[str, Any]:
    if not isinstance(shot, dict):
        raise ValueError("each shot must be an object")
    merged = {**defaults, **shot}
    if not isinstance(merged.get("name"), str) or not merged["name"].strip():
        raise ValueError("each shot needs a non-empty name")
    return merged


def output_path(output_dir: Path, name: str) -> Path:
    base = output_dir.resolve()
    candidate = (base / name).resolve()
    if candidate != base and base not in candidate.parents:
        raise ValueError(f"shot name escapes output_dir: {name}")
    candidate.parent.mkdir(parents=True, exist_ok=True)
    return candidate


async def capture(config: dict[str, Any]) -> None:
    try:
        from playwright.async_api import async_playwright
    except ModuleNotFoundError as exc:
        raise RuntimeError(
            "Python Playwright is required. In an isolated environment run: "
            "python -m pip install playwright && python -m playwright install chromium"
        ) from exc

    defaults = config.get("defaults", {})
    if not isinstance(defaults, dict):
        raise ValueError("defaults must be an object")

    base_url = config["base_url"].rstrip("/") + "/"
    output_dir = Path(config.get("output_dir", "docs/images/readme"))

    async with async_playwright() as playwright:
        browser = await playwright.chromium.launch(headless=True)
        try:
            for raw_shot in config["shots"]:
                shot = merged_shot(defaults, raw_shot)
                viewport = shot.get("viewport", {"width": 1440, "height": 900})
                if not isinstance(viewport, dict):
                    raise ValueError("viewport must be an object")

                context = await browser.new_context(
                    viewport={
                        "width": int(viewport.get("width", 1440)),
                        "height": int(viewport.get("height", 900)),
                    },
                    color_scheme=shot.get("color_scheme", "dark"),
                    device_scale_factor=float(shot.get("device_scale_factor", 1)),
                )
                page = await context.new_page()
                try:
                    target = shot.get("url") or urljoin(
                        base_url, str(shot.get("path", "/")).lstrip("/")
                    )
                    await page.goto(
                        target,
                        wait_until=shot.get("wait_until", "domcontentloaded"),
                        timeout=int(shot.get("timeout_ms", 30_000)),
                    )

                    wait_for = shot.get("wait_for")
                    if wait_for:
                        await page.locator(wait_for).wait_for(
                            state="visible",
                            timeout=int(shot.get("timeout_ms", 30_000)),
                        )

                    wait_ms = int(shot.get("wait_ms", 0))
                    if wait_ms:
                        await page.wait_for_timeout(wait_ms)

                    hide = shot.get("hide", [])
                    if not isinstance(hide, list):
                        raise ValueError("hide must be a list of CSS selectors")
                    for selector in hide:
                        await page.locator(str(selector)).evaluate_all(
                            "elements => elements.forEach(element => "
                            "element.style.visibility = 'hidden')"
                        )

                    destination = output_path(output_dir, shot["name"])
                    screenshot_options = {
                        "path": str(destination),
                        "animations": "disabled",
                    }
                    selector = shot.get("selector")
                    if selector:
                        await page.locator(selector).screenshot(**screenshot_options)
                    else:
                        await page.screenshot(
                            **screenshot_options,
                            full_page=bool(shot.get("full_page", False)),
                        )
                    print(destination)
                finally:
                    await context.close()
        finally:
            await browser.close()


def main() -> int:
    args = parse_args()
    try:
        config = load_config(args.config)
        asyncio.run(capture(config))
    except (OSError, ValueError, RuntimeError, json.JSONDecodeError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
