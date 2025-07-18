import random
from rsa import *

def generate_public_r(n, p):
    r = []
    for _ in range(n):
        while True:
            r_i = random.randint(1, p - 1)
            if r_i not in r:
                r.append(r_i)
                break
    return r

def create_poly_coef(t, p):
    a = []
    for _ in range(t):
        while True:
            a_i = random.randint(1, p - 1)
            if a_i not in a:
                a.append(a_i)
                break
    print("Секрет = ", a[0])
    return a

def calculate_s_i(r, a, n, p):
    s = []
    for i in range(n):
        s_i = 0
        for degree, coef in enumerate(a):
            s_i += coef * pow(r[i], degree, p)
        s_i = s_i % p
        s.append(s_i)
    return s

def generate_users_keys(r, s_i, n):
    keys = [(r[i], s_i[i]) for i in range(n)]
    return keys

def select_random_t_users(users_keys, t):
    return random.sample(users_keys, t)

def restore_secret(users_keys, p, t):
    users = select_random_t_users(users_keys, t)
    secret = 0
    for i in range(t):
        xi, yi = users[i]
        term = yi
        for j in range(t):
            if j == i:
                continue
            xj, _ = users[j]
            denominator = (xj - xi) % p
            _, inv_denominator, _ = euclidean_algorithm(denominator, p)
            term = (term * xj * inv_denominator) % p
        secret = (secret + term) % p
    return secret

def main():
    n = 10
    t = 7
    p = generate_p(128)
    
    r = generate_public_r(n, p)
    a = create_poly_coef(t, p)
    s_i = calculate_s_i(r, a, n, p)
    users_keys = generate_users_keys(r, s_i, n)
    
    a = [0]
    
    secret = restore_secret(users_keys, p, t)
    print(f"Восстановленное секретное число из {t} пользователей = ", secret)

if __name__ == "__main__":
    main()