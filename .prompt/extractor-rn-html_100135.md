不是 Run post-analysis image recognition on an existing output directory when needed:      是 运行完 extractor_x11.py 自动运行  analyse_x11.py来解析  extractor_x11.py 的输出
2.  也不存在 +python3 extractor-rn-html/scripts/extractor_x11.py --prepare-login     是没有会话session，extractor_x11.py会启动一个新的对话让用户登录，而大模型直接停止对话   用户再次执行 extractor-rn-html <link> 复用session
3.唤醒词只有extractor-rn-html <link>  别乱加
