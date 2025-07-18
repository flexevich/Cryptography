import random
import socket
import json
import numpy as np
import os
import sys
parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.append(parent_dir)
from rsa import *

def generate_matrix(field_size: int, m: int) -> np.array:
    # Генерация симметричной матрицы коэффициентов для многочлена f(x,y) степени 2m.
    # field_size: размер конечного поля F
    # m: параметр безопасности
    # return: симметричная матрица
    poly = [[0] * (m + 1) for _ in range(m + 1)]
    for i in range(m + 1):
        for j in range(i, m + 1):
            poly[i][j] = random.randint(0, field_size - 1)
            if i != j:
                poly[j][i] = poly[i][j]
    return np.array(poly)

def compute_personal_polynomial(user_id: int, polynomial: np.array, field_size: int, m: int) -> np.array:
    # Вычисление персонального многочлена для пользователя.
    # user_id: идентификатор пользователя (скаляр)
    # polynomial: симметричная матрица
    # field_size: размер поля
    # m: параметр безопасности
    # :return: коэффициенты персонального многочлена
    user_id_vector = np.array([pow(user_id, i, field_size) for i in range(m + 1)])[:, None]
    return polynomial @ user_id_vector

def register_user(user_name: str, field_size: int, polynomial: np.array, user_ids: dict, m: int) -> tuple:
    # Регистрация пользователя: генерация уникального ID и персонального многочлена.
    # user_name: имя пользователя
    # field_size: размер поля
    # polynomial: симметричная матрица
    # user_ids: словарь зарегистрированных пользователей
    # m: параметр безопасности
    # :return: (публичный ID, персональный многочлен)
    while True:
        user_id = random.randint(1, field_size - 1)
        if user_id not in user_ids.values():
            break
    user_ids[user_name] = user_id
    personal_poly = compute_personal_polynomial(user_id, polynomial, field_size, m)
    return user_id, personal_poly.flatten().tolist()

def main():
    # Параметры системы
    field_size = generate_p(128)
    m = 5
    user_ids = {}
    polynomial = generate_matrix(field_size, m)
    
    print(f"Доверенный центр запущен с размером поля {field_size} и m={m}")
    print(f"Симметричная матрица многочлена:\n{polynomial}")

    # Настройка сокет-сервера
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:
        server_socket.bind(('localhost', 5000))
        server_socket.listen(2)
        print("Сервер запущен на localhost:5000, ожидание подключений...")
        try:
            # Принимаем подключения от двух пользователей (Алисы и Боба)
            conn_A, addr_A = server_socket.accept()
            print(f"Подключение от {addr_A} (предположительно Алиса)")
            name_A = conn_A.recv(1024).decode()
            conn_B, addr_B = server_socket.accept()
            print(f"Подключение от {addr_B} (предположительно Боб)")
            name_B = conn_B.recv(1024).decode()
            # Регистрируем пользователей и отправляем параметры
            user_id_A, personal_poly_A = register_user(name_A, field_size, polynomial, user_ids, m)
            user_id_B, personal_poly_B = register_user(name_B, field_size, polynomial, user_ids, m)
            # Отправляем данные Алисе
            conn_A.send(json.dumps({
                "user_id": user_id_A,
                "personal_poly": personal_poly_A,
                "field_size": field_size
            }).encode())
            print(f"Отправлены параметры для {name_A}: ID={user_id_A}, poly={personal_poly_A}")
            # Отправляем данные Бобу
            conn_B.send(json.dumps({
                "user_id": user_id_B,
                "personal_poly": personal_poly_B,
                "field_size": field_size
            }).encode())
            print(f"Отправлены параметры для {name_B}: ID={user_id_B}, poly={personal_poly_B}")
            # Закрываем соединения
            conn_A.close()
            conn_B.close()
        except Exception as e:
            print(f"Ошибка: {e}")
        finally:
            server_socket.close()
            print("Сервер завершил работу")

if __name__ == "__main__":
    main()