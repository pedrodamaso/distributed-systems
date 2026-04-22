import socket
import threading
import queue
import time

HOST = '0.0.0.0'
PORT = 5001
POOL_SIZE = 4
REQUEST_QUEUE = queue.Queue(maxsize=100)


def simular_trabalho():
    end = time.perf_counter() + 0.002
    while time.perf_counter() < end:
        pass
    time.sleep(0.008)


def worker(thread_id: int):
    while True:
        conn, addr = REQUEST_QUEUE.get()
        try:
            conn.recv(64)
            simular_trabalho()
            conn.sendall(b"OK\n")
        finally:
            conn.close()
            REQUEST_QUEUE.task_done()


def main():
    threads = []
    for i in range(POOL_SIZE):
        t = threading.Thread(target=worker, args=(i,), daemon=True)
        t.start()
        threads.append(t)

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as srv:
        srv.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        srv.bind((HOST, PORT))
        srv.listen()
        print(f"[Pool] Ouvindo na porta {PORT} com {POOL_SIZE} threads")
        while True:
            conn, addr = srv.accept()
            REQUEST_QUEUE.put((conn, addr))


if __name__ == '__main__':
    main()
