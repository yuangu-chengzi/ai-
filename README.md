## 📦 安装运行
环境要求
Windows/Linux/Mac OS

Python 3.6+

GCC编译器

DeepSeek API账户
## 快速游玩
1. 将 `config.example.py` 复制为 `config.py`
2. 在 `config.py` 中填入您的DeepSeek API密钥
3.   编译运行
gcc guess_game.c -o guess_game.exe
guess_game.exe
4. 运行游戏即可体验完整AI功能
## AI猜物游戏介绍 (AI Guess Game)
🎯 项目简介
一个基于AI Agent的智能猜物游戏，结合C语言的高效性和DeepSeek AI的创造力，为玩家提供富有挑战性和趣味性的互动体验。

🎮 创新游戏机制
渐进式提示系统：AI生成从模糊到具体的5条线索，逐步引导玩家思考

智能答案判断：支持同义词和相近概念匹配，提升游戏容错率

动态内容生成：每次游戏都是全新的挑战，保证无限重玩价值

🤖 AI深度融合
实时内容创作：利用DeepSeek API动态生成谜题和线索

语境理解：AI能理解玩家的猜测意图，进行智能判断

多类别覆盖：涵盖日常生活、工具、电子设备、动物等多样主题


💻 跨语言协同
C语言核心：负责游戏逻辑、用户交互和性能优化

Python桥梁：处理AI API调用和数据处理

系统调用集成：通过popen实现跨语言通信

🎯 工程化实践
模块化设计：功能分离，便于维护和扩展

错误恢复机制：API失败时自动切换至本地物品库

配置安全：采用config.py管理敏感信息，符合最佳实践

编码处理：全面支持UTF-8，解决中英文环境兼容问题

# AI生成的示例谜题
{
    "item": "umbrella",
    "hints": [
        "I can open and close",
        "I protect you from weather",
        "I have a curved handle", 
        "I'm made of fabric and metal",
        "You carry me when it rains"
    ]
}
自适应难度
线索渐进：从抽象描述到具体特征

🔄 工作流程
初始化：C程序启动，调用Python生成秘密物品

游戏循环：显示线索 → 获取输入 → AI判断 → 更新状态

智能交互：DeepSeek API实时分析玩家猜测

结束处理：显示结果，释放资源