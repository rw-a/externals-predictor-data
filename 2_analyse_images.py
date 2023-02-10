from PIL import Image
from constants import ALLOWED_NUMBER_OF_INTERVALS


class ImageParser:
    def __init__(self, filename: str):
        """Settings"""
        self.WHITE_PIXEL = (255, 255, 255)  # index of 0
        self.BLACK_PIXEL = (0, 0, 0)        # index of 1
        self.BLUE_PIXEL = (145, 189, 228)   # index of 2
        self.BLUE_SEPARATOR_PIXEL_1 = (172, 207, 237)   # darker than 2
        self.BLUE_SEPARATOR_PIXEL_2 = (188, 229, 255)   # is considered white but is useful for separating bars

        """Init"""
        self.filename = filename
        self.image_original = Image.open(filename)
        self.image = self.quantize_image()

        """Variables"""
        self.y_axis = 0         # the x-coordinate of the y-axis
        self.x_axis = 0         # the y-coordinate of the x-axis
        self.intervals = []     # the x-coordinates of the intervals on the x-axis
        self.bars = {}          # the x-coordinates of the bars (with the value being their height)

        """Methods"""
        self.locate_y_axis()
        self.locate_x_axis()
        self.locate_intervals()
        self.measure_bars()

    def quantize_image(self):
        image_palette = Image.new("P", (3, 1))
        image_palette.putpalette((
            # ORDER MATTERS HERE
            *self.WHITE_PIXEL,  # index of 0
            *self.BLACK_PIXEL,  # index of 1
            *self.BLUE_PIXEL,   # index of 2
            *self.BLUE_SEPARATOR_PIXEL_1,
            *self.BLUE_SEPARATOR_PIXEL_2
        ))

        new_image = self.image_original.quantize(colors=3, palette=image_palette, dither=Image.Dither.NONE)

        new_image.save("quantised.png")
        return new_image

    def locate_y_axis(self):
        # dict with key being x-coord of last black pixel in the first consecutive group of black pixels in each row
        last_black_pixels = {}
        for y in range(self.image.height):
            # find the first black pixel in each row and add it to the dict
            black_pixels_found = False
            for x in range(self.image.width):
                pixel = self.image.getpixel((x, y))
                if black_pixels_found and pixel != 1:     # the first white pixel after the last black pixel
                    if x in last_black_pixels:
                        last_black_pixels[x] += 1
                    else:
                        last_black_pixels[x] = 1
                    break
                if not black_pixels_found and pixel == 1:  # if pixel is the black pixel to be found
                    black_pixels_found = True

            # check if there has been many black pixels on the same x-coord (i.e. vertical line = y-axis)
            if len(last_black_pixels) > 0:
                for x_coord, frequency in last_black_pixels.items():
                    if frequency > 5:
                        self.y_axis = x_coord
                        if self.y_axis / self.image.width > 0.2:
                            print(f"WARNING: Possibly invalid y-axis position ({self.y_axis}) in {self.filename}")
                        return

    def locate_x_axis(self):
        first_black_pixels = {}  # dict with key being y-coord of first black pixel in each column
        for x in range(self.y_axis, self.image.width):
            # find the first black pixel in each column (starting from bottom) and add it to the dict
            for y in range(self.image.height - 1, 0, -1):
                pixel = self.image.getpixel((x, y))
                if pixel == 1:  # if pixel is black
                    if y in first_black_pixels:
                        first_black_pixels[y] += 1
                    else:
                        first_black_pixels[y] = 1
                    break
            # check if there has been many black pixels on the same x-coord (i.e. vertical line = y-axis)
            if len(first_black_pixels) > 0:
                for y_coord, frequency in first_black_pixels.items():
                    if frequency > 5:
                        self.x_axis = y_coord + 1   # +1 because it needs to be the pixel before the first black pixel
                        if self.x_axis / self.image.height < 0.8:
                            print(f"WARNING: Possibly invalid x-axis position ({self.x_axis}) in {self.filename}")
                        return

    def locate_intervals(self):
        skip_remaining_black_pixels = False     # ensures that consecutive black pixels are only counted once
        for x in range(self.y_axis, self.image.width):
            pixel = self.image.getpixel((x, self.x_axis))
            if pixel == 1 and not skip_remaining_black_pixels:     # if black pixel
                self.intervals.append(x)
                skip_remaining_black_pixels = True
            elif pixel != 1:
                skip_remaining_black_pixels = False

        if len(self.intervals) not in ALLOWED_NUMBER_OF_INTERVALS:
            print(f"WARNING: Possibly invalid number of intervals ({len(self.intervals)}) in {self.filename}")

    def measure_bars(self):
        bar_found = False
        bar_x_start = 0
        bar_y_start = 0
        bar_max_height = 0

        x = self.y_axis
        while x < self.image.width:
            y = bar_y_start + 1 if bar_found else self.x_axis - 5   # once bar found, start searching from known start
            while y > 0:
                pixel = self.image.getpixel((x, y))
                if pixel == 2:  # if pixel is blue
                    if not bar_found:
                        bar_x_start = x
                        bar_y_start = y
                        bar_found = True
                    else:
                        # if found that the next y start is lower
                        if y > bar_y_start:
                            bar_y_start = y
                elif bar_found:
                    if y < bar_y_start:    # if still continuing to search bar
                        # if the bar height in this column is greater
                        bar_height = bar_y_start - y
                        if bar_height > bar_max_height:
                            bar_max_height = bar_height
                        break
                    elif y == bar_y_start:     # if start of the next column should be a blue but isn't, the bar is done
                        bar_x_middle = round((bar_x_start + x) / 2)
                        # self.bars[bar_x_middle] = bar_max_height
                        self.bars[bar_x_middle] = (bar_y_start, bar_max_height)     # for debugging when graphing
                        bar_found = False
                        bar_x_start = 0
                        bar_y_start = 0
                        bar_max_height = 0
                        break
                y -= 1
            x += 1
        print(self.bars)

        new_image = Image.new("RGB", (self.image.width, self.image.height))
        for bar, position in self.bars.items():
            for i in range(position[1]):
                new_image.putpixel((bar, position[0] - i), (255, 0, 0))
        new_image.save("bars.png")

    """Determine total height of all bars"""

    """Convert height of each bar to percentage"""

    """Get percentage of each raw score"""


image = ImageParser("pdfs/snr_chemistry_21_subj_rpt/Total-page10-img01.jpg")
