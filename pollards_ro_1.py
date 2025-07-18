import random
import math
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

def f(x, n):
    return (x**2 + 1) % n

def pollards_ro(n, c=1):
    a = c
    b = c
    while True:
        a = f(a)
        b = f(f(b))
        d,_,_ = euclidean_algorithm(a - b, n)
        if 1 < d < n:
            return d, n // d
        if d == n:
            return None

def pollards_ro_1(n, B):
    a = random.randint(2, n - 2)
    d, _, _ = euclidean_algorithm(a, n)
    if d >= 2:
        return d, n // d
    
    l = 0
    for p in B:
        l = math.floor(math.log(n)/math.log(p))
        a = fast_exp_mod(a, p**l, n)

    d, _, _ = euclidean_algorithm(a - 1, n)
    if d == 1 and d == n:
        return None
    else:
        return d, n // d  




if __name__ == "__main__":
    # n = int(input("введите число:"))
    # result = pollards_ro(n)
    # if result:
    #     print(f"Найден делитель: {result}")
    # else:
    #     print("Делитель не найден")

    n = int(input("введите число:"))  
    B = [2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31]
    result = pollards_ro_1(n, B)
    if result:
        print(f"Найден делитель: {result}")
    else:
        print("Делитель не найден")
    