import random
import math
import ast
import json
def euclidean_algorithm(x, y):
    a_2 = 1; a_1 = 0
    b_2 = 0; b_1 = 1
    while y != 0:
        q = x // y
        r = x - q * y
        a = a_2 - q * a_1
        b = b_2 - q * b_1

        x = y; y = r
        a_2 = a_1; a_1 = a
        b_2 = b_1; b_1 = b

    m = x; a = a_2; b = b_2
    return m, a, b 
def fast_exp_mod(a, n, m):  
    x = 1
    while n > 0:
        if n & 1:
            x = (x * a) % m
        a = (a * a) % m
        n = n >> 1
    return x

def generate_p(k):
    while True:
        p = random.getrandbits(k)
        p = p | (1 << k - 1)
        p = p | 1
        if miller_rabin(p):
            return p

def miller_rabin(n):
    if n <= 1:
        return False
    if n <= 3:
        return True
    if n % 2 == 0:
        return False

    s, d = 0, n - 1
    while d % 2 == 0:
        s += 1
        d //= 2
    for _ in range(5):
        a = random.randint(2, n - 2)
        x = pow(a, d, n)
        if x == 1 or x == n - 1:
            continue
        for _ in range(s - 1):
            x = pow(x, 2, n)
            if x == n - 1:
                break
        else:
            return False
    return True

def pollards_ro_1(n, B):
    a = random.randint(2, n - 2)
    d,_,_  = euclidean_algorithm(a, n)
    if d >= 2:
        return d  # Найден делитель

    for p in B:
        l = math.floor(math.log(n, p))
        a = fast_exp_mod(a, p**l, n)

    d,_,_ = euclidean_algorithm(a - 1, n)
    if 1 < d < n:
        return d  # Найден делитель
    else:
        return None  # Делитель не найден

def factorize(n, B):
    factors = []
    if n == 1:
        return factors
    if miller_rabin(n):
        factors.append(n)
        return factors
    d = pollards_ro_1(n, B)
    if d is None:
        return factors
    factors += factorize(d, B)
    factors += factorize(n // d, B)
    return factors

def check_primitive_element(alpha, p, factors):
    for q in factors:
        if fast_exp_mod(alpha, (p - 1) // q, p) == 1:
            return False
    return True

def find_primitive_element(p, factors, max=1000):
    for _ in range(max):
        alpha = random.randint(2, p - 1)
        if check_primitive_element(alpha, p, factors):
            return alpha
    return None

def split_into_blocks(message, block_size):
    return [message[i:i+block_size] for i in range(0, len(message), block_size)]
def pudding(message, block_size):
    last_block = message[-1]
    pad_len = block_size - len(last_block)
    if pad_len == 0:
        pad = bytes([block_size] * block_size)
        message.append(pad)
    else:
        pad = bytes([pad_len] * pad_len)
        message[-1] = last_block + pad
    return message
def remove_padding(message):
    last_block = message[-1]
    pad_len = last_block[-1]
    last_block_unpadded = last_block[:-pad_len]
    message[-1] = last_block_unpadded    
    return message

def encrypt(message, alpha, b, p, r):
       
    c1 = fast_exp_mod(alpha, r, p)
    c2 = (message*fast_exp_mod(b, r, p)) % p
    return (c1, c2)    
    
def encrypt_msg(message, alpha, b, p, r, block_size):
    m_by = message.encode('utf-8')
    # print(m_by)
    split = split_into_blocks(m_by, block_size)
    # print(split)
    msg_pud = pudding(split, block_size)
    # print(msg_pud)
    encrypted_blocks = []
    for block in msg_pud:
        m_int = int.from_bytes(block, 'big')
        c1, c2 = encrypt(m_int, alpha, b, p, r)
        encrypted_blocks.append((c1, c2))
    # print(encrypted_blocks)
    return encrypted_blocks

def decrypt(c1, c2, a, p):
    c11 = pow(pow(c1, a, p), -1, p)
    m = (c2 * c11) % p
    decrypted_message = m.to_bytes((m.bit_length() + 7) // 8, 'big').decode('utf-8')
    
    return decrypted_message

def decrypt_msg(encrypted_blocks, a, p):
    decrypt_blocks = []
    for c1, c2 in encrypted_blocks:
        decrypted = decrypt(c1, c2, a, p)
        decrypt_blocks.append(decrypted)
    # print(decrypt_blocks)
    msg_by = [decrypt_blocks_i.encode('utf-8') for decrypt_blocks_i in decrypt_blocks]
    del_pud = remove_padding(msg_by)
    # print(del_pud)
    result = ''.join([b.decode('utf-8') for b in del_pud])
    # print(result)
    return result

def encrypt_message(message, alpha, b, p, block_size):
    r = random.randint(0, p - 2)
    encrypted_blocks = encrypt_msg(message, alpha, b, p, r, block_size)
    # save_to_file('encrypted_blocks.txt', encrypted_blocks)
    return encrypted_blocks

def decrypt_message(encrypted, a, p):
    decrypted_message = decrypt_msg(encrypted, a, p)
    return decrypted_message

def save_to_file(filename, data):
    with open(filename, 'w') as file:
        file.write(str(data))

def read_from_file(filename):
    with open(filename, 'r') as file:
        content = file.read()
        return ast.literal_eval(content)

def save_encrypted_message(ciphertext, filename):
    encrypted_message = {
        "Version": 0,
        "EncryptedContentInfo": {
            "ContentType": "text",
            "ContentEncryptionAlgorithmIdentifier": "ElgamalEncryption",
            "encryptedContent":  ciphertext,
            "OPTIONAL": {}
        }
    }
    with open(filename, 'w') as file:
        json.dump(encrypted_message, file, indent=4)

def save_encrypted_PrivateKey(a, filename):
    key = {
        "ElgamalPrivateKey": {
            "a": a,  
        }
    }
    with open(filename, 'w') as file:
        json.dump(key, file, indent=4)
        
def save_encrypted_PublicKey(p, alpha, b, filename):
    key = {
        "ElgamalPublicKey": {
            "P": p,
            "alpha": alpha,
            "B": b
        }
    }
    with open(filename, 'w') as file:
        json.dump(key, file, indent=4)
    
def load_encrypted_message(filename):
    with open(filename, 'r') as file:
        encrypted_message = json.load(file)
    ciphertext = encrypted_message["EncryptedContentInfo"]["encryptedContent"]
    return ciphertext

def generate(k):
    p = generate_p(k)
    a = random.randint(1, p-2)
    phi = p - 1
    B = [2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31]
    factors = factorize(phi, B)
    alpha = find_primitive_element(p, factors)
    b = fast_exp_mod(alpha, a, p)
    save_encrypted_PrivateKey(a, 'PrivateKeyElgamal.json')
    save_encrypted_PublicKey(p, alpha, b, 'PublicKeyElgamal.json')
    save_to_file('p.txt', p)
    save_to_file('a.txt', a)
    save_to_file('alpha.txt', alpha)
    save_to_file('b.txt', b)
    return p, a, alpha, b

if __name__ == "__main__":
    k = 512
    block_size = 64
    flag = True
    while flag:
        print("Выберите действие:")
        print("1. Генерация параметров")
        print("2. Зашифрование")
        print("3. Расшифрование")
        print("4. Выход")
        choice = input("Введите номер действия: ")

        if choice == '1':
            p, a, alpha, b = generate(k)
            print(f"Параметры p, a, alpha, b сгенерированы и сохранены в файлы.")
        elif choice == '2':
            alpha = read_from_file('alpha.txt')
            b = read_from_file('b.txt')
            p = read_from_file('p.txt')
            message = input("Введите сообщение для зашифрования: ")
            encrypted = encrypt_message(message, alpha, b, p, block_size)
            save_encrypted_message(encrypted, 'ciphertext_Elgamal.json')
            print(f"Зашифрованное сообщение: {encrypted}")
        elif choice == '3':
            a = read_from_file('a.txt')
            p = read_from_file('p.txt')
            encr = load_encrypted_message("ciphertext_Elgamal.json")
            decrypted = decrypt_message(encr, a, p)
            print(f"Расшифрованное сообщение: {decrypted}")
        elif choice == "4":
            flag = False
    
    
    
    