import socket
import json

from sha import *


class Client:
    def __init__(self, host='127.0.0.1', port=12345):
        self._host = host
        self._port = port
        self._user_id = None
        self._secret = None
        self._hash_type = sha256
        self._attempt = 0

    # def _hash_message(self, message: bytes) -> str:
    #     return self._algo_map[self._hash_type](message)

    def _compute_initial_hash(self, secret: str, n: int) -> bytes:
        result = secret
        for _ in range(n):
            result = bytes.fromhex(self._hash_type(result))
        return result.hex()

    def register(self, user_id: str, secret: str, hash_type: str, n: int = 1000):

        self._user_id = user_id
        self._secret = secret
        self._hash_type = hash_type

        h_n_w = self._compute_initial_hash(secret, n)

        data = {
            'action': 'register',
            'user_id': user_id,
            'hash_type': hash_type,
            'h_n_w': h_n_w,
            'max_attempts': n
        }

        self._attempt = 0

        response = self._send_request(data)
        print(f"Регистрация: {response.get('message')}")

    def authenticate(self):
        if not self._user_id or not self._secret:
            print("Ошибка: Пользователь не зарегистрирован")
            return

        self._attempt += 1
        current_hash = self._compute_initial_hash(self._secret, 1000 - self._attempt)

        data = {
            'action': 'authenticate',
            'user_id': self._user_id,
            'current_hash': current_hash,
            'attempt': self._attempt
        }
        response = self._send_request(data)
        print(f"Аутентификация: {response.get('message')}")

    def _send_request(self, data: dict) -> dict:
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.connect((self._host, self._port))
                s.sendall(json.dumps(data).encode())
                return json.loads(s.recv(1024).decode())
        except Exception as e:
            return {'message': f'Ошибка соединения: {e}'}

    def run(self):
        while True:
            print("\n1. Регистрация")
            print("2. Аутентификация")
            print("3. Выход")
            choice = input("Выберите действие: ")

            if choice == '1':
                user_id = input("Введите идентификатор пользователя: ")
                secret = input("Введите секретный пароль: ").encode("utf-8")
                print("Доступные хеш-функции:", ', '.join(self._algo_map.keys()))
                hash_func = input("Выберите хеш-функцию: ")
                self.register(user_id, secret, hash_func)

            elif choice == '2':
                self.authenticate()

            elif choice == '3':
                print("Выход.")
                break

            else:
                print("Неверный выбор, попробуйте снова.")


if __name__ == "__main__":
    client = Client()
    client.run()