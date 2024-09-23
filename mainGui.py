import sys
import cv2
import torch
import pygame
from gtts import gTTS
from threading import Thread
from PyQt5.QtCore import QTimer, Qt
from PyQt5.QtGui import QImage, QPixmap
from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QLineEdit, QPushButton, QVBoxLayout

# YOLOv5 모델 로드
model = torch.hub.load('ultralytics/yolov5', 'custom', path="./Subway_Crowd_control_AI/Subway_Crowd_control_AI.pt")

# pygame 초기화
pygame.mixer.init()

# 안내 방송 재생 함수
def play_audio_announcement():
    pygame.mixer.music.load("./Subway_Crowd_control_AI/announcements/ttswomanEng.mp3")
    pygame.mixer.music.play()
    while pygame.mixer.music.get_busy():
        continue

# 글로벌 상태 변수
is_audio_playing = False
is_head_count_above_threshold = False

# 머리 개수 감지 및 상태 업데이트 함수
def detect_and_update_head_count():
    global is_audio_playing, is_head_count_above_threshold

    while True:
        ret, frame = video_capture.read()
        frame_rgb = frame[:, :, ::-1]
        detection_results = model(frame_rgb)
        head_count = sum(1 for *box, label, conf in detection_results.xyxy[0] if int(label) == 0)

        if not is_audio_playing:
            if head_count > (max_people - 1) and not is_head_count_above_threshold:
                audio_thread = Thread(target=play_audio_announcement)
                audio_thread.start()
                is_audio_playing = True
                is_head_count_above_threshold = True
            elif head_count <= (max_people - 1):
                is_head_count_above_threshold = False
        elif is_audio_playing and not pygame.mixer.music.get_busy():
            if head_count > (max_people - 1):
                audio_thread = Thread(target=play_audio_announcement)
                audio_thread.start()
                is_head_count_above_threshold = True
            else:
                is_audio_playing = False

# 메인 윈도우 클래스
class HeadCountApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setup_ui()

    # UI 구성 함수
    def setup_ui(self):
        self.setWindowTitle("Head Count Monitoring")
        self.setGeometry(100, 100, 800, 600)

        self.max_people_label = QLabel("최대 허용 인원수를 입력하세요: ")
        self.max_people_input = QLineEdit()
        self.start_button = QPushButton("감지 시작")
        self.start_button.clicked.connect(self.start_head_count_detection)

        self.video_display = QLabel()
        self.video_display.setFixedSize(640, 480)

        layout = QVBoxLayout()
        layout.addWidget(self.max_people_label)
        layout.addWidget(self.max_people_input)
        layout.addWidget(self.start_button)
        layout.addWidget(self.video_display)

        self.setLayout(layout)

    # 감지 시작 함수
    def start_head_count_detection(self):
        global max_people, video_capture
        max_people = int(self.max_people_input.text())
        video_capture = cv2.VideoCapture(0)

        detection_thread = Thread(target=detect_and_update_head_count)
        detection_thread.start()

        self.start_video_stream()

    # 실시간 비디오 스트리밍 시작
    def start_video_stream(self):
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_video_frame)
        self.timer.start(1000 // 30)

    # 실시간 비디오 프레임 업데이트
    def update_video_frame(self):
        ret, frame = video_capture.read()
        if ret:
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            detection_results = model(frame_rgb)
            frame_with_boxes = draw_detection_boxes(frame_rgb, detection_results)

            height, width, channels = frame_with_boxes.shape
            bytes_per_line = channels * width
            qt_image = QImage(frame_with_boxes.data, width, height, bytes_per_line, QImage.Format_RGB888)
            scaled_image = qt_image.scaled(640, 480, aspectRatioMode=1)
            self.video_display.setPixmap(QPixmap.fromImage(scaled_image))

    # 'Q' 키를 눌렀을 때 애플리케이션 종료
    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Q:
            video_capture.release()
            app.quit()
            sys.exit()

# 감지된 객체에 경계 상자 그리기
def draw_detection_boxes(frame, detection_results):
    for *box, label, conf in detection_results.xyxy[0]:
        if int(label) == 0:  # 사람이 감지된 경우
            x1, y1, x2, y2 = map(int, box)
            cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
    return frame

if __name__ == '__main__':
    app = QApplication(sys.argv)
    main_window = HeadCountApp()
    main_window.show()
    sys.exit(app.exec_())
