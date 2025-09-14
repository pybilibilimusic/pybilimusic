# PyBiliMusic

一个基于 **Python** 与 **Qt Designer (PyQt)** 开发的智能桌面音乐播放系统。

[![Python](https://img.shields.io/badge/Python-3.8%2B-blue?logo=python)](https://www.python.org/)
[![Qt](https://img.shields.io/badge/Qt-PyQt-green?logo=qt)](https://www.qt.io/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
![Status](https://img.shields.io/badge/Status-Developing-orange)

## ✨ 特性

- **🎶 Bilibili 音源集成**：直接从Bilibili搜索和播放音乐
- **🎤 语音识别控制**：使用语音命令（如"播放音乐"、"下一首"）与播放器交互（规划中）
- **🕹️ Micro:bit 无线遥控**：将Micro:bit变为物理遥控器，通过按钮、传感器实现切歌、调节音量等操作（开发中）
- **🎨 美观的GUI界面**：采用Qt框架打造，界面现代且用户友好
- **🔧 技术栈**：本项目是多项技术的有趣结合，包括：
  - 客户端开发 (PyQt)
  - 网络API调用 (Bilibili)
  - 硬件串口通信 (Micro:bit)
  - 语音识别

## 🚀 快速开始

### 环境要求

- Python 3.8+

### 注意事项

1. 本项目仍在积极开发中，目前可正常使用的模块只有 `download_mp3_backup.py`，其他模块敬请期待！
2. 请勿使用本程序进行任何非法用途，包括但不限于批量下载、恶意传播等
3. 所有视频及音乐所有权归原UP主所有，开发者不承担任何法律责任

### 安装与运行

```bash
# 1. 克隆本仓库
git clone https://github.com/pybilibilimusic/pybilimusic.git

# 2. 进入项目目录
cd pybilimusic  

# 3. 安装依赖
pip install -r requirements.txt

# 4. 运行当前可用的模块
python download_mp3_backup.py
```

## 🤝 如何贡献
我们欢迎任何形式的贡献！

提交 Bug 或功能建议：[GitHub Issues](https://github.com/pybilibilimusic/pybilimusic/issues)

提交代码：Fork 本项目并发起 Pull Request

## 📄 许可证
本项目采用 MIT 许可证开源。

## 开发笔记：本项目由一名热爱编程的高一学生开发，旨在学习和探索技术的乐趣。欢迎交流与指导！
