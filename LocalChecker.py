import threading
import tkinter
from PIL import Image, ImageTk
from time import sleep
import pyscreenshot
import cv2
import pygame

pygame.mixer.init()


class App:
    def __init__(self):
        self.root = tkinter.Tk()
        self.root.geometry('250x150+400+200')
        self.root.resizable(False, False)
        self.root.title('Check local')
        self.root.iconbitmap(default='img/neutral.ico')

        self.but_start = tkinter.Button(text='Start', command=self.check_local_start)
        self.but_start.pack(fill='x', padx=10, pady=8)

        self.but_stop = tkinter.Button(text='Stop', command=self.check_local_stop)
        self.but_stop.pack(fill='x', padx=10)
        self.but_stop['state'] = 'disabled'

        image = Image.open('img/crab.png')
        image = image.resize((100, 80), Image.LANCZOS)
        image = ImageTk.PhotoImage(image)

        self.label = tkinter.Label(image=image)
        self.label.pack()

        self.stopped = True

        self.root.mainloop()

    def check_local_start(self):
        if self.stopped:
            th = threading.Thread(target=self.check_local_thread, daemon=True)
            self.stopped = False
            th.start()
            self.but_start['state'] = 'disabled'
            self.but_stop['state'] = 'normal'

    def check_local_stop(self):
        if not self.stopped:
            self.stopped = True
            self.but_start['state'] = 'normal'
            self.but_stop['state'] = 'disabled'

    def check_local_thread(self):
        while True:
            if self.stopped:
                break
            cords = find_local_chat()
            if not cords:
                continue
            found_coordinates = check_local(cords)

            if len(found_coordinates) != 0:
                play_alarm()


def find_local_chat():
    x1, y1, x2, y2 = 0, 0, 0, 0

    img_full_screen = pyscreenshot.grab()
    img_full_screen.save('img/full_screen.png')
    img_full_screen = cv2.imread('img/full_screen.png')
    img_full_screen_gray = cv2.cvtColor(img_full_screen, cv2.COLOR_BGR2GRAY)
    data = Image.fromarray(img_full_screen_gray)
    data.save('321.png')
    threshold = 0.95

    img_left_top = cv2.imread('img/left_top.png', cv2.IMREAD_GRAYSCALE)
    data = Image.fromarray(img_left_top)
    data.save('123.png')
    centroids = find_fragments(img_full_screen_gray, img_left_top, threshold)
    for char in centroids[1:, :]:
        x1 = char[0]
        y1 = char[1]

    img_right_top = cv2.imread('img/right_top.png', cv2.IMREAD_GRAYSCALE)
    centroids = find_fragments(img_full_screen_gray, img_right_top, threshold)
    _, b = img_right_top.shape
    for char in centroids[1:, :]:
        if char[0] < x1 or char[1] < y1:
            continue
        if char[1] != y1:
            continue
        x2 = char[0] + b
        break

    img_right_bot = cv2.imread('img/right_bot.png', cv2.IMREAD_GRAYSCALE)
    centroids = find_fragments(img_full_screen_gray, img_right_bot, threshold)
    a, b = img_right_bot.shape
    for char in centroids[1:, :]:
        if char[1] < y1:
            continue
        if char[0] + b != x2:
            continue
        y2 = char[1] + a
        break

    if x1 == 0 or y1 == 0 or x2 == 0 or y2 == 0:
        return False
    return int(x1), int(y1), int(x2), int(y2)


def check_local(cords):
    x1, y1, x2, y2 = cords
    img_full_screen = cv2.imread('img/full_screen.png')
    img_full_screen_gray = cv2.cvtColor(img_full_screen, cv2.COLOR_BGR2GRAY)

    threshold = 0.95
    img_neutral = cv2.imread('img/neutral.png', cv2.IMREAD_GRAYSCALE)
    img_minus = cv2.imread('img/minus.png', cv2.IMREAD_GRAYSCALE)
    images_for_check = [img_neutral, img_minus]
    found_coordinates = []
    for image in images_for_check:
        centroids = find_fragments(img_full_screen_gray, image, threshold)
        for char in centroids[1:, :]:
            if x1 < char[0] < x2 and y1 < char[1] < y2:
                found_coordinates.append((char[0], char[1]))
    return found_coordinates


def play_alarm():
    pygame.mixer.music.load('songs/alarm.mp3')
    pygame.mixer.music.play()
    sleep(1.5)
    pygame.mixer.music.stop()


def find_fragments(image, fragment, threshold):
    res = cv2.matchTemplate(image, fragment, cv2.TM_CCOEFF_NORMED)
    res = cv2.convertScaleAbs(res, alpha=255)
    bw = cv2.threshold(res, threshold * 255, 255, cv2.THRESH_BINARY)[1]
    _, _, _, centroids = cv2.connectedComponentsWithStats(bw)
    return centroids


if __name__ == '__main__':
    app = App()
