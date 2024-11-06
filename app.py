import sys
import cv2
import numpy as np
import insightface
from PyQt5 import QtWidgets, QtGui, QtCore
from PyQt5.QtWidgets import QLabel, QVBoxLayout, QHBoxLayout, QWidget, QFrame, QPushButton
from PyQt5.QtGui import QPixmap, QImage, QIcon
from PyQt5.QtCore import Qt, QTimer
from insightface.app import FaceAnalysis
import onnxruntime as ort


class VideoConferenceApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Video Conference")
        self.setGeometry(100, 100, 1000, 700)
        self.setStyleSheet("background-color: #f4f5f7;")

        # Set default values for attributes
        self.using_gpu = False
        self.swap_faces = False

        # Initialize face swap model and face detection
        self.initialize_models()

        # Main layout
        main_layout = QVBoxLayout(self)

        # Conditional GPU alert banner
        if not self.using_gpu:
            gpu_alert = self.create_gpu_alert()
            main_layout.addWidget(gpu_alert)

        # Header with meeting info
        header = self.create_header()
        main_layout.addWidget(header)

        # Main video area with live webcam feed
        self.video_area = self.create_main_video_area()
        main_layout.addWidget(self.video_area)

        # Control buttons
        controls = self.create_controls()
        main_layout.addLayout(controls)

        self.setLayout(main_layout)

        # Start webcam feed
        self.cap = cv2.VideoCapture(0)
        self.timer = QTimer()
        self.timer.timeout.connect(self.display_webcam_feed)
        self.timer.start(30)  # Update frame every 30 ms

    def initialize_models(self):
        # Check if GPU (CUDAExecutionProvider) is available
        available_providers = ort.get_available_providers()
        swapper_model_path = 'src/inswapper_128.onnx'

        # Attempt to use GPU if CUDAExecutionProvider is available
        if 'CUDAExecutionProvider' in available_providers:
            try:
                self.swapper = insightface.model_zoo.get_model(swapper_model_path, download=False, download_zip=False)
                self.providers = ['CUDAExecutionProvider']
                self.using_gpu = True
                print("Using GPU for processing.")
            except Exception as e:
                print(f"Failed to use GPU: {e}")
                self.providers = ['CPUExecutionProvider']
                self.using_gpu = False
                print("Falling back to CPU for processing.")
        else:
            print("CUDAExecutionProvider not available. Falling back to CPU.")
            self.providers = ['CPUExecutionProvider']
            self.using_gpu = False
            # Initialize the model on CPU if GPU is not available
            self.swapper = insightface.model_zoo.get_model(swapper_model_path, download=False, download_zip=False)

        # Initialize FaceAnalysis for face detection
        self.app_model = FaceAnalysis(name='buffalo_l', providers=self.providers)
        self.app_model.prepare(ctx_id=0 if self.using_gpu else -1, det_size=(320, 320))

        # Load default image for face swapping
        default_img_path = 'assets/face.jpg'
        self.default_img = cv2.imread(default_img_path)
        faces_in_default_img = self.app_model.get(self.default_img)
        if len(faces_in_default_img) == 0:
            raise Exception("No face detected in the default image.")
        self.default_face = faces_in_default_img[0]

    def create_gpu_alert(self):
        # Create a banner for non-GPU alert
        alert = QLabel("We are not using GPU")
        alert.setFixedHeight(40)
        alert.setAlignment(Qt.AlignCenter)
        alert.setStyleSheet("""
            background-color: #ffcccb;
            color: #b22222;
            font-size: 14px;
            font-weight: bold;
            border-radius: 10px;
            padding: 5px;
        """)
        return alert

    def create_header(self):
        header = QFrame()
        header.setFixedHeight(80)
        header.setStyleSheet("background-color: white; border-radius: 10px;")

        header_layout = QHBoxLayout(header)
        header_layout.setContentsMargins(20, 10, 20, 10)

        meeting_info = QLabel("Demo Call")
        meeting_info.setStyleSheet("font-size: 16px; color: #333333; font-weight: bold;")

        participants = QLabel()
        participants.setPixmap(QPixmap("user_icon.png").scaled(30, 30, Qt.KeepAspectRatio, Qt.SmoothTransformation))

        meeting_id = QLabel("| Project Morphis")
        meeting_id.setStyleSheet("font-size: 14px; color: #666666;")

        header_layout.addWidget(meeting_info)
        header_layout.addStretch()
        header_layout.addWidget(participants)
        header_layout.addWidget(meeting_id)

        return header

    def create_main_video_area(self):
        # Use QWidget for responsive resizing without fixed size
        self.video_frame = QWidget()
        self.video_frame.setStyleSheet("""
            background-color: #eeeeee; 
            border-radius: 20px;
            border: 2px solid #cccccc;
        """)

        # QLabel for displaying video without fixed size
        self.video_label = QLabel(self.video_frame)
        self.video_label.setAlignment(Qt.AlignCenter)
        self.video_label.setStyleSheet("border-radius: 18px;")

        # Use a layout to control positioning
        video_layout = QVBoxLayout(self.video_frame)
        video_layout.setContentsMargins(10, 10, 10, 10)
        video_layout.addWidget(self.video_label)

        return self.video_frame

    def resizeEvent(self, event):
        # Update video display size when the window is resized
        self.update_video_display_size()
        super().resizeEvent(event)

    def update_video_display_size(self):
        # Set video_label size to fit within video_frame with padding
        frame_width = self.video_frame.width()
        frame_height = self.video_frame.height()
        self.video_label.resize(frame_width - 20, frame_height - 20)

    def create_controls(self):
        control_layout = QHBoxLayout()
        control_layout.setAlignment(Qt.AlignCenter)

        # Swap button for toggling face swap
        self.swap_button = QPushButton()
        self.swap_button.setFixedSize(50, 50)
        self.swap_button.setIcon(QIcon("assets/rec.png"))  # Inactive state image
        self.swap_button.setIconSize(QtCore.QSize(40, 40))
        self.swap_button.setStyleSheet("""
            border: none;
            border-radius: 25px;
            background-color: transparent;
        """)
        self.swap_button.clicked.connect(self.toggle_face_swap)

        # GPU status button, showing the correct icon based on whether GPU is available
        gpu_icon = "gpu.png" if self.using_gpu else "cpu.png"
        self.gpu_button = QPushButton()
        self.gpu_button.setFixedSize(50, 50)
        self.gpu_button.setIcon(QIcon(gpu_icon))
        self.gpu_button.setIconSize(QtCore.QSize(40, 40))
        self.gpu_button.setStyleSheet("""
            border: none;
            border-radius: 25px;
            background-color: transparent;
        """)

        # Add buttons to the layout
        control_layout.addWidget(self.swap_button)
        control_layout.addWidget(self.gpu_button)

        return control_layout

    def toggle_face_swap(self):
        # Toggle face swap state and change icon
        self.swap_faces = not self.swap_faces
        self.swap_button.setIcon(QIcon("assets/rec2.png") if self.swap_faces else QIcon("assets/rec.png"))

    def display_webcam_feed(self):
        ret, frame = self.cap.read()
        if ret:
            # Resize frame for efficiency
            frame = cv2.resize(frame, (640, 360))

            if self.swap_faces:
                frame = self.perform_face_swap(frame)

            # Convert frame to display in QLabel
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            qt_image = QImage(rgb_frame.data, rgb_frame.shape[1], rgb_frame.shape[0], QImage.Format_RGB888)
            if not qt_image.isNull():  # Ensure image is not null before displaying
                self.video_label.setPixmap(QPixmap.fromImage(qt_image))

    def perform_face_swap(self, frame):
        faces_in_frame = self.app_model.get(frame)
        if len(faces_in_frame) > 0:
            face_in_frame = faces_in_frame[0]
            try:
                frame = self.swapper.get(frame, face_in_frame, self.default_face, paste_back=True)
            except Exception as e:
                print(f"Error during face swap: {e}")
        return frame

    def closeEvent(self, event):
        self.cap.release()
        event.accept()


if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    window = VideoConferenceApp()
    window.show()
    sys.exit(app.exec_())
