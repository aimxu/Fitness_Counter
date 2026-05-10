import cv2
import numpy as np
from ultralytics import YOLO
from ultralytics.utils.checks import check_imshow
from ultralytics.utils.plotting import Annotator


class AIGym:
    """A class to manage the gym steps of people in a real-time video stream based on their poses."""

    def __init__(
            self,
            kpts_to_check=None,
            line_thickness=2,
            pose_up_angle=145.0,
            pose_down_angle=90.0,
            pose_type="pullup",
    ):
        """
        Initializes the AIGym class with the specified parameters.
        Args:
            kpts_to_check (list, optional): Indices of keypoints to check. Defaults to [6, 8, 10].
            line_thickness (int, optional): Thickness of the lines drawn. Defaults to 2.
            pose_up_angle (float, optional): Angle threshold for the 'up' pose. Defaults to 145.0.
            pose_down_angle (float, optional): Angle threshold for the 'down' pose. Defaults to 90.0.
            pose_type (str, optional): Type of pose to detect ('pullup', 'pushup', 'abworkout', 'squat'). Defaults to "pullup".
        """
        self.kpts_to_check = kpts_to_check or [6, 8, 10]  # Default keypoints
        self.tf = line_thickness
        self.poseup_angle = pose_up_angle
        self.posedown_angle = pose_down_angle
        self.pose_type = pose_type

        # Initialize attributes
        self.im0 = None
        self.keypoints = None
        self.annotator = None
        self.env_check = check_imshow(warn=True)
        self.count = []
        self.angle = []
        self.stage = []

    def estimate_pose_angle(self, a, b, c):
        """计算三个关键点之间的角度"""
        a = np.array(a)  # First
        b = np.array(b)  # Mid
        c = np.array(c)  # End

        radians = np.arctan2(c[1] - b[1], c[0] - b[0]) - np.arctan2(a[1] - b[1], a[0] - b[0])
        angle = np.abs(radians * 180.0 / np.pi)
        if angle > 180.0:
            angle = 360 - angle

        return angle

    def draw_specific_points(self, kpts, indices, radius=5, color=(0, 255,0)):
        """绘制特定关键点"""
        img = self.im0.copy()
        for idx in indices:
            if idx < len(kpts):
                x, y = int(kpts[idx][0]), int(kpts[idx][1])
                cv2.circle(img, (x, y), radius, color, -1)
        return img

    def plot_angle_and_count_and_stage(self, angle_text, count_text, stage_text, center_kpt):
        """在图像上标注角度、计数和阶段信息"""
        if self.annotator is None:
            return

        x, y = int(center_kpt[0]), int(center_kpt[1])
        #绘制角度
        cv2.putText(self.im0, f"Angle: {angle_text:.1f}", (x + 20, y - 40),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)

        #绘制计数
        cv2.putText (self.im0, f"Count: {count_text}", (x + 20, y - 10),
                     cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)

        #绘制阶段
        cv2.putText (self.im0, f"Stage: {stage_text}", (x + 20, y + 20),
                     cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)


    def obj_exe(self, im0, results):
        """
        Function used to count the gym steps.
        Args:
            im0 (ndarray): Current frame from the video stream.
            results (list): Pose estimation data.
        """
        self.im0 = im0

        if not len(results[0]):
            return self.im0

        # Initialize annotator object
        self.annotator = Annotator(self.im0, line_width=self.tf)

        # If there are more humans in the current frame, extend the count, angle, and stage lists
        if len(results[0]) > len(self.count):
            new_human = len(results[0]) - len(self.count)
            self.count.extend([0] * new_human)
            self.angle.extend([0] * new_human)
            self.stage.extend(["-"] * new_human)

        # Get keypoints from the pose estimation result
        self.keypoints = results[0].keypoints.data

        # Iterate over each detected person
        for ind, k in enumerate(self.keypoints):
            if self.pose_type in {"pushup", "pullup", "abworkout", "squat"}:
                # Calculate the angle between keypoints
                self.angle[ind] = self.estimate_pose_angle(
                    k[int(self.kpts_to_check[0])].cpu(),
                    k[int(self.kpts_to_check[1])].cpu(),
                    k[int(self.kpts_to_check[2])].cpu(),
                )

                # Draw keypoints (no need to pass 'shape' argument)
                self.im0 = self.draw_specific_points(k, self.kpts_to_check, radius=10)

                # Determine the exercise stage and count
                if self.pose_type in {"abworkout", "pullup"}:
                    if self.angle[ind] > self.poseup_angle:
                        self.stage[ind] = "down"
                    if self.angle[ind] < self.posedown_angle and self.stage[ind] == "down":
                        self.stage[ind] = "up"
                        self.count[ind] += 1

                elif self.pose_type in {"pushup", "squat"}:
                    if self.angle[ind] > self.poseup_angle:
                        self.stage[ind] = "up"
                    if self.angle[ind] < self.posedown_angle and self.stage[ind] == "up":
                        self.stage[ind] = "down"
                        self.count[ind] += 1

                # Annotate the angle, count, and stage on the image
                self.plot_angle_and_count_and_stage(
                    angle_text=self.angle[ind],
                    count_text=self.count[ind],
                    stage_text=self.stage[ind],
                    center_kpt=k[int(self.kpts_to_check[1])],
                )

            # Draw keypoint lines
            self.annotator.kpts(k, radius=1, kpt_line=True)

        return self.im0