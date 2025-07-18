import socket
import json

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
    name = "Alice"
    
    # Подключение к доверенному центру 
    try:
        socket_A = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        socket_A.connect(('localhost', 5000))
    except ConnectionRefusedError:
        print("Ошибка: Доверенный центр недоступен")
        return
    
    # Отправляем имя доверенному центру
    socket_A.send(name.encode())
    
    # Получаем параметры от доверенного центра
    try:
        recv = json.loads(socket_A.recv(1024).decode())
    except json.JSONDecodeError:
        print("Ошибка: Некорректные данные от доверенного центра")
        socket_A.close()
        return
    
    socket_A.close()
    
    # Проверяем полученные данные
    if not all(key in recv for key in ["user_id", "personal_poly", "field_size"]):
        print("Ошибка: Неполные данные от доверенного центра")
        return
    
    # Получаем параметры Алисы
    user_id_A = recv["user_id"]
    personal_poly_A = recv["personal_poly"]
    field_size = recv["field_size"]
    
    # Подключение к Бобу
    try:
        socket_A = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        socket_A.connect(("localhost", 5001))
    except ConnectionRefusedError:
        print("Ошибка: Клиент Б недоступен")
        return
    
    # Отправляем идентификатор Алисы
    socket_A.send(json.dumps({"user_id_A": user_id_A}).encode())

    # Получаем идентификатор Боба
    recv = json.loads(socket_A.recv(1024).decode())
    user_id_B = recv["user_id_B"]
    
    socket_A.close()
    
    # Вычисляем общий ключ
    key = compute_shared_key(user_id_B, personal_poly_A, field_size)
    
    # Выводим результаты
    print(f"Алиса: ID = {user_id_A}, Персональный многочлен = {personal_poly_A}")
    print(f"Общий ключ Алисы: {key}")

if __name__ == "__main__":
    main()