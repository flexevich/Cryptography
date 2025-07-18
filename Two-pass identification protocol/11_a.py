import socket
import json
import sys
import time
import random
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad
from rsa import *

# Константы
ID_A = 123784
ID_B = 543217
HOST = "127.0.0.1"
PORT = 65432



def tsa_or_rand(choice):
    #Генерирует временную метку или простое число в зависимости от выбора
    if choice == '1':
        now_utc = time.strftime("%y%m%d%H%M%SZ", time.gmtime())
        return now_utc
    elif choice == '2':
        return str(generate_p(512))
    else:
        print("ошибка")
        sys.exit(1)

def aes_encrypt(bit_key, plaintext):
    #Шифрует текст с помощью AES
    byte_key = int(bit_key, 2).to_bytes(16, byteorder='big')
    if isinstance(plaintext, str):
        plaintext = plaintext.encode('utf-8')
    padded_data = pad(plaintext, AES.block_size)
    cipher = AES.new(byte_key, AES.MODE_ECB)
    return cipher.encrypt(padded_data).hex()

def aes_decrypt(bit_key, ciphertext_hex):
    #Расшифровывает текст с помощью AES
    byte_key = int(bit_key, 2).to_bytes(16, byteorder='big')
    cipher = AES.new(byte_key, AES.MODE_ECB)
    ciphertext = bytes.fromhex(ciphertext_hex)
    decrypted_data = cipher.decrypt(ciphertext)
    return unpad(decrypted_data, AES.block_size).decode('utf-8')

def start_client():
    #Запускает клиентскую часть протокола идентификации
    # Генерация случайного ключа
    key = ''.join([str(random.randint(0, 1)) for _ in range(128)])
    
    # Получение данных от пользователя
    mess1 = input("Введите mess1 (шифротекст): ")
    mess2 = input("Введите mess2 (открытый текст): ")
    choice = input("Выберите временную метку (1) или простое число (2): ")
    value = tsa_or_rand(choice)
    
    # Подготовка данных для отправки
    temp_data = {
        "message 1": mess1,
        "ID1": ID_A,
        "value": value
    }
    encoded_data = aes_encrypt(key, json.dumps(temp_data))
    
    data_to_send = {
        "key": key,
        "open message": mess2,
        "encode message": encoded_data
    }
    
    print("\nОтправляемые данные:")
    print(f"Ключ: {key}")
    print(f"Открытое сообщение: {mess2}")
    print(f"Расшифрованное сообщение: {mess1}")
    print(f"ID1: {ID_A}")
    print(f"Значение: {value}")
    
    # Отправка данных и получение ответа
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((HOST, PORT))
        s.sendall(json.dumps(data_to_send).encode('utf-8'))
        
        response = s.recv(4096)
        if not response:
            print("Ответ не получен")
            return
        
        try:
            result = json.loads(response.decode('utf-8'))
            print("\nПолучен ответ от сервера:")
            print(f"Открытое сообщение: {result['open message4']}")
            
            if 'encode message3' in result:
                decrypted = aes_decrypt(key, result['encode message3'])
                decrypted_data = json.loads(decrypted)
                
                print("Расшифрованные данные ответа:")
                print(f"Сообщение 3: {decrypted_data['message 3']}")
                print(f"ID отправителя: {decrypted_data['ID2']}")
                print(f"Значение: {decrypted_data['value']}")
                
                if decrypted_data['value'] == value and decrypted_data['ID2'] == ID_B:
                    print("\nИдентификация прошла успешно!")
                else:
                    print("\nОшибка идентификации!")
                    if decrypted_data['value'] != value:
                        print("Неверное значение")
                    if decrypted_data['ID2'] != ID_B:
                        print("Неверный ID2")
        except Exception as e:
            print(f"Ошибка обработки ответа: {e}")

if __name__ == "__main__":
    start_client()