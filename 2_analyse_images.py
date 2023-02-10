from PIL import Image


class ImageParser:
    def __init__(self, filename: str):
        self.image = Image.open(filename)
        self.image_quantized = self.quantize_image()

        self.y_axis = 0     # the horizontal position of the y-axis
        self.x_axis = 0     # the vertical position of the x-axis

        # self.generate_false_colour()

    @staticmethod
    def is_black_pixel(pixel: tuple):
        return pixel[0] < 2 and pixel[1] < 2 and pixel[2] <= 75

    @staticmethod
    def is_blue_pixel(pixel: tuple):
        return 140 < pixel[0] < 160 and 50 < pixel[1] < 120 and pixel[2] > 200

    def quantize_image(self):
        image_palette = Image.new("P", (3, 1))
        image_palette.putpalette((
            0, 0, 0,
            255, 255, 255,
            145, 189, 228
        ))

        new_image = self.image.quantize(colors=3, palette=image_palette, dither=Image.Dither.NONE)

        # new_image.save("quantise.png")
        return new_image

    def locate_y_axis(self):
        pass

    """Find position of y-axis"""

    """Find position of x-axis, starting horizontally from y-axis"""

    """Find position of tick marks on x-axis"""

    """Find position of bars"""

    """Determine value of each bar"""

    """Determine total height of all bars"""

    """Convert height of each bar to percentage"""

    """Get percentage of each raw score"""


image = ImageParser("pdfs/snr_study_religion_20_subj_rpt/Externals-page09-img01.jpg")
