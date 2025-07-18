import socket
import json
import os
import time
from sha import *
from rsa import *

# Глобальные переменные
bits = 256  # Размер ключей (для теста, в реальных системах 2048+)
e, n, d = None, None, None  # RSA-ключи TSA
port = 5000  # Порт для TSA
type_hash = "sha256"  # Тип хеша (определяется из данных)

def generate_tsa_keys(bits):
    global e, n, d
    print("🔧 Генерация RSA-ключей TSA...")
    priv_file = "tsa_private_10.json"
    pub_file = "tsa_public_10.json"
    if not os.path.exists(priv_file):
        p = generate_p(bits // 2)  # Генерируем простое число p
        q = generate_p(bits // 2)  # Генерируем простое число q
        (e, n), (d, _) = rsa(p, q)  # Генерируем ключи
        save_private_key((d, n), priv_file)  # Сохраняем закрытый ключ
        save_public_key((e, n), pub_file)  # Сохраняем открытый ключ
        print("Ключи TSA сгенерированы и сохранены")
        print(f"Проверка ключей: e * d mod phi = {(e * d) % ((p-1)*(q-1))}")
    else:
        private_key = load_private_key(priv_file)
        public_key = load_public_key(pub_file)
        e, n = public_key
        d = private_key[0]
        print("Ключи TSA загружены из файлов")

def hash_m_from_type_hash(message, hash_type):
    global type_hash
    if hash_type == "sha256":
        return sha256(message)
    print(f"Неподдерживаемый тип хеша: {hash_type}")
    raise ValueError("Неподдерживаемый тип хеша")

def sign(hash_msg, d, n):
    hash_int = int(hash_msg, 16)
    signature = encrypt_message(hash_int, d, n)  # Используем encrypt_message вместо fast_exp_mod
    return hex(signature)[2:]  # Форматируем в hex без префикса 0x

def check_signature(L, alpha, p, signature, message, hash_type):
    print("Проверка подписи лидера")
    U, E, S = signature['U'], signature['E'], signature['S']
    E_int = int(E, 16)
    UL = (U * L) % p
    if pow(UL, E_int, p) == 0:
        print("Ошибка: (U * L)^E mod p = 0, обратный элемент не существует")
        return False
    inv_UL_E = pow(UL, -E_int, p)
    alpha_S = fast_exp_mod(alpha, S, p)
    R_tilda = (inv_UL_E * alpha_S) % p
    E_tilda = hash_m_from_type_hash(message + str(R_tilda).encode("utf-8") + str(U).encode("utf-8"), "sha256")
    print(f"U: {U}, E: {E}, S: {S}")
    print(f"R_tilda: {R_tilda}")
    print(f"E_tilda: {E_tilda}")
    print(f"Ожидаемое E: {E}")
    if E_tilda == E:
        print("Подпись лидера прошла проверку")
        return True
    else:
        print("Подпись лидера не прошла проверку")
        return False

# def create_timestamp_signature():
#     timestamp = time.strftime("%y%m%d%H%M%SZ", time.gmtime())
#     return timestamp

def validate_signature(data):
    global type_hash
    print("Обработка данных от лидера")
    try:
        message = data['EncapsulatedContentInfo']['OCTET_STRING_OPTIONAL'].encode("utf-8")
        type_hash = data['DigestAlgorithmIdentifiers']
        L = data['SignerInfos']['SubjectPublicKeyInfo']['L']
        alpha = data['SignerInfos']['SubjectPublicKeyInfo']['alpha']
        p = data['SignerInfos']['SubjectPublicKeyInfo']['p']
        signature = data['SignerInfos']['SignatureValue']

        if not check_signature(L, alpha, p, signature, message, type_hash):
            return {"error": "Подпись не прошла проверку"}

        new_message = (
            message +
            str(signature["U"]).encode("utf-8") +  # Преобразуем U в строку
            signature["E"].encode("utf-8") +
            str(signature["S"]).encode("utf-8")  # Преобразуем S в строку
        )
        hash_new_message = sha256(new_message)
        now_utc_time = time.strftime("%y%m%d%H%M%SZ", time.gmtime())
        hash_plus_time = (hash_new_message + now_utc_time).encode('utf-8')
        server_signature = encrypt_message(hash_plus_time, d, n)
        signed_data = {
            'Hash': hash_plus_time,
            'Timestamp': {
                'UTCTime': now_utc_time,
            },
            'Signature': server_signature,
            'Certificate': {
                'publicExponent': e,
                'N': n
            }
        }
        print("Данные успешно обработаны")
        return signed_data
    except Exception as err:
        print(f"Ошибка обработки данных: {err}")
        return {"error": f"Ошибка обработки: {err}"}

def save_to_file(filename, data):
    with open(filename, "w") as f:
        json.dump(data, f, indent=4)
    print(f"Данные сохранены в {filename}")

def handle_client(conn, addr):
    print(f"Подключён клиент {addr}")
    try:
        data = conn.recv(10 * 1024 * 1024).decode("utf-8")
        if not data:
            print("Пустые данные от клиента")
            return
        pkcs7_data = json.loads(data)
        print("Данные получены")
        response = validate_signature(pkcs7_data)
        save_to_file("tsa_response.json", response)
        conn.sendall(json.dumps(response).encode("utf-8"))
        print("Данные отправлены")
    except Exception as err:
        print(f"Ошибка обработки клиента {addr}: {err}")
    finally:
        conn.close()
        print(f"Соединение с {addr} закрыто")

def start_server(port):
    generate_tsa_keys(bits)  # Генерируем или загружаем ключи при старте
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.bind(('localhost', port))
    sock.listen(1)
    print(f"Сервер TSA запущен на порту {port}")
    while True:
        try:
            conn, addr = sock.accept()
            handle_client(conn, addr)
        except KeyboardInterrupt:
            print("\nСервер остановлен")
            break
        except Exception as err:
            print(f"Ошибка сервера: {err}")
    sock.close()

if __name__ == "__main__":
    start_server(port)