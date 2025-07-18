import socket
import json
import random

def compute_shared_key(user_id: int, personal_poly: list, field_size: int) -> int:
    # Вычисление общего ключа с другим пользователем.
    # user_id: публичный ID другого пользователя (скаляр)
    # personal_poly: персональный многочлен
    # field_size: размер поля
    # :return: общий ключ
    key = 0
    for power, coeff in enumerate(personal_poly):
        term = coeff * pow(user_id, power, field_size)
        key = (key + term) % field_size
    return key

def main():
    # Имя клиента
    name = "Bob"
    
    # Подключение к доверенному центру 
    try:
        socket_B = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        socket_B.connect(('localhost', 5000))
    except ConnectionRefusedError:
        print("Ошибка: Доверенный центр недоступен")
        return
    
    # Отправляем имя доверенному центру
    socket_B.send(name.encode())
    
    # Получаем параметры от доверенного центра
    try:
        recv = json.loads(socket_B.recv(1024).decode())
    except json.JSONDecodeError:
        print("Ошибка: Некорректные данные от доверенного центра")
        socket_B.close()
        return
    
    socket_B.close()
    
    # Проверяем полученные данные
    if not all(key in recv for key in ["user_id", "personal_poly", "field_size"]):
        print("Ошибка: Неполные данные от доверенного центра")
        return
    
    # Получаем параметры Боба
    user_id_B = recv["user_id"]
    personal_poly_B = recv["personal_poly"]
    field_size = recv["field_size"]
    
    # Настройка сервера для связи с Алисой
    try:
        socket_B = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        socket_B.bind(("localhost", 5001))
        socket_B.listen(1)
        print("Боб ожидает подключения Алисы на localhost:5001...")
    except OSError:
        print("Ошибка: Порт 5001 занят или недоступен")
        socket_B.close()
        return
    
    # Принимаем подключение от Алисы
    try:
        conn, addr = socket_B.accept()
        print(f"Подключение от {addr} (предположительно Алиса)")
        
        # Получаем идентификатор Алисы
        recv = json.loads(conn.recv(1024).decode())
        user_id_A = recv["user_id_A"]

        # Отправляем идентификатор Боба
        conn.send(json.dumps({"user_id_B": user_id_B}).encode())
        
        conn.close()
        socket_B.close()
    except json.JSONDecodeError:
        print("Ошибка: Некорректные данные от Алисы")
        conn.close()
        socket_B.close()
        return
    
    # Вычисляем общий ключ
    key = compute_shared_key(user_id_A, personal_poly_B, field_size)
    
    # Выводим результаты
    print(f"Боб: ID = {user_id_B}, Персональный многочлен = {personal_poly_B}")
    print(f"Общий ключ Боба: {key}")

if __name__ == "__main__":
    main()