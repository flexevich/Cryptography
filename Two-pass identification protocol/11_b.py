import socket
import json
import sys
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad
from rsa import *

# Constants
ID_A = 123784
ID_B = 543217
HOST = "127.0.0.1"
PORT = 65432

def aes_encrypt(bit_key, plaintext):
    byte_key = int(bit_key, 2).to_bytes(16, byteorder='big')
    if isinstance(plaintext, str):
        plaintext = plaintext.encode('utf-8')
    padded_data = pad(plaintext, AES.block_size)
    cipher = AES.new(byte_key, AES.MODE_ECB)
    return cipher.encrypt(padded_data).hex()

def aes_decrypt(bit_key, ciphertext_hex):
    byte_key = int(bit_key, 2).to_bytes(16, byteorder='big')
    cipher = AES.new(byte_key, AES.MODE_ECB)
    ciphertext = bytes.fromhex(ciphertext_hex)
    decrypted_data = cipher.decrypt(ciphertext)
    return unpad(decrypted_data, AES.block_size).decode('utf-8')

def start_server():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind((HOST, PORT))
        s.listen()
        print("Сервер ожидает подключения...")
        
        conn, addr = s.accept()
        with conn:
            print(f"Подключено: {addr}")
            data = conn.recv(4096)
            if not data:
                print("Данные не получены")
                return
            
            try:
                received_data = json.loads(data.decode('utf-8'))
                open_message2 = received_data['open message']
                key = received_data['key']
                
                decrypted_data = aes_decrypt(key, received_data['encode message'])
                decrypted_json = json.loads(decrypted_data)
                
                decrypted_message1 = decrypted_json['message 1']
                id1 = decrypted_json['ID1']
                value = decrypted_json['value']
                
                print("\nПолученные данные:")
                print(f"Ключ: {key}")
                print(f"Открытое сообщение: {open_message2}")
                print(f"Расшифрованное сообщение: {decrypted_message1}")
                print(f"ID1: {id1}")
                print(f"Значение: {value}")
                
                # Проверка ID отправителя
                if id1 != ID_A:
                    print("Неверный ID1")
                    return
                
                # Подготовка ответа
                mess3 = input("Введите mess3 (шифротекст): ")
                mess4 = input("Введите mess4 (открытый текст): ")
                
                temp_data = {
                    "message 3": mess3,
                    "ID2": ID_B,
                    "value": value
                }
                encoded_data = aes_encrypt(key, json.dumps(temp_data))
                
                data_to_send = {
                    "open message4": mess4,
                    "encode message3": encoded_data
                }
                
                # Отправка ответа
                conn.sendall(json.dumps(data_to_send).encode('utf-8'))
                print("Ответ успешно отправлен")
                print("\n✅ Идентификация успешна")
                
            except Exception as e:
                print(f"Ошибка обработки данных: {e}")

if __name__ == "__main__":
    start_server()