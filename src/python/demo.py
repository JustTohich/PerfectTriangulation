from tkinter import *
import triangulate
import triangulate2

points = []


def left_mouse(event, canvas):
    canvas.create_oval([event.x - 2, event.y - 2, event.x + 2, event.y + 2], fill="black")
    points.append([event.x, -event.y])
    triangulate2.triangulate(points)


def main():
    root = Tk()
    window_width = 500
    window_height = 500
    root.minsize(width=window_width, height=window_height)
    root.maxsize(width=window_width, height=window_height)
    canvas = Canvas(master=root, width=window_width, height=window_height)
    canvas.pack()
    root.bind('<Button-1>', lambda e: left_mouse(e, canvas))
    root.mainloop()


if __name__ == '__main__':
    main()
