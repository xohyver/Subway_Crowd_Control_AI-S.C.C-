# Subway Crowd Control AI(S.C.C)
-how to use : 



# 📃 프로젝트 정보

### 1. 제작기간
'23.07.07 ~ '23.09.02

### 2. 참여 인원
> |                    Name                    |  Position   |
> | :----------------------------------------: | :---------: |
> | [태현수](https://github.com/xohyver/) |   AI develop  |

### 3.[역할] : AI 개발자
- 시스템 설계 및 구현 :
병렬 Thread 및 Opencv 이용 실시간 웹캠 시스템 구축, Pygame 이용 안내방송 송출 설계 
- 데이터 수집 및 모델 학습 :
모델 학습을 위한 이미지 수집 및 Yolov5 커스텀 트레이닝

### 4. 사용 기술
> Python3  
> Opencv  
> Yolov5  
> Torch

# 📊 Structure
- 카메라가 사람의 머리 상단을 촬영함
- Yolov5 이용 객체 인식으로 머리 개수 파악
- 설정해둔 임계값 이상의 머리 감지시 안내방송 mp3 재생으로 인원 통제 유도

# 🔑 핵심기능

### 1. 최대인원 설정
> 프로그램 실행 후 사용자는 카메라가 비추는 공간의 최대 인원 수를 입력합니다.

### 2. 실시간 웹캠 탐지
> Opencv 및 병렬 Thread로 실시간 객체탐지를 수행하여 인원을 파악합니다.

# 문제 해결
### 1. 촬영각 설계
> 처음 카메라 각도를 하방 45도로 설계했으나, 먼 거리의 객체 인식 정확도 저하 등의 문제로 카메라각을 천장에서 바닥을 바라보는 각도로 변경하여 정확도를 향상시킴

### 2. 모델 부적합
> 공개 모델을 사용한 결과 사람의 얼굴까지 한번에 인식하여 얼굴이 가려지면 정확도가 저하됨. 따라서 머리 상단만을 라벨링한 데이터를 수집하여 모델을 생성함

# 📕 기타 자료

### 시연영상
https://youtu.be/7izh1vydHPA?si=Bczb0R-mfdPYqIDC





















# Subway_Crowd_Control_AI
이것은 지하철의 인원을 효과적으로 관리하기 위한 프로그램입니다. 사람의 머리를 인식하여 인원을 세고, 설정한 최대인원에 도달하면 안내방송이 출력됩니다. 이 프로그램은 사람의 머리를 학습한 가중치 파일을 기반으로 구동됩니다./This is a program designed to effectively manage the number of passengers in the subway. It detects people's heads to count the number of passengers, and when the maximum capacity is reached, it plays a guidance announcement. This program is based on weight files that have been trained to detect human heads.


# How to use
1. main.py에서 Subway_Crowd_control_AI.pt 파일과 안내음성 파일의 디렉토리를 설정하는 코드를 변경하세요./Modify the directory paths for "Subway_Crowd_control_AI.pt" and the guidance audio files in the "main.py" file.
2. main.py파일을 실행시키세요./Run main.py
3. 처음 뜨는 화면에 최대인원을 설정하고 start를 누르세요./On the initial screen, set the maximum capacity and press 'start'.
4. 객체인식을 수행하면 됩니다./Perform object recognition.

# Train
직접 머리 이미지 800장을 수집한 뒤  roboflow를 이용해 데이터셋을 생성한 후, yolov5로 커스텀 트레이닝을 하여 가중치 파일인 Subway_Crowd_control_AI.pt을 추출했다. Subway_Crowd_control_AI.pt를 이용하여 객체인식을 수행한다./After collecting 800 head images manually and generating a dataset using Roboflow, I performed custom training with YOLOv5 to obtain the weight file 'Subway_Crowd_control_AI.pt'. I will use 'Subway_Crowd_control_AI.pt' to perform object recognition.

# Tips
1.안내음성의 성별을 바꿀 수 있습니다. ttswomanEng/ttsmanEng에 따라 각각 남성, 여성의 음성을 담고 있습니다. main.py에서  play_announcement함수 내에 음성파일 경로를 수정하세요./You can change the gender of the guidance voice. Depending on whether you choose "ttswomanEng" or "ttsmanEng," you will have female or male voices, respectively. Please modify the audio file path within the "play_announcement" function in "main.py.

2. 만약 웹캠을 연결하고싶다면 line 87에서 cap = cv2.VideoCapture(0)를 카메라 인덱스에 맞게 변경하세요./If you want to connect a webcam, please change "cap = cv2.VideoCapture(0)" on line 87 to the appropriate camera index.

3.mainGui.py는 Pyqt5를 사용하여 GUI가 존재하는 버전이고, main.py는 GUI가 존재하지 않는 버전입니다./MainGui.py is a version with a GUI using Pyqt5, and main.py is a version without a GUI.


이 코드는 하나의 문제가 있는데 코드를 종료하기 위해서 에디터 프로그램까지 완전히 종료해야한다는 점입니다. 터미널에서 Ctrl+C를 눌러도 음성 재생이 멈추지 않습니다. 이문제를 해결 가능한 방법을 아는 분은 nmykga@gmail.com으로 피드백 주시면 감사하겠습니다./The issue with this code is that in order to exit the code, you have to completely exit the editor program as well. Even if you press Ctrl+C in the terminal, the audio playback does not stop. If anyone knows a solution to this problem, please provide feedback to nmykga@gmail.com. Thank you.





