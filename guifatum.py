# -*- coding: utf8 -*-
"""
EvgenZhaba

GUI v4 для модуля fatum

Реализует:

      Обращения к модулю fatum, использование генераторов псевдослучайных и квантово случайных чисел.
      Загрузку данных из конфига, создаётся при первом запуске.
      Загрузку изображения как карты.
      Сохранение полученных координат как изображения в файл result.png
      ЛКМ - получение координаты в GUI по клику на нужную точку и запись её в текстовый файл result.txt как ссылку на гугл карты.
      ПКМ - проведение одной итерации сужения радиуса.
      СКМ - проведение всех итераций сужения радиуса.
      Полученные координаты и нажатия ЛКМ также сохраняются в файл-изображение result.png.

При первом запуске программа создаёт стандартный конфиг, и делает вычисления по нему.
Впоследствии исходные данные в конфиге можно изменить.
Также, если в папке есть изображение "input.png", то программа загружает его в качестве фона. Например, можно загрузить карту любимой игры, и сгенерировать точки для неё.

      Алгоритм поиска аттракторов и репеллеров.
      
      Текущий радиус начинается с максимального, затем сужается до минимального.
      Каждый этап перебираются все точки, которые могут быть центром круга с текущим радиусом, не выходящего за пределы основного круга.
      Относительно каждой точки строится круг, считается количество точек в нём и сумма расстояний до них.
      Затем эти точки сортируются: сперва по количеству точек, затем по сумме расстояний.
      Та точка, что имеет всех больше соседей, лежащих наиболее близко - аттрактор.
      Та точка, что имеет меньше всех соседей, и которые лежат наиболее далеко - репеллер.
"""


from fatum import *
from tkinter import Tk, Canvas, NW
from PIL import Image, ImageTk, ImageDraw
import configparser
import os
import time
import math

WX = 512
WY = 512
LAT, LONG, RADIUS, GENER, POINTS, MAX_RADIUS, MIN_RADIUS, A_RADIUS  = [None for i in range(8)]
ATTRACTOR, REPELLER = [None for i in range(2)]
POINTS_LIST = []

def create_config(path):
    """
    Создаёт конфиг
    """
    config = configparser.ConfigParser(allow_no_value=True)
    config.add_section("Settings")
    config.set("Settings", "#широта")
    config.set("Settings", "lat", "55.753215")
    config.set("Settings", "#долгота")
    config.set("Settings", "long", "37.622504")
    config.set("Settings", "#радиус в метрах")
    config.set("Settings", "radius", "1000")
    config.set("Settings", "#какой генератор использовать: pseudo - обычный рандом, quantum - квантовый")
    config.set("Settings", "gener", "pseudo")
    config.set("Settings", "#количество точек для генерации(не больше ~29000)")
    config.set("Settings", "points", "1000")
    config.set("Settings", "#максимальный радиус вокруг точки, в котором будет искаться скопление, в метрах, не больше radius")
    config.set("Settings", "max_raduis", "200")
    config.set("Settings", "#минимальный радиус вокруг точки, в котором будет искаться скопление, в метрах, не больше max_raduis")
    config.set("Settings", "min_raduis", "5")
    config.set("Settings", "#количество шагов, более 0")
    config.set("Settings", "number_steps", "50")
    
    with open(path, "w") as config_file:
        config.write(config_file)

def get_settings():
    """
    Задаёт значения из конфига, если он есть, иначе создаёт конфиг по умолчанию
    """
    path = "config.ini"
    if not os.path.exists(path):
        create_config(path)

    config = configparser.ConfigParser()
    config.read(path)
    
    global LAT, LONG, RADIUS, GENER, POINTS, MAX_RADIUS, MIN_RADIUS, A_RADIUS
    try:
        LAT = config.getfloat("Settings", "lat")
        LONG = config.getfloat("Settings", "long")
        RADIUS = config.getfloat("Settings", "radius")
        GENER = config.get("Settings", "gener")
        POINTS = config.getint("Settings", "points")
        MAX_RADIUS = config.getfloat("Settings", "max_raduis") / RADIUS
        MIN_RADIUS = config.getfloat("Settings", "min_raduis") / RADIUS
        steps = config.getfloat("Settings", "number_steps")
        A_RADIUS = (MAX_RADIUS - MIN_RADIUS) / steps # относительное значение искомого радиуса
    except:
        print("Конфиг испорчен")
        exit()

def write_result(x, y, msg=""):
    """
    Дозаписывает в файл результатов ссылки на вычисленные координаты
    """
    with open("result.txt", "a") as f:
        answer = get_google_latlon(x, y)
        f.write(time.ctime() + " " + msg + "\n")
        f.write(answer + "\n"+ "\n")
        f.close()

def leftclick(event, canvas):
    """
    При ЛКМ на форме программы происходит вычисление координаты в указанной точке и запись её в файл
    """
    global LAT, LONG, RADIUS
    x = (event.x - WX/2) / (WX/2)
    y = -(event.y - WY/2) / (WY/2)
    d, phi = cart2pol(x, y)
    dr = d * RADIUS
    latlon = get_latlon(LAT, LONG, dr, phi) #вычислить новую координату по заданному смещению
    print(latlon)
    write_result(*latlon, msg="click")

    x = WX/2 + round(x * WX / 2)
    y = WY/2 - round(y * WY / 2)
    
    draw.ellipse((x-10,y-10,x+10,y+10), outline="blue")
    draw.point([x-1, y-1], (0,0,255))
    draw.point([x-1, y+1], (0,0,255))
    draw.point([x, y], (0,0,255))
    draw.point([x+1, y-1], (0,0,255))
    draw.point([x+1, y+1], (0,0,255))
    
    global im
    image.save("result.png")
    im = ImageTk.PhotoImage(file="result.png")
    canvas.itemconfig('canv', image=im)

def get_len_xy(xy1, xy2):
    x = abs(xy1[0]-xy2[0])
    y = abs(xy1[1]-xy2[1])
    return math.sqrt(x*x + y*y)

def findfatum():
    """
    Поиск аттрактора и репеллера
    """
    global POINTS_LIST, ATTRACTOR, REPELLER, MAX_RADIUS
    T_PL = []
    for i in range(len(POINTS_LIST)):
        len_xy = 0
        t_sum_points = 0
        m_len_xy = get_len_xy(POINTS_LIST[i], [0,0]) # расстояние от центра
        if m_len_xy < 1 - MAX_RADIUS: # ищем только внутри окружности так, чтобы найденный круг не вылезал за его пределы
            for j in range(len(POINTS_LIST)):
                t_len_xy = get_len_xy(POINTS_LIST[i], POINTS_LIST[j]) # расстояние от точки до точки
                if t_len_xy < MAX_RADIUS:
                    len_xy -= t_len_xy
                    t_sum_points += 1
            T_PL.append(POINTS_LIST[i]+[t_sum_points, len_xy])
    T_PL.sort(key = lambda i: (i[2], i[3]))
    if len(T_PL) > 1:
        ATTRACTOR = T_PL[-1]
        REPELLER = T_PL[0]
    else:
        ATTRACTOR = REPELLER = None

def rightclick(event, canvas):
    """
    Вывод аттрактора и репеллера(однократный)
    """
    global ATTRACTOR, REPELLER, A_RADIUS, MAX_RADIUS, MIN_RADIUS
    
    if MAX_RADIUS > MIN_RADIUS:
        findfatum()
        A = ATTRACTOR
        RL = REPELLER
        msg = "Текущий радиус: " + str(round(MAX_RADIUS * RADIUS, 2))
        if (A == None) or (RL == None):
            msg += " Аттрактор и репеллер вычислить не удалось: малая длина радиуса"
        else:
            R = MAX_RADIUS
            canvas.create_oval(WX/2+(A[0]-R)*WX/2, WY/2-(A[1]-R)*WY/2, 
                    WX/2+(A[0]+R)*WX/2, WX/2-(A[1]+R)*WY/2, outline="green")
            canvas.create_oval(WX/2+(RL[0]-R)*WX/2, WY/2-(RL[1]-R)*WY/2, 
                    WX/2+(RL[0]+R)*WX/2, WX/2-(RL[1]+R)*WY/2, outline="red")

        print(msg)   
        MAX_RADIUS -= A_RADIUS

def centerclick(event, canvas):
    """
    Вывод аттрактора и репеллера(всех)
    """
    global MAX_RADIUS, MIN_RADIUS
    while MAX_RADIUS > MIN_RADIUS:
        rightclick(event, canvas)
    
def calculate(canvas):
    """
    Вычисления с использованием модуля fatum
    """
    global LAT, LONG, RADIUS, GENER, POINTS
    
    get_settings() #получение исходных данных
    if GENER == "quantum":
        set_number_points(POINTS) #установка количества точек
        set_new_datacash() #получение нового кэша квантово случайных чисел
  
    global draw  
    for i in range(POINTS):
        if GENER == "pseudo":
            rand = get_pseudorandom() #получить псевдослучайные числа
        elif GENER == "quantum":
            rand = get_quantumrandom() #получить квантово случайные числа
        else:
            print("Выбран неверный генератор")
            exit()
        
        xy = get_random_latlon(LAT, LONG, RADIUS, rand) #получить новые координаты на основе заданных случайных чисел
        POINTS_LIST.append([xy[2], xy[3]])
        
        x = WX/2 + round(xy[2] * WX / 2)
        y = WY/2 - round(xy[3] * WY / 2)
        
        draw.point([x, y-1], (0,0,0))
        draw.point([x, y+1], (0,0,0))
        draw.point([x-1, y], (0,0,0))
        draw.point([x+1, y], (0,0,0))
        
    image.save("result.png")

    
if __name__ == "__main__":
    """
    Выполняется при запуске модуля, отрисовка GUI
    """
    
    try:
        image = Image.open("input.png")
        (WX, WY) = image.size
    except:
        image = Image.new("RGB", (WX,WY), (255,255,255))
    draw = ImageDraw.Draw(image)   
    
    root = Tk()
    root.minsize(WX, WY)
    root.resizable(width=False, height=False)

    canvas = Canvas(root, width=WX, height=WY, bg="white")
    canvas.pack()
        
    root.bind("<Button-1>", lambda event,c=canvas: leftclick(event, c))
    root.bind("<Button-2>", lambda event,c=canvas: centerclick(event, c))
    root.bind("<Button-3>", lambda event,c=canvas: rightclick(event, c))
   
    calculate(canvas)
   
    im = ImageTk.PhotoImage(file="result.png")
    canvas.create_image(0, 0, anchor=NW, image=im, tag="canv")
    
    root.mainloop()
