import csv
import numpy as np
from PIL import Image
from constants import NUMBER_OF_INTERVALS


class ImageParser:
    def __init__(self, filename: str):
        """Settings"""
        self.DEBUG = True

        self.WHITE_PIXEL = (255, 255, 255)  # index of 0
        self.BLACK_PIXEL = (2, 2, 2)        # index of 1
        self.BLUE_PIXEL = (165, 199, 233)  # index of 2

        self.X_AXIS_WIDTH = 4

        """Init"""
        self.filename = filename
        self.image_original = Image.open(filename)
        self.image = self.preprocess_image()

        """Variables"""
        self.y_axis = 0         # the x-coordinate of the y-axis (from the right-most black pixel)
        self.x_axis = 0         # the y-coordinate of the x-axis (from the bottom-most black pixel)
        self.intervals = []     # the x-coordinates of the intervals on the x-axis
        self.bars_x = []        # the x-coordinates (centre) of the bars in the graph
        self.bars_height = {}   # dict mapping x-coordinate (centre) of bars to their height
        self.bars = {}          # dict mapping x-coordinate (centre) of bars to their percentage (actually decimal)
        self.score_lookup = {}  # dict mapping raw score to percentile

        """Methods"""
        self.locate_y_axis()
        self.locate_x_axis()
        self.locate_intervals()
        self.locate_bars()
        self.get_bar_height()
        self.calculate_bar_percentages()
        self.get_score_mapping()

        if self.DEBUG:
            with open("lookup.csv", 'w') as file:
                writer = csv.writer(file)
                for percentile in self.score_lookup.values():
                    writer.writerow([percentile])

    def preprocess_image(self):
        palette = [
            # ORDER MATTERS HERE
            *self.WHITE_PIXEL,  # index of 0
            *self.BLACK_PIXEL,  # index of 1
            *self.BLUE_PIXEL,   # index of 2
        ]

        image_palette = Image.new("P", (3, 1))
        image_palette.putpalette(palette)

        quantised_image = self.image_original.quantize(colors=3, palette=image_palette, dither=Image.Dither.NONE)

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

        # TEST
        differences = np.ediff1d(self.intervals)
        median_diff = np.median(differences)
        for i in differences:
            discrepancy = abs(i - median_diff)
            if discrepancy > 1:
                print(f"WARNING: Possibly invalid position of interval (discrepancy of {discrepancy}) in {self.filename}")

    def locate_bars(self):
        """Locates the x-coordinates (center) of each bar"""
        if len(self.intervals) not in NUMBER_OF_INTERVALS:
            print(f"ERROR: Invalid number of intervals ({len(self.intervals)}) in {self.filename}. SKIPPING")

        num_bars = NUMBER_OF_INTERVALS[len(self.intervals)]
        self.bars_x = np.round(np.linspace(self.intervals[0], self.intervals[-1], num_bars)).astype(int)

    def get_bar_height(self):
        for bar_x in self.bars_x:
            # Take the median of 3 columns in the bar to prevent outliers
            heights = []
            for x in range(bar_x - 1, bar_x + 2):
                height = 0
                for y in range(self.x_axis - self.X_AXIS_WIDTH):
                    pixel = self.image.getpixel((x, y))
                    if pixel == 2:
                        height += 1
                        if self.DEBUG:
                            self.image.putpixel((x, y), (255, 0, 0))
                heights.append(height)

            median_height = int(np.median(heights))
            self.bars_height[bar_x] = median_height

        if self.DEBUG:
            self.image.save("bars.png")

    def calculate_bar_percentages(self):
        """Convert height of each bar to percentage"""
        total_height = sum(self.bars_height.values())
        for bar_x, height in self.bars_height.items():
            self.bars[bar_x] = height / total_height

    def get_score_mapping(self):
        """Enumerate the bars to convert them into their corresponding raw score"""
        for raw_score, percentile in enumerate(self.bars.values()):
            self.score_lookup[raw_score] = percentile


image = ImageParser("pdfs/engineering_21/Internals-page05-img01.png")
