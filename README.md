# fatum
Поиск аттракторов и репеллеров случайно сгенерированных географических точек.

Используется Python 3.3 и выше, поскольку в этой версии добавили venv.

В папке со скриптом выполнить следующие команды:
1. Сперва создадим виртуальное окружение:
```
python -m venv fatum
```
Будет создана папка fatum в текущей папке.

2. Активируем виртуальное окружение

Для Windows:
```
fatum\Scripts\activate
```
Для linux:
```
source fatum/bin/activate
```
После включения в командной строке будет метка, что сейчас находимся в виртуальном окружении: в начале строки будет (fatum).

3. Устанавливаем зависимости:
```
pip install requests pillow
```

4. Запускаем скрипт:
```
python guifatum.py
```
После работы скрипта создастся файл конфига. В нём можно сделать правки и запустить скрипт ещё раз, пока не будет получен требуемый результат.

5. После работы со скриптом выключаем виртуальное окружение.
Для Windows.
```
fatum\Scripts\deactivate
```
Для linux:
```
deactivate
```

В ходе использования скрипта генерируются случайные точки, затем программа пытается определить аттракторы и репеллеры. Право выбора точек оставлено за пользователем. Справка из файла guifatum.py:

GUI v3 для модуля fatum
```
Реализует:

      Обращения к модулю fatum, использование генераторов псевдослучайных и квантово случайных чисел.
      Загрузку данных из конфига, создаётся при первом запуске.
      Сохранение полученных координат как изображения в файл result.png
      ЛКМ - получение координаты в GUI по клику на нужную точку и запись её в текстовый файл как ссылку на гугл карты.
      ПКМ - проведение одной итерации сужения радиуса.
      СКМ - проведение всех итераций сужения радиуса.
      Полученные координаты и нажатия ЛКМ также сохраняются в файл-изображение.

При первом запуске программа создаёт стандартный конфиг, и делает вычисления по нему.
Впоследствии исходные данные в конфиге можно изменить.

      Алгоритм поиска аттракторов и репеллеров.
      Текущий радиус начинается с максимального, затем сужается до минимального.
      Каждый этап перебираются все точки, которые могут быть центром круга с текущим радиусом, не выходящего за пределы основного круга.
      Относительно каждой точки строится круг, считается количество точек в нём и сумма расстояний до них.
      Затем эти точки сортируются: сперва по количеству точек, затем по сумме расстояний.
      Та точка, что имеет всех больше соседей, лежащих наиболее близко - аттрактор.
      Та точка, что имеет меньше всех соседей, и которые лежат наиболее далеко - репеллер.
 ```
