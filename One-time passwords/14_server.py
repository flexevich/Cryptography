import socket, json

from sha import *


class Server:
    def __init__(self, host='127.0.0.1', port=12345):
        self._host = host
        self._port = port
        self._hash_type = None
        self.users = {}
        self._algo_map = {
            "sha256": lambda m: sha256(m),
        }

    def _hash_message(self, user_id ,message: bytes) -> str:
        return self._algo_map[self.users[user_id]['hash_type']](message)

    def _register(self, data):
        user_id = data['user_id']
        hash_type = data['hash_type']
        h_n_w = data['h_n_w']
        max_attempts = data['max_attempts']

        self.users[user_id] = {
            'hash_type': hash_type,
            'hash': h_n_w,
            'attempt': 0,
            'max_attempts': max_attempts
        }

        return {'message': f'Пользователь {user_id} зарегистрирован.'}
    
    def _authenticate(self, data):
        user_id = data['user_id']
        current_hash = data['current_hash']

        if user_id not in self.users:
            return {'message': f'Пользователь {user_id} не зарегистрирован.'}
        
        user = self.users[user_id]
        
        if data['attempt'] != user['attempt'] + 1:
            return {'success': False, 'message': 'Неверный номер попытки'}
        
        current_hash = self._hash_message(user_id, bytes.fromhex(current_hash))
        if user['hash'] == current_hash:
            self.users[user_id]['attempt'] += 1
            self.users[user_id]['hash'] = data['current_hash']
            return {'message': f'Пользователь {user_id} аутентифицирован.'}
        else:
            return {'message': f'Пользователь {user_id} не аутентифицирован.'}
        
    def handle_request(self, data) :
        action = data.get('action')
        if action == 'register':
            return self._register(data)
        elif action == 'authenticate':
            return self._authenticate(data)
        return {'success': False, 'message': 'Неверное действие'}
    
    def start_server(self):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.bind((self._host, self._port))
            s.listen()
            print(f"Центр аутентификации запущен на {self._host}:{self._port}")
            while True:
                conn, addr = s.accept()
                with conn:
                    data = json.loads(conn.recv(1024).decode())
                    response = self.handle_request(data)
                    conn.sendall(json.dumps(response).encode())

if __name__ == "__main__":
    server = Server()
    server.start_server()