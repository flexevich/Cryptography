import socket
import random
import json
from laba6 import *

def B():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)  # Allow port reuse
        s.bind(("localhost", 5000))
        s.listen(1)
        print("B запущен и ожидает подключения...")
        
        # Принимаем подключение от клиента
        conn, addr = s.accept()
        print(f"Подключен клиент: {addr}")
        
        with conn:  # Работаем с клиентским сокетом
            # Чтение длины сообщения
            len_bytes = conn.recv(4)
            if len(len_bytes) != 4:
                raise Exception("Не удалось прочитать длину ответа")
            length = int.from_bytes(len_bytes, 'big')
            
            # Чтение данных ключа
            data = b""
            while len(data) < length:
                chunk_ = conn.recv(min(1024, length - len(data)))
                if not chunk_:
                    raise Exception("Соединение прервано клиентом")
                data += chunk_
            
            # Декодирование и разбор ключа
            str_data = data.decode('utf-8')
            json_ = json.loads(str_data)
            alpha = json_["alpha"]
            p = json_["p"]
            g = json_["g"]
            
            # Генерация y, beta и k
            y = random.randint(2, p - 1)
            beta = fast_exp_mod(g, y, p)
            k = fast_exp_mod(alpha, y, p)
            
            # Отправка beta клиенту
            data = {
                "beta": beta  # Исправлено с "deta" на "beta"
            }
            data_json = json.dumps(data)
            data_bytes = data_json.encode('utf-8')
            data_length = len(data_bytes)
            data_length_bytes = data_length.to_bytes(4, 'big')
            
            conn.sendall(data_length_bytes)
            conn.sendall(data_bytes)
            
            # Запись в файл
            with open('17_B.txt', 'w') as f:  # Исправлено на 17_B.txt
                f.write(f"p: {p}\n")
                f.write(f"g: {g}\n")
                f.write(f"Y: {y}\n")
                f.write(f"beta: {beta}\n")
                f.write(f"K: {k}\n")

if __name__ == "__main__":
    B()