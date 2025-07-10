import os
import time
import argparse

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

    print(f"[DISK WRITE] Wrote {size_mb} MB in {elapsed:.2f} s ({speed:.2f} MB/s)")

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

    print(f"[DISK READ] Read {mb_read:.2f} MB in {elapsed:.2f} s ({speed:.2f} MB/s)")

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Disk I/O Speed Test")
    parser.add_argument('--operation', choices=['read', 'write'], help="Operation type")
    parser.add_argument('--filename', type=str, help="File to read/write")
    parser.add_argument('--size_mb', type=int, nargs='?', help="Size in MB (for write)", default=1024)
    parser.add_argument('--block_size_kb', type=int, help="Block size in KB")
    args = parser.parse_args()

    if args.operation == 'write':
        disk_write(args.filename, args.size_mb, args.block_size_kb)
    elif args.operation == 'read':
        disk_read(args.filename, args.block_size_kb)
