import cv2
import torch
import pygame
from threading import Thread

# 모델 불러오기
model = torch.hub.load('ultralytics/yolov5', 'custom', path="./Subway_Crowd_control_AI/Subway_Crowd_control_AI.pt")

# pygame 초기화
pygame.mixer.init()

# 음성 안내 방송 재생 상태 변수
is_audio_playing = False

# 카메라 설정
cap = cv2.VideoCapture(0)

# 최대 인원 수 입력 받기
max_people = int(input("최대 허용 인원을 입력하세요: "))

# 음성 안내 방송 재생 함수
def play_audio():
    pygame.mixer.music.load("./Subway_Crowd_control_AI/announcements/ttswomanEng.mp3")
    pygame.mixer.music.play()
    while pygame.mixer.music.get_busy():
        continue

while True:
    # 웹캠 프레임 읽기
    ret, frame = cap.read()
    if not ret:
        break

    # YOLOv5를 통해 사람 감지
    frame_rgb = frame[:, :, ::-1]
    results = model(frame_rgb)
    
    # 사람 수 계산 (label이 0인 경우 사람으로 간주)
    head_count = sum(1 for *box, label, conf in results.xyxy[0] if int(label) == 0)

    # 감지된 인원이 최대 인원을 초과하는지 확인
    if not is_audio_playing and head_count > max_people:
        # 음성 안내 방송 재생을 비동기로 실행
        Thread(target=play_audio).start()
        is_audio_playing = True
    elif is_audio_playing and not pygame.mixer.music.get_busy():
        # 방송이 끝나면 상태를 초기화
        is_audio_playing = False

    # 웹캠 화면 출력 (실시간 피드백)
    cv2.imshow("Webcam", frame)

    # 'q'를 눌러 프로그램 종료
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# 자원 해제
cap.release()
cv2.destroyAllWindows()
