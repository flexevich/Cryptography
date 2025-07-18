import random   
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
def generate_p(k):

    while True:
        p = random.getrandbits(k)
        p = p | (1 << k - 1)
        p = p | 1
        if miller_rabin(p):
            return p
def jacobi_symbol(a, p):
    
    if p <= 0 or p % 2 == 0:
        raise ValueError("p должно быть положительным нечетным числом")

    g = 1

    if a == 0:
        return 0

    if a == 1:
        return g

    k = 0
    b = a
    while b % 2 == 0:
        b //= 2
        k += 1

    if k % 2 == 0:
        s = 1
    else:
        if p % 8 in (1, 7):
            s = 1
        elif p % 8 in (3, 5):
            s = -1

    if b == 1:
        return g * s

    if b % 4 == 3 and p % 4 == 3:
        s = -s

    return g * s * jacobi_symbol(p % b, b)
def mod_2 ( a,  p ) : 

    if jacobi_symbol(a, p) != 1:
        print("Символ Якоби (a/p) не равен 1, решение не существует.")
        return None
    k = 0
    h = p - 1
    while h % 2 == 0:
        k += 1
        h //= 2

    a1 = pow(a, (h + 1) // 2, p)
    a2 = pow(a, h, p)
    N = random.randint(2, 100)
    with open('N.xt', 'w', encoding='utf-8') as file:
        file.write(str(N))
    while jacobi_symbol(N, p) != -1:
        N += 1
    N1 = pow(N, h, p)
    N2 = 1
    j = 0

    for i in range(k - 1):
        b = (a1 * N2) % p
        c = (a2 * b * b) % p
        d = pow(c, 2 ** (k - 2 - i), p)
        if d == 1:
            j = 0
        elif d == p - 1:
            j = 1
        N2 = (N2 * pow(N1, 2 ** j, p)) % p

    x1 = (a1 * N2) % p
    x2 = p - x1
    return x1, x2
def fast_exp_mod(a, n, m):  
    x = 1
    while n > 0:
        if n & 1:
            x = (x * a) % m
        a = (a * a) % m
        n = n >> 1
    return x

def save_encrypted_message(ciphertext, filename):
    encrypted_message = {
        "Version": 0,
        "EncryptedContentInfo": {
            "ContentType": "text",
            "ContentEncryptionAlgorithmIdentifier": "rabinEncryption",
            "encryptedContent":  ciphertext,
            "OPTIONAL": {}
        }
    }
    with open(filename, 'w') as file:
        json.dump(encrypted_message, file, indent=4)

def save_encrypted_PrivateKey(prime1, prime2, filename):
    key = {
        "RABINPrivateKey": {
            "prime1": prime1, 
            "prime2": prime2,
            "description": {
                "prime1": "Prime factor p of n",
                "prime2": "Prime factor q of n"
            }
        }
    }
    with open(filename, 'w') as file:
        json.dump(key, file, indent=4)
def save_encrypted_PublicKey(N, filename):
    key = {
        "RABINPublicKey": {
            "N": N,
            "description": {
                "prime1": "n = q * p"
            }
        }
    }
    with open(filename, 'w') as file:
        json.dump(key, file, indent=4)    

def load_encrypted_message(filename):
    with open(filename, 'r') as file:
        encrypted_message = json.load(file)
    ciphertext = encrypted_message["EncryptedContentInfo"]["encryptedContent"]
    return ciphertext

def encrypt(a, n):
    encrypt_n = fast_exp_mod(a, 2, n)
    return encrypt_n

def split_into_blocks(message, block_size):
    return [message[i:i+block_size] for i in range(0, len(message), block_size)]


def pudding(message):
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

def encrypt_block(message, n):
    encrypted_blocks = [encrypt(block, n) for block in message]
    
    return encrypted_blocks

def decrypt_block(message, p, q):
    decrypt_message = []
    message_block = message
    
    for block in message_block:
        decripted = []
        
        decripted = decrypt(block, p, q)
        for m in decripted:
            try:
                msg = m.to_bytes((m.bit_length() + 7) // 8, 'big').decode()
                decrypt_message.append(msg)
            except:
                continue
            
    msg_dy = [block.encode('utf-8') for block in decrypt_message]
    return msg_dy
        

def decrypt(c, p, q):
    n = p * q
    mp1, mp2 = mod_2(c, p)
    mq1, mq2 = mod_2(c, q)
    _, yp, yq = euclidean_algorithm(p, q)
    m1 = (mp1 * q * yq + mq1 * p * yp) % n
    m2 = n - m1
    if m2 < 0:
        m2+=n
    m3 = (mq2 * p * yp - mp2 * q * yq) % n
    m4 = n - m3
    if m4 < 0:
        m4+=n    
    decrypted = [m1, m2, m3, m4]
    return decrypted

def save_to_file(filename, data):
    with open(filename, 'w') as file:
        file.write(str(data))

def read_from_file(filename):
    with open(filename, 'r') as file:
        content = file.read()
        return int(content)

def generate(k):
    p = generate_p(k)
    q = generate_p(k)
    while p % 4 != 3:
        p = generate_p(k)
    while q % 4 != 3:
        q = generate_p(k)
    n = p * q
    save_to_file('p.txt', p)
    save_to_file('q.txt', q)
    save_to_file('n.txt', n)
    save_encrypted_PrivateKey(q, p, 'PrivateRabin.json')
    save_encrypted_PublicKey(n, 'PublicRabin.json')            
    return p, q, n

def encrypt_message(message, n, block_size=8):
    a_by = message.encode('utf-8')
    split = split_into_blocks(a_by, block_size)
    msg_pud = pudding(split)
    a_num = [int.from_bytes(a_by, 'big') for a_by in msg_pud]
    encr = encrypt_block(a_num, n)
    return encr

def decrypt_message(encr ,p, q):
    
    decrypt_bl = decrypt_block(encr, p, q)
    del_pud = remove_padding(decrypt_bl)
    result = ''.join([b.decode() for b in del_pud])
    return result

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
            p, q, n = generate(k)   
            print(f"Параметры p, q, n сгенерированы и сохранены в файлы.")
        elif choice == '2':
            n = read_from_file('n.txt')
            message = input("Введите сообщение для зашифрования: ")
            encrypted = encrypt_message(message, n, block_size)
            save_encrypted_message(encrypted, 'ciphertext_Rabin.json')
            print(f"Зашифрованное сообщение: {encrypted}")
        elif choice == '3':
            p = read_from_file('p.txt')
            q = read_from_file('q.txt')
            encr = load_encrypted_message("ciphertext_Rabin.json")
            decrypted = decrypt_message(encr , p, q)
            print(f"Расшифрованное сообщение: {decrypted}")
        elif choice == "4":
            flag = False 
# if __name__ == "__main__":
#     k = 255  # Длина ключа в битах
#     p = generate_p(k)
#     q = generate_p(k)
#     while q == p:
#         q = generate_p(k)      
#     n = p * q
#     block_size = 8

    
#     message = "Hello my name is Dmitry"
#     a_by = message.encode('utf-8')
#     split = split_into_blocks(a_by,block_size)
#     msg_pud = pudding(split)
#     print(msg_pud)
#     a_num  = [int.from_bytes(a_by, 'big') for a_by in msg_pud]
#     print(a_num)
#     encr = encrypt_block(a_num, n)
#     print(encr)
#     decrypt_bl = decrypt_block(encr, p, q)
#     print(decrypt_bl)
    
#     del_pud = remove_padding(decrypt_bl)
#     print(del_pud)
#     result = ''.join([b.decode() for b in del_pud])
    
#     print(result)
    # encr = encrypt_block(a_num, n)
    # print(encr)
    # enc = encrypt_block(message, block_size, n)
    # with open('encrypt_block.txt', 'w', encoding='utf-8') as file:
    #      file.write(str(enc))
    # print(f"Зашифрованные блоки: {enc}")

    # Дешифрование
    # dec = decrypt(encr, p, q)
    # with open('decrypt_block.txt', 'w', encoding='utf-8') as file:
    #       file.write(str(dec))
    # print(dec)


    # for m in dec:
    #     try:
    #         msg = m.to_bytes((m.bit_length() + 7) // 8, 'big').decode()
    #         print(f"message: {msg}")
    #     except:
    #         continue
    
    
      