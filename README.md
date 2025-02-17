# 블랙박스
프로세스를 사용해서 블랙바스를 날짜와 시간별로 저장하기

## 사용법
*isWEBCAM: 웹캠이나 녹화본 쓸지 설정 (웹켐: 0, 녹화본: 1)  
*basic_path: 블랙박스 영상 경로 설정
*video_duration: 블랙박스 영상 길이 설정
*folder_duration: 폴더 생성 빈도 설정
*storageCheck_duration: 폴더 저장 용량 확인 빈도
*max_storage: 폴더 저장 용량 

## 프로그램 주요 요소

### 프로세스
#### Multiprocessing
모든 프로세스들을 **multiprocessing** 이라는 한 변수로 관리 가능
<code>running = multiprocessing.Value('b', True)  # Boolean flag (0 or 1)</code>

#### 메인 (프로세스 총 정리)
프로세스들을 열고 닫는 순서는 아래와 같습니다:
1. process = multiprocessing.Process(target=*function*, args=(running,))
2. process.start()
3. process.terminate()
4. process.join(timeout=*float*)

'''
if __name__ == "__main__":
    p1 = multiprocessing.Process(target=createBlackbox, args=(running,))
    p2 = multiprocessing.Process(target=checkStorageFunc, args=(running,))

    p1.start()
    p2.start()

    # ✅ 키보드에서 'q' 누르면 모든 프로그램들을 즉시 종료
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
'''

### OpenCV 
#### 비디오 생성
1.비디오 설정
  * <pre><code>cv2.VideoCapture(*숫자/비디오 경로*)</code></pre>
    * 웹캠 녹화: 1
    * 녹음본: 비디오 경로 (예: C:\\Users\\syoun\\blackbox\\data\\vtest.avi)
2. 비디오 생성
  * <code>cv2.VideoWriter(videoName + '.avi', fourcc, fps, frameSize)</code>
    1. <code> videoName + '.avi' </code></pre>: 비디오 경로 설정하기
    2. <code> fourcc </code>: 비디오 객체 만들기
      * <code>fourcc = cv2.VideoWriter_fourcc(*'XVID') </code></pre>
    3. <code> fps </code></pre>: 프레임 레이트 설정하기
      * <code> fps = int(cap.get(cv2.CAP_PROP_FPS)) </code></pre>
    4. <code> frameSize </code></pre>: 카메라의 이미지 사이즈 설정하기
      * <code> frameSize = (int(cap.get(cv2.CAP_PROP_FRAME_WIDTH)), int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))) </code></pre>
3. 비디오 녹화
  * <code> retval, frame = cap.read()  </code> : 프레임 읽기
  * <code> out.write(frame) </code> : 프레임 저장하기
  * 녹화 중에도 사용자가 프로그램 종료를 명시했는지 감지: 프레임이 바뀌는 빈도에 맞춰 키보드 입력 감지 
    '''
    delay = int(1000 / fps) 
    if cv2.waitKey(delay) == 113: 
      break
    '''
4. 비디오 종료
   '''
   cap.release()
   out.release()
   cv2.destroyAllWindows() #미리보기 창 닫기
  '''

### 기타 요소
#### 시간
<pre><code> time.time() </code></pre>: 현재 시간을 알려준다
  * <pre><code> import time </code></pre>
#### 날짜 + 시간
<code>datetime.now()</code> : 현재 날짜와 시간을 알려준다
<code> now.strftime("%Y%m%d_%H%M%S") </code>: 날짜와 시간을 문자열로 바꿔준다
#### 폴더 경로
* <code> os.path.join(base_path, path_add1, ..., filename) </code> 폴더의 경로를 설정할 수 있다
* <code> for dirpath, dirnames, filenames in os.walk(basic_path) </code> 함수를 사용하여, 폴더 안에 있는 모든 파일들을 목록으로 불러와 for 루프로 확인 할 수 있다 
* <code> os.path.islink(path) </code> 함수를 사용하여 폴더 용량을 추척 할 때 파일이 아닌 것을 걸러 낼 수 있다 
#### 키보드 입력 탐지
    '''
    import keyboard
    if keyboard.is_pressed('q'):
        running = False
        break
    '''
<code> cv2.waitKey(1) & 0xFF == ord('q') </code> 와 달리 <pre><code> keyboard.is_pressed('q') </code></pre>
  * 키보드 입력을 항상 주의한다: 여기에서 <pre><code> waitKey(1) </code></pre> 는 1 milisecond만 키보드 입력을 주의한다
  * <code> 0xFF </code> 는 키보드 입력 시 cv2가 이해 할 수 있는 것들로만 입력값을 제안한다
  * <code> ord('q') </code> 의 자리에 해당 ASCII 숫자만 넣어도 되지만, 알아보기 쉬어 자주 사용 된다
    * 다만 'Esc'같은 입력값들은 ASCII 숫자로만 지정 할 수 있다
       

