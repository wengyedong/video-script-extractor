#!/usr/bin/env python3
import subprocess
import sys
import os
import argparse
import json

try:
    from tqdm import tqdm
    from faster_whisper import WhisperModel
except ImportError as e:
    print(f"✗ 错误: 缺少必要的依赖包: {e}")
    print("请使用以下命令安装依赖:")
    print("pip install faster-whisper tqdm torch")
    sys.exit(1)

def check_environment():
    """检查环境配置"""
    # 检查 ffmpeg 是否安装
    try:
        subprocess.run(["ffmpeg", "-version"], capture_output=True, check=True)
        print("✓ ffmpeg 已安装")
    except (subprocess.SubprocessError, FileNotFoundError):
        print("✗ 错误: ffmpeg 未安装，请先安装 ffmpeg")
        sys.exit(1)
    
    # 检查 CUDA 可用性
    try:
        import torch
        if torch.cuda.is_available():
            print("✓ CUDA 可用，将使用 GPU 加速")
            return "cuda", "float16"
        else:
            print("⚠ CUDA 不可用，将使用 CPU")
            return "cpu", "int8"
    except ImportError:
        print("⚠ torch 未安装，将使用 CPU")
        return "cpu", "int8"

def extract_audio(video_path):
    """从视频中提取音频"""
    # 生成输出文件路径
    base_name = os.path.splitext(video_path)[0]
    audio_path = f"{base_name}.wav"
    
    # 构建 ffmpeg 命令
    cmd = [
        "ffmpeg", "-i", video_path,
        "-ar", "16000",  # 采样率 16000Hz
        "-ac", "1",      # 单声道
        "-c:a", "pcm_s16le",  # 16位 PCM 编码
        "-y",  # 覆盖已有文件
        audio_path
    ]
    
    print(f"正在提取音频到 {audio_path}...")
    
    # 执行 ffmpeg 命令
    try:
        subprocess.run(cmd, check=True)
        print("✓ 音频提取成功")
        return audio_path
    except subprocess.SubprocessError as e:
        print(f"✗ 音频提取失败: {e}")
        sys.exit(1)

def transcribe_audio(audio_path, device, compute_type):
    """使用 faster-whisper 进行语音识别"""
    print(f"正在加载 faster-whisper 模型 (device: {device}, compute_type: {compute_type})...")
    
    # 加载模型
    try:
        model = WhisperModel("base", device=device, compute_type=compute_type)
    except Exception as e:
        print(f"✗ 模型加载失败: {e}")
        sys.exit(1)
    
    print("正在进行语音识别...")
    
    # 进行语音识别，使用 tqdm 显示进度
    segments, info = model.transcribe(audio_path, language=None)  # 自动语言检测
    
    # 收集识别结果
    transcription = []
    for segment in tqdm(segments, desc="识别进度"):
        transcription.append({
            "start": segment.start,
            "end": segment.end,
            "text": segment.text
        })
    
    print(f"✓ 语音识别完成，识别到 {len(transcription)} 个片段")
    return transcription, info

def generate_output_files(video_path, transcription, info, output_dir=None):
    """生成输出文件"""
    base_name = os.path.splitext(os.path.basename(video_path))[0]
    
    # 确定输出目录
    if output_dir:
        # 确保输出目录存在
        os.makedirs(output_dir, exist_ok=True)
        # 生成输出文件路径
        json_path = os.path.join(output_dir, f"{base_name}.json")
    else:
        # 使用默认目录（视频文件所在目录）
        base_dir = os.path.dirname(video_path)
        json_path = os.path.join(base_dir, f"{base_name}.json")
    json_data = {
        "video_path": video_path,
        "duration": info.duration,
        "language": info.language,
        "segments": transcription
    }
    
    try:
        with open(json_path, "w", encoding="utf-8") as f:
            json.dump(json_data, f, ensure_ascii=False, indent=2)
        print(f"✓ JSON 文件已生成: {json_path}")
    except Exception as e:
        print(f"✗ JSON 文件生成失败: {e}")
        sys.exit(1)
    
    # 生成 Markdown 文件
    if output_dir:
        md_path = os.path.join(output_dir, f"{base_name}.md")
    else:
        md_path = os.path.join(base_dir, f"{base_name}.md")
    md_content = f"# 视频转录结果\n\n"
    md_content += f"**视频路径**: {video_path}\n"
    md_content += f"**时长**: {info.duration:.2f} 秒\n"
    md_content += f"**识别语言**: {info.language}\n\n"
    md_content += "## 转录内容\n\n"
    
    for i, segment in enumerate(transcription, 1):
        start_time = format_time(segment["start"])
        end_time = format_time(segment["end"])
        md_content += f"### [{start_time} → {end_time}]\n"
        md_content += f"{segment['text']}\n\n"
    
    try:
        with open(md_path, "w", encoding="utf-8") as f:
            f.write(md_content)
        print(f"✓ Markdown 文件已生成: {md_path}")
    except Exception as e:
        print(f"✗ Markdown 文件生成失败: {e}")
        sys.exit(1)
    
    return json_path, md_path

def format_time(seconds):
    """将秒数格式化为时分秒"""
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    if hours > 0:
        return f"{hours:02d}:{minutes:02d}:{secs:02d}"
    else:
        return f"{minutes:02d}:{secs:02d}"



def video_extractor(video_path, output_dir=None):

    # 检查输入文件是否存在
    if not os.path.exists(video_path):
        print(f"✗ 错误: 输入文件不存在: {video_path}")
        sys.exit(1)
    
    # 检查文件扩展名
    if not video_path.lower().endswith(".mp4"):
        print("✗ 错误: 仅支持 .mp4 格式的视频文件")
        sys.exit(1)
    
    # 步骤 1: 环境检查
    device, compute_type = check_environment()
    
    # 步骤 2: 音频提取
    audio_path = extract_audio(video_path)
    
    # 步骤 3: 语音识别
    transcription, info = transcribe_audio(audio_path, device, compute_type)
    
    # 步骤 4: 生成输出文件
    json_path, md_path = generate_output_files(video_path, transcription, info, output_dir)
    
    print("\n✓ 所有任务完成！")

if __name__ == "__main__":
    """主函数"""
    # 解析命令行参数
    parser = argparse.ArgumentParser(description="视频转录工具")
    parser.add_argument("video_path", help="输入视频文件路径")
    parser.add_argument("--output-dir", dest="output_dir", help="指定输出目录路径")
    args = parser.parse_args()
    video_extractor(args.video_path, args.output_dir)