n = int(input())
m = int(input())

arr = [ int(input()) for _ in range(n)]  # 正确初始化数组
arr.sort()  # 二分查找要求数组有序

left = 0
right = n - 1
found = False

while left <= right:
    mid = (left + right) // 2
    if arr[mid] == m:
        print(mid)
        found = True
        break
    elif arr[mid] < m:
        left = mid + 1
    else:
        right = mid - 1

if not found:
    print(-1)  

