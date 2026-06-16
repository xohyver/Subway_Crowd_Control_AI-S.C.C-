import cv2
import pygame
from threading import Thread
from ultralytics import YOLO


model = YOLO("C:\MyProjects\Subway_Crowd_Control_AI\e150b16p30.pt")


pygame.mixer.init()
is_audio_playing = False

cap = cv2.VideoCapture(0)


max_people = int(input("최대 허용 인원을 입력하세요: "))


# 안내방송 재생 함수
def play_audio():
    global is_audio_playing
    pygame.mixer.music.load("./announcements/ttswomanEng.mp3")
    pygame.mixer.music.play()
    while pygame.mixer.music.get_busy():
        continue
    is_audio_playing = False 

while True:
    ret, frame = cap.read()
    if not ret:
        break

    # YOLOv11 추론
    results = model(frame, verbose=False)[0]

    # class 0 (head) 개수 카운트
    head_count = len(results.boxes)

    # 바운딩박스 그리기
    for box in results.boxes:
        x1, y1, x2, y2 = map(int, box.xyxy[0])
        cls = int(box.cls[0])
        label = model.names[cls]
        cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
        cv2.putText(frame, label, (x1, y1 - 5),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)

    # 현재 인원 수 화면 출력
    status_color = (0, 0, 255) if head_count > max_people else (0, 255, 0)
    cv2.putText(frame, f"Count: {head_count} / {max_people}",
                (10, 40), cv2.FONT_HERSHEY_SIMPLEX, 1.2, status_color, 2)

    # 안내방송 트리거
    if not is_audio_playing and head_count > max_people:
        is_audio_playing = True
        Thread(target=play_audio, daemon=True).start()

    cv2.imshow("S.C.C - Subway Crowd Control", frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
pygame.mixer.quit()
