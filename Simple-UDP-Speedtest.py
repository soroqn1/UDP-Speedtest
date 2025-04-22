import sys
import argparse
import socket
import threading
import time
import hashlib
import struct
import errno

DEFAULT_PORT = 5005


def run_server(port=DEFAULT_PORT):
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind(("", port))
    print(f"[+] Server listening on UDP port {port}")

    lock = threading.Lock()
    stats = {"received": 0, "errors": 0, "bytes": 0}

    def report():
        last_time = time.time()
        last_bytes = 0
        while True:
            time.sleep(1)
            now = time.time()
            with lock:
                total_bytes = stats["bytes"]
                total_received = stats["received"]
                total_errors = stats["errors"]

            bps = (total_bytes - last_bytes) / (now - last_time) if now > last_time else 0
            err_rate = (total_errors / total_received * 100) if total_received > 0 else 0
            print(f"Rate: {bps:.2f} B/s | Packets: {total_received} | Errors: {total_errors} | Err%: {err_rate:.2f}")

            last_time = now
            last_bytes = total_bytes

    threading.Thread(target=report, daemon=True).start()

    expected_seq = 1
    while True:
        data, addr = sock.recvfrom(65535)
        if len(data) < 8:
            continue  # ignore too-small packets

        seq, = struct.unpack('!I', data[:4])
        recv_checksum = data[4:8]
        payload = data[8:]

        calc_checksum = hashlib.md5(data[:4] + payload).digest()[:4]

        with lock:
            stats['received'] += 1
            stats['bytes'] += len(payload)
            if recv_checksum != calc_checksum or seq != expected_seq:
                stats['errors'] += 1
            expected_seq = seq + 1


def run_client(ip: str, mtu: int, port=DEFAULT_PORT, delay: float = 0.0):
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    # Increase send buffer size to handle higher throughput
    try:
        buf_size = mtu * 2000
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_SNDBUF, buf_size)
    except Exception:
        pass  # platform may not allow resizing

    seq = 1
    payload_size = mtu - 8  # header (4 bytes seq + 4 bytes checksum)

    print(f"[+] Sending UDP packets to {ip}:{port} with MTU {mtu} (payload {payload_size} bytes) and delay {delay}s")
    try:
        while True:
            payload = bytes(payload_size)
            header = struct.pack('!I', seq)
            checksum = hashlib.md5(header + payload).digest()[:4]
            packet = header + checksum + payload
            try:
                sock.sendto(packet, (ip, port))
            except OSError as e:
                # Buffer full: wait briefly, then retry
                if e.errno in (errno.ENOBUFS, errno.EAGAIN, errno.EWOULDBLOCK):
                    time.sleep(max(0.01, delay))
                    continue
                else:
                    raise
            seq += 1
            # Optional inter-packet delay to avoid overwhelming buffer
            if delay > 0:
                time.sleep(delay)
    except KeyboardInterrupt:
        print("\n[!] Client stopped by user.")


def main():
    parser = argparse.ArgumentParser(description="UDP speedtest for local-network or internet.")
    parser.add_argument('-ip', type=str, help='Server IP address (client mode)')
    parser.add_argument('-mtu', type=int, help='MTU size in bytes (client mode)')
    parser.add_argument('-port', type=int, default=DEFAULT_PORT, help='UDP port (default: 5005)')
    parser.add_argument('-delay', type=float, default=0.0, help='Optional delay between packets in seconds')

    args = parser.parse_args()

    if args.ip and args.mtu:
        run_client(args.ip, args.mtu, args.port, args.delay)
    else:
        run_server(args.port)


if __name__ == '__main__':
    main()
