import cv2
import os, shutil
import time
import multiprocessing
import keyboard  # ✅ Detects 'q' anywhere
from datetime import datetime

# ✅ Shared variable for stopping all processes
running = multiprocessing.Value('b', True)  # Boolean flag (0 or 1)

isWEBCAM = False #웹캠이 있는지 확인
basic_path = 'C:\\Users\\syoun\\blackbox\\'
video_duration = 10
folder_duration = 40
storageCheck_duration = 80
max_storage = 270
folderSize = 0

##비디오 만들기 함수들
#비디오 생성하기
def createVideo(now):
    print("🔴 비디오 녹화 시작") 
    ##녹화 설정
    #webcam인 경우 카메라 번호를 입력
    if isWEBCAM: 
        cap = cv2.VideoCapture(0)
    else: #webcam이 아닌 경우 지정한 비디오로부터 녹화 시작하기
        video_fileName = os.path.join(basic_path, 'data', 'vtest.avi')
        cap = cv2.VideoCapture(video_fileName) 
    #VideoWriter 객체 생성하기
    fourcc = cv2.VideoWriter_fourcc(*'XVID') #코덱?? 설정
    videoName = currDateTime_toStr(now,"video") #비디오 파일 이름 설정
    fps = int(cap.get(cv2.CAP_PROP_FPS))  #프레임 레이트 설정
    # 카메라의 이미지 사이즈
    frameSize = (int(cap.get(cv2.CAP_PROP_FRAME_WIDTH)), int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT)))
    #출력 파일 설정
    out_color = cv2.VideoWriter(videoName + '.avi', fourcc, fps, frameSize)
    # out_gray = cv2.VideoWriter(videoName + '_gray.avi', fourcc, fps, frameSize, isColor=False) 
    
    #녹화 시작
    recording = True 
    start_time = time.time() #녹화 시간 추적
    while time.time() - start_time < video_duration:
        retval, frame = cap.read()  #프레임 읽기
        #프레임 저장
        out_color.write(frame)  
        grayFrame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY) 
        # out_gray.write(grayFrame) 
        #미리보기 표시
        cv2.imshow('Color Recording', frame)  
        # cv2.imshow('Grayscale Recording', grayFrame)
        delay = int(1000 / fps)
        if cv2.waitKey(delay) == 113:
            break   

    #비디오 녹화 출력하기
    print("녹화 종료")
    cap.release()
    out_color.release()
    # out_gray.release()
    cv2.destroyAllWindows() #미리보기 창 닫기

#날짜+현재시간으로 폴더 이름 짓기
def currDateTime_toStr(now, fileType):
    now_toStr = ''
    now_toStr = now.strftime("%Y%m%d_%H%M")
    if fileType == "video":
        now_toStr += '\\' + now.strftime("%Y%m%d_%H%M%S")
    return basic_path + now_toStr

#새로운 폴더 만들기         
def createFolder(now):
    #새 폴더 경로 지정하기
    new_path = currDateTime_toStr(now, "folder")
    print(new_path)
    if not os.path.exists(new_path): # 동일한 폴더가 있는지 확인 
        os.mkdir(new_path) #지정한 경로에 새로운 폴더 추가
    else:
        print("📦 동일한 폴더가 있어 폴더 생선 취소")

### 🔹 블랙박스 프로세스 (폴더 & 녹화)
def createBlackbox(running):
    print(f'🔴 블랙박스 시작: {datetime.now()}')
    
    while running.value:  # ✅ Use shared value
        now = datetime.now()
        createFolder(now)
        createVideo(now)
        time.sleep(folder_duration)  # Sleep for 5 seconds
    print("🛑 블랙박스 종료")

### 🔹 저장 용량 확인 프로세스
def checkStorageFunc(running):
    global folderSize
    while running.value:
        print("📦 폴더 용량 확인 중...")
        time.sleep(storageCheck_duration)  # Simulate checking storage

        if folderSize > max_storage:
            print("⚠ 용량 초과! 파일 삭제 필요")

    print("🛑 저장 용량 확인 종료")

### 🔹 메인 실행 부분
if __name__ == "__main__":
    running = multiprocessing.Value('b', True)  # ✅ Shared boolean flag

    p1 = multiprocessing.Process(target=createBlackbox, args=(running,))
    p2 = multiprocessing.Process(target=checkStorageFunc, args=(running,))

    p1.start()
    p2.start()

    # ✅ Main process detects 'q' and stops all child processes
    while running.value:  
        if keyboard.is_pressed('q'):  # ✅ Global key press detection
            print("🛑 프로그램 종료 요청됨")
            running.value = False
            break

    # ✅ Properly stop processes
    p1.terminate()
    p2.terminate()

    p1.join(timeout=5)
    p2.join(timeout=5)

    print("✅ 블랙박스 프로그램 종료 완료")
