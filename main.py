import sys
import cv2
import torch
import pygame
from gtts import gTTS
from threading import Thread
from PyQt5.QtCore import QTimer, Qt
from PyQt5.QtGui import QImage, QPixmap
from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QLineEdit, QPushButton, QVBoxLayout

# 모델 불러오기
model = torch.hub.load('ultralytics/yolov5', 'custom', path="C:/ai/headhunter/best.pt")

# pygame 초기화
pygame.mixer.init()

# 음성 송출을 담당할 함수
def play_announcement():
    pygame.mixer.music.load("C:/ai/headhunter/ttswomanEng.mp3")
    pygame.mixer.music.play()
    while pygame.mixer.music.get_busy():
        continue

is_announcement_playing = False
is_previous_head_count_more_than_2 = False

# 머리 개수 업데이트 함수
def update_head_count():
    global is_announcement_playing, is_previous_head_count_more_than_2

    while True:
        ret, frame = cap.read()
        frame_rgb = frame[:, :, ::-1]
        results = model(frame_rgb)
        num_heads = sum([1 for *box, label, conf in results.xyxy[0] if int(label) == 0])

        if not is_announcement_playing:
            if num_heads > (inline - 1) and not is_previous_head_count_more_than_2:
                announcement_thread = Thread(target=play_announcement)
                announcement_thread.start()
                is_announcement_playing = True
                is_previous_head_count_more_than_2 = True
            elif num_heads <= (inline - 1) and is_previous_head_count_more_than_2:
                is_previous_head_count_more_than_2 = False
        elif is_announcement_playing and pygame.mixer.music.get_busy() == False:
            if num_heads > (inline - 1):
                announcement_thread = Thread(target=play_announcement)
                announcement_thread.start()
                is_previous_head_count_more_than_2 = True
            else:
                is_announcement_playing = False

class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("Head Count App")
        self.setGeometry(100, 100, 800, 600)

        self.inline_label = QLabel("Set the maximum number of people:")
        self.inline_input = QLineEdit()
        self.start_button = QPushButton("Start")
        self.start_button.clicked.connect(self.start_detection)

        self.video_label = QLabel()
        self.video_label.setFixedSize(640, 480)  # 비디오 화면 크기 조절

        layout = QVBoxLayout()
        layout.addWidget(self.inline_label)
        layout.addWidget(self.inline_input)
        layout.addWidget(self.start_button)
        layout.addWidget(self.video_label)

        self.setLayout(layout)

    def start_detection(self):
        global inline, cap
        inline = int(self.inline_input.text())
        #카메라 인덱싱
        cap = cv2.VideoCapture(0)
        detection_thread = Thread(target=update_head_count)
        detection_thread.start()
        self.start_webcam_stream()

    def start_webcam_stream(self):
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_webcam_frame)
        self.timer.start(1000 // 30)  # 웹캠 프레임 업데이트 간격 설정 (정수로 변환)

    def update_webcam_frame(self):
        ret, frame = cap.read()
        if ret:
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            results = model(frame_rgb)
            frame_with_boxes = draw_boxes(frame_rgb, results)  # 경계 상자 그리기 추가
            h, w, ch = frame_with_boxes.shape
            bytes_per_line = ch * w
            convert_to_Qt_format = QImage(frame_with_boxes.data, w, h, bytes_per_line, QImage.Format_RGB888)
            p = convert_to_Qt_format.scaled(640, 480, aspectRatioMode=1)
            self.video_label.setPixmap(QPixmap.fromImage(p))

    # 'q' 키를 눌렀을 때 어플리케이션 종료
    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Q:
            app.quit()  # 어플리케이션 종료
            sys.exit()  # 터미널 종료

# 객체 감지 결과에 경계 상자를 그리는 함수
def draw_boxes(frame, results):
    for *box, label, conf in results.xyxy[0]:
        if int(label) == 0:  # 클래스 인덱스가 0인 경우
            x1, y1, x2, y2 = map(int, box)
            cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)  # 경계 상자 그리기 (녹색)
    return frame

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
