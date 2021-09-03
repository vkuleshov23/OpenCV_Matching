# Программа Python для иллюстрации
# соответствие шаблона

import cv2

import numpy as np
from imutils.video import VideoStream
import imutils
from time import sleep
# Читать основное изображение
#img_rgb = cv2.imread('mainimage.jpg').
vs = VideoStream(src=0, usePiCamera=False, resolution=(1024, 720), framerate=32).start()
sleep(2)

# Прочитайте шаблон
template__ = cv2.imread('white1.png',0)

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

def resize(MinPercent):
    for size in range(MinPercent, 100):
        width = int(template__.shape[1] * size / 100)
        height = int(template__.shape[0] * size / 100)
        dsize = (width, height)
        # if rotation(cv2.resize(template__, dsize)) == True:
        #     return True
        if getContourse(cv2.resize(template__, dsize)) == True:
            return True
    return False
  
def getContourse(template):

    # Преобразовать его в оттенки серого
    img_gray = cv2.cvtColor(img_rgb, cv2.COLOR_BGR2GRAY)
  
    # Сохраняем ширину и высоту шаблона в ш и ч
    w, h = template.shape[::-1]
  
    # Выполнять операции сопоставления.
    res = cv2.matchTemplate(img_gray,template,cv2.TM_CCOEFF_NORMED)
  
    # Укажите порог
    threshold = 0.8
  
    # Сохранять координаты совпадающей области в массиве
    loc = np.where( res >= threshold) 
    flag = False
    # Нарисуйте прямоугольник вокруг соответствующей области.
    for pt in zip(*loc[::-1]):
        flag = True
        cv2.rectangle(img_rgb, pt, (pt[0] + w, pt[1] + h), (0,255,255), 2, 8, 0)
    return flag

while True:
    img_rgb = vs.read()
    img_rgb = cv2.GaussianBlur(img_rgb, (3, 3), 0)
    resize(25)
    # Показать окончательное изображение с соответствующей области.
    cv2.imshow('krasivoe',img_rgb)
    if cv2.waitKey(1) == 27:
        break
vs.stop()
cv2.destroyAllWindows()