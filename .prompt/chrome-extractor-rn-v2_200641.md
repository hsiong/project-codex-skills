chrome-extractor-rn-v2是完整的代码，不依赖chrome-extractor-rn，chrome-extractor-rn后面我要改成其他的功能；
2. 不是基于screenshots， 而是应该是评论全部展开以后，将html丢给 ollama 分析， ollama模型使用 qwen3.5 27b，这样来获取 title、正文、评论、互动数据、图片和视频； 后续的图片识别也是使用 ollama 来识别；
3. 这个识别不单是ollama，后续可以支持其他接口地址不同，协议我会保持与ollama一致； 模型也可以通过入参调整
