import socket
import threading
import time
import argparse

def handle_tcp_client(conn, addr):
    print(f"[SERVER][TCP] Connection from {addr}")
    mode = conn.recv(3).decode()
    if mode == 'tpf':
        save_to_file = True
    elif mode == 'tcp':
        save_to_file = False
    else:
        print(f"[SERVER][TCP] Unexpected mode '{mode}' from {addr}, closing connection.")
        conn.close()
        return

    total_bytes = 0
    start_time = time.time()
    if save_to_file:
        with open(f"received_from_{addr[0]}_{addr[1]}.bin", "wb") as f:
            while True:
                data = conn.recv(4096)
                if not data:
                    break
                f.write(data)
                total_bytes += len(data)
    else:
        while True:
            data = conn.recv(4096)
            if not data:
                break
            total_bytes += len(data)
    end_time = time.time()
    duration = end_time - start_time
    mb = total_bytes / (1024 * 1024)
    speed = mb / duration if duration > 0 else 0
    print(f"[SERVER][TCP] {addr}: Received {mb:.2f} MB in {duration:.2f} s ({speed:.2f} MB/s)")
    conn.close()

def tcp_server(port):
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind(('', port))
    server_socket.listen(5)

    while True:
        conn, addr = server_socket.accept()
        threading.Thread(target=handle_tcp_client, args=(conn, addr)).start()

def udp_server(port):
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind(('', port))
    sock.settimeout(0.5)
    client_stats = {}
    file_handlers = {}



    try:
        while True:
            try:
                data, addr = sock.recvfrom(65535)
                if addr not in client_stats:
                    mode = data[:3]
                    if mode == b'udp':
                        print(f"[SERVER][UDP] Receiving from {addr}")
                        client_stats[addr] = {'bytes': 0, 'start_time': time.time(), 'save': False}
                    elif mode == b'upf':
                        print(f"[SERVER][UDP] Receiving file from {addr}")
                        client_stats[addr] = {'bytes': 0, 'start_time': time.time(), 'save': True}
                        file_handlers[addr] = open(f"received_from_{addr[0]}_{addr[1]}.bin", "wb")
                    else:
                        continue
                else:
                    if client_stats[addr]['save']:
                        file_handlers[addr].write(data)
                    client_stats[addr]['bytes'] += len(data)
            except socket.timeout:
                now = time.time()
                for addr in list(client_stats.keys()):
                    duration = now - client_stats[addr]['start_time']
                    if duration >= 10:
                        mb = client_stats[addr]['bytes'] / (1024 * 1024)
                        speed = mb / duration if duration > 0 else 0
                        print(f"[SERVER][UDP] {addr}: Received {mb:.2f} MB in {duration:.2f} s ({speed:.2f} MB/s)")
                        if client_stats[addr]['save']:
                            file_handlers[addr].close()
                            del file_handlers[addr]
                        del client_stats[addr]
    except KeyboardInterrupt:
        print("[SERVER] Stopped by user.")
    finally:
        sock.close()
        for f in file_handlers.values():
            f.close()

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Speedtest Server Auto Save File TCP/UDP")
    parser.add_argument('--port', type=int, default=5201, help="Port to listen on")
    args = parser.parse_args()

    print(f"[SERVER] Listening on port {args.port}...")
    threading.Thread(target=tcp_server, args=(args.port,), daemon=True).start()
    threading.Thread(target=udp_server, args=(args.port,), daemon=True).start()

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("[SERVER] Shutting down.")
