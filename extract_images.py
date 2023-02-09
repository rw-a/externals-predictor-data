from pikepdf import Pdf, PdfImage

filename = "snr_accounting_20_subj_rpt.pdf"
example = Pdf.open(filename)

for i, page in enumerate(example.pages):
    for j, (name, raw_image) in enumerate(page.images.items()):
        image = PdfImage(raw_image)
        out = image.extract_to(fileprefix=f"{filename}-page{i:03}-img{j:03}")