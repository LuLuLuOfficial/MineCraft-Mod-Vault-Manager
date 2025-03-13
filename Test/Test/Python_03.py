import threading
import time

A = []
for n in range(10000000):
    print(n)
    A.append(n)

# Function for Part 1
def part1():
    start = time.time()
    for n in range(len(A)):
        if n in A:
            pass
    end = time.time()
    print(f'<Part 1> Time Used: {end-start}')

# Function for Part 2
def part2():
    start = time.time()
    b = tuple(A)
    for n in range(len(b)):
        if n in b:
            pass
    end = time.time()
    print(f'<Part 2> Time Used: {end-start}')

# Create threads
thread1 = threading.Thread(target=part1)
thread2 = threading.Thread(target=part2)

# Start the threads
thread1.start()
thread2.start()

# Wait for both threads to finish
thread1.join()
thread2.join()
