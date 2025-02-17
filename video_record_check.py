import cv2
import os
import sys

isWEBCAM = True

if isWEBCAM:
    cap = cv2.VideoCapture(0)
else:
    fileName = 'blackbox\\data\\vtest.avi'
    abs_path = os.path.abspath(fileName)
    print("Absolute path to video file:", abs_path)
    if not os.path.exists(fileName):
        print("Error: Video file does not exist.")
        sys.exit()
    cap = cv2.VideoCapture(fileName)

if not cap.isOpened():
    print("Error: Could not open video source.")
    sys.exit()

# 카메라의 이미지 사이즈
frameSize = (int(cap.get(cv2.CAP_PROP_FRAME_WIDTH)), int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT)))

print("Frame Size:", frameSize)

# 카메라에서 전달되는 초당 프레임 수
fps = int(cap.get(cv2.CAP_PROP_FPS))
print("FPS:", fps)

# 코덱 설정
fourcc = cv2.VideoWriter_fourcc(*'XVID')

# 컬러 동영상 녹화를 위해
out1 = cv2.VideoWriter('record0_color.mp4', fourcc, fps, frameSize)
# grayscale 동영상 녹화를 위해
out2 = cv2.VideoWriter('record0_gray.mp4', fourcc, fps, frameSize, isColor=False)

if not out1.isOpened() or not out2.isOpened():
    print("Error: Could not open video file for writing.")
    sys.exit()

while True:
    retval, frame = cap.read()
   
    if not retval:
        print("Error: Failed to capture frame.")
        break
    
    out1.write(frame)
    grayFrame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    out2.write(grayFrame)

    cv2.imshow('frame', frame)
    cv2.imshow('gray', grayFrame)
    delay = int(1000 / fps)
    
    if cv2.waitKey(delay) == 27:
        break

cap.release()
out1.release()
out2.release()
cv2.destroyAllWindows()
