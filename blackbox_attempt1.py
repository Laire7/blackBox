#####!!!!!주의사항!!!!!
####2번째 스레드와 프로세스 동시에 이용하는 코드는 제대로 실행은 되지 않지만
####openCV 영상 개념들이 지금은 더 급한 것 같아
####금요일 설명부터 들을 생각입니다. 설명 제안해주셔서 감사합니다!

####블랙박스 만들기 (10분만/10개만 성공적으로 생성)
# 1. 60초에 동영상 한개가 생성되도록 한다.
#    파일명은 20240902_161903.avi

# 2. 폴더 생성은 날짜+현재시간
#    20240902_16 00분~59분
#    한시간마다 폴더 생성

# 3. 블랙박스 녹화 폴더가 500MB이면
#    가장 오래된 녹화 폴더 삭제

import cv2, os, time
import threading, multiprocessing
import numpy as np
from datetime import datetime

###글로벌 변수
running = True # 프로그램 종료 변수
isWEBCAM = False #웹캠이 있는지 확인
# basic_path = 'C:/Users/SBA/opencvDojang/blackboxData/' # 폴더 저장소 지정
basic_path = 'C:\\Users\\syoun\\blackbox\\' #집에서 사용하는 폴더 저장 경로
video_duration = 3 #비디오 몇 초까지 녹화 할지 지정
folder_duration = 5 #폴더를 몇 초마다 생성할지 지정
storageCheck_duration = 10 #폴더 용량 몇 초마다 확인 할지 지정
max_storage = 270 #최대 폴더 용량 지정하기(MB)
folderSize = 0 #새로운 폴더를 생성 할때마다 폴더 사이즈를 업데이트 하기 위해 글로버 변수로 지정

#프로그램 종료를 전달 할 수 있는 변수, lock 객체 생성 
running_duringThread = True
lock = threading.Lock() 

###스레드 설정
#비디오 녹화 시간 설정
def video_thread(time_stopVideo, running):
    print(f'video thread started')
    global running_duringThread
    for _ in range(video_duration):
        if cv2.waitKey(1) & 0xFF == ord('q'):
            running_duringThread = False
            # running = False
            break
        if not (running and running_duringThread):  # running이 False이면 바로 종료
            break
        
    time_stopVideo.set()  # 이벤트 설정 (녹화 중지)

#폴더 생성 시간 설정
def newfolder_thread(time_createFolder, running): 
    print(f'newfolder_thread started')
    global running_duringThread
    for i in range(folder_duration):
        print(f'i: {i}')
        if cv2.waitKey(1) & 0xFF == ord('q'):
            running_duringThread = False
            # running = False
            print(f'break')
            break
        if not (running and running_duringThread):
            time_createFolder.set()
            break
        time.sleep(1)
            

#폴더 용량 확인하기    
def storageCheck_thread(time_checkStorage, running):
    print(f'storagecheck_thread started')
    global running_duringThread
    for _ in range(storageCheck_duration):
        if cv2.waitKey(1) & 0xFF == ord('q'):
            running_duringThread = False
            # running = False
            break
        if not (running and running_duringThread):
            break
        time.sleep(1)
    time_checkStorage.set()

###함수 목록    
##폴더 만들기 함수들
#새로운 폴더 만들기         
def createFolder(now, running):
    print(f'createfolder func started')
    #새 폴더 경로 지정하기
    new_path = currDateTime_toStr(now, "folder")
    print(new_path)
    if not os.path.exists(new_path): # 동일한 폴더가 있는지 확인 
        os.mkdir(new_path) #지정한 경로에 새로운 폴더 추가
        os.chdir(new_path) #지정 한 경로 안으로 들어가기
        running = createVideo(now, running)
    return running
        
#날짜+현재시간으로 폴더 이름 짓기
def currDateTime_toStr(now, fileType):
    print(f'currdatetime func started')
    # global basic_path #기존 경로 불러오기
    now_toStr = ''
    #날짜+현재시간을 문자열로 설정해서
    if fileType=="folder":
        now_toStr = now.strftime("%Y%m%d_%H")
    elif fileType=="video":
        now_toStr = now.strftime("%Y%m%d_%H%M%S")
    #새 폴더 경로 리턴 해주기
    return basic_path + now_toStr
           
#새로운 폴더 언제 생성할지 설정하기
def folderFunc(now, running):
    print(f'folderfunc func started')
    running = createFolder(now, running)
    while(running and running_duringThread):
        ##스레드 설정
        #폴더 스레드 중지 
        time_createFolder = threading.Event() # 폴더 생성 중지 이벤트 생성  
        #폴더 생성 스레드 생성 및 시작
        folderTimer= threading.Thread(target=newfolder_thread, args=(time_createFolder,running))
        folderTimer.start() 
        #폴더 이벤트 확인 (5초 경과)
        if time_createFolder.is_set():
            print(f'time_createFolder_is_set()')
            folderTimer.join()
            now = datetime.now()
            running = createFolder(now, running)
            global folderSize
            folderSize += str(os.path.join(basic_path, currDateTime_toStr(now,"folder"))).st_size #폴더 생성하자 마자 폴더 용량 업데이트 하기
        if cv2.waitKey(1) & 0xFF == ord('q'):
            running = False
            break
    return (running and running_duringThread)

##비디오 만들기 함수들
#비디오 생성하기
def createVideo(now, running):
    print(f'createvideo func started')
    ##스레드 설정
    #녹화 중지 이벤트 생성
    time_stopVideo = threading.Event()
    #타이머 스레드 생성 및 시작
    startRecording = threading.Thread(target=video_thread, args=(time_stopVideo, running))
    startRecording.start()

    ##녹화 설정
    #webcam인 경우 카메라 번호를 입력
    if isWEBCAM: 
        cap = cv2.VideoCapture(0)
    else: #webcam이 아닌 경우 지정한 비디오로부터 녹화 시작하기
        video_fileName = basic_path + 'YTN_CCTV.mp4'
        cap = cv2.VideoCapture(video_fileName) 
    #VideoWriter 객체 생성하기
    fourcc = cv2.VideoWriter_fourcc(*'XVID') #코덱?? 설정
    videoName = currDateTime_toStr(now,"video") #비디오 파일 이름 설정
    fps = int(cap.get(cv2.CAP_PROP_FPS))  #프레임 레이트 설정
    #읽는 비디오 파일 크기로 프레임 크기 설정
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH)) 
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    frameSize = (width,height)
    #출력 파일 설정
    out_color = cv2.VideoWriter(videoName + '.avi', fourcc, fps, frameSize)
    out_gray = cv2.VideoWriter(videoName + '_gray.avi', fourcc, fps, frameSize, isColor=False) 
    #녹화 시작
    recording = True
    while recording and running and running_duringThread:
        ret, frame = cap.read()  #프레임 읽기
        if ret:
            #프레임 저장
            out_color.write(frame)  
            grayFrame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY) 
            out_gray.write(grayFrame) 
            #미리보기 표시
            cv2.imshow('Color Recording', frame)  
            cv2.imshow('Grayscale Recording', grayFrame)  
            # 'q' 키를 누르면 즉시 종료
            if cv2.waitKey(1) & 0xFF == ord('q'):
                recording = False
                running = False
                break
        #타이머 이벤트 확인 (1분 경과 여부)
        if time_stopVideo.is_set():
            startRecording.join()
            recording = False        
    #비디오 녹화 출력하기
    cap.release()
    out_color.release()
    out_gray.release()
    cv2.destroyAllWindows() #미리보기 창 닫기
    return (running and running_duringThread)
    
##폴더 용량 조정하는 함수들
#폴더 사이즈를 유지하기 위해 폴더를 처음 만든 순서대로 지우기
def deleteFiles(running):
    print(f'deletefiles func started')
    sorted_folder_list = sorted(basic_path, key=lambda x: tuple(map(int, x.split('_')))) # sortFolder by dateCreated (as specified in folder name)
    print(f'폴더 정렬: {sorted_folder_list}')
    del_i = 0 # 파일을 만드는 순서대로 지우기
    global folderSize
    while (folderSize>max_storage) and running and (del_i<len(sorted_folder_list)):
        # removedFile = str(os.remove(basic_path + sorted_folder_list[del_i]))
        # folderSize -= fileStats.st_size #폴더를 지우자 마자 폴더 용량 업데이트 하기
        print(f'removedFile:', str(basic_path + sorted_folder_list[del_i]))
        if cv2.waitKey(1) & 0xFF == ord('q'):
            running = False
            break
        del_i += 1
    print(f'<용량 업데이트>현재 폴더 용량은: {folderSize}')     
    return running
        
#폴더 용량 측정하기
def check_folderSize(running):
    print(f'checkfoldersize func started')
    global folderSize
    try:
        #폴더 내 모든 파일과 하위 폴더를 순회
        for dirpath, dirnames, filenames in os.walk(basic_path):
            for f in filenames:
                f_p = os.path.join(dirpath, f)
                #os.path.islink() 함수를 사용하여 심볼릭 링크는 크기에 포함하지 않도록 함
                if not os.path.islink(f_p):
                    folderSize += int(round(os.path.getsize(f_p)/ (1024*1024))) #폴더 용량을 byte 단위에서 -> megabyte (mb)로 변경
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    recording = False
                break
            if cv2.waitKey(1) & 0xFF == ord('q'):
                running = False
                break
                        
    except FileNotFoundError:
        print(f"<오류> 폴더를 찾을 수 없습니다: {basic_path}")
        return 0
    return running 

    # # 바이트 크기를 KB, MB, GB 단위로 변환 (선택 사항)
    # if folder_size_bytes > 0:
    #     folder_size_kb = folder_size_bytes / 1024
    #     folder_size_mb = folder_size_kb / 1024
    #     folder_size_gb = folder_size_mb / 1024

###메인 프로그램 함수            
#블랙박스 프로그램 설정            
def createBlackbox(running, queue):
    print(f'createblackbox func started')
    #현재 시간 측정
    now = datetime.now()
    print(f'블랙박스 프로그램이 {now} 에 시작되었습니다')
    while(running):
        running = folderFunc(now, running)
        now = datetime.now()  #현재 시간 업데이트
        if cv2.waitKey(1) & 0xFF == ord('q'):
            running = False
            break

    queue.put(running)

#폴더 용량 사이즈 언제 확인할지 설정하기
def checkStorageFunc(running, queue):
    print(f'checkstoragefunc func started')
    #폴더 사이즈 측정하기 시작
    global folderSize
    while(running and running_duringThread):
        ##스레드 설정
        #폴더 스레드 중지 
        time_checkStorage = threading.Event() # 폴더 생성 중지 이벤트 생성  
        #폴더 생성 스레드 생성 및 시작
        startCheckStorage=threading.Thread(target=newfolder_thread, args=(time_checkStorage, running))
        startCheckStorage.start() 
        
        if folderSize > max_storage: #새로운 폴더가 생성하자 마자 용량이 업데이트 되어, 용량 초과를 넘으면 바로 지우기까지 연계
            running = deleteFiles(running)
 
        #타이머 이벤트 확인 (1분 경과 여부)
        if time_checkStorage.is_set():
            startCheckStorage.join()
            running = running and running_duringThread
            running = check_folderSize(running)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            running = False
            break
    queue.put(running)
        
###메인 프로그램 실행
if __name__ == "__main__":
    running = True #프로그램 종료 변수 일단 True로 할당하기
    
    # 멀티프로세싱 큐 생성
    queue = multiprocessing.Queue()
    # 첫 번째 프로세스 생성 및 시작
    p1 = multiprocessing.Process(target=createBlackbox, args=(running, queue))
    p1.start()

    # 두 번째 프로세스 생성 및 시작
    p2 = multiprocessing.Process(target=checkStorageFunc, args=(running, queue))
    p2.start()
    
    while(running):
        if cv2.waitKey(1) & 0xFF == ord('q'):
            running = False
            break
        # 프로세스가 완료될 때까지 대기
        p1.join()
        p2.join()
        running = queue.get() and queue.get()
    print(f'블랙박스 프로그램이 종료되었습니다. 프로그램을 이용해 주셔서 감사합니다.')