import cv2
import os
import pandas as pd
import numpy as np
from tqdm import tqdm
from PIL import Image as im
from pdf2image import convert_from_path
import pytesseract

pytesseract.pytesseract.tesseract_cmd = "C:\\Program Files\\Tesseract-OCR\\tesseract.exe"

images_path = "images"
pdf_path = "Label.pdf"
csv_path = "Device_Details.csv"
excel_path = "Device_Details.xlsx"
symbols_path = "symbols"
resized_symbols_path = "resized_symbols"

confidence = 0.69


def symbol_resize():
    for symbol in os.listdir(symbols_path):
        img = im.open(os.path.join(symbols_path, symbol))
        img = img.resize((188, 80))
        img = img.convert('RGB')
        img.save(f"{resized_symbols_path}/{symbol.split('.')[0]}.jpg")


def get_image_contours(img_gray):
    _, thresh = cv2.threshold(
        img_gray, 0, 255, cv2.THRESH_OTSU | cv2.THRESH_BINARY_INV)
    rect_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (30, 14))
    dilation = cv2.dilate(thresh, rect_kernel, iterations=1)
    contours, _ = cv2.findContours(dilation, cv2.RETR_TREE,
                                   cv2.CHAIN_APPROX_SIMPLE)

    return contours


def get_details(image, contours):

    details = []

    for cnt in contours:
        if cv2.contourArea(cnt) > 1800 and cv2.contourArea(cnt) < 20000:

            x, y, w, h = cv2.boundingRect(cnt)

            cropped = image[y:y + h, x:x + w]
            text = pytesseract.image_to_string(cropped)

            details.append(text)

    return details


def get_symbol_code(gray, symbols_path):

    sym_code = []

    for symbol in os.listdir(symbols_path):
        sym_img = cv2.imread(os.path.join(symbols_path, symbol), 0)

        res = cv2.matchTemplate(gray, sym_img, cv2.TM_CCOEFF_NORMED)

        if np.any(res > confidence):
            sym_code.append(symbol.split(".")[0])

    if "4" in sym_code:
        sym_code.insert(0, sym_code.pop(sym_code.index("4")))

    return "".join(sym_code)


def detail_entry(headers, details, symbol_code):

    row_info = []

    for header in headers:

        res = list(filter(lambda x: header in x, details))
        if res:
            if res[0].startswith("REF"):
                elem = res[0].split(" ")[1][:-1]
                row_info.append(elem)
            else:
                elem = res[0].split(": ")[1][:-1]

                if header != "Device Name":
                    elem = int(elem)

                if len(details) >= 10 and header == "Device Name":
                    dev_full = list(
                        filter(lambda x: not " " in x and len(x) != 0, details))

                    if dev_full:
                        elem = elem + " " + dev_full[0][:-1]

                row_info.append(elem)

    row_info.append(symbol_code)

    return row_info


def create_file(format=".xlsx", pdf=False):

    details_list = []

    col_headers = ["Device Name", "REF", "LOT",
                   "Qty", "Symbols"]

    details_list.append(col_headers)

    if pdf:
        images = convert_from_path(pdf_path, size=(1426, 774))

        print(f"Entering device details...")

        for image in tqdm(images):
            img = np.array(image)
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

            contours = get_image_contours(gray)

            im2 = img.copy()

            details = get_details(im2, contours)
            symbol_code = int(get_symbol_code(gray, resized_symbols_path))

            all_details = detail_entry(col_headers, details, symbol_code)

            details_list.append(all_details)

        print("Successfully entered details!")
    else:
        print(f"Entering device details...")

        for image in tqdm(os.listdir(images_path)):
            img = cv2.imread(os.path.join(images_path, image))
            img = cv2.resize(img, (1426, 774))
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

            contours = get_image_contours(gray)

            im2 = img.copy()

            details = get_details(im2, contours)
            symbol_code = int(get_symbol_code(gray, resized_symbols_path))

            all_details = detail_entry(col_headers, details, symbol_code)

            details_list.append(all_details)

        print("Successfully entered details!")

    details_file = pd.DataFrame(details_list)

    if format == ".xlsx":
        print(f"Exporting {excel_path}...")
        details_file.to_excel(excel_path, index=None, header=False)
    else:
        print(f"Exporting {csv_path}...")
        details_file.to_csv(csv_path, index=None, header=False)


if __name__ == '__main__':

    # symbol_resize()

    format = input("Enter file format (.csv or .xlsx): ")
    create_file(format=format, pdf=True)
