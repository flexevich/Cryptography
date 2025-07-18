import socket
import json
import random
from laba6 import fast_exp_mod

# Глобальные переменные
p, q, alpha, k_i, P_i = None, None, None, None, None
t_i = None  # Случайное число для R_i
port = 5001  # Порт для user1

def calculate_R_i(alpha, p, q):
    global t_i
    t_i = random.randint(1, q - 1)
    R_i = fast_exp_mod(alpha, t_i, p)
    print(f"R_i вычислен: {R_i}")
    return R_i

def calculate_S_i(t_i, k_i, lambda_i, E, q):
    E_int = int(E, 16)
    S_i = (t_i + k_i * lambda_i * E_int) % q
    print(f"S_i вычислен: {S_i}")
    return S_i

def save_to_file(filename, data):
    with open(filename, "w") as f:
        json.dump(data, f, indent=4)
    print(f"Данные сохранены в {filename}")

def handle_leader(conn, addr):
    global p, q, alpha, k_i, P_i
    print(f"Подключён лидер {addr}")
    try:
        # Получение параметров
        data = conn.recv(2048).decode("utf-8")
        if not data:
            print("Пустые данные от лидера")
            return
        params = json.loads(data)
        p = params["p"]
        q = params["q"]
        alpha = params["alpha"]
        k_i = params["k"]
        P_i = params["P"]
        print("Параметры получены: p, q, alpha, k_i, P_i")
        save_to_file("user1_params.json", params)

        # Получение lambda_i и вычисление R_i
        lambda_i_str = conn.recv(1024).decode("utf-8")
        lambda_i = int(lambda_i_str)
        print(f"Получен lambda_i: {lambda_i}")
        R_i = calculate_R_i(alpha, p, q)
        conn.sendall(str(R_i).encode("utf-8"))
        print(f"R_i отправлен: {R_i}")

        # Получение E и вычисление S_i
        E = conn.recv(1024).decode("utf-8")
        print(f"Получен E: {E}")
        S_i = calculate_S_i(t_i, k_i, lambda_i, E, q)
        conn.sendall(str(S_i).encode("utf-8"))
        print(f"S_i отправлен: {S_i}")

        # Сохранение результатов
        results = {"R_i": R_i, "S_i": S_i, "lambda_i": lambda_i, "E": E}
        save_to_file("user1_results.json", results)
    except Exception as err:
        print(f"Ошибка обработки лидера {addr}: {err}")
    finally:
        conn.close()
        print(f"Соединение с {addr} закрыто")

def start_server(port):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.bind(('localhost', port))
    sock.listen(1)
    print(f"Сервер клиента запущен на порту {port}")
    while True:
        try:
            conn, addr = sock.accept()
            handle_leader(conn, addr)
        except KeyboardInterrupt:
            print("\nСервер остановлен")
            break
        except Exception as err:
            print(f"Ошибка сервера: {err}")
    sock.close()

if __name__ == "__main__":
    start_server(port)