# coding=utf-8

from packages import *
import cfg


class messageHandler(QMessageBox):
    def __init__(self, title="", text="", traceback=""):
        super(messageHandler, self).__init__()
        self.title_ = title
        self.text_ = text
        self.message = traceback

    def showwarning(self):
        self.setWindowTitle(self.title_)
        self.setWindowIcon(QIcon(cfg.icon1))
        self.setIcon(QMessageBox.Warning)
        self.setStandardButtons(QMessageBox.Ok)
        self.setAttribute(Qt.WA_DeleteOnClose)
        self.setFont(QFont("ZHSRXT-GBK", 12))
        self.setText(self.text_ + str(self.message))
        self.exec_()

    def showinfo(self):
        self.setWindowTitle(self.title_)
        self.setWindowIcon(QIcon(cfg.icon1))
        self.setIcon(QMessageBox.Information)
        self.setStandardButtons(QMessageBox.Ok)
        self.setAttribute(Qt.WA_DeleteOnClose)
        self.setFont(QFont("ZHSRXT-GBK", 12))
        self.setText(self.text_ + str(self.message))
        self.exec_()
