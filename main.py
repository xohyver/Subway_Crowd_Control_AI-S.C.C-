import cv2
import torch
import pygame
from threading import Thread

# 모델 불러오기
model = torch.hub.load('ultralytics/yolov5', 'custom', path="./Subway_Crowd_control_AI/Subway_Crowd_control_AI.pt")

#사전 설정
pygame.mixer.init()
is_audio_playing = False  #음성 중복 재생을 막기위한 변수 설정

cap = cv2.VideoCapture(0)

# 최대 인원 수 설정
max_people = int(input("최대 허용 인원을 입력하세요: "))

# 안내방송 재생 함수
def play_audio():
    pygame.mixer.music.load("./Subway_Crowd_control_AI/announcements/ttswomanEng.mp3")
    pygame.mixer.music.play()
    while pygame.mixer.music.get_busy():
        continue

while True:
    ret, frame = cap.read()
    if not ret:
        break

    frame_rgb = frame[:, :, ::-1]  #rgb를 bgr로 변환
    results = model(frame_rgb)
    
    head_count = sum(1 for *box, label, conf in results.xyxy[0] if int(label) == 0)  #모델을 통해 카운트 된 사람 머리 개수

    if not is_audio_playing and head_count > max_people:
        Thread(target=play_audio).start() #Thread 활용하여 병렬처리
        is_audio_playing = True
        
    elif is_audio_playing and not pygame.mixer.music.get_busy():
        # 안내 방송 종료 후 상태 초기화
        is_audio_playing = False

    # 화면 출력
    cv2.imshow("Webcam", frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break


cap.release()
cv2.destroyAllWindows()
