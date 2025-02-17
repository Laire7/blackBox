import multiprocessing
import time

# 프로세스 함수 정의
def sum_numbers(start, end, queue):
    total = 0
    for i in range(start, end + 1):
        total += i
    queue.put(total)  # 결과를 큐에 넣습니다.

if __name__ == '__main__':
    # 시작 시간 측정
    start_time = time.time()

    # 큐 생성
    queue = multiprocessing.Queue()

    # 프로세스 생성 및 시작
    p1 = multiprocessing.Process(target=sum_numbers, args=(1, 25000000, queue))
    p2 = multiprocessing.Process(target=sum_numbers, args=(25000001, 50000000, queue))
    p3 = multiprocessing.Process(target=sum_numbers, args=(50000001, 75000000, queue))
    p4 = multiprocessing.Process(target=sum_numbers, args=(75000001, 100000000, queue))
    p1.start()
    p2.start()
    p3.start()
    p4.start()

    # 프로세스가 종료될 때까지 대기
    p1.join()
    p2.join()
    p3.join()
    p4.join()

    # 결과를 큐에서 가져와 합산
    total_sum = 0
    for _ in range(4):  # 4개의 프로세스 결과를 가져옵니다.
        total_sum += queue.get()

    # 종료 시간 측정
    end_time = time.time()

    # 결과 출력
    print("1부터 100000000까지의 합:", total_sum)
    print("실행 시간:", end_time - start_time, "초")