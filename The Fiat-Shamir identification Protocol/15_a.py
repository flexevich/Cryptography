import socket
import random
import sys
import os
from rsa import *
parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.append(parent_dir)
def iter(b_socket, n ,s):
    for i in range(10):
        z = random.randint(1, n - 1)
        x = pow(z, 2, n)
        b_socket.send(str(x).encode())
        print(f"Отправка {i + 1} на B", f"Отправлено x = {x}")
        c = int(b_socket.recv(1024).decode())
        print(f"Получение {i + 1} от B", f"Получен c = {c}")

        if c:
            y = (z * s) % n
        else:
            y = z
        
        b_socket.send(str(y).encode())
        print(f"Отправка {i + 1} на B", f"Отправлено y = {y}")

    return b_socket.recv(1024).decode()

def A():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as ts_socket:
        ts_socket.connect(("localhost", 5000))
        print("Соединение c Трастовым сервером установлено!")

        n = int(ts_socket.recv(1024).decode())
        print(f"Получен от TS значение n = {n}")
        ts_socket.close()
    print("Соединение c Трастовым сервером закрыто!")

    while True:
        s = random.randint(1, n - 1)
        gcd, _, _ = euclidean_algorithm(s, n)
        if gcd == 1:
            break
        
    print(f"Расчитано s = {s}")
    #1
    v = pow(s, 2, n)
    print(f"Расчитано v = {v}")

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as b_socket:
        b_socket.connect(("localhost", 5001))
        print("Соединение c B установлено!")

        b_socket.send(str(v).encode())
        print(f"Отправлено B значение v = {v}")

        confirmation = iter(b_socket, n, s)
        print(f"Получение от B {confirmation}")
        print("Идентификация прошла успешно" if confirmation == "success" else "Идентификация провалена")     

        b_socket.close()
    print("Соединение c B закрыто!")

if __name__ == '__main__':
    A()