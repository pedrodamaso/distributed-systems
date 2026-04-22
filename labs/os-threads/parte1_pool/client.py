import socket
import sys

HOST = '127.0.0.1'
PORT = int(sys.argv[1]) if len(sys.argv) > 1 else 5001


def enviar_pedido():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((HOST, PORT))
        s.sendall(b"pedido\n")
        resposta = s.recv(16)
        return resposta


if __name__ == '__main__':
    r = enviar_pedido()
    print(f"Resposta: {r.decode().strip()}")
