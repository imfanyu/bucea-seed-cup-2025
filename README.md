# 北京建筑大学 2025年 第五届“萌新种子杯” — 视觉循迹仿真

本项目为 **北京建筑大学 2025年 第五届“萌新种子杯”** 中 **“视觉循迹仿真”** 赛道的官方仿真环境。

* 🌐 **比赛官网**：[https://epic314.bucea.online/event](https://epic314.bucea.online/event)
* 📄 **命题文档**：详细规则、评分标准及违规判定请查阅根目录下的 **[萌新种子杯-视觉循迹仿真命题文档.pdf](萌新种子杯-视觉循迹仿真命题文档.pdf)**

## 📁 目录结构说明

* **`VisualTracking/`**
    * **官方仿真环境**：包含比赛专用的 Webots 场景文件和基础示例。
    * `worlds/world1.wbt`：比赛地图。
    * `controllers/demo_controller/`：官方提供的基础示例代码，演示了基本的电机调用。

* **`fanyuo_controller/`**
    * **赛后参考代码**：比赛结束后开源的完整参考方案。
    * 包含视觉处理与 PID 运动控制逻辑，仅供赛后学习与复盘使用。

* **`python-3.8.5-amd64.exe`**
    * 推荐使用的 Python 安装包。

## 🛠️ 环境配置要求

请严格使用以下版本以避免兼容性问题：

1.  **Webots 仿真软件**：版本 **R2021a**
    * [官方下载地址 (GitHub)](https://github.com/cyberbotics/webots/releases/tag/R2021a)
2.  **编程语言**：Python 3.8.x
    * 可直接安装根目录下的 exe 文件。

## 🚀 快速开始 (Quick Start)

1.  **启动仿真环境**
    * 打开 Webots R2021a。
    * 选择菜单栏 `File` -> `Open World...`，打开文件 `VisualTracking/worlds/world1.wbt`。

2.  **运行示例**
    * 场景默认加载了 `demo_controller`。
    * 点击界面上方的 **Play (▶)** 按钮。
    * 你将看到小车执行基础的前进动作，这表明仿真环境已配置正确。

---
*祝大家比赛顺利！*
