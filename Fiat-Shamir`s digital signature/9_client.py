import json
import socket
import random
from sha import *
from RSA import *

def generate_fiat_shamir_keys(k, m):
    # Генерация n = p * q
    p = generate_p(k)
    q = generate_p(k)
    while q == p:
        q = generate_p(k)
    n = p * q
    # Генерация закрытого ключа
    a = [random.randint(2, n-1) for _ in range(m)]
    # Генерация открытого ключа
    b = [pow(pow(a_i, -1, n), 2, n) for a_i in a]
    return (b, n), (a, n)

def fiat_shamir_sign(message, priv_key, hash_f, m):
    a, n = priv_key
    r = random.randint(1, n-1)
    x = fast_exp_mod(r, 2, n)
    message_bytes = message.encode('utf-8')
    x_bytes = x.to_bytes((x.bit_length() + 7) // 8, 'big')
    s = hash_f(message_bytes + x_bytes)
    s_bits = [int(c) for c in bin(int(s, 16))[2:].zfill(m)]
    t = r
    for i in range(m):
        if s_bits[i] == 1:
            t = (t * a[i]) % n
    return t, s

def fiat_shamir_verify(message, signature, pub_key, hash_f, m):
    t, s = int(signature["t"]), signature["s"]
    b, n = [int(bi) for bi in pub_key["b"]], int(pub_key["n"])
    w = fast_exp_mod(t, 2, n)
    s_bits = [int(c) for c in bin(int(s, 16))[2:].zfill(m)]
    for i in range(m):
        if s_bits[i] == 1:
            w = (w * b[i]) % n
    message_bytes = message.encode('utf-8')
    w_bytes = w.to_bytes((w.bit_length() + 7) // 8, 'big')
    s_prime = hash_f(message_bytes + w_bytes)
    return s_prime == s

def save_public_key(pub_key, filename):
    b, n = pub_key
    with open(filename, 'w') as f:
        json.dump({'b': [str(bi) for bi in b], 'n': str(n)}, f)

def save_private_key(priv_key, filename):
    a, n = priv_key
    with open(filename, 'w') as f:
        json.dump({'a': [str(ai) for ai in a], 'n': str(n)}, f)

def main():
    message = "Helli world"
    k = 1024
    m = 256
    block_size = 128

    pub_key, priv_key = generate_fiat_shamir_keys(k, m)
    save_public_key(pub_key, 'public_key.json')
    save_private_key(priv_key, 'private_key.json')

    # Формирование подписи
    t, s = fiat_shamir_sign(message, priv_key, sha256, m)
    print('Signature: t =', t, 's =', s)

    s_bytes = t.to_bytes((t.bit_length() + 7) // 8, 'big') + bytes.fromhex(s)
    comb = message.encode('utf-8') + s_bytes
    hash_m_ = sha256(comb)

    Client = {
        "CMSVersion": "1",
        "DigestAlgorithmIdentifiers": "SHA-256",
        "EncapsulatedContentInfo": {
            "ContentType": "text/plain",
            "OCTET STRING": message
        },
        "SignerInfos": {
            "CMSVersion": "1",
            "SignerIdentifier": "Cherenkov",
            "DigestAlgorithmIdentifiers": "SHA-256",
            "SignatureAlgorithmIdentifier": "Fiat-Shamir",
            "SignatureValue": {"t": str(t), "s": s},
            "SubjectPublicKeyInfo": {
                "b": [str(bi) for bi in pub_key[0]],
                "n": str(pub_key[1])
            },
            "UnsignedAttributes": {
                "ObjectIdentifier": "signature-time-stamp",
                "SET_OF_AttributeValue": ''
            }
        }
    }
    with open("client.json", "w", encoding="utf-8") as file:
        json.dump(Client, file, indent=4)

    request = {
        "signature": {"t": str(t), "s": s},
        "message": message,
        "hash_algorithm": "SHA-256",
        "pub_key": {"b": [str(bi) for bi in pub_key[0]], "n": str(pub_key[1])}
    }
    request_b = json.dumps(request).encode('utf-8')

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as stream:
        try:
            stream.connect(('127.0.0.1', 9090))
            request_length = len(request_b)
            request_length_bytes = request_length.to_bytes(4, 'big')
            stream.sendall(request_length_bytes)
            stream.sendall(request_b)
            print("Запрос отправлен успешно")
            length_bytes = stream.recv(4)
            if len(length_bytes) != 4:
                raise Exception("Не удалось прочитать длину ответа")
            response_length = int.from_bytes(length_bytes, 'big')
            response_data = b""
            while len(response_data) < response_length:
                chunk = stream.recv(min(1024, response_length - len(response_data)))
                response_data += chunk
            response = json.loads(response_data.decode('utf-8'))
            print("Ответ от TSA:", response)

            if "error" in response:
                raise Exception(f"Ошибка от сервера: {response['error']}")

            timestamp = response["timestamp"]
            tsa_signature = response["tsa_signature"]
            tsa_pub_key = response["tsa_pub_key"]
            hash_m_ = response["hash_m"]

            # Проверка хеша
            # check_sign = (hash_m_ + timestamp).encode('utf-8')
            # check_sign_hash = sha256(check_sign)
            # if check_sign_hash != hash_m_:
            #     raise Exception("Хеш в ответе не совпадает")

            if not fiat_shamir_verify((hash_m_ + timestamp), tsa_signature, tsa_pub_key, sha256, m):
                raise Exception("Подпись TSA не верна")

            Client["SignerInfos"]["UnsignedAttributes"]["SET_OF_AttributeValue"] = {
                "timestamp": timestamp,
                "tsa_signature": tsa_signature,
                "tsa_pub_key": tsa_pub_key,
                "hash_m": hash_m_
            }
            with open("client_9.json", "w", encoding="utf-8") as file:
                json.dump(Client, file, indent=4)
            print("Структура Client обновлена и сохранена")
        except Exception as e:
            print(f"Ошибка: {e}")
            raise

if __name__ == "__main__":
    main()