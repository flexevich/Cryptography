import socket
import random


def B():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as ts_socket:
        ts_socket.connect(("localhost", 5000))
        print("Соеденение", "Соединение c Трастовым сервером установлено!")

        n = int(ts_socket.recv(1024).decode())
        print("Получение от TS", f"Получен n = {n}")
        ts_socket.close()
    print("Соеденение", "Соединение c Трастовым сервером закрыто!")

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as socket_server:
        socket_server.bind(("localhost", 5001))
        socket_server.listen(1)
        print("Сервер", "Запущен на localhost:5001")

        a_socket, addr = socket_server.accept()
        print("Соеденение", "Соединение c A установлено!")

        v = int(a_socket.recv(1024).decode())
        print("Получение от A", f"v = {v}")

        for i in range(10):
            x = int(a_socket.recv(1024).decode())
            print(f"Получение {i + 1} от A", f"Получен x = {x}")
            c = random.randint(0, 1)
            a_socket.send(str(c).encode())
            print(f"Отправка {i + 1} на A", f"Отправлено c = {x}")
            y = int(a_socket.recv(1024).decode())
            print(f"Получение {i + 1} от A", f"Получен y = {y}")

            if not (y != 0 and ((x * pow(v, c, n)) % n == pow(y, 2, n))):
                print(f"Итерация {i+1} Верификации", "Неудача")
                a_socket.send("Идентификация провалена".encode())
                a_socket.close()
                print("Идентификация провалена")
                return

            print(f"Итерация {i+1} Верификации", "Успех")

        a_socket.send("success".encode())
        print("Финал", "Идентификация прошла успешно")
        print("Идентификация прошла успешно")    

        a_socket.close()
        socket_server.close()
    print("Соеденение", "Соединение c A закрыто!")

if __name__ == '__main__':
    B()