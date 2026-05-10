import cv2
import argparse
from ultralytics import YOLO
from aigym import AIGym
def process_video(source, pose_type="pullup", show=True, save_path=None):
    """处理视频源(摄像头或文件)

    Args:
        source:视频源(摄像头索引或文件路径
        pose_type:运动类型(pullup,pushup,squat,abworkout)
        show:是否显示实时画面:
        save_path:保存视频的路径(可选)
    """
    #初始化YOL0-Pose模型
    model = YOLO('yolo11n-pose.pt')
    #初始化AIGym
    gym = AIGym(pose_type=pose_type)
    #打开视频源
    cap = cv2.VideoCapture(source)

    if not cap.isOpened():
        print(f"无法打开视频源:{source}")
        return
    # 获取视频属性
    fps = int(cap.get(cv2.CAP_PROP_FPS))
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    # 初始化视频写入器
    writer = None
    if save_path:
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        writer = cv2.VideoWriter(save_path, fourcc, fps, (width, height))

    print(f"开始处理视频，运动类型:{pose_type}")
    print("按'q'键退出")

    while True:
        ret, frame = cap.read()
        if not ret:
            break
        # 使用YoLo-Pose进行姿势估计
        results = model.predict(frame, verbose=False)
        # 处理姿势数据
        processed_frame = gym.obj_exe(frame, results)
        # 显示结果
        if show:
            cv2.imshow('PiscTrace -健身动E计数', processed_frame)

            # 按q键退出
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
        # 保存视频
        if writer:
            writer.write(processed_frame)
    # 清理资源
    cap.release()
    if writer:
        writer.release()
    cv2.destroyAllWindows()
    print("处理完成!")

def main():
    parser = argparse.ArgumentParser(description='PiscTrace - 基于YoLo-Pose的健身动作计数系统')
    parser.add_argument('--source', type=str, default='0',
                help ='视频源: 摄像头索引(θ, 1, 2...)或视频文件路径')
    parser.add_argument('--pose', type=str, default='pullup', choices=['pullup', 'pushup', 'squat', 'abworkout'],
                         help='运动类型:pullup(引|体向上),pushup(俯卧撑),squat(深蹲)，abworkout(腹肌训练)')
    parser.add_argument('--save', type=str, default=None, help='保存处理后的视频路径(可选)')
    parser.add_argument('--no-show', action='store_true', help ='不显示实时画面')
    args = parser.parse_args()

    args = parser.parse_args

    # 处理source参数
    try:
        source = int(args.source)  # 尝试作为摄像头索引
    except ValueError:
        source = args.source  # 作为文件路径
    # 运行处理
    process_video(
        source=source,
        pose_type=args.pose, show=not args.no_show, save_path=args.save
    )


if __name__ == '__main__':
    main()

