from tkinter import Canvas
from PIL import Image
import io


class Drawer:

    def __init__(self, scale, canvas: Canvas):
        self.scale = scale
        self.canvas = canvas

    def draw_grid(self):
        y_start = 0
        y_end = int(self.canvas['height'])
        x_start = 0
        x_end = int(self.canvas['width'])
        for x in range(self.scale, x_end, self.scale):
            line = ((x, y_start), (x, y_end))
            self.canvas.create_line(line, fill='grey')
        for y in range(self.scale, y_end, self.scale):
            line = ((x_start, y), (x_end, y))
            self.canvas.create_line(line, fill='grey')

    def set_pixel(self, x: int, y: int):
        if(self.scale == 1):
            return self.canvas.create_line(x, y, x + 1, y)
        x1 = x * self.scale
        x2 = x1 + self.scale
        y1 = y * self.scale
        y2 = y1 + self.scale
        return self.canvas.create_rectangle([(x1, y1), (x2, y2)], fill='black')

    def save_image(self, path: str):
        ps = self.canvas.postscript(colormode ='color')
        img = Image.open(io.BytesIO(ps.encode('utf-8')))
        img.save(path)

    def draw_line(self, x1: int, y1: int, x2: int, y2: int):
        set_pixels = []
        dx = x2 - x1
        dy = y2 - y1

        sign_x = 1 if dx > 0 else -1 if dx < 0 else 0
        sign_y = 1 if dy > 0 else -1 if dy < 0 else 0

        if dx < 0:
            dx = -dx
        if dy < 0:
            dy = -dy

        if dx > dy:
            pdx, pdy = sign_x, 0
            es, el = dy, dx
        else:
            pdx, pdy = 0, sign_y
            es, el = dx, dy

        x, y = x1, y1

        error, t = el / 2, 0

        set_pixels.append(self.set_pixel(x, y))

        while t < el:
            error -= es
            if error < 0:
                error += el
                x += sign_x
                y += sign_y
            else:
                x += pdx
                y += pdy
            t += 1
            set_pixels.append(self.set_pixel(x, y))
        return set_pixels

    def draw_circle(self, x1: int, y1: int, r: int):
        set_pixels = []
        x = 0
        y = r
        d = 3 - 2 * y
        while x <= y:
            set_pixels.append(self.set_pixel(x1 + x, y1 + y))
            set_pixels.append(self.set_pixel(x1 + x, y1 - y))
            set_pixels.append(self.set_pixel(x1 - x, y1 - y))
            set_pixels.append(self.set_pixel(x1 - x, y1 + y))
            set_pixels.append(self.set_pixel(x1 + y, y1 + x))
            set_pixels.append(self.set_pixel(x1 + y, y1 - x))
            set_pixels.append(self.set_pixel(x1 - y, y1 + x))
            set_pixels.append(self.set_pixel(x1 - y, y1 - x))
            if d < 0:
                d = d + 4 * x + 6
            else:
                d = d + 4 * (x - y) + 10
                y = y - 1
            x = x + 1
        return set_pixels
