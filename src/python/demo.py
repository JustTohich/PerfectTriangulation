from draw import Drawer
from tkinter import *
from collections import deque
import copy


class Integer:
    def __init__(self, val):
        self.val = val


def left_mouse(event, drawer, p_b):
    p_b[0].val = int(event.x / drawer.scale)
    p_b[1].val = int(event.y / drawer.scale)


def right_mouse(event, drawer, p_b, points, drawing: Integer):
    drawing.val = 1
    x = int(event.x / drawer.scale)
    y = int(event.y / drawer.scale)
    points.extend(drawer.draw_line(p_b[0].val, p_b[1].val, x, y))
    p_b[0].val = x
    p_b[1].val = y


def right_mouse_release(drawer, stack, points, drawing: Integer):
    stack.append(copy.copy(points))
    points.clear()
    drawing.val = 0


def main():
    root = Tk()
    window_width = 100
    window_height = 100
    root.minsize(width=window_width, height=window_height)
    root.maxsize(width=window_width, height=window_height)
    canvas = Canvas(master=root, width=window_width, height=window_height)
    canvas.pack()
    drawer = Drawer(canvas)

    stack = deque()
    points = list()
    drawing = Integer(0)

    p_b = (Integer(0), Integer(0))
    root.bind('<Button-1>', lambda e: left_mouse(e, drawer, p_b))
    root.bind('<Button-3>', lambda e: right_mouse(e, drawer, p_b, points, drawing))
    root.bind('<B3-Motion>', lambda e: right_mouse(e, drawer, p_b, points, drawing))
    root.bind('<ButtonRelease-3>', lambda e: right_mouse_release(drawer, stack, points, drawing))
    root.mainloop()


if __name__ == '__main__':
    main()