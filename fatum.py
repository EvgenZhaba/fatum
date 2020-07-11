# -*- coding: utf8 -*-
"""
EvgenZhaba

Модуль реализует:
    Вычисление псевдослучайной координаты.
    Вычисление квантово случайной координаты с применением КГСЧ(запроса к сайту).
В процессе обращения формируется кэш для заданных n точек, которые задаются перед использованием.
После установки количества точек выполняется запрос к сайту и запись значений в кэш.
К кэшу можно обратиться n раз, то есть сколько точек было задано.
    Формирование ссылки по координатам на картах google.
"""

from math import asin, sin, cos, pi, sqrt, atan2
import urllib.request, json
import requests
import random

R_EARTH = 6356863
POINTS = 1 #количество заданных точек
DATACASH = [] 
DATA_POINTER = 0
DATA_LENGTH = 1024
BLOCK_LENGTH = 1024
LENTGH_NUMBER = 12 #в одном байте 2 символа, тут 6 байт

def get_random_latlon(lat, lon, r, rand):
    """
    Принимает координаты, радиус и 3 случайных значения для генерации
    Возвращает случайные координаты в окружности с заданным радиусом, и соответствующую точку в декартовых координатах
    """
    #сгенерируем случайную точку в полярных координатах в окружности с заданным радиусом
    #http://qaru.site/questions/41617/generate-a-random-point-within-a-circle-uniformly
    
    dr, phi, x, y = get_random_point(rand)
    d = dr * r # радиус
    n_lat, n_lon = get_latlon(lat, lon, d, phi) #вычислим точку
    
    return n_lat, n_lon, x, y

def get_random_point(rand):
    """
    Принимает 3 случайных значения для генерации точки
    Возвращает точку в полярных и декартовых координатах
    """
    u = rand[0] + rand[1]
    r = 2-u if u>1 else u
    phi = rand[2] * 2 * pi
    x = r * cos(- phi + pi/2) #точка в декартовых координатах
    y = r * sin(- phi + pi/2) #с преобразованиями азимута
    return r, phi, x, y

def get_latlon(lat, lon, d, phi):
    """
    Принимает координаты и точку в полярных координатах
    Возвращает координаты с заданным смещением
    """
    #рассчитаем координаты новой точки 
    #https://dxdy.ru/topic30224.html
    g_lat = lat * pi/180 #в радианы
    g_lon = lon * pi/180 #в радианы

    global R_EARTH
    l = d/R_EARTH #угловое расстояние
    n_lat = asin(sin(g_lat)*cos(l)+cos(g_lat)*sin(l)*cos(phi)) 
    n_lon = lon + asin(sin(phi)*sin(l)/cos(n_lat)) * 180/pi #в градусы
    n_lat *= 180/pi #в градусы
    return n_lat, n_lon

def cart2pol(x, y):
    """
    Переводит декартовы координы в полярные с учётом азимута
    """
    rho = sqrt(x**2 + y**2)
    phi = atan2(y,x)
    phi = - phi + pi/2
    return(rho, phi)

def get_google_latlon(lat, lon):
    """
    Принимает координаты
    Возвращает координату на картах google
    """
    return "https://www.google.com/maps/search/?api=1&query="+str(lat) + "," + str(lon)

def get_pseudorandom():
    """
    Возвращает три псевдослучайных значения
    """
    return [random.random() for i in range(3)]

def set_new_datacash():
    """
    Устанавливает новый кэш значений КГСЧ, зависит от количества заданных точек
    """
    global DATACASH
    sum = POINTS * (LENTGH_NUMBER // 2) * 3 #длина байта 2 символа
    length = (sum // BLOCK_LENGTH) + 1
    if length < DATA_LENGTH:
        try:
            response = requests.get("https://qrng.anu.edu.au/API/jsonI.php?length=" + str(length)
                + "&type=hex16&size=" + str(BLOCK_LENGTH))
            jsondata = response.json()
            DATACASH = "".join(jsondata['data'])
            print("Кэш КГСЧ успешно обновлён")
        except:
            print("Ошибка запроса к КГСЧ для создания кэша")
    else:
        print("Слишком много точек")

def get_quantumrandom():
    """
    Возвращает три квантово случайных значения из кэша
    """
    #float - число двойной точности, мантисса состоит из 52 бит = 6.5 байт, пренебрежём половиной байта
    ret = [0,0,0]
    global DATA_POINTER
    for i in range(3):
        bp = DATA_POINTER
        try:
            ret[i] = float.fromhex("0x0." + DATACASH[bp:bp+LENTGH_NUMBER-1] + "p+0") #формирование числа из строки с hex16
        except:
            print("Ошибка доступа к кэшу КГСЧ")
            exit()
        DATA_POINTER += LENTGH_NUMBER 
        if DATA_POINTER > len(DATACASH) - LENTGH_NUMBER: #проверка на выход за пределы кэша
            DATA_POINTER -= LENTGH_NUMBER
            print("Ошибка чтения кэша значений КГСЧ")
            return (0,0,0)
    return ret

def set_number_points(points):
    """
    Устанавливает количество точек для запроса к квантовому генератору случайных чисел
    """
    global POINTS
    POINTS = points

def get_mean(points):
    """
    Возвращает среднее арифметическое точек
    """
    p = list(zip(*points))
    return (sum(p[0]) / len(p[0]), sum(p[1]) / len(p[1]))
    
def clip_points(points, center, radius):
    """
    Отсекает точки вне заданной окружности
    """
    ret = []
    for p in points:
        if (p[0]-center[0])**2 + (p[1]-center[1])**2 < radius ** 2:
            ret.append(p)
    return ret
