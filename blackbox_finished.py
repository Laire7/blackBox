import cv2
import os, shutil
import time
import multiprocessing
import keyboard  # ✅ Detects 'q' anywhere
from datetime import datetime

# ✅ 모든 뜨레들을 한 변수로 관리
running = multiprocessing.Value('b', True)  # 불리언 (0 or 1)

# 전역 변수들 
isWEBCAM = False #웹캠이 있는지 확인
basic_path = 'C:\\Users\\syoun\\blackbox\\'
video_duration = 10
folder_duration = 40
storageCheck_duration = 80
max_storage = 5000
folderSize = 0

## 비디오 녹화하고 저장하기
def createVideo(now):
    print("🔴 비디오 녹화 시작") 
    ##녹화 설정
    #webcam인 경우 카메라 번호를 입력
    if isWEBCAM: 
        cap = cv2.VideoCapture(0)
    else: #webcam이 아닌 경우 지정한 비디오로부터 녹화 시작하기
        video_fileName = os.path.join(basic_path, 'data', 'vtest.avi')
        cap = cv2.VideoCapture(video_fileName) 
    
    fourcc = cv2.VideoWriter_fourcc(*'XVID')  #VideoWriter 객체 생성하기 (코덱?으로 설정)
    videoName = currDateTime_toStr(now,"video") #비디오 파일 이름 설정
    fps = int(cap.get(cv2.CAP_PROP_FPS))  #프레임 레이트 설정
    frameSize = (int(cap.get(cv2.CAP_PROP_FRAME_WIDTH)), int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))) # 카메라의 이미지 사이즈
    #출력 파일 설정
    out_color = cv2.VideoWriter(videoName + '.avi', fourcc, fps, frameSize)
    # out_gray = cv2.VideoWriter(videoName + '_gray.avi', fourcc, fps, frameSize, isColor=False) 
    
    #녹화 시작
    start_time = time.time() #녹화 시간 추적
    while time.time() - start_time < video_duration:
        #프레임 읽기
        retval, frame = cap.read()  
        #프레임 저장 
        out_color.write(frame) 
        # grayFrame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY) #영상을 흑백으로 바꾸기
        # out_gray.write(grayFrame) #흑백 영상 출력
        #영상 미리보기
        cv2.imshow('Color Recording', frame)  
        # cv2.imshow('Grayscale Recording', grayFrame) #흑백 영상 미리보기
        # 녹음 중에도 프로그램 종료 감지
        delay = int(1000 / fps) # 프레임이 바뀌는 빈도에 맞춰 키보드 입력 감지
        if cv2.waitKey(delay) == 113: 
            break   

    #비디오 녹화 출력하기
    print("녹화 종료")
    cap.release()
    out_color.release()
    # out_gray.release()
    cv2.destroyAllWindows() #미리보기 창 닫기

## 날짜+현재시간으로 폴더 이름 짓기
def currDateTime_toStr(now, fileType):
    now_toStr = ''
    now_toStr = now.strftime("%Y%m%d_%H%M")
    if fileType == "video":
        now_toStr += '\\' + now.strftime("%Y%m%d_%H%M%S")
    return basic_path + now_toStr

## 새로운 폴더 만들기         
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

# 폴더 용량 측정하기
def check_folderSize():
    global folderSize
    try:
        #폴더 내 모든 파일과 하위 폴더를 순회
        for dirpath, dirnames, filenames in os.walk(basic_path):
            for f in filenames:
                f_p = os.path.join(dirpath, f)
                #os.path.islink() 함수를 사용하여 심볼릭 링크는 크기에 포함하지 않도록 함
                if not os.path.islink(f_p):
                    folderSize += int(round(os.path.getsize(f_p)/ (1024*1024))) #폴더 용량을 byte 단위에서 -> megabyte (mb)로 변경
                    print(f'folderSize is {folderSize}')
                if keyboard.is_pressed('q'):
                    running.value = False
                    break
            if keyboard.is_pressed('q'):
                running.value = False
                break
    except FileNotFoundError:
        print(f"<오류> 폴더를 찾을 수 없습니다: {basic_path}")

##폴더 용량 관리하기
#폴더 사이즈를 유지하기 위해 폴더를 처음 만든 순서대로 지우기
def deleteFiles():
    try: 
        folder_list = [f for f in os.listdir(basic_path) if os.path.isdir(os.path.join(basic_path, f)) and '_' in f]
        sorted_folder_list = sorted(folder_list, key=lambda x: tuple(map(int, x.split('_'))) if '_' in x else (99999999, 99)) # sortFolder by dateCreated (as specified in folder name)
        print(f'폴더 정렬: {sorted_folder_list}')
        del_i = 0 # 파일을 만드는 순서대로 지우기
        global folderSize
        while (folderSize>max_storage) and running.value and (del_i<len(sorted_folder_list)):
            folder_path = os.path.join(basic_path, sorted_folder_list[del_i])
            for root, dirs, files in os.walk(folder_path, topdown=False):
                for name in files:
                    file_path = os.path.join(root, name)
                    os.remove(file_path)
                    folderSize -= os.path.getsize(file_path) / (1024 * 1024)
                for name in dirs:
                    os.rmdir(os.path.join(root, name))
            os.rmdir(folder_path)
            print(f'removedFolder: {folder_path}')
            del_i += 1
        print(f'<용량 업데이트>현재 폴더 용량은: {folderSize}')
    except Exception as e:
        print(f"<오류> 파일 삭제 중 오류 발생: {e}")

### 🔹 저장 용량 확인 프로세스
def checkStorageFunc(running):
    global folderSize
    while running.value:
        print("📦 폴더 용량 확인 중...")
        check_folderSize()
        if folderSize > max_storage:
            print("⚠ 용량 초과! 파일 삭제 필요")
            deleteFiles()
    print("🛑 저장 용량 확인 종료")

### 🔹 메인 실행 부분
if __name__ == "__main__":
    p1 = multiprocessing.Process(target=createBlackbox, args=(running,))
    p2 = multiprocessing.Process(target=checkStorageFunc, args=(running,))

    p1.start()
    p2.start()

    # ✅ 키보드에서'q' 누르면 모든 프로그램들을 즉시 종료
    while running.value:  
        if keyboard.is_pressed('q'):  # ✅ 키보드에서 'q' 감지
            print("🛑 프로그램 종료 요청됨")
            running.value = False
            break

    # ✅ 프로그램 종료
    p1.terminate()
    p2.terminate()

    p1.join(timeout=5)
    p2.join(timeout=5)

    print("✅ 블랙박스 프로그램 종료 완료")
