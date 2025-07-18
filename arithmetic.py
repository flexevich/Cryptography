import random
# обобщенный (расширенный) алгоритм Евклида
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
# алгоритм быстрого возведения в степень
def fast_exp(a, n):
    x = 1
    while n > 0:
        if n & 1:
            x = x * a
        a = a * a
        n = n >> 1
    return x
# алгоритм быстрого возведения в степень по модулю
def fast_exp_mod(a, n, m):  
    x = 1
    while n > 0:
        if n & 1:
            x = (x * a) % m
        a = (a * a) % m
        n = n >> 1
    return x
#символ Якоби
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
#тест на простоту числа n
def fermat_test(n):
    
    if n <= 1 or n == 4:
        return "Число n составное"
    if n <= 3:
        return "Число n, вероятно, простое"
    
    for _ in range(5):

        a = random.randint(2, n-2)

        r = pow(a, n-1, n)

        if r != 1:
            print("Число n составное")
            return
    
    print("Число n, вероятно, простое")
    return
# Тест Соловэя-Штрассена для проверки простоты числа n.
def Solovey_Strassen(n):
    if n <= 1 or n == 4:
        return "Число n составное"
    if n <= 3:
        return "Число n, вероятно, простое"
    
    for _ in range(5):

        a = random.randint(2, n-2)

        r = pow(a, (n-1)//2, n)

        if r != 1 and r != n-1:
            print("Число n составное")
            return
        
    s = jacobi_symbol(a, n)
    if r % n == s % n:
        print("Число n, вероятно, простое")
        return
    else: 
        print("Число n составное")
    return
# тест Миллера-Рабина для проверки простоты числа n.
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

def mod(a, b, m):
    d, _, _ = euclidean_algorithm(a, m)
    if b % d != 0:
        return "Решений нет"
    a1 = a // d
    b1 = b // d
    m1 = m // d
    
    _,x0, _ = euclidean_algorithm(a1, m1)
    x0 = (x0 * b1) % m1
    solutions = []
    for k in range(d):
        new_solution = x0 + k * m1
        solutions.append(new_solution)
    return solutions
    
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
    N = 2
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



def system(a_list, m_list):
    M = 1
    for mi in m_list:
        M *= mi  
    x = 0
    for a, m in zip(a_list, m_list):
        Mi = M // m
        
        yi = euclidean_algorithm(Mi, m)
        x += a * Mi * yi
    return x % M, M

def gen_polinom(p, k):
    polinom = [random.randint(0, p-1) for _ in range(k + 1)]

    if polinom[0] == 0:
        polinom[0] = random.randint(1, p-1)
    return polinom


def division(d, polinom, p):
    while len(d) >= len(polinom):
        c = d[0] // polinom[0]

        for i in range(len(polinom)):
            d[i] -= polinom[i] * c

        if d[0] == 0:
            d.pop(0)

    for i in range(len(d)):
        if d[i] != 0:
            d[i] %= p
    return d


def sum(polinom1, polinom2, p):
    max_len = max(len(polinom1), len(polinom2))
    sum = [0] * max_len
    for i in range(max_len):

        if i < len(polinom1):
            a = polinom1[i]
        else:
            a = 0
        if i < len(polinom2):
            b = polinom2[i]
        else:
            b = 0

        sum[i] = (a + b) % p

    return sum


def multiplication(polinom1, polinom2, n, p):
    mult = [0] * (len(polinom1) + len(polinom2) - 1)

    for i in range(len(polinom1)):
        for j in range(len(polinom2)):
            mult[i + j] += (polinom1[i] * polinom2[j]) % p

    while len(mult) > len(n) and mult[0] == 0:
        mult.pop(0)

    if len(mult) >= len(n):
        mult = division(mult, n, p)
    return mult





    
def describe_number(num):
    match num:
        case 0:
            return 0
        case 1:
            print(" ")
            print("#################################################################")
            print(" ")
            x = int(input("Введите значение x: "))
            y = int(input("Введите значение y: "))
            m, a, b = euclidean_algorithm(x, y)
            print(f"НОД({x}, {y}) = {m}")
            print(f"Коэффициенты: a = {a}, b = {b}")
            return
        case 2:
            print(" ")
            print("#################################################################")
            print(" ")
            a = int(input("Введите основание a: "))
            n = int(input("Введите степень n: "))
            fast_exp1 = fast_exp(a, n)
            print(f"{a}^{n} = {fast_exp1}")
        case 3:
            print(" ")
            print("#################################################################")
            print(" ")
            a = int(input("Введите основание a: "))
            n = int(input("Введите степень n: "))
            m = int(input("Введите модуль m: "))
            fast_exp_mod1 = fast_exp_mod(a, n, m)
            print(f"{a}^{n} mod {m} = {fast_exp_mod1}") 
        case 4:
            print(" ")
            print("#################################################################")
            print(" ")
            a = int(input("Введите число а: "))
            p = int(input("Ведите число p: "))
            jacobi_symbol = jacobi_symbol(a, p)
            print(f"Символ Якоби ({a}/{p}) = {jacobi_symbol}")
        case 5:
            print(" ")
            print("#################################################################")
            print(" ")
            n = int(input("Введите число: "))
            fermat_test(n)
        case 6: 
            print(" ")
            print("#################################################################")
            print(" ")
            n = int(input("Введте число: "))
            Solovey_Strassen(n)
        case 7:
            print(" ")
            print("#################################################################")
            print(" ")
            n = int(input("Введите число: "))
            if miller_rabin(n):
                print("Число n, вероятно, простое")
            else:
                print("Число n составное")
        case 8:
            print(" ")
            print("#################################################################")
            print(" ")
            n = int(input("Введите разряд: "))
            prime_number = generate_p(n)
            print("Сгенерированное простое число:", prime_number)
        case 9:
            print(" ")
            print("#################################################################")
            print(" ")
            a = int(input("Введите a: "))
            b = int(input("Введите b: "))
            m = int(input("Ввудите m: "))
            print(f"{a}x = {b} (mod {m})")
            result = mod(a, b, m)
            for solution in result:
                print(f"Решения сравнения: x = {solution} (mod {m})")


        case 10:
            print(" ")
            print("#################################################################")
            print(" ")
            a = int(input("Введите a: "))
            p = int(input("Ввудите p: "))
            x1, x2 = mod_2(a, p)
            print(f"Решения сравнения x^2 = {a} (mod {p}): x1 = {x1}, x2 = {x2}")
        case 11: 
            print(" ")
            print("#################################################################")
            print(" ")
            n = int(input("Введите количество уравнений: "))
            a_list = []
            m_list = []
            for i in range(n):
                a = int(input(f"Введите остаток a{i+1}: "))
                m = int(input(f"Введите модуль m{i+1}: "))
                a_list.append(a)
                m_list.append(m)

            for i in range(n):
                for j in range(i + 1, n):
                    m, _, _ = euclidean_algorithm(m_list[i], m_list[j])
                    if m != 1:
                        raise ValueError(f"Модули m{i+1} и m{j+1} не взаимно просты.")

            try:
                solution, M = system(a_list, m_list)  
                print(f"Решение системы сравнений: x ≡ {solution % M} mod {M}")
            except ValueError as e:
                print(e)
        case 12:
            p = int(input("Введите над каким полем происходит построение: "))
            k = int(input("Введите степень построения: "))
            neprivod = list(map(int, input("Введите неприводимый полином над этим полем").split()))
            print(f"Неприводимый полином: {neprivod}")
        
            # polinom1 = [1, 2]
            # polinom2 = [1, 0]
            polinom1 = gen_polinom(p, random.randint(1, k - 1))
            print(f"Полином 1: {polinom1}")
            polinom2 = gen_polinom(p, random.randint(1, k - 1))
            print(f"Полином 2: {polinom2}")
        
            print(f"Сложение: {sum(polinom1, polinom2, p)}")
            print(f"Произведение 1 на 2: {multiplication(polinom1, polinom2, neprivod, p)}")
            
            

a = True
while a:
    print(" ")
    print("#################################################################")
    print(" ")
    print("1 - Обобщенный (расширенный) алгоритм Евклида") 
    print("2 - Алгоритм быстрого возведения в степень")
    print("3 - Алгоритм быстрого возведения в степень по модулю")
    print("4 - Символ Якоби")
    print("5 - Тест Ферма (Алгоритм проверки чисел на простоту)")
    print("6 - Тест Соловэя-Штрассена (Алгоритм проверки чисел на простоту)")
    print("7 - Тест Миллера-Рабина (Алгоритм проверки чисел на простоту)")
    print("8 - Генерация простого числа заданной размерности")
    print("9 - Решение сравнения первой степени")
    print("10 - Решение сравнения второй степени")
    print("11 - Решение системы сравнений")
    print("12 - Построение конечного поля и реализация операций над данным полем")
    print("0 - Выход")
    num = int(input("Выберете алгоритм: "))        
    if describe_number(num) == 0:
        a = False
    


