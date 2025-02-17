import cv2
import os
import time
import multiprocessing
import keyboard  # ✅ Detects 'q' anywhere
from datetime import datetime

# ✅ Shared variable for stopping all processes
running = multiprocessing.Value('b', True)  # Boolean flag (0 or 1)

basic_path = 'C:\\Users\\syoun\\blackbox\\'
video_duration = 3
folder_duration = 5
storageCheck_duration = 10
max_storage = 270
folderSize = 0

### 🔹 블랙박스 프로세스 (폴더 & 녹화)
def createBlackbox(running):
    now = datetime.now()
    print(f'🔴 블랙박스 시작: {now}')
    
    while running.value:  # ✅ Use shared value
        print("📂 폴더 생성 & 녹화 진행 중...")
        time.sleep(2)  # Simulate work

    print("🛑 블랙박스 종료")

### 🔹 저장 용량 확인 프로세스
def checkStorageFunc(running):
    global folderSize
    while running.value:
        print("📦 폴더 용량 확인 중...")
        time.sleep(3)  # Simulate checking storage

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