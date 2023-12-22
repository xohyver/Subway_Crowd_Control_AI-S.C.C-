# Subway_Crowd_Control_AI
이것은 지하철의 인원을 효과적으로 관리하기 위한 프로그램입니다. 사람의 머리를 인식하여 인원을 세고, 설정한 최대인원에 도달하면 안내방송이 출력됩니다/This is a program designed to effectively manage the number of passengers in the subway. It detects people's heads to count the number of passengers, and when the maximum capacity is reached, it plays a guidance announcement.

#How_to_Use
1. main.py에서 best50.pt파일과 안내음성 파일의 디렉토리를 설정하는 코드를 변경하세요./Modify the directory paths for "best50.pt" and the guidance audio files in the "main.py" file.
2. main.py파일을 실행시키세요./Run main.py
3. 처음 뜨는 화면에 최대인원을 설정하고 start를 누르세요./On the initial screen, set the maximum capacity and press 'start'.
4. 객체인식을 수행하면 됩니다./Perform object recognition.

#Train
직접 머리 이미지 800장을 수집한 뒤  roboflow를 이용해 데이터셋을 생성한 후, yolov5로 커스텀 트레이닝을 하여 가중치 파일인 best50.pt을 추출했다. best50.pt를 이용하여 객체인식을 수행한다./After collecting 800 head images manually and generating a dataset using Roboflow, I performed custom training with YOLOv5 to obtain the weight file 'best50.pt'. I will use 'best50.pt' to perform object recognition.

#Tips
안내음성의 성별을 바꿀 수 있습니다. ttswomanEng/ttsmanEng에 따라 각각 남성, 여성의 음성을 담고 있습니다. main.py에서  play_announcement함수 내에 음성파일 경로를 수정하세요./You can change the gender of the guidance voice. Depending on whether you choose "ttswomanEng" or "ttsmanEng," you will have female or male voices, respectively. Please modify the audio file path within the "play_announcement" function in "main.py.





