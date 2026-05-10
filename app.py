import os
import cv2
import json
import time
from datetime import datetime
from flask import Flask, render_template, Response, request, jsonify, send_file
from werkzeug.utils import secure_filename
from aigym import AIGym
from ultralytics import YOLO
app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['OUTPUT_FOLDER'] = 'output'
app.config['MAX CONTENT LENGTH'] = 100 * 1024 * 1024 # 100MB
#创建必要的目录
os.makedirs (app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs (app.config['oUTPUT_FOLDER'], exist_ok=True)
#全局变量
model = None
aigym_instance = None
Camera = None
is_processing = False

#允许的视频格式
ALLOWED_EXTENSIONS = ('mp4', 'avi', 'mov','mkv', 'wmv')
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS
def init_model():
    """初始化YOLO模型"""
    global model
    if model is None:
        try:
            model = YOLO('yolov8n-pose.pt')
            print("YoLov8n-pose模型加载成功")
        except Exception as e:
            print(f"模型加载失败:{e}")
            return False
    return True

@app.route('/')
def index():
    """主页"""
    return render_template('index.html')


@app.route('/start_camera', methods=['POST'])
def start_camera():
    """启动摄像头"""
    global camera, aigym_instance

    data = request.json
    pose_type = data.get('pose_type', 'pullup')

    if not init_model():
        return jsonify({'error':'模型加载失败'}),500
    try:
        camera = cv2.VideoCapture(0)
        if not camera.isopened():
            return jsonify({'error':'无法打开摄像头'}), 500

        aigym_instance = AIGym(pose_type=pose_type)
        return jsonify({'success': True})
    except Exception as e:return jsonify({'error': str(e)}), 500


@app.route('/stop_camera', methods=['PoST'])
def stop_camera():
    """停止摄像头"""
    global camera
    if camera is not None:
        camera.release()
        Camera=None
    return jsonify({'success': True})

def generate_frames():
    """生成视频流帧"""
    global camera, aigym_instance
    while camera is not None and camera.isOpened():
        success, frame = camera.read()
        if not success:
            break
    if aigym_instance is not None:
        results = model(frame, verbose=False)
        frame = aigym_instance.obj_exe(frame, results)

    ret, buffer = cv2.imencode('.jpg', frame)
    frame = buffer.tobytes()
    yield (b'--frame\r\n'b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')


@app.route('/video_feed')
def video_feed():
    """视频流路由"""
    return Response(generate_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')


@app.route('/upload_video', methods=['POST'])
def upload_video():
    """上传视频文件"""
    if 'video' not in request.files:
        return jsonify({'error':'没有选择文件'}),400

    file = request.files['video']
    pose_type = request.form.get('pose_type', 'pullup')

    if file.filename == '':
        return jsonify({'error':'没有选择文件'}),400

    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        input_path = os.path.join(app.config['UPLOAD_FOLDER'], f"{timestamp}_{filename}")
        output_filename = f"{timestamp}_processed_{filename}"
        output_path = os.path.join(app.config['OUTPUT_FOLDER' ], output_filename)
        file.save(input_path)

        #异步处理视频
        return jsonify({
            'success': True,
            'task id': timestamp,
            'filename': output_filename
        })
    return jsonify({'error':'文件格式不支持'}),400


@app.route('/process_video/<task_id>')
def process_video_route(task_id):
    """处理视频文件"""
    global is_processing
    if is_processing:
        return jsonify({'error':'正在处理其他任务'}),429

    is_processing = True
    try:
        #查找对应的视频文件
        upload_files = os.listdir(app.config['UPLOAD_FOLDER'])
        input_file = None
        for f in upload_files:
            if f.startswith(task_id):
                input_file = f
                break
        if not input_file:
            return jsonify({'error':'找不到上传的文件'}),404

        input_path = os.path.join(app.config['UPLOAD_FOLDER'], input_file)
        output_filename = f"{task_id}_processed.mp4"
        output_path = os.path.join(app.config['oUTPUT_FOLDER' ], output_filename)
        #获取pose_type
        pose_type = request.args.get('pose_type', 'pullup')
        #处理视频
        if not init_model():
            return jsonify({'error':'模型加载失败('}),500
        aigym = AIGym(pose_type=pose_type)

        cap = cv2.VideoCapture(input_path)
        if not cap.isOpened():
            return jsonify({'error':'无法打开视频文件'}),500
        # 获取视频属性
        fps = int(cap.get(cv2.CAP_PROP_FPS))
        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

        # 创建输出视频
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        out = cv2.VideoWriter(output_path, fourcc, fps, (width, height))

        frame_count = 0
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        while True:
            ret, frame = cap.read
            if not ret:
                break
            results = model(frame, verbose=False)
            processed_frame = aigym.obj_exe(frame, results)
            out.write(processed_frame)

            frame_count += 1
            if frame_count % 30 == 0:  # 每30帧更新一次进度
                progress = (frame_count / total_frames) * 100
                print(f"处理进度:{progress:.1f}%")

        cap.release()
        out.release()

        return jsonify({
            'success': True,
            'download_url': f'/download/{output_filename}'
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        is_processing = False


@app.route('/download/<filename>')
def download_file(filename):
    """下载处理后的视频"""
    file_path = os.path.join(app.config['oUTPUT_FOLDER' ], filename)
    if os.path.exists(file_path):
        return send_file(file_path, as_attachment=True)
    return jsonify({'error':'文件不存在'}),404


@app.route('/status')
def get_status():
    """获取系统状态"""
    return jsonify({
        'model_loaded': model is not None,
        'camera_active': camera is not None and camera.isopened() if camera else False,
        'is_processing': is_processing
    })

if __name__ == '__main__':
    print('正在初始化YoLo模型...')
    init_model()
    print("启动PiscTrace Web应用...")
    app.run(host='0.0.0.0', port=5000, debug=False)