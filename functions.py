# coding=utf-8

from pypdf import PdfReader, PdfMerger
from PIL import Image, ImageFilter
from pillow_heif import register_heif_opener
from PySide2.QtCore import QRunnable

import os
import fitz
import cgitb
import io
import convert_gui

cgitb.enable(format="text")

ERROR_CODE = ""
DONE_CODE = ""

def ErrorReturn():
    global ERROR_CODE
    ERROR_CODE_ = ERROR_CODE
    ERROR_CODE = ""
    return ERROR_CODE_

def DoneReturn():
    global DONE_CODE
    DONE_CODE_ = DONE_CODE
    DONE_CODE = ""
    return DONE_CODE_


class FunctionsHandler(QRunnable):

    def __init__(self, function=None, files=None, output="", allpage=False, pagenum=1, format_="JPEG", size=(),
                 quality=80, sharpen=False, optimize=False, dpi_ori=False,
                 dpi_custom=(96, 96), usr_pwd="", own_pwd=""):
        super().__init__()

        self.function_: int
        self.files: str
        self.dpi_ori: bool
        self.optimize_: bool
        self.sharpen_: bool
        self.format_: str
        self.quality_: int
        self.size_: tuple
        self.dpi_custom_: tuple
        self.page_all: bool
        self.page_num: int
        self.usr_pwd: str
        self.own_pwd: str

        self.all_page = allpage
        self.page_num = pagenum
        self.format_ = format_
        self.size_ = size
        self.quality_ = quality
        self.quality_default = 80
        self.sharpen_ = sharpen
        self.optimize_ = optimize
        self.dpi_ori = dpi_ori
        self.dpi_custom = dpi_custom
        self.dpi_default = (96, 96)

        self.function_ = function
        self.files = files
        self.out_dir = output

        self.usr_pwd = usr_pwd
        self.own_pwd = own_pwd

        self.dic = {
            "JPEG": ".jpeg",
            "PNG": ".png",
            "TIFF": ".tiff",
            "WEBP": ".webp",
            "BMP": ".bmp",
            "ICO": ".ico"
        }

        self.data = convert_gui.Converter().data

    def run(self):
        global ERROR_CODE, DONE_CODE
        # if not self.files:
        #     return
        # if not type(self.files) is str:
        #     return

        try:
            if self.function_ == 1:
                self.extract_image(self.files)

            elif self.function_ == 2:
                self.extract_text(self.files)

            elif self.function_ == 4:
                self.encrypt(self.files)

            elif self.function_ == 5:
                self.decrypt(self.files)

            elif self.function_ == 6:
                self.convert_image(self.files)

        except Exception as e:
            ERROR_CODE = e
            print(e)

    def img_pdf(self, files, save_name):
        register_heif_opener()
        global ERROR_CODE, DONE_CODE
        ls = []
        if not files:
            return

        try:
            for i in range(1, len(files)):
                image = Image.open(files[i])
                # ls.append(image.convert("RGB"))
                ls.append(image)
            im = Image.open(files[0])
            if files.__len__() > 1:
                im.save(save_name, format="PDF", save_all=True, append_images=ls)
            else:
                im.save(save_name, format="PDF")

            DONE_CODE = save_name
            print(DONE_CODE)

        except Exception as e:
            ERROR_CODE = e
            print(e)

    def extract_image(self, path):
        global ERROR_CODE, DONE_CODE
        # print(self.out_dir)
        count = 0
        reader = PdfReader(path)
        page_num = len(reader.pages)
        name = os.path.splitext(os.path.basename(path))[0]
        try:
            if self.all_page:
                for i in range(page_num):
                    page = reader.pages[i]
                    image = page.images
                    # print(image)
                    for j in image:
                        # print(j.data)
                        image = Image.open(io.BytesIO(j.data))
                        # with open(f"{name}_image_{i + 1}" + ".png", "wb") as fp:
                        #     fp.write(j.data)
                        byte = io.BytesIO()
                        image.save(byte, format=self.format_)
                        # print(byte.tell())
                        image.save(os.path.join(self.out_dir, f"{name}_image_{i + 1}" + self.dic[self.format_]))
            else:
                num = self.page_num - 1
                page = reader.pages[num]
                image = page.images
                for i in image:
                    # with open(i.name + str(count), "wb") as fp:
                    #     fp.write(i.data)
                    count += 1

                    image = Image.open(io.BytesIO(i.data))
                    byte = io.BytesIO()
                    image.save(byte, format=self.format_)
                    # print(byte.tell())
                    image.save(os.path.join(self.out_dir, f"{name}_image_{count}" + self.dic[self.format_]))

            DONE_CODE = self.out_dir

        except Exception as e:
            ERROR_CODE = e
            print(e)

    def extract_text(self, path):
        global ERROR_CODE, DONE_CODE
        texts = []
        reader = PdfReader(path)
        page_num = len(reader.pages)
        name = os.path.splitext(os.path.basename(path))[0]

        try:
            if self.all_page:
                for i in range(page_num):
                    page = reader.pages[i]
                    text = page.extract_text()
                    # print(text)
                    texts.append(text)
                    # print(texts)
                    # for j in image:
                if os.path.exists(f"{name}.txt"):
                    os.remove(f"{name}.txt")
                for j in range(len(texts)):
                    with open(os.path.join(self.out_dir, f"{name}" + ".txt"), "a", encoding="utf-8") as fp:
                        fp.write(texts[j])

            else:
                page = reader.pages[self.page_num - 1]
                text = page.extract_text()
                with open(os.path.join(f"{name}_page_{self.page_num}" + ".txt"), "w", encoding="utf-8") as fp:
                    fp.write(text)

            DONE_CODE = self.out_dir

        except Exception as e:
            ERROR_CODE = e
            print(e)

    def merge(self, files, save_name):
        global ERROR_CODE, DONE_CODE
        if not files:
            return

        merger = PdfMerger()

        for pdf in files:
            merger.append(pdf)

        try:
            merger.write(save_name)
            merger.close()

            DONE_CODE = str(save_name)

        except Exception as e:
            ERROR_CODE = e
            print(e)

    def encrypt(self, path):
        global DONE_CODE, ERROR_CODE, pdf

        try:
            pdf = fitz.open(path)

        except Exception as e:
            ERROR_CODE = e
            print(e)

        encr_method = fitz.PDF_ENCRYPT_AES_256

        perm = (fitz.PDF_PERM_ACCESSIBILITY
                | fitz.PDF_PERM_PRINT
                | fitz.PDF_PERM_COPY
                | fitz.PDF_PERM_ANNOTATE
                )

        name = os.path.splitext(os.path.basename(path))[0]

        encrypted_file = os.path.join(self.out_dir, f"{name}_encrypted.pdf")

        # if os.path.exists(encrypted_file):
        #     os.remove(encrypted_file)

        try:
            if (self.usr_pwd or self.own_pwd) == "":
                return
            pdf.save(encrypted_file,
                     owner_pw=self.own_pwd,
                     user_pw=self.usr_pwd,
                     encryption=encr_method,
                     permissions=perm
                     )

            DONE_CODE = self.out_dir

        except Exception as e:
            ERROR_CODE = e
            print(e)

    def decrypt(self, path):
        global owner_pwd, ERROR_CODE, DONE_CODE, pdf

        name = os.path.splitext(os.path.basename(path))[0]

        try:
            pdf = fitz.open(path)

        except Exception as e:
            ERROR_CODE = e
            print(e)

        if self.own_pwd == "":
            return

        if pdf.needs_pass:
            owner_pwd = self.own_pwd

        rc = pdf.authenticate(owner_pwd)
        if rc not in (1, 4, 6):
            ERROR_CODE = "WRONG PWD"
            return

        decrypted_file = os.path.join(self.out_dir, f"{name}_decrypted.pdf")

        encr_method = fitz.PDF_ENCRYPT_NONE
        try:
            pdf.save(decrypted_file,
                     encryption=encr_method,
                     )

            DONE_CODE = self.out_dir

        except Exception as e:
            ERROR_CODE = e
            print(e)

    def convert_image(self, path):
        global image, format_, dpi, size_, quality, ERROR_CODE, DONE_CODE
        register_heif_opener()

        name = os.path.splitext(os.path.basename(path))[0]
        image = Image.open(path)
        if self.format_ == "PNG":
            format_ = self.dic["PNG"]
        elif self.format_ == "JPEG":
            format_ = self.dic["JPEG"]
            image = image.convert("RGB")
        elif self.format_ == "BMP":
            format_ = self.dic["BMP"]
        elif self.format_ == "TIFF":
            format_ = self.dic["TIFF"]
        elif self.format_ == "WEBP":
            format_ = self.dic["WEBP"]
        elif self.format_ == "ICO":
            format_ = self.dic["ICO"]
            if self.size_:
                size_ = self.size_
                try:
                    image = image.resize(size_)
                except Exception as e:
                    ERROR_CODE = e
                    print(e)
            else:
                try:
                    image = image.resize((32, 32))
                    size_ = (32, 32)
                except Exception as e:
                    ERROR_CODE = e
                    print(e)

        else:
            format_ = self.dic["JPEG"]
            image = image.convert("RGB")

        if self.sharpen_:
            image = image.filter(ImageFilter.SHARPEN)

        if self.dpi_ori:
            try:
                if "dpi" in image.info:
                    dpi = image.info['dpi']
                    print(dpi)

                else:
                    print("dpi not found")
                    dpi = self.dpi_default

            except Exception as e:
                ERROR_CODE = e
                print(e)

        else:
            dpi = self.dpi_custom

        if self.quality_ == 0 or self.quality_ == 80:
            quality = self.quality_default
        else:
            quality = self.quality_

        # byte = io.BytesIO()
        save_name = os.path.join(self.out_dir, str(name) + format_)

        try:
            if self.format_ == "ICO":
                image.save(save_name, bitmap_format="bmp", sizes=[size_])

            else:
                image.save(save_name, format=self.format_, quality=quality, dpi=dpi, optimize=self.optimize_)

            DONE_CODE = self.out_dir

        except Exception as e:
            ERROR_CODE = e
            print(e)

        # image.save(byte, format="BMP", quality=self.quality_, optimize=self.optimize_, bitmap_format="bmp")
        # for i in range(byte.tell() + 1):
        #     # print(i)
        #     if i < byte.tell():
        #         continue
        #
        #     print("done")
        #
        # print("total: " + str(byte.tell() / 1024))


# IMG2PDF = 0
PDF2IMAGE = 1
PDF2TEXT = 2
# MERGEPDF = 3
ENCRYPTION = 4
DECRYPTION = 5
IMG2IMG = 6
