import csv
from PIL import Image


class ImageParser:
    def __init__(self, filename: str):
        self.image = Image.open(filename)
        self.image_hsv = self.image.convert("HSV")
        self.y_axis = 0     # the horizontal position of the y-axis
        self.x_axis = 0     # the vertical position of the x-axis

        self.locate_y_axis()

    @staticmethod
    def is_black_pixel(pixel: tuple):
        return pixel[0] < 2 and pixel[1] < 2 and pixel[2] > 250

    @staticmethod
    def is_blue_pixel(pixel: tuple):
        return 140 < pixel[0] < 160 and 50 < pixel[1] < 120 and pixel[2] > 200

    def locate_y_axis(self):
        with open("output.csv", 'w') as file:
            writer = csv.writer(file)
            for y in range(self.image.height):
                row = []
                for x in range(self.image.width):
                    pixel = self.image_hsv.getpixel((x, y))
                    row.append(pixel)
                writer.writerow([*row, "\n"])

    """Find position of y-axis"""

    """Find position of x-axis, starting horizontally from y-axis"""

    """Find position of tick marks on x-axis"""

    """Find position of bars"""

    """Determine value of each bar"""

    """Determine total height of all bars"""

    """Convert height of each bar to percentage"""

    """Get percentage of each raw score"""


image = ImageParser("pdfs/snr_study_religion_20_subj_rpt/Externals-page09-img01.jpg")
