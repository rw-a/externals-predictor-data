from PIL import Image
from constants import ALLOWED_NUMBER_OF_INTERVALS


class ImageParser:
    def __init__(self, filename: str):
        """Settings"""
        self.WHITE_PIXEL = (255, 255, 255)  # index of 0
        self.BLACK_PIXEL = (0, 0, 0)        # index of 1
        self.BLUE_PIXEL = (145, 189, 228)   # index of 2
        self.BLUE_SEPARATOR_PIXEL_1 = (188, 229, 255)   # is considered white but is useful for separating bars
        self.BLUE_SEPARATOR_PIXEL_2 = (172, 207, 237)

        """Init"""
        self.filename = filename
        self.image_original = Image.open(filename)
        self.image = self.quantize_image()

        """Variables"""
        self.y_axis = 0         # the x-coordinate of the y-axis
        self.x_axis = 0         # the y-coordinate of the x-axis
        self.intervals = []     # the x-coordinates of the intervals on the x-axis

        """Methods"""
        self.locate_y_axis()
        self.locate_x_axis()
        self.locate_intervals()

    def quantize_image(self):
        image_palette = Image.new("P", (3, 1))
        image_palette.putpalette((
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
        for y in range(self.image.height - 1):
            # find the first black pixel in each row and add it to the dict
            black_pixels_found = False
            for x in range(self.image.width - 1):
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
                        return

    def locate_x_axis(self):
        first_black_pixels = {}  # dict with key being y-coord of first black pixel in each column
        for x in range(self.y_axis, self.image.width - 1):
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
                        return

    def locate_intervals(self):
        skip_remaining_black_pixels = False     # ensures that consecutive black pixels are only counted once
        for x in range(self.y_axis, self.image.width - 1):
            pixel = self.image.getpixel((x, self.x_axis))
            if pixel == 1 and not skip_remaining_black_pixels:     # if black pixel
                self.intervals.append(x)
                skip_remaining_black_pixels = True
            elif pixel != 1:
                skip_remaining_black_pixels = False

        if len(self.intervals) not in ALLOWED_NUMBER_OF_INTERVALS:
            print(f"WARNING: Possibly invalid number of intervals ({len(self.intervals)}) found in {self.filename}")

    """Find position of bars"""

    """Determine value of each bar"""

    """Determine total height of all bars"""

    """Convert height of each bar to percentage"""

    """Get percentage of each raw score"""


image = ImageParser("pdfs/snr_chemistry_21_subj_rpt/Total-page10-img01.jpg")
