# 视频转录工具

一个基于 faster-whisper 的视频语音转录工具，可以将视频中的语音转换为文字，并生成结构化的输出文件。

## 功能特性

- 🎯 **高效语音识别**：使用 faster-whisper 模型，支持多语言自动检测
- 📊 **多格式输出**：生成 JSON 和 Markdown 两种格式的转录结果
- ⚡ **硬件加速**：自动检测 CUDA 可用性，优先使用 GPU 加速
- 🎬 **音频提取**：内置 ffmpeg 调用，自动从视频中提取音频
- 📱 **时间戳**：为每个转录片段添加精确的时间戳
- 📁 **自定义输出目录**：支持指定输出目录，自动创建不存在的目录结构

## 安装指南

### 1. 安装 Python 依赖

```bash
# 使用默认源
pip install -r requirements.txt

# 或使用国内源加速
pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
```

### 2. 安装系统依赖

#### Windows

1. 从 [ffmpeg 官网](https://ffmpeg.org/download.html) 下载 Windows 版本
2. 解压并将 `bin` 目录添加到系统环境变量 `PATH`

#### Linux

```bash
# Ubuntu/Debian
apt update && apt install ffmpeg

# CentOS/RHEL
yum install ffmpeg
```

#### macOS

```bash
brew install ffmpeg
```

## 使用方法

### 基本用法

```bash
python video_extractor.py input_video.mp4
```

### 指定输出目录

```bash
# 指定输出目录（自动创建不存在的目录）
python video_extractor.py input_video.mp4 --output-dir /path/to/output

# 支持多级目录
python video_extractor.py input_video.mp4 --output-dir output/videos/transcriptions
```

<br />

## 输出文件

执行完成后，会在以下位置生成文件：
- 默认：视频文件所在目录
- 自定义：使用 `--output-dir` 指定的目录



### 1. JSON 文件 (`input_video.json`)

```json
{
  "video_path": "input_video.mp4",
  "duration": 10.0,
  "language": "zh",
  "segments": [
    {
      "start": 0.0,
      "end": 5.0,
      "text": "这是一段测试文本。"
    }
  ]
}
```

### 2. Markdown 文件 (`input_video.md`)

```markdown
# 视频转录结果

**视频路径**: input_video.mp4
**时长**: 10.00 秒
**识别语言**: zh

## 转录内容

### [00:00 → 00:05]
这是一段测试文本。
```

## 依赖项

- **Python 3.7+**
- **faster-whisper**：语音识别模型
- **tqdm**：进度条显示
- **torch**：深度学习框架
- **ffmpeg**：音频提取工具

## 系统要求

- **CPU 模式**：任何现代 CPU 均可运行
- **GPU 模式**：需要 NVIDIA 显卡和 CUDA 支持

## 示例

### 示例命令

```bash
# 处理视频文件（默认输出到视频所在目录）
python video_extractor.py test.mp4

# 处理视频文件并指定输出目录
python video_extractor.py test.mp4 --output-dir output

# 处理视频文件并指定多级输出目录
python video_extractor.py test.mp4 --output-dir output/videos/transcriptions
```

### 示例输出

#### JSON 输出

- 包含视频信息和转录片段
- 每个片段包含开始时间、结束时间和文本内容

#### Markdown 输出

- 格式化的文档结构
- 包含视频基本信息
- 按时间戳组织的转录内容

## 注意事项

1. **文件格式**：仅支持 `.mp4` 格式的视频文件
2. **语言支持**：自动检测语言，支持多种语言
3. **硬件要求**：
   - GPU 模式：推荐 NVIDIA GTX 1060 或更高
   - CPU 模式：可能会较慢，适合短视频
4. **网络要求**：首次运行时需要下载模型文件（约 1.5GB）
5. **输出质量**：识别 accuracy 取决于音频质量和说话清晰度

## 故障排除

### 常见错误

1. **ffmpeg 未安装**
   - 错误信息：`ffmpeg 未安装，请先安装 ffmpeg`
   - 解决方法：按照安装指南安装 ffmpeg 并添加到 PATH
2. **依赖项缺失**
   - 错误信息：`缺少必要的依赖包`
   - 解决方法：运行 `pip install -r requirements.txt`
3. **CUDA 不可用**
   - 提示信息：`CUDA 不可用，将使用 CPU`
   - 解决方法：安装 NVIDIA 驱动和 CUDA Toolkit（可选）
4. **模型下载失败**
   - 错误信息：`模型加载失败`
   - 解决方法：检查网络连接，重新运行命令

## 许可证

MIT License

## 贡献

欢迎提交 Issue 和 Pull Request 来改进这个项目！
