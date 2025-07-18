import random
import json
import socket
import hashlib
from laba6 import *
from rsa import *
from sha import *

# Список клиентов
CLIENTS = [("127.0.0.1", 5001), ("127.0.0.1", 5002)]

# Глобальные переменные
g = 2  # Количество участников
bits = 256  # Размер ключей
n, e, d = None, None, None  # RSA-ключи
p, q, alpha, z, L = None, None, None, None, None  # Параметры подписи
k_i, P_i = [], []  # Ключи участников
sockets = []  # Сокеты для клиентов
lambda_i = []  # Список lambda_i
U, E, S = None, None, None  # Параметры подписи
T, R_i = None, None  # Временные параметры

def gen_p_and_q(bits):
    global p, q
    while True:
        q = generate_p(bits)
        p = 2 * q + 1
        if miller_rabin(p):
            break
    print("p и q сгенерированы")

def is_primitive_root(g, p):
    phi = p - 1
    B = [2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31]
    factors = factorize(phi, B)
    return check_primitive_element(g, p, factors)

def gen_alpha(p):
    global alpha
    for _ in range(1000):
        g = random.randint(2, p - 2)
        if is_primitive_root(g, p):
            alpha = fast_exp_mod(g, 2, p)
            break
    else:
        raise ValueError("Не удалось найти примитивный корень")
    print("alpha сгенерирован")

def gen_L(alpha, p, q):
    global z, L
    z = random.randint(1, q - 1)
    L = fast_exp_mod(alpha, z, p)
    print("L сгенерирован")

def create_user_keys(g, alpha, p, q):
    global k_i, P_i
    k_i, P_i = [], []
    for _ in range(g):
        k = random.randint(1, q - 1)
        P = fast_exp_mod(alpha, k, p)
        k_i.append(k)
        P_i.append(P)
    print("Ключи участников сгенерированы")

def connect_to_clients():
    global sockets
    sockets = []
    for ip, port in CLIENTS:
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.connect((ip, port))
            sockets.append(sock)
            print(f"Подключено к клиенту {ip}:{port}")
        except socket.error:
            print(f"Клиент {ip}:{port} недоступен!")

def close_sockets():
    for sock in sockets:
        sock.close()
    print("Сокеты закрыты")

def send_params(sockets, p, q, alpha, k_i, P_i):
    for i in range(len(sockets)):
        params = {
            "p": p,
            "q": q,
            "alpha": alpha,
            "k": k_i[i],
            "P": P_i[i]
        }
        sockets[i].send(json.dumps(params).encode("utf-8"))
    print("Параметры отправлены")

def hash_message(message, hash_type):
    if hash_type == "sha256":
        return sha256(message)
    elif hash_type == "sha512":
        return sha512(message)
    else:
        raise ValueError("Неподдерживаемый тип хеша")

def calculate_lambda(P_i, message, hash_type, d, n):
    global lambda_i
    lambda_i = []
    for i in range(len(P_i)):
        hash_val = int(hash_message(message, hash_type), 16)
        lambda_i.append(fast_exp_mod(P_i[i] + hash_val, d, n))
    print("Lambda_i посчитаны")

def calculate_U(P_i, lambda_i, p):
    global U
    U = 1
    for i in range(len(P_i)):
        U = (U * fast_exp_mod(P_i[i], lambda_i[i], p)) % p
    print("U посчитан")

def send_and_recv_data(sockets, data):
    recv_data = []
    for i, sock in enumerate(sockets):
        item = data[i] if isinstance(data, list) else data
        sock.sendall(str(item).encode("utf-8"))
        response = sock.recv(1024).decode("utf-8")
        recv_data.append(int(response))
    return recv_data

def calculate_E(R_i, message, hash_type, alpha, p, q):
    global E, T
    T = random.randint(1, q - 1)
    R_sh = fast_exp_mod(alpha, T, p)
    R = R_sh
    for r_i in R_i:
        R = (R * r_i) % p
    E = hash_message(message + str(R).encode("utf-8") + str(U).encode("utf-8"), hash_type)
    print("E посчитан")

def verify_signatures(R_i, S_i, P_i, lambda_i, E, alpha, p):
    E_int = int(E, 16)
    for i in range(len(R_i)):
        exponent = lambda_i[i] * E_int
        base = fast_exp_mod(P_i[i], exponent, p)
        try:
            inv = pow(base, -1, p)
        except ValueError:
            print(f"Не удалось найти обратный элемент для участника {i}")
            return False
        left = (inv * fast_exp_mod(alpha, S_i[i], p)) % p
        if left != R_i[i]:
            print(f"Подпись участника {i} недействительна")
            return False
    print("Все подписи проверены успешно")
    return True

def calculate_S(S_i, T, z, E, q):
    global S
    E_int = int(E, 16)
    S_sh = (T + z * E_int) % q
    S = (S_sh + sum(S_i)) % q
    print("S посчитан")

def create_pkcs7(message, hash_type, L, alpha, p, U, E, S):
    return {
        "CMSVersion": "1",
        "DigestAlgorithmIdentifiers": hash_type,
        "EncapsulatedContentInfo": {
            "ContentType": "Data",
            "OCTET_STRING_OPTIONAL": message.decode("utf-8")
        },
        "SignerInfos": {
            "CMSVersion": "1",
            "SignerIdentifier": "GroupSignature",
            "DigestAlgorithmIdentifiers": hash_type,
            "SignatureAlgorithmIdentifier": "Groupdsi",
            "SubjectPublicKeyInfo": {
                "L": L,
                "alpha": alpha,
                "p": p
            },
            "SignatureValue": {
                "U": U,
                "E": E,
                "S": S
            },
            "UnsignedAttributes": {
                "ObjectIdentifier": "signature-time-stamp",
                "SET_OF_AttributeValue": {}
            }
        }
    }

def send_recv_TSA(pkcs7_data):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect(("127.0.0.1", 5000))
        print("Соединение с TSA установлено")
        s.sendall(json.dumps(pkcs7_data).encode("utf-8"))
        recv_data = s.recv(2048).decode("utf-8")
        print("Данные от TSA получены")
        return json.loads(recv_data)

def verify_timestamp_signature(pkcs7_data, hash_type):
    print("Проверка подписи TSA")
    client_signature = pkcs7_data['SignerInfos']['SignatureValue']
    message = pkcs7_data['EncapsulatedContentInfo']['OCTET_STRING_OPTIONAL'].encode("utf-8")
    msg_plus_sign = message + str(client_signature["U"]).encode("utf-8") + client_signature["E"].encode("utf-8") + str(client_signature["S"]).encode("utf-8")
    
    server_data = pkcs7_data['SignerInfos']['UnsignedAttributes']['SET_OF_AttributeValue']
    hash_msg_plus_sign = sha256(msg_plus_sign)
    utc_time_server = server_data['Timestamp']['UTCTime']
    right_server_hash = hash_msg_plus_sign + utc_time_server[:-1]

    server_signature = int(server_data['Signature'], 16)
    server_e = server_data['Certificate']['publicExponent']
    server_n = server_data['Certificate']['N']
    hash_from_signature_server = decrypt_message(server_signature, server_e, server_n)  # Используем decrypt_message

    if hash_from_signature_server != right_server_hash:
        print(f"server_data['Signature']: {server_data['Signature']}")
        print(f"hash_from_signature_server: {hash_from_signature_server}")
        print(f"right_server_hash: {right_server_hash}")
        print("Неверная подпись TSA")
        return False
    print("Проверка TSA завершена успешно")
    return True

def save_final_signature(pkcs7_data):
    output_path = "signature_with_TSA.json"
    with open(output_path, "w") as f:
        json.dump(pkcs7_data, f, indent=4)
    print("Подпись с меткой TSA сохранена")

if __name__ == "__main__":
    # Инициализация параметров
    print("🔧 Генерация RSA-ключей...")
    (e, n), (d, n) = rsa(generate_p(bits), generate_p(bits))
    save_public_key((e, n), "public_key_10.json")
    save_private_key((d, n), "private_key_10.json")
    print("Ключи сгенерированы")

    gen_p_and_q(bits)
    gen_alpha(p)
    gen_L(alpha, p, q)
    create_user_keys(g, alpha, p, q)

    # Подпись
    message = "Привет!".encode("utf-8")
    hash_type = "sha256"

    connect_to_clients()
    send_params(sockets, p, q, alpha, k_i, P_i)
    calculate_lambda(P_i, message, hash_type, d, n)
    calculate_U(P_i, lambda_i, p)

    R_i = send_and_recv_data(sockets, lambda_i)
    print("R_i получены")
    calculate_E(R_i, message, hash_type, alpha, p, q)
    S_i = send_and_recv_data(sockets, E)
    print("S_i получены")

    if verify_signatures(R_i, S_i, P_i, lambda_i, E, alpha, p):
        calculate_S(S_i, T, z, E, q)
        close_sockets()

        # Взаимодействие с TSA
        pkcs7_data = create_pkcs7(message, hash_type, L, alpha, p, U, E, S)
        timestamp_signature = send_recv_TSA(pkcs7_data)
        pkcs7_data['SignerInfos']['UnsignedAttributes']['SET_OF_AttributeValue'] = timestamp_signature

        if verify_timestamp_signature(pkcs7_data, hash_type):
            save_final_signature(pkcs7_data)