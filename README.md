# 基于YOLO-Pose的健身动作计数系统

## 项目简介
本项目基于CSDN博客文章实现，使用YOLO-Pose模型进行实时健身动作检测和计数。系统支持俯卧撑、引体向上、深蹲等多种健身动作的实时监控和自动计数。
原始博客链接: https://blog.csdn.net/weixin_43697107/article/details/149233144
---

## 功能特性
- ✅ **实时摄像头检测**: 通过摄像头实时检测健身动作
- ✅ **视频文件分析**: 上传本地视频文件进行分析
- ✅ **多种运动类型**: 支持俯卧撑、引体向上、深蹲、腹肌训练
- ✅ **Web界面**: 现代化的Web界面，操作简单直观
- ✅ **实时计数**: 实时显示动作完成次数和状态
- ✅ **结果保存**: 支持将处理结果保存为视频文件

---

## 技术栈
- **YOLO-Pose**: 人体姿态估计模型
- **OpenCV**: 计算机视觉处理
- **Flask**: Web框架
- **TailwindCSS + DaisyUI**: 前端UI框架
- **Python**: 后端开发语言

---

## 快速开始

### 1. 环境准备
```bash
# 克隆项目
git git clone https://github.com/aimxu/Fitness_Counter.git
cd Fitness_Counter

# 安装依赖
pip install -r requirements.txt
```

### 2. 运行项目

#### 方式1: 命令行模式
```bash
# 实时摄像头检测
python demo_camera.py --pose pushup

# 视频文件分析
python demo_video.py --video test_video.mp4 --pose pullup
```

#### 方式2: Web界面模式
```bash
# 启动web服务
python app.py

# 访问 http://localhost:5000
```

### 3. 使用说明

#### Web界面使用
1. **实时检测**:
   - 点击"实时摄像头检测"
   - 选择运动类型
   - 点击"开始检测"按钮
   - 系统将使用摄像头实时检测动作

2. **视频分析**:
   - 点击"视频文件分析"
   - 选择运动类型
   - 上传视频文件
   - 等待处理完成后下载结果

#### 命令行使用
```bash
# 查看帮助
python main.py --help

# 实时摄像头的俯卧撑
python main.py --source 0 --pose pushup

# 分析视频文件中的引体向上
python main.py --source video.mp4 --pose pullup --save output.mp4
```

---

## 项目结构
```
Fitness_Counter/
├── aigym.py              # 核心算法实现
├── app.py                # Web应用主程序
├── main.py               # 命令行主程序
├── demo_camera.py        # 摄像头演示脚本
├── demo_video.py         # 视频分析演示脚本
├── requirements.txt      # Python依赖
├── templates/
│   └── index.html        # Web界面模板
├── uploads/              # 上传视频文件目录
├── output/               # 处理结果输出目录
└── README.md             # 项目说明文档
```

---

## 运动类型说明

| 运动类型 | 检测关键点 | 计数逻辑 |
|---------|-----------|---------|
| 俯卧撑 | 肩膀、肘部、手腕 | 肘部角度变化判断上下动作 |
| 引体向上 | 肩膀、肘部、手腕 | 手臂弯曲程度判断拉起和放下 |
| 深蹲 | 臀部、膝盖、脚踝 | 膝盖角度变化判断下蹲和起立 |
| 腹肌训练 | 肩膀、臀部、膝盖 | 身体弯曲程度判断动作完成 |

---

## 性能要求
- **内存**: 至少4GB RAM
- **显卡**: 支持CUDA的NVIDIA显卡（推荐）
- **摄像头**: 支持720p或1080p分辨率
- **Python**: 3.7或更高版本

---

## 常见问题

**Q: 模型下载失败怎么办?**
A: 确保网络连接正常，模型会自动下载到本地。如果下载失败，可以手动下载:
```bash
wget https://github.com/ultralytics/assets/releases/download/v8.1.0/yolov8n-pose.pt
```

**Q: 摄像头无法打开?**
A: 检查摄像头权限设置，确保Python有权限访问摄像头设备。

**Q: 处理速度慢怎么办?**
A:
1. 使用GPU加速（需要安装CUDA版本的PyTorch）
2. 降低视频分辨率
3. 减少检测频率

**Q: 计数不准确?**
A:
1. 确保摄像头角度合适，能够清晰看到全身
2. 调整角度阈值参数
3. 确保动作标准规范

---

## 开发计划
- [ ] 添加更多运动类型支持
- [ ] 实现动作质量评估
- [ ] 添加训练数据统计
- [ ] 支持多人同时检测
- [ ] 移动端应用开发