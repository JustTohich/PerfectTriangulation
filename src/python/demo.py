from tkinter import *
# from triangulate import triangulate
# from triangulate2 import triangulate
from triangle_mesh import triangulate

points = []


def left_mouse(event, canvas):
    canvas.create_oval([event.x - 1, event.y - 1, event.x + 1, event.y + 1], fill="black")
    points.append([event.x, -event.y])
    triangulate(points)


def main():
    root = Tk()
    window_width = 1920
    window_height = 1080
    root.minsize(width=window_width, height=window_height)
    canvas = Canvas(master=root, width=window_width, height=window_height)
    canvas.pack()
    root.bind('<Button-1>', lambda e: left_mouse(e, canvas))
    root.mainloop()


if __name__ == '__main__':
    main()
