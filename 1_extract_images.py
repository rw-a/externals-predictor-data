import os
import glob
from pikepdf import Pdf, PdfImage
from constants import IMAGES_DIRECTORY

FOLDER_NAME = "pdfs"
if not os.path.exists(FOLDER_NAME):
    os.mkdir(FOLDER_NAME)


for filename in glob.glob(f"{FOLDER_NAME}/*.pdf"):
    if os.path.exists(filename[:-4]):   # skip if subject has already been analysed
        continue
    os.mkdir(filename[:-4])     # [:-4] removes the .pdf ending

    pdf = Pdf.open(filename)
    year = int("20" + filename[filename.index("_subj_rpt") - 2: filename.index("_subj_rpt")])

    for graph_type, page_number in IMAGES_DIRECTORY[year].items():
        page = pdf.pages[page_number - 1]

        if len(page.images) < 1:    # if a page has no images, try the previous one instead
            page = pdf.pages[page_number - 2]

        for image_index, image_data in enumerate(page.images.values()):
            image = PdfImage(image_data)
            out = image.extract_to(fileprefix=f"{filename[:-4]}/"
                                              f"{graph_type}-page{page_number:02}-img{image_index + 1:02}")
