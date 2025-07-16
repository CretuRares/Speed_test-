import socket
import time
import argparse
import threading
import json
import os
import random

results = []
lock = threading.Lock()

def format_speed(bytes_sent, elapsed, unit):
    if elapsed <= 0:
        return 0, unit
    bits_sent = bytes_sent * 8
    if unit == 'k':
        speed = bits_sent / 1024 / elapsed
        unit_label = 'Kbit/s'
    elif unit == 'K':
        speed = bytes_sent / 1024 / elapsed
        unit_label = 'KByte/s'
    elif unit == 'm':
        speed = bits_sent / (1024 * 1024) / elapsed
        unit_label = 'Mbit/s'
    else:
        speed = bytes_sent / (1024 * 1024) / elapsed
        unit_label = 'MByte/s'
    return speed, unit_label

def format_data(bytes_sent, unit):
    bits_sent = bytes_sent * 8
    if unit == 'k':
        value = bits_sent / 1024
        label = 'Kbit'
    elif unit == 'K':
        value = bytes_sent / 1024
        label = 'KByte'
    elif unit == 'm':
        value = bits_sent / (1024 * 1024)
        label = 'Mbit'
    else:
        value = bytes_sent / (1024 * 1024)
        label = 'MByte'
    return value, label

def tcp_client_thread(host, port, duration, unit, file_name):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect((host, port))

  
    if file_name:
        sock.sendall(b'tpf')
    else:
        sock.sendall(b'tcp')

    total_bytes = 0
    start_time = time.time()

    try:
        if file_name:
            if not os.path.exists(file_name):
                print(f"[CLIENT][TCP] File '{file_name}' not found.")
                sock.close()
                return
            with open(file_name, 'rb') as f:
                while time.time() - start_time < duration:
                    packet_size = random.randint(512, 4096)
                    data = f.read(packet_size)
                    if not data:
                        break
                    sock.sendall(data)
                    total_bytes += len(data)
        else:
  
            while time.time() - start_time < duration:
                packet_size = random.randint(512, 4096)
                data = os.urandom(packet_size)
                sock.sendall(data)
                total_bytes += len(data)
    except Exception as e:
        print(f"[CLIENT][TCP] Error: {e}")
    finally:
        sock.shutdown(socket.SHUT_WR)
        end_time = time.time()
        elapsed = end_time - start_time
        data_sent, data_unit = format_data(total_bytes, unit)
        speed, speed_unit = format_speed(total_bytes, elapsed, unit)
        print(f"[CLIENT][TCP] Sent {data_sent:.2f} {data_unit} in {elapsed:.2f} s ({speed:.2f} {speed_unit})")
        with lock:
            results.append({
                "protocol": "TCP",
                "bytes_sent": total_bytes,
                "duration_s": elapsed,
                "data_sent": f"{data_sent:.2f} {data_unit}",
                "speed": f"{speed:.2f} {speed_unit}"
            })
        sock.close()

def udp_client_thread(host, port, duration, packet_size, unit, file_name):
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)


    if file_name:
        sock.sendto(b'upf', (host, port))
    else:
        sock.sendto(b'udp', (host, port))

    total_bytes = 0
    start_time = time.time()

    try:
        if file_name:
            if not os.path.exists(file_name):
                print(f"[CLIENT][UDP] File '{file_name}' not found.")
                sock.close()
                return
            with open(file_name, 'rb') as f:
                while time.time() - start_time < duration:
                    packet_size_rand = random.randint(64, packet_size)
                    data = f.read(packet_size_rand)
                    if not data:
                        break
                    sock.sendto(data, (host, port))
                    total_bytes += len(data)
 
        else:
  
            while time.time() - start_time < duration:
                packet_size_rand = random.randint(64, packet_size)
                data = os.urandom(packet_size_rand)
                sock.sendto(data, (host, port))
                total_bytes += len(data)
    except Exception as e:
        print(f"[CLIENT][UDP] Error: {e}")
    finally:
        end_time = time.time()
        elapsed = end_time - start_time
        data_sent, data_unit = format_data(total_bytes, unit)
        speed, speed_unit = format_speed(total_bytes, elapsed, unit)
        print(f"[CLIENT][UDP] Sent {data_sent:.2f} {data_unit} in {elapsed:.2f} s ({speed:.2f} {speed_unit})")
        with lock:
            results.append({
                "protocol": "UDP",
                "bytes_sent": total_bytes,
                "duration_s": elapsed,
                "data_sent": f"{data_sent:.2f} {data_unit}",
                "speed": f"{speed:.2f} {speed_unit}"
            })
        sock.close()

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Speedtest Client TCP/UDP")
    parser.add_argument('--host', type=str, default='127.0.0.1', help="Server IP")
    parser.add_argument('--port', type=int, default=5201, help="Server port")
    parser.add_argument('--duration', type=int, default=10, help="Test duration")
    parser.add_argument('--mode', choices=['tcp', 'udp'], default='tcp', help="TCP or UDP")
    parser.add_argument('--packet_size', type=int, default=1024, help="UDP max packet size")
    parser.add_argument('--threads', type=int, default=1, help="Threads")
    parser.add_argument('--format', choices=['k', 'K', 'm', 'M'], default='M', help="Display units")
    parser.add_argument('--json', action='store_true', help="Output JSON")
    parser.add_argument('--file_name', type=str, help="File to send instead of random data")
    args = parser.parse_args()

    threads_list = []
    for _ in range(args.threads):
        if args.mode == 'tcp':
            t = threading.Thread(target=tcp_client_thread, args=(args.host, args.port, args.duration, args.format, args.file_name))
        else:
            t = threading.Thread(target=udp_client_thread, args=(args.host, args.port, args.duration, args.packet_size, args.format, args.file_name))
        t.start()
        threads_list.append(t)

    for t in threads_list:
        t.join()

    if results:
        total_bytes = sum(r["bytes_sent"] for r in results)
        total_duration = max(r["duration_s"] for r in results)
        data_sent, data_unit = format_data(total_bytes, args.format)
        speed, speed_unit = format_speed(total_bytes, total_duration, args.format)
        print(f"[CLIENT][AGGREGATE] Sent {data_sent:.2f} {data_unit} in {total_duration:.2f} s ({speed:.2f} {speed_unit}) using {args.threads} thread(s).")

        if args.json:
            with open("speedtest_results.json", "w") as f:
                json.dump({"aggregate": {
                    "threads": args.threads,
                    "total_bytes": total_bytes,
                    "total_duration_s": total_duration,
                    "data_sent": f"{data_sent:.2f} {data_unit}",
                    "speed": f"{speed:.2f} {speed_unit}"
                }, "threads_results": results}, f, indent=4)
            print("[CLIENT] Results saved to speedtest_results.json")
