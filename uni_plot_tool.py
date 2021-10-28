import numpy as np
import cv2
from PIL import Image, ImageDraw, ImageFont
from matplotlib import pyplot as plt
from matplotlib.backends.backend_agg import FigureCanvasAgg
from matplotlib.ticker import MaxNLocator


def quick_show(img: np.array):
    cv2.imshow('', img)
    cv2.waitKey(0)


def add_alpha(img: np.array) -> np.array:
    img_b, img_g, img_r = cv2.split(img)
    img_a = np.ones(img_b.shape, dtype=img_b.dtype) * 255
    return cv2.merge((img_b, img_g, img_r, img_a))


def length_uni(font: ImageFont.truetype, text: str, length: int) -> str:
    new_text = ''
    for char in text:
        if font.getsize(new_text)[0] >= length:
            return new_text
        new_text += char
    return new_text


def simple_plot(bg: np.array, img: np.array, pos: list, relative: tuple = (0, 0)):
    # pos and relative should be like (y, x)
    y_img, x_img, chn = img.shape
    y_max, x_max, chn = bg.shape
    y_pos, x_pos = pos[0] + relative[0], pos[1] + relative[1]
    y_des, x_dex = y_pos + y_img, x_pos + x_img
    if y_max <= y_pos or x_max <= x_pos:
        return
    if y_max < y_des:
        y_des, y_img = y_max, y_max - y_pos
    if x_max < x_dex:
        x_dex, x_img = x_max, x_max - x_pos
    bg[y_pos:y_des, x_pos:x_dex, :] = img[:y_img, :x_img, :]


def bg_duplicator(base: np.array, y_px: int, x_px: int) -> np.array:
    y_base, x_base, chn = base.shape
    bg = np.zeros((y_px, x_px, 4), dtype=base.dtype)
    y_index, x_index = y_px // y_base + 1, x_px // x_base + 1
    for y_cnt in range(y_index):
        for x_cnt in range(x_index):
            simple_plot(bg, base, [y_cnt * y_base, x_cnt * x_base])
    return bg


def png_superimpose(bg: np.array, img: np.array, pos: list or tuple = (0, 0), transparency: float = 1.0):
    # pos should be like (y, x), images coded in BGR
    y_max, x_max, chn = bg.shape
    y_pos, x_pos = pos
    y_dis, x_dis, chn = img.shape
    y_des, x_des = y_pos + y_dis, x_pos + x_dis
    if y_max <= y_pos or x_max <= x_pos:
        return
    if y_max < y_des:
        y_des = y_max
        y_dis = y_max - y_pos
    if x_max < x_des:
        x_des = x_max
        x_dis = x_max - x_pos
    uni_img = (img[:y_dis, :x_dis, 3] / 255.0) * transparency
    uni_bg = 1 - uni_img

    for chn in range(3):
        bg[y_pos: y_des, x_pos:x_des, chn] = uni_bg * bg[y_pos: y_des, x_pos:x_des, chn] + \
                                             uni_img * img[:y_dis, :x_dis, chn]


def parabola_gradient(bg: np.array, a: float, c: float, axis: str = 'x0'):
    """
    Function to add simple gradient filter, using parabola method.
    Parabola described by quadratic function needs three parameters to define, means y=ax^2+bx+c or x=ay^2+by+c
    In 'x0' and 'y0' option, the function picks the y value range from [-1, 1] to build the filter
    In other 4 options, the function will only pick the half side of it, makes it an unilateral filter
    :param bg:   background, cv2 image
    :param a:    parameter of quadratic function
    :param c:    parameter of quadratic function
    :param axis: available axes 'x0', 'x+', 'x-', 'y0', 'y+', 'y-'
    :return:
    """
    y_dis, x_dis, chn = bg.shape

    def get_axis(op: str, dis: int) -> np.array:
        if op == '0':
            __axis = np.linspace(-1, 1, dis)
        elif op == '+':
            __axis = np.linspace(0, 1, dis)
        elif op == '-':
            __axis = np.linspace(-1, 0, dis)
        else:
            return
        return __axis

    if axis[0] == 'x':
        x_axis = get_axis(axis[1], x_dis)
        for index in range(x_dis):
            y_value = a * x_axis[index] ** 2 + c
            if y_value > 1:
                y_value = 1
            if y_value < 0:
                y_value = 0
            bg[:, index, :] = bg[:, index, :] * y_value

    elif axis[0] == 'y':
        y_axis = get_axis(axis[1], y_dis)
        for index in range(y_dis):
            x_value = a * y_axis[index] ** 2 + c
            if x_value > 1:
                x_value = 1
            if x_value < 0:
                x_value = 0
            bg[index, :, :] = bg[index, :, :] * x_value
    else:
        return


def simple_rectangle(size: tuple, color: tuple, dt: type):
    x, y = size
    size = (y, x)
    rect_b, rect_g, rect_r = \
        np.ones(size, dtype=dt) * color[0], np.ones(size, dtype=dt) * color[1], np.ones(size, dtype=dt) * color[2]
    rect_a = np.ones(size, dt) * 255
    return cv2.merge((rect_b, rect_g, rect_r, rect_a))


def grid_plot(bg: np.array, img_list: tuple or list, base: tuple, precession: tuple, limit: int, axis: str = 'x'):
    """
    Function to plot a set of images in the shape of matrix or grid.
    :param bg:         Just background
    :param img_list:   Image set you want to plot
    :param base:       Base position of all images, like the top left corner of the matrix
    :param precession: It defines how much length should a new image goes compared to its predecessor
    :param limit:      It defines how many elements can a row or a column contain
    :param axis:       'x' means the function will fill the matrix by row, 'y' fills it by column
    :return:
    """
    y_base, x_base = base
    y_pre, x_pre = precession
    list_len = len(img_list)
    for index in range(list_len):
        if axis == 'x':
            y_add, x_add = (index // limit) * y_pre, (index % limit) * x_pre  # addition
        else:  # Function won't check validity of axis arg
            y_add, x_add = (index % limit) * y_pre, (index // limit) * x_pre
        y_cur, x_cur = y_base + y_add, x_base + x_add  # current
        png_superimpose(bg, img_list[index], (y_cur, x_cur))


def grid_text(text_list: list, color_list: list, base: tuple, precession: tuple,
              limit: int, pen: ImageDraw.Draw, font: ImageFont.truetype, axis: str = 'x'):  # Blatant plagiarism
    x_base, y_base = base
    x_pre, y_pre = precession
    list_len = len(text_list)
    for index in range(list_len):
        if axis == 'y':
            x_add, y_add = (index // limit) * x_pre, (index % limit) * y_pre  # addition
        else:  # Function won't check validity of axis arg
            x_add, y_add = (index % limit) * x_pre, (index // limit) * y_pre
        x_cur, y_cur = x_base + x_add, y_base + y_add  # current
        text = text_list[index]
        if type(text) != str:
            text = str(text)
        pen.text((x_cur, y_cur), text, color_list[index], font=font)


# The very approving method, but it can't generate a transparent background.
def plot_matplotlib_legacy(bg: np.array, fig: plt.figure, pos: tuple):
    fig.canvas = FigureCanvasAgg(plt.gcf())
    fig.canvas.draw()
    x_can, y_can = fig.canvas.get_width_height()
    buf = np.fromstring(fig.canvas.tostring_argb(), dtype=bg.dtype)
    buf.shape = (x_can, y_can, 4)
    buf = np.roll(buf, 3, axis=2)
    img = Image.frombytes('RGBA', (x_can, y_can), buf.tostring())
    img = np.asarray(img)
    png_superimpose(bg, img, pos)


def plot_matplotlib(bg: np.array, pos: tuple, temp_dir: str):
    plt.savefig(temp_dir + '/data/matplotlib.png', transparent=True)
    img = cv2.imread(temp_dir + '/data/matplotlib.png', cv2.IMREAD_UNCHANGED)
    png_superimpose(bg, img, pos)


def hex_2_rgb(raw_color: str) -> tuple:
    if raw_color[0] == '#':
        raw_color = raw_color[1:]
    if len(raw_color) is 6:
        r = int(raw_color[0:2], 16)
        g = int(raw_color[2:4], 16)
        b = int(raw_color[4:6], 16)
    else:
        return 0, 0, 0
    return r, g, b


def rgb_2_hex(raw_color: tuple, add_well=True) -> str:
    if add_well:
        color = '#'
    else:
        color = ''
    for chn in raw_color:
        chn = int(chn)
        color += str(hex(chn))[-2:].replace('x', '0').upper()
    return color


def set_spines_color(ax):
    pass


class Anchor(object):
    def __init__(self, bg: np.array, name: str, free: tuple = (0, 0), father: classmethod.__class__ = None):
        self.bg = bg
        self.name = name
        self.free = free

        self.father, self.children = None, []
        self.grid, self.precession = (0, 0), (0, 0)
        self.grid_id = (0, 0)

        self.x, self.y = self.free[0], self.free[1]
        if father is not None:
            self.set_father(father)

    def update_pos(self):
        if not self.father:
            self.x, self.y = self.free
        else:
            self.x = self.father.x + self.grid_id[0] * self.father.precession[0] + self.free[0]
            self.y = self.father.y + self.grid_id[1] * self.father.precession[1] + self.free[1]

    def set_father(self, father: classmethod.__class__):
        self.father = father
        father.children.append(self)
        self.update_pos()

    def creat_grid(self, grid: tuple, precession: tuple):
        self.grid, self.precession = grid, precession

    def set_grid(self, grid_id: tuple):
        if not self.father:
            raise AttributeError('Can not set grid ID to an orphan anchor.')
        grid, precession = self.father.grid, self.father.precession
        if grid_id[0] > grid[0] or grid_id[1] > grid[1]:
            raise IndexError('Grid ID number(%d, %d) out of scope(%d, %d).'
                             % (grid_id[0], grid_id[1], grid[0], grid[1]))
        self.grid_id = grid_id
        self.update_pos()

    def set_absolute(self, absolute: tuple):
        self.x, self.y = absolute


class AnchorImage(Anchor):
    def __init__(self, bg: np.array, name: str, img: np.array,
                 free: tuple = (0, 0), father: classmethod.__class__ = None):
        Anchor.__init__(self, bg, name, free, father)
        self.img = img

        self.size_y, self.size_x, self.chn = img.shape

    def plot(self, transparency: float = 1.0, is_cv2: bool = True):
        if is_cv2:
            png_superimpose(self.bg, self.img, (self.y, self.x), transparency)


class AnchorText(Anchor):
    def __init__(self, bg: np.array, name: str, text: str,
                 free: tuple = (0, 0), father: classmethod.__class__ = None):
        Anchor.__init__(self, bg, name, free, father)
        self.text = text
