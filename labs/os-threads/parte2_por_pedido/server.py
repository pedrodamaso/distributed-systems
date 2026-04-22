import socket
import threading
import time

HOST = '0.0.0.0'
PORT = 5002


def simular_trabalho():
    end = time.perf_counter() + 0.002
    while time.perf_counter() < end:
        pass
    time.sleep(0.008)


def handle_client(conn, addr):
    try:
        conn.recv(64)
        simular_trabalho()
        conn.sendall(b"OK\n")
    finally:
        conn.close()


def main():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as srv:
        srv.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        srv.bind((HOST, PORT))
        srv.listen()
        print(f"[Por Pedido] Ouvindo na porta {PORT}")
        while True:
            conn, addr = srv.accept()
            t = threading.Thread(target=handle_client, args=(conn, addr), daemon=True)
            t.start()


if __name__ == '__main__':
    main()
