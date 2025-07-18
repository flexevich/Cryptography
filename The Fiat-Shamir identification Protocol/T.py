import socket
import sys
import os
# Получаем путь к родительской директории
parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
# Добавляем его в системные пути
sys.path.append(parent_dir)
from rsa import *
def T():
    p = generate_p(512)
    q = generate_p(512)
    n = p * q
    print("Сгенерированы", f"p={p}, q={q}, n={n}")
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(('localhost', 5000))
        s.listen(2)
        print("Ключи сгенерированы и сервер запущен...")
        conn_A, addr_A = s.accept()
        print(f"Соедениени с А {addr_A}")
        conn_B, addr_B = s.accept()
        print(f"Соедениени с B {addr_B}")
        conn_A.send(str(n).encode())
        conn_B.send(str(n).encode())
        print("Sent to A", n)
        print("Sent to B", n)   

        conn_A.close()
        conn_B.close()
        s.close()
        print("Сервер закрыт")

if __name__ == "__main__":
    T()
        