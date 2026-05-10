import sys
import os
sys.path.append (os.path.dirname(os.path.abspath(__file__)))

from main import process_video
import argparse
def demo_camera():
    """摄像头实时检测演示"""
    parser = argparse.ArgumentParser(description='PiscTrace摄像头实时检测演示')
    parser.add_argument('--pose', type=str, default='pullup',
                        choices=['pullup', 'pushup','squat','abworkout'],
                        help='选择运动类型:pullup(引体向上),pushup(俯卧撑),squat(深蹲),abworkout(腹肌训练)')
    parser.add_argument('--camera', type=int, default=0,help='摄像头索引，默认为0')
    args = parser.parse_args()

    print("=" *50)
    print("PiscTrace-基于YoLo-Pose的健身动作计数系统")
    print("=" * 50)
    print(f"运动类型:{args.pose}")
    print(f"摄像头:{args.camera}")
    print("操作说明:")
    print("-按'q'键退出程序")
    print("-确保摄像头权限已开启")
    print("=" * 50)

    try:
        process_video(
            source=args.camera,
            pose_type=args.pose,
            show=True,
            save_path=None,
        )
    except KeyboardInterrupt:
        print("\n程序已退出")
    except Exception as e:
        print(f"运行错误:{e}")
        print("请检查:")
        print("1.摄像头是否正常工作")
        print("2.是否已安装YoLOv8n - pose模型")
        print("3.是否已安装所有依赖包")

    if __name__ == "__main__":
        demo_camera()