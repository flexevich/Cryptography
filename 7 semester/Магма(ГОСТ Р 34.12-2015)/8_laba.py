# ШИФР МАГМА (ГОСТ Р 34.12-2015)

# S-блоки
S = [
    [12, 4, 6, 2, 10, 5, 11, 9, 14, 8, 13, 7, 0, 3, 15, 1],
    [6, 8, 2, 3, 9, 10, 5, 12, 1, 14, 4, 7, 11, 13, 0, 15],
    [11, 3, 5, 8, 2, 15, 10, 13, 14, 1, 7, 4, 12, 9, 6, 0],
    [12, 8, 2, 1, 13, 4, 15, 6, 7, 0, 10, 5, 3, 14, 9, 11],
    [7, 15, 5, 10, 8, 1, 6, 13, 0, 9, 3, 14, 11, 4, 2, 12],
    [5, 13, 15, 6, 9, 2, 12, 10, 11, 7, 8, 1, 4, 3, 14, 0],
    [8, 14, 2, 5, 6, 9, 1, 12, 15, 4, 11, 0, 13, 10, 3, 7],
    [1, 7, 14, 13, 0, 5, 8, 3, 4, 15, 10, 6, 9, 12, 11, 2]
]


# преобразование байт - 32-битное 
def bytes_to_u32(data):
    return int.from_bytes(data, byteorder='big')


# преобразование 32-битного - байты
def u32_to_bytes(value):
    return value.to_bytes(4, byteorder='big')


# нелинейное S-блок преобразование
def s(value):
    result = 0
    for i in range(8):
        n = (value >> (4 * i)) & 0x0F
        s_value = S[i][n] 
        result += (s_value << (4 * i))
    return result


# сложение с ключом, S-подстановка, циклический сдвиг на 11 бит
def g(key, value):
    sum_val = (value + key)  & 0xFFFFFFFF
    t_val = s(sum_val)
    result = ((t_val << 11) | (t_val >> 21))  & 0xFFFFFFFF
    return result


def gen_keys(key_bytes):
    k = []
    for i in range(8):
        k.append(bytes_to_u32(key_bytes[i * 4:(i + 1) * 4]))

    keys = []
    for _ in range(3):
        keys.extend(k)
    keys.extend(reversed(k))

    return keys


def encode(key, plaintext):
    keys = gen_keys(key)

    left = bytes_to_u32(plaintext[:4])
    right = bytes_to_u32(plaintext[4:])

    for i in range(31):
        f_result = g(keys[i], right)
        left, right = right, left ^ f_result

    f_result = g(keys[31], right)
    left = left ^ f_result

    return u32_to_bytes(left) + u32_to_bytes(right)


def decode(key, ciphertext):
    keys = gen_keys(key)[::-1]

    left = bytes_to_u32(ciphertext[:4])
    right = bytes_to_u32(ciphertext[4:])

    for i in range(31):
        f_result = g(keys[i], right)
        left, right = right, left ^ f_result

    f_result = g(keys[31], right)
    left = left ^ f_result

    return u32_to_bytes(left) + u32_to_bytes(right)


def print_round_keys(keys):
    print(f" ")
    print("Раундовые ключи:")
    for i, k in enumerate(keys, 1):
        print(f"  K{i:2d} = {k:08X}")


def main():

    print("МАГМА (ГОСТ Р 34.12-2015)")
    print(f" ")

    # ввод ключа
    key_hex = input("Ключ (64 hex символа): ").strip().replace(" ", "")
    key = bytes.fromhex(key_hex)

    # вывод раундовых ключей
    keys = gen_keys(key)
    # print_round_keys(keys)

    # выбор режима
    mode = input("\nРежим (1 — Шифрование, 2 — Дешифрование): ").strip()

    if mode == '1':
        plaintext_hex = input("Открытый текст (16 hex символов): ").strip().replace(" ", "")
        plaintext = bytes.fromhex(plaintext_hex)

        ciphertext = encode(key, plaintext)

        print(f" ")
        print(f"M (открытый текст) = {plaintext.hex()}")
        print(f"C (шифртекст)      = {ciphertext.hex()}")

    elif mode == '2':
        ciphertext_hex = input("Шифртекст (16 hex символов): ").strip().replace(" ", "")
        ciphertext = bytes.fromhex(ciphertext_hex)

        plaintext = decode(key, ciphertext)

        print(f" ")
        print(f"C (шифртекст)      = {ciphertext.hex()}")
        print(f"M (открытый текст) = {plaintext.hex()}")

    else:
        print("Неверный режим.")


if __name__ == "__main__":
    main()