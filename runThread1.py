import time

# 시작 시간 측정
start_time = time.time()

# 1부터 100000000까지의 합을 계산
total_sum = 0
for i in range(1, 100000001):
    total_sum += i

# 종료 시간 측정
end_time = time.time()

# 결과 출력
print("1부터 100000000까지의 합:", total_sum)
print("실행 시간:", end_time - start_time, "초")