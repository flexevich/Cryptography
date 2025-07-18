import math
import re

def euclidean_algorithm(x, y):
    a_2, a_1 = 1, 0
    b_2, b_1 = 0, 1
    while y != 0:
        q = x // y
        r = x - q * y
        a = a_2 - q * a_1
        b = b_2 - q * b_1

        x, y = y, r
        a_2, a_1 = a_1, a
        b_2, b_1 = b_1, b

    return x, a_2, b_2

def order(a, p):
    phi = p - 1
    div = set()
    for i in range(1, int(math.sqrt(phi)) + 1):
        if phi % i == 0:
            div.add(i)
            div.add(phi // i)
    for d in sorted(div):
        if pow(a, d, p) == 1:
            return d  
    return -1  

def f(c, u, v, p):
    if c < p // 3:
        new_c = (b * c) % p
        new_u = (u + 1) % (p - 1)
        new_v = v
    elif c < 2 * p // 3:
        new_c = (c * c) % p
        new_u = (2 * u) % (p - 1)
        new_v = (2 * v) % (p - 1)
    else:
        new_c = (a * c) % p
        new_u = u
        new_v = (v + 1) % (p - 1)

    return new_c, new_u, new_v

def pollards_rho(a, b, p):
    r = order(a, p)
    if r == -1:
        print("Решения нет ")
        return None

    if pow(b, r, p) != 1:
        print("Решений нет")
        return None

    u, v = 2, 2  
    c = (pow(a, u, p) * pow(b, v, p)) % p
    d = c
    u_d, v_d = u, v

    for _ in range(10000):
        c, u, v = f(c, u, v, p)
        d, u_d, v_d = f(d, u_d, v_d, p)  
        d, u_d, v_d = f(d, u_d, v_d, p)  

        if c == d:
            break

    delta_u = (u - u_d) % (p - 1)
    delta_v = (v_d - v) % (p - 1)

    g, inv, _ = euclidean_algorithm(delta_u, p - 1)
    if delta_v != 0:
        print("решения нет")
        return 0
    delta_u //= g
    delta_v //= g
    mod = (p - 1) // g

    x = (inv * delta_v) % mod

    
    return x

def read_file(filename):
    with open(filename, 'r') as file:
        text = file.read()

    a_match = re.search(r"a\s*=\s*(\d+)", text)
    b_match = re.search(r"b\s*=\s*(\d+)", text)
    p_match = re.search(r"p\s*=\s*(\d+)", text)

    a = int(a_match.group(1))
    b = int(b_match.group(1))
    p = int(p_match.group(1))

    return a, b, p

if __name__ == "__main__":
    filename = "number_for_laba3.txt"
    a, b, prime_number = read_file(filename)
    r = order(a, prime_number)
    print(f"Порядок числа {a} по модулю {prime_number}: {r}")

    x = pollards_rho(a, b, prime_number)
    if x is not None:
        print(f"Дискретный логарифм x (a^x ≡ b mod p) = {x}")
    else:
        print("Решений нет")