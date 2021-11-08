import numpy as np

from cfg_read import *


def quick_show(img: np.array):
    cv2.imshow('', img)
    cv2.waitKey(0)


def add_alpha(img: np.array) -> np.array:
    img_b, img_g, img_r = cv2.split(img)
    img_a = np.ones(img_b.shape, dtype=np.uint8) * 255
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


def png_superimpose(bg: np.array, img: np.array,
                    pos: list or tuple = (0, 0), opacity: float = 1.0, is_add: bool = False):
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
    uni_img = (img[:y_dis, :x_dis, 3] / 255.0) * opacity
    if is_add:  # two transparent images add together
        uni_bg = bg[y_pos: y_des, x_pos:x_des, 3] / 255.0
        for chn in range(3):
            bg[y_pos: y_des, x_pos:x_des, chn] = uni_bg * bg[y_pos: y_des, x_pos:x_des, chn] + \
                                                 uni_img * img[:y_dis, :x_dis, chn]
        bg[y_pos: y_des, x_pos:x_des, 3] = (1 - (1 - uni_bg) * (1 - uni_img)) * 255
    else:  # a transparent image adds on a concrete background
        uni_bg = 1 - uni_img
        for chn in range(4):
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


def simple_rectangle(size: tuple, color: tuple, dt: type, width: int = 0):
    rect_b, rect_g, rect_r = \
        np.ones(size, dtype=dt) * color[0], np.ones(size, dtype=dt) * color[1], np.ones(size, dtype=dt) * color[2]
    rect_a = np.ones(size, dt) * 255
    if width:
        rect_a[width: size[0] - width, width: size[1] - width] = 0
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


def plot_matplotlib(bg: np.array, pos: tuple):
    plt.savefig(local_dir + '/data/matplotlib.png', transparent=True)
    img = cv2.imread(local_dir + '/data/matplotlib.png', cv2.IMREAD_UNCHANGED)
    png_superimpose(bg, img, pos)


def get_matplotlib(fig: plt.figure):
    if not fig:
        return
    plt.savefig(local_dir + '/data/matplotlib.png', transparent=True)
    img = cv2.imread(local_dir + '/data/matplotlib.png', cv2.IMREAD_UNCHANGED)
    return img


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


def rgb_2_bgr(raw_color: tuple) -> tuple:
    return raw_color[2], raw_color[1], raw_color[0]


def rgb_2_hex(raw_color: tuple, add_well=True) -> str:
    if add_well:
        color = '#'
    else:
        color = ''
    for chn in raw_color:
        chn = int(chn)
        color += str(hex(chn))[-2:].replace('x', '0').upper()
    return color


def outer_glow(img: np.array, color: tuple, radius: int, is_gaussian: bool = False):
    """
    Using blur(box blur) to create outer glow, it returns only glow, not glowed image
    :param img:    Image with alpha channel
    :param color:  Color of the glow
    :param radius: Size of the box. Higher the value, wider the glow.
    :param is_gaussian: Using Gaussian blur if validated.
    :return:       Glow image which add glowed margin (width = radius)
    """
    img_y, img_x, chn = img.shape
    alpha = np.zeros((img_y + 2 * radius, img_x + 2 * radius), dtype=img.dtype)
    glow_y, glow_x = alpha.shape
    alpha[radius:-radius, radius:-radius] = img[:, :, 3]
    if is_gaussian:
        alpha = cv2.GaussianBlur(alpha, (radius, radius), 0.8, 0.8)
    else:
        alpha = cv2.blur(alpha, (radius, radius))
    glow_r = np.ones((glow_y, glow_x), dtype=img.dtype) * color[0]
    glow_g = np.ones((glow_y, glow_x), dtype=img.dtype) * color[1]
    glow_b = np.ones((glow_y, glow_x), dtype=img.dtype) * color[2]
    glow = cv2.merge((glow_b, glow_g, glow_r, alpha))

    return glow


class Anchor(object):
    """
    Based on (y, x) axis system and (B, G, R, (A)) color system (in line with OpenCV)
    It means PIL coordinate and color will be transformed into OpenCV way.
    Honestly I don't know why they set these systems such counter-instinctively :(
    """

    def __init__(self, bg: np.array, name: str, free: tuple = (0, 0), father: classmethod.__class__ = None):
        self.bg = bg
        self.name = name
        self.free = free

        self.father = None
        self.grid, self.precession = (0, 0), (0, 0)
        self.grid_id = (0, 0)

        self.y, self.x = self.free
        if father is not None:
            self.set_father(father)

        self.absolute = None

    def update_pos(self):
        if not self.father:
            self.y, self.x = self.free
        else:
            self.y = self.father.y + self.grid_id[0] * self.father.precession[0] + self.free[0]
            self.x = self.father.x + self.grid_id[1] * self.father.precession[1] + self.free[1]

    def set_father(self, father: classmethod.__class__):
        self.father = father
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
        self.absolute = absolute

    def set_free(self, free: tuple):
        self.free = free
        self.update_pos()

    def show_pos(self, length: int = 10):
        for index in range(length):
            self.bg[self.y, self.x + index] = [0, 0, 255, 255]
            self.bg[self.y + index, self.x] = [0, 0, 255, 255]


class AnchorImage(Anchor):
    def __init__(self, bg: np.array, name: str, img: np.array,
                 free: tuple = (0, 0), father: classmethod.__class__ = None):
        Anchor.__init__(self, bg, name, free, father)
        self.img = img

        self.size_y, self.size_x, self.chn = img.shape

    def plot(self, opacity: float = 1.0, offset: tuple = (0, 0),
             y_reverse: bool = False, x_reverse: bool = False, trans_bg: bool = False):
        if self.absolute:
            png_superimpose(self.bg, self.img, self.absolute, opacity)
            return
        self.update_pos()
        plot_y, plot_x = self.y + offset[0] - y_reverse * self.size_y, self.x + offset[1] - x_reverse * self.size_x
        png_superimpose(self.bg, self.img, (plot_y, plot_x), opacity, is_add=trans_bg)

    def plot_center(self, opacity: float = 1.0, offset: tuple = (0, 0), trans_bg: bool = False):
        bg_y, bg_x, chn = self.bg.shape
        pos_y, pos_x = abs(bg_y - self.size_y) // 2, abs(bg_x - self.size_x) // 2
        png_superimpose(self.bg, self.img, (pos_y + offset[0], pos_x + offset[1]), opacity, is_add=trans_bg)


class AnchorText(Anchor):
    def __init__(self, bg: np.array, name: str, text: str, pen: ImageDraw.Draw, font: ImageFont.truetype,
                 free: tuple = (0, 0), father: classmethod.__class__ = None):
        Anchor.__init__(self, bg, name, free, father)
        self.text = text
        self.pen = pen
        self.font = font

    def plot(self, color: tuple, offset: tuple = (0, 0), pos: str = 'l'):
        """
        Render text on background.
        :param color:  Color of the text, (R, G, B)
        :param offset: Extra offset to set
        :param pos:    Way to arrange the text. 'l' means flush left, 'c' means center, 'r' means flush right
        """
        if pos == 'c':
            length = self.font.getsize(self.text)[0]
            offset = (offset[0], offset[1] - length // 2)
        elif pos == 'r':
            length = self.font.getsize(self.text)[0]
            offset = (offset[0], offset[1] - length)
        color = rgb_2_bgr(color)
        if self.absolute:
            self.pen.text((self.absolute[1] + offset[1], self.absolute[0] + offset[0]), self.text, color, self.font)
            return
        self.update_pos()
        self.pen.text((self.x + offset[1], self.y + offset[0]), self.text, color, font=self.font)

    def plot_shadow(self, color: tuple, shadow: dict, offset: tuple = (0, 0), pos: str = 'l', width: int = 1):
        dir_table = {0: (-2, 0), 1: (-1, 1), 2: (0, 2), 3: (1, 1), 4: (2, 0), 5: (1, -1), 6: (0, -2), 7: (-1, -1)}
        for index in range(8):
            offset_dir = dir_table[index]
            offset_cur = (offset_dir[0] * width + offset[0], offset_dir[1] * width + offset[1])
            self.plot(color, offset_cur, pos)
        if shadow['validity']:
            shadow_color, shadow_dir = shadow['color'], shadow['direction']
            offset_dir = dir_table[shadow_dir]
            offset_cur = (offset_dir[0] * width + offset[0], offset_dir[1] * width + offset[1])
            self.plot(shadow_color, offset_cur, pos)


def generate_frame(corner: tuple, side: tuple, size: tuple, width: tuple, color: tuple, opacity: float) -> np.array:
    top_left, top_right, btm_left, btm_right = corner
    side_top, side_right, side_btm, side_left = side
    content_size = (size[0] - 2 * width[0], size[1] - 2 * width[1])
    img = np.zeros((size[0], size[1], 4), dtype=np.uint8)

    content_r = np.ones(content_size, dtype=np.uint8) * color[0]
    content_g = np.ones(content_size, dtype=np.uint8) * color[1]
    content_b = np.ones(content_size, dtype=np.uint8) * color[2]
    content_a = np.ones(content_size, dtype=np.uint8) * int(opacity * 255)
    content = cv2.merge((content_b, content_g, content_r, content_a))

    side_top = bg_duplicator(side_top, side_top.shape[0], size[1])
    side_right = bg_duplicator(side_right, size[0], side_right.shape[1])
    side_btm = bg_duplicator(side_btm, side_btm.shape[0], size[1])
    side_left = bg_duplicator(side_left, size[0], side_left.shape[1])

    png_superimpose(img, content, width)
    png_superimpose(img, side_top, (0, 0))
    png_superimpose(img, side_right, (0, size[1] - side_right.shape[1]))
    png_superimpose(img, side_btm, (size[0] - side_btm.shape[0], 0))
    png_superimpose(img, side_left, (0, 0))
    png_superimpose(img, top_left, (0, 0))
    png_superimpose(img, top_right, (0, size[1] - top_right.shape[1]))
    png_superimpose(img, btm_left, (size[0] - btm_left.shape[0], 0))
    png_superimpose(img, btm_right, (size[0] - btm_right.shape[0], size[1] - btm_right.shape[1]))

    return img


def generate_line_box(size, color: tuple, inner_color: tuple, width: int, opacity: float,
                      corner: dict = None, glow: dict = None, bg_img: np.array = None) -> np.array:
    box_y, box_x = size
    l_a = np.ones((box_y, box_x), dtype=np.uint8) * 255
    line_box = np.ones((box_y, box_x, 3), dtype=np.uint8) * 255
    cv2.rectangle(line_box, (0, 0), (box_x, box_y), color=rgb_2_bgr(color), thickness=-1)
    l_b, l_g, l_r = cv2.split(line_box)
    line_box = cv2.merge((l_b, l_g, l_r, l_a))

    inner_y, inner_x = box_y - 2 * width, box_x - 2 * width
    inner_bgr = np.ones((inner_y, inner_x, 3), dtype=np.uint8)
    cv2.rectangle(inner_bgr, (0, 0), (inner_x, inner_y), color=rgb_2_bgr(inner_color), thickness=-1)
    inner_a = np.ones((inner_y, inner_x), dtype=np.uint8) * int(255 * opacity)
    inner_b, inner_g, inner_r = cv2.split(inner_bgr)
    inner = cv2.merge((inner_b, inner_g, inner_r, inner_a))
    line_box[width:-width, width:-width, :] = inner

    if bg_img is not None:
        bg_fill = bg_duplicator(bg_img, inner_y, inner_x)
        png_superimpose(line_box, bg_fill, (width, width))

    if glow:
        expand, g_color, radius, g_opacity = glow['expand'], glow['color'], glow['radius'], glow['opacity']
        concrete = np.ones((box_y + 2 * expand, box_x + 2 * expand, 4), dtype=np.uint8) * int(255 * opacity)
        glowed = outer_glow(concrete, g_color, radius, is_gaussian=False)
        glowed[expand + radius:-(expand + radius), expand + radius:-(expand + radius), :] = \
            np.zeros((box_y, box_x, 4), dtype=np.uint8)
        png_superimpose(glowed, line_box, (expand + radius, expand + radius))
        if not corner:
            return glowed
    else:
        glowed = expand = radius = None
    if corner:
        c_width, length, margin, c_color = corner['width'], corner['length'], corner['margin'], corner['color']
        c_a = np.ones((length, length), dtype=np.uint8) * 255
        c_a[c_width:, c_width:] = np.zeros((length - c_width, length - c_width), dtype=np.uint8)
        c_img = np.zeros((length, length, 3), dtype=np.uint8)
        cv2.rectangle(c_img, (0, 0), (length, length), color=rgb_2_bgr(c_color), thickness=-1)
        c_r, c_g, c_b = cv2.split(c_img)
        c_img = cv2.merge((c_r, c_g, c_b, c_a))

        if glow:
            img = glowed
            img_y, img_x = box_y + 2 * margin, box_x + 2 * margin
            base_y = base_x = expand + radius - margin
        else:
            img_y, img_x = box_y + 2 * margin, box_x + 2 * margin
            base_y = base_x = 0
            img = np.zeros((img_y, img_x, 4), dtype=np.uint8)
            img[margin:-margin, margin:-margin, :] = line_box

        png_superimpose(img, c_img, (base_y, base_x))
        c_img = cv2.flip(c_img, 1)
        png_superimpose(img, c_img, (base_y, base_x + img_x - length))
        c_img = cv2.flip(c_img, 0)
        png_superimpose(img, c_img, (base_y + img_y - length, base_x + img_x - length))
        c_img = cv2.flip(c_img, 1)
        png_superimpose(img, c_img, (base_y + img_y - length, base_x))
    else:
        return line_box
    return img


def generate_bar(gradients: list or tuple, length: int, bg: dict) -> np.array:
    left, bar, right = gradients
    img_y, img_x = left.shape[0], length
    left_x, right_x = left.shape[1], right.shape[1]
    if bar.shape[2] == 3:
        bar = add_alpha(bar)
    bar = bg_duplicator(bar, img_y, length - (left_x + right_x))

    img = np.zeros((img_y, img_x, 4), dtype=np.uint8)
    png_superimpose(img, left, (0, 0))
    png_superimpose(img, right, (0, length - right_x))
    png_superimpose(img, bar, (0, left_x))

    if bg['validity']:
        try:
            bg_img, bg_pos = bg['image'], bg['pos']
            if bg_img.shape[2] == 3:
                bg_img = add_alpha(bg_img)
            png_superimpose(img, bg_img, (0, bg_pos))
        except KeyError:
            raise Warning('Parameter missing, the corner will be omitted.')
    return img
