import os
import time
import argparse
import threading
import random

def disk_write(filename, size_mb, block_size_kb):
    total_bytes = size_mb * 1024 * 1024
    block = b'x' * (block_size_kb * 1024)
    written = 0

    start_time = time.time()
    with open(filename, 'wb') as f:
        while written < total_bytes:
            f.write(block)
            written += len(block)
    end_time = time.time()
    elapsed = end_time - start_time
    speed = size_mb / elapsed if elapsed > 0 else 0
    print(f"[SEQ WRITE] {size_mb} MB in {elapsed:.3f} s ({speed:.2f} MB/s)")

def random_write_thread(filename, block_size_kb, iterations):
    block_size = block_size_kb * 1024
    file_size = os.path.getsize(filename)
    block = os.urandom(block_size)  # Random data
    with open(filename, 'r+b') as f:
        for _ in range(iterations):
            offset = random.randint(0, file_size - block_size)
            f.seek(offset)
            f.write(block)

def threaded_random_write_test(filename, block_size_kb, num_threads, iterations_per_thread):
    threads = []
    start_time = time.time()
    for _ in range(num_threads):
        t = threading.Thread(target=random_write_thread, args=(filename, block_size_kb, iterations_per_thread))
        t.start()
        threads.append(t)
    for t in threads:
        t.join()
    end_time = time.time()
    total_data_mb = num_threads * iterations_per_thread * block_size_kb / 1024
    elapsed = end_time - start_time
    speed = total_data_mb / elapsed if elapsed > 0 else 0
    print(f"[{num_threads}Thrd WRITE] {total_data_mb:.2f} MB in {elapsed:.3f} s ({speed:.2f} MB/s)")

def disk_read(filename, block_size_kb):
    block_size = block_size_kb * 1024
    total_read = 0
    
    start_time = time.time()
    with open(filename, 'rb') as f:
        while True:
            data = f.read(block_size)
            if not data:
                break
            total_read += len(data)
    end_time = time.time()
    elapsed = end_time - start_time
    mb_read = total_read / (1024 * 1024)
    speed = mb_read / elapsed if elapsed > 0 else 0
    print(f"[READ] {mb_read:.2f} MB in {elapsed:.3f} s ({speed:.2f} MB/s)")

def random_read_thread(filename, block_size_kb, iterations):
    block_size = block_size_kb * 1024
    file_size = os.path.getsize(filename)
    with open(filename, 'rb') as f:
        for _ in range(iterations):
            offset = random.randint(0, file_size - block_size)
            f.seek(offset)
            f.read(block_size)

def threaded_random_read_test(filename, block_size_kb, num_threads, iterations_per_thread):
    threads = []
    start_time = time.time()
    for _ in range(num_threads):
        t = threading.Thread(target=random_read_thread, args=(filename, block_size_kb, iterations_per_thread))
        t.start()
        threads.append(t)
    for t in threads:
        t.join()
    end_time = time.time()
    total_data_mb = num_threads * iterations_per_thread * block_size_kb / 1024
    elapsed = end_time - start_time
    speed = total_data_mb / elapsed if elapsed > 0 else 0
    print(f"[{num_threads}Thrd READ] {total_data_mb:.2f} MB in {elapsed:.3f} s ({speed:.2f} MB/s)")

def access_time_test(filename, block_size_kb):
    block_size = block_size_kb * 1024
    iterations = 1000
    file_size = os.path.getsize(filename)
    with open(filename, 'rb') as f:
        start_time = time.time()
        for _ in range(iterations):
            offset = random.randint(0, file_size - block_size)
            f.seek(offset)
            f.read(block_size)
        end_time = time.time()
    avg_access_time = ((end_time - start_time) / iterations) * 1000
    print(f"[ACCESS TIME] Avg: {avg_access_time:.3f} ms over {iterations} random {block_size_kb}KB reads")

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Disk I/O")
    parser.add_argument('--operation', choices=['read', 'write', 'both'], default='both')
    parser.add_argument('--filename', type=str, required=True)
    parser.add_argument('--size_mb', type=int, default=1024)
    parser.add_argument('--block_size_kb', type=int, default=4)
    parser.add_argument('--threads', type=int, default=64)
    parser.add_argument('--iterations', type=int, default=200)
    args = parser.parse_args()

    if args.operation in ['write', 'both']:
        print("\n---Write Test, 1024Kb block size---")
        disk_write(args.filename, args.size_mb, 1024)
        print(f"\n---Write Test, {args.block_size_kb} Kb block size---")
        disk_write(args.filename, args.size_mb, args.block_size_kb)
        print("\n---Threads Write Test---")
        threaded_random_write_test(args.filename, args.block_size_kb, args.threads, args.iterations)

    if args.operation in ['read', 'both']:
        print("\n---Sequential Read Test---")
        disk_read(args.filename, 1024)
        print("\n---Read Test---")
        disk_read(args.filename, args.block_size_kb)
        print("\n---Threads Read Test---")
        threaded_random_read_test(args.filename, args.block_size_kb, args.threads, args.iterations)
        print("\n---Access Time Test---")
        access_time_test(args.filename, args.block_size_kb)
