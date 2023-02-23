import numpy as np
from PIL import Image, ImageFilter
from constants import ALLOWED_NUMBER_OF_INTERVALS


class ImageParser:
    def __init__(self, filename: str):
        """Settings"""
        self.DEBUG = True
        self.SEPARATE_BLUES = False

        self.WHITE_PIXEL = (255, 255, 255)  # index of 0
        self.BLACK_PIXEL = (2, 2, 2)        # index of 1
        if self.SEPARATE_BLUES:
            self.BLUE_PIXEL = (145, 189, 228)  # index of 2
            self.BLUE_SEPARATOR_PIXEL_1 = (172, 207, 237)   # darker than 2
            self.BLUE_SEPARATOR_PIXEL_2 = (188, 229, 255)   # is considered white but is useful for separating bars
        else:
            # actually in between true blue and separator blue
            self.BLUE_PIXEL = (165, 199, 233)  # index of 2

        """Init"""
        self.filename = filename
        self.image_original = Image.open(filename)
        self.image = self.preprocess_image()

        """Variables"""
        self.y_axis = 0         # the x-coordinate of the y-axis (from the right-most black pixel)
        self.x_axis = 0         # the y-coordinate of the x-axis (from the bottom-most black pixel)
        self.intervals = []     # the x-coordinates of the intervals on the x-axis
        self.bar_base = 0       # the y-coordinate of the bottom of the bars in the graph
        self.bar_base_colour = None  # the main colour of the bar bases
        self.bars = []          # tuples containing the start and end x-coordinates of the bars

        """Methods"""
        self.locate_y_axis()
        self.locate_x_axis()
        self.locate_intervals()
        self.locate_bar_base()
        self.get_bar_x_coordinates()

    def preprocess_image(self):
        edge_enhanced_image = self.image_original.filter(ImageFilter.EDGE_ENHANCE_MORE)

        palette = [
            # ORDER MATTERS HERE
            *self.WHITE_PIXEL,  # index of 0
            *self.BLACK_PIXEL,  # index of 1
            *self.BLUE_PIXEL,   # index of 2
        ]
        if self.SEPARATE_BLUES:
            palette.extend(self.BLUE_SEPARATOR_PIXEL_1)
            palette.extend(self.BLUE_SEPARATOR_PIXEL_2)

        image_palette = Image.new("P", (3, 1))
        image_palette.putpalette(palette)

        quantised_image = edge_enhanced_image.quantize(colors=3, palette=image_palette, dither=Image.Dither.NONE)

        if self.DEBUG:
            quantised_image.save("quantised.png")

        return quantised_image

    def locate_y_axis(self):
        """Finds the x-coordinate of the right-most pixel of the y-axis"""
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
                        return self.y_axis

        print("ERROR: Couldn't locate y-axis")

    def locate_x_axis(self):
        """Finds the y-coordinate of the bottom of the x-axis"""
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
                        return self.x_axis

        print("ERROR: Couldn't locate x-axis")

    def locate_intervals(self):
        """Locates the x-coordinates (left-most pixel) of the axis-ticks of the x-axis"""
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

    def locate_bar_base(self):
        for y in range(self.x_axis - 10, 0, -1):   # start a few pixels above the bottom of the x-axis
            num_black_pixels_in_row = 0
            for x in range(self.y_axis, self.image.width):
                pixel = self.image.getpixel((x, y))
                if pixel == 1:
                    num_black_pixels_in_row += 1

            if num_black_pixels_in_row >= 10:
                # if a lot of black pixels, most are probs black. otherwise, base is mostly blue probs
                self.bar_base_colour = 1 if num_black_pixels_in_row >= 100 else 2
                self.bar_base = y
                return self.bar_base
        print(f"ERROR: Couldn't locate bar base")

    def get_bar_x_coordinates(self):
        in_bar = False
        bar_x_start = 0

        for x in range(self.y_axis, self.image.width):
            pixel = self.image.getpixel((x, self.bar_base))

            if not in_bar:
                if (self.bar_base_colour == 1 and
                    (pixel == 1 or (pixel == 2 and self.image.getpixel((x, self.bar_base + 1)) == 1)))\
                        or (self.bar_base_colour == 2 and (pixel == 2 or pixel == 1)):
                    """
                    Detects if this pixel is the bottom-left pixel of a bar
                    
                    Case 1: bar base colour is black
                        1. Pixel is black,
                        2. Pixel is blue and pixel above is black (in case current pixel wasn't made black)
                    
                    Case 2: bar base colour is blue
                        1. Pixel is blue or black
                    """

                    in_bar = True
                    bar_x_start = x
            else:
                if pixel == 0:
                    self.bars.append((bar_x_start, x))
                    in_bar = False
                    bar_x_start = 0
        print(self.bars)
        return self.bars

    """Convert height of each bar to percentage"""

    """Get percentage of each raw score"""


image = ImageParser("pdfs/engineering_21/Internals-page05-img01.png")
