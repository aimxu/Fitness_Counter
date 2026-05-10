import sys
import os
sys.path.append (os.path.dirname(os.path.abspath(__file__)))

from main import process_video
import argparse
from datetime import datetime

def demo_video():
    """视频文件分析演示"""
    parser = argparse.ArgumentParser(description='PiscTrace视频文件分析演示')
    parser.add_argument('--video', type=str, required=True,help='输入视频文件路径')
    parser.add_argument('--pose', type=str, default='pushup',
                        choices=['pullup', 'pushup','squat','abworkout'],
                        help='选择运动类型:pullup(引体向上)，pushup(俯卧撑)，squat(深蹲)，abworkout(腹肌训练)')
    parser.add_argument('--output-dir', type=str, default='output',
                        help='输出目录，默认为output')

    args = parser.parse_args()
    #检查输入文件是否存在
    if not os.path.exists(args.video):
        print(f"错误:视频文件'{args.video}'不存在")
        return
    #创建输出目录
    os.makedirs(args.output_dir, exist_ok=True)
    #生成输出文件名
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = os.path.basename(args.video)
    name, ext = os.path.splitext (filename)
    output_file = os.path.join(args.output_dir, f"{name}_{args.pose}_{timestamp}{ext}")

    print("=" * 60)
    print("PiscTrace-基于YoLO-Pose的视频动作分析系统")
    print("=" * 60)
    print(f"输入视频:{args.video}")
    print(f"运动类型:{args.pose}")
    print(f"输出文件:{output_file}")
    print("=" * 60)
    try:
        process_video(
            source=args.video,
            pose_type=args.pose,
            show=True,
            save_path=output_file
        )
        print(f"\n处理完成!结果已保存到:{output_file}")
    except KeyboardInterrupt:
        print("\n程序已中断")
    except Exception as e:
        print(f"处理错误:{e}")
        print("请检查:")
        print("1.视频文件是否损坏")
        print("2.是否已安装所有依赖包")
        print("3.磁盘空间是否充足")

if __name__ == '__main__':
    demo_video()