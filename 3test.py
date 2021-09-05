# Программа Python для иллюстрации
# соответствие шаблона

import cv2
import sys
import numpy as np
from imutils.video import VideoStream
import imutils
from time import sleep

#Проверка, что аргумент (шаблон) был передан
if len(sys.argv) < 2:
    print("have no argument!    (png, jpg, ...)")
    exit()

# Читать основное изображение
#img_rgb = cv2.imread('mainimage.jpg').
vs = VideoStream(src=0, usePiCamera=False, resolution=(1024, 720), framerate=32).start()
sleep(2)
img_rgb = None
# список для усредненых точек найденных шаблонов на картинке(чтобы не было наслоения найденного одного и того же изображения)
# чтобы можно было проверять на уникальность
average_points = []
# аналогично, только хранятся расстояния average_sizes[0] соответвует average_pionts[0] | [1] == [1] | ...
average_sizes = []
#костанта, зачащая допустимую разницу размера, при котором не будет записываться новое значение
# Пример: (точка 100, 100 не будет записыаться, если имеются точки: (100-DIFFERENCE, 100), (100, 100-DIFFERENCE), (100-DIFFERENCE, 100-DIFFERENCE), (100+DIFFERENCE, 100), ...) 
DIFFERENCE = 20
#минимальный процент от размера шаблона
MIN = 20
#максимальный процент от размера шаблона (максимум - 100)
MAX = 100
#модуль разницы размеров шаблона
MODULE = 5
# Ядро свертки для размытия изображение (должно быть нечетным)
BLUR_CORE_CONVULTION = (3, 3)
#Имя файла для результатов
FILE = "result.txt"
# порог вхождения сопадений
TRESHOLD = 0.8
# Прочитайте шаблон
template__ = cv2.imread(sys.argv[1] , 0)

#Поиск среднего значения из найденных точек изображений шаблона (при одинаковом размере шаблона), чтобы получить точно 1 значение
def findAverage(array):
    x = 0
    x_sum = 0
    y = 0
    y_sum = 0
    
    for p in array:
        x_sum += p[0]
        y_sum += p[1]

    return ((int)(x_sum/len(array)), (int)(y_sum/len(array)))

#проверка на то, что точка еще в пределах 1го найденного изображения (из многих)
def checkPixel(minPoint, point):
    
    if point[0] > (minPoint[0] + DIFFERENCE):
        return False
    if point[1] > (minPoint[1] + DIFFERENCE):
        return False
    return True

#добавление точки в список найденных значений, если оно не в пределах другого изображения
def addAveragePoint(points, minDif, w, h):
    #Нахоим среднее из положений одного и того же изображения
    point = findAverage(points)
    for pt in average_points:
        if point[0] <= pt[0] + minDif and point[0] >= pt[0]:
            return
        if point[0] >= pt[0] - minDif and point[0] <= pt[0]:
            return
        if point[1] <= pt[1] + minDif and point[1] >= pt[1]:
            return
        if point[1] >= pt[1] - minDif and point[1] <= pt[1]:
            return
    #если прошла проверка, то добавляем элемент (полагая, что это новый)
    average_points.append(point)
    average_sizes.append((w,h))

#очистка списка (нужна, пока используется запись камеры а не фото)
def clearAverageLists():
    average_sizes.clear()
    average_points.clear()

def writeToFILE(data):
    #запись результатов в файл
    file = open(FILE, "w")
    # print(getDataForFILE())
    file.write(data)
    file.close()

#вырисовывание рамки объекта и ее положения 
def print_result():
    i = 0
    while i < len(average_sizes):
        #рисовка рамки
        cv2.rectangle(img_rgb, average_points[i], (average_points[i][0] + average_sizes[i][0], average_points[i][1] + average_sizes[i][1]), (0,255,255), 2, 8, 0)
        #рисовка координат
        cv2.putText(img_rgb, str(average_points[i][0]) + ", " + str(average_points[i][1]), (average_points[i][0],average_points[i][1]), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0,255,255), 2)
        # print(str(average_points[i]))
        i += 1

def getDataForFILE():
    i = 0
    string = ""
    while i < len(average_sizes):
        string += str(average_points[i]) + ", " + str(average_sizes[i][0]) + ", " + str(average_sizes[i][1]) + "\n"
        i += 1
    return string

# def rotation(template):
#     for deg in range(0, 360):
#         if deg % 5 == 0:
#             (h, w) = template.shape[:2]
#             center = (int(w / 2), int(h / 2))
#             rotation_matrix = cv2.getRotationMatrix2D(center, deg, 1)
#             route_img = cv2.warpAffine(template, rotation_matrix, (w, h))
#             if getContourse(route_img) == True:
#                 return True
#     return False

#основная функция (вызывает другие), тут проходит уменщение шаблона и поиск шаблона на изображении
def findingWithResize(MinPercent, maxPercent, module):
    if ((MinPercent < 0 or MinPercent > 100) or (maxPercent > 100 or maxPercent < 0) or (maxPercent < MinPercent)):
        print("Wrong MIN, MAX sizes")
        exit()
    for size in range(MinPercent, maxPercent):
        #Ищем, только если шаблон увеличится на module процентов
        if size%module == 0:
            #нахождение ширины и высоты
            width = int(template__.shape[1] * size / 100)
            height = int(template__.shape[0] * size / 100)
            dsize = (width, height)
            # if rotation(cv2.resize(template__, dsize)) == True:
            #     return True

            if getContourse(cv2.resize(template__, dsize)) == True:
                return True
    return False
#Поиск шаблона
def getContourse(template):
  
    # Сохраняем ширину и высоту шаблона
    w, h = template.shape[::-1]
  
    # Выполнять операции сопоставления.
    res = cv2.matchTemplate(img_gray,template,cv2.TM_CCOEFF_NORMED)
  
    # Сохранять координаты совпадающей области в массиве
    #координаты упорядочены по x, y (запись проходит вдоль икса)
    loc = np.where( res >= TRESHOLD) 
    # флаг о том, что надо прекращать (для отладки)
    flag = False

    #инициализация флага о входе в цикл
    flag_about_in = False
    #инициализация списка для одного изображения
    points = []
    #инициализация минимума точки, при которой мы будем проверять, полагая, что это одно изображение
    minimum = (999999, 99999)

    for pt in zip(*loc[::-1]):
        
        if minimum[0] > pt[0]:
            if minimum[1] > pt[1]:
                minimum = pt
        #если точка является тем же изображением, то добавляем ее в список для дальнейшего поиска среднего значения
        if checkPixel(minimum, pt) == True:
            points.append(pt)
        #в ином случае, это другое изображение
        else:
            #добавляем старое в массив изображений
            addAveragePoint(points, DIFFERENCE, w, h)
            #чистим список, для дальнейшей записи точек нового изображения
            points.clear()
            #устанавливаем точку как минимум для нового изобраения
            minimum = pt
            #добавляем ее в список для дальнейшего поиска среднего значения
            points.append(pt)
        flag_about_in = True
        
        # flag = True
    
    if flag_about_in == True:    
        addAveragePoint(points, DIFFERENCE, w, h)
    return flag

stop_flag = False
i = 0
while True:
# while i != 1:
    i = 1
    #сделать снимок экрана
    img_rgb = vs.read()
    #добавление размытости
    img_rgb = cv2.GaussianBlur(img_rgb, BLUR_CORE_CONVULTION , 0)
    #преобразовать изображение в оттенки серого
    img_gray = cv2.cvtColor(img_rgb, cv2.COLOR_BGR2GRAY)
    #условие для отладки
    if stop_flag == False:
        #поиск всех совпадений для изображения
        stop_flag = findingWithResize(MIN, MAX, MODULE)
        #нарисовка рамок и координат
        print_result()
        #Запись в файл
        writeToFILE(getDataForFILE())
        #отчиска списка (для отладки)
        clearAverageLists()
        #ОТОБРАЗИТЬ ИЗОБРАЖЕНИЕ
        cv2.imshow('krasivoe',img_rgb)
    #чтобы закрыть окно
    if cv2.waitKey(1) == 27:
        break
# while True:
#     cv2.imshow('krasivoe',img_rgb)
#     if cv2.waitKey(1) == 27:
#         break

vs.stop()
cv2.destroyAllWindows()