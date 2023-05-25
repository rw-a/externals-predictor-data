import os
import glob
from pikepdf import Pdf, PdfImage
from constants import IMAGES_DIRECTORY

FOLDER_NAME = "pdfs"
USE_IMAGES_DIRECTORY = True

if not os.path.exists(FOLDER_NAME):
    os.mkdir(FOLDER_NAME)


for filename in glob.glob(f"{FOLDER_NAME}/*.pdf"):
    try:
        year = int("20" + filename[filename.index("_subj_rpt") - 2: filename.index("_subj_rpt")])
        folder_name = filename.replace("snr_", "").replace("_subj_rpt", "").replace(".pdf", "")
        if os.path.exists(folder_name):   # skip if subject has already been analysed
            print(f"Skipping {filename} since folder {folder_name} already exists.")
            continue
        os.mkdir(folder_name)     # [:-4] removes the .pdf ending
    except:
        print(f"ERROR: Reading {filename}")
        continue

    pdf = Pdf.open(filename)

    if USE_IMAGES_DIRECTORY:
        page_categories = IMAGES_DIRECTORY[year]
    else:
        page_categories = {f"Unknown{page_num}": page_num for page_num in range(1, len(pdf.pages) + 1)}

    for graph_type, page_number in page_categories.items():
        page = pdf.pages[page_number - 1]

        if len(page.images) < 1:    # if a page has no images, try the previous one instead
            page = pdf.pages[page_number - 2]

        for image_index, image_data in enumerate(page.images.values()):
            image = PdfImage(image_data)
            out = image.extract_to(
                fileprefix=f"{folder_name}/{graph_type}-page{page_number:02}-img{image_index + 1:02}")
