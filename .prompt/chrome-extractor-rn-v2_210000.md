根据 extractor_rn_v2.py 更新 chrome-extractor-rn-v2 skill.md。
主要更新：
1. 字段更新：支持 `title`、`正文`、`评论`、`互动数据`、`图片`、`视频`。
2. 互动数据格式：`点赞: xx, 收藏: xx, 评论: xx, 分享：xx`。
3. 表情处理：输出为 `![emoji](url)`。
4. 评论格式：按 parent-comment 分块，使用 markdown blocks。
5. 流程更新：增加了 Xephyr 会话和预登录的支持。
6. 清理逻辑：同步了代码中更激进的 HTML 清理逻辑。
