import cv2
import math
import numpy as np
import random

from .vigenere import Vigenere
from pathlib import Path
import ntpath

from main import Ui_MainWindow
from PyQt5 import QtCore, QtWidgets, QtGui

class imageLSB():
    def __init__(self):
        self.mask_one = [1, 2, 4, 8, 16, 32, 64, 128]
        self.mask_or = self.mask_one.pop(0)

        self.mask_zero = [254, 253, 251, 247, 239, 223, 191, 127]
        self.mask_and = self.mask_zero.pop(0)

        self.curr_pos = 0
        self.curr_channel = 0

        self.encrypted = False
        self.randomized = False

    def reset(self):
        self.mask_one = [1, 2, 4, 8, 16, 32, 64, 128]
        self.mask_or = self.mask_one.pop(0)

        self.mask_zero = [254, 253, 251, 247, 239, 223, 191, 127]
        self.mask_and = self.mask_zero.pop(0)

        self.curr_pos = 0
        self.curr_channel = 0

    def readImage(self, filename):
        self.reset()

        try:
            image = cv2.imread(filename)

            self.path = filename

            self.image = image
            self.height, self.width, self.channels = image.shape
            self.size = self.width * self.height
            self.map = list(range(self.size))
        except Exception as exception:
            return 'FAILED'

    def writeImage(self, filename):
        cv2.imwrite(filename, self.image)

    def get_xy(self, z):
        x = z // self.width
        y = z % self.width

        return x, y

    def next_pos(self):
        if (self.curr_channel == (self.channels - 1)):
            self.curr_channel = 0

            if (self.curr_pos == (len(self.map) - 1)):
                self.curr_pos = 0

                if (self.mask_or == 128):
                    return 'FAILED'
                else:
                    self.mask_or = self.mask_one.pop(0)
                    self.mask_and = self.mask_zero.pop(0)
            else:
                self.curr_pos += 1
        else:
            self.curr_channel += 1

    def read_bit(self):
        x, y = self.get_xy(self.map[self.curr_pos])
        val = self.image[x, y][self.curr_channel]
        val = int(val) & self.mask_or

        self.next_pos()

        if (val > 0):
            return 1
        else:
            return 0

    def read_bits(self, N):
        bits = 0

        for i in range(N):
            bits = (bits << 1) | self.read_bit()

        return bits

    def put_value(self, bits):
        for b in bits:
            x, y = self.get_xy(self.map[self.curr_pos])
            val = list(self.image[x, y])

            if (int(b) == 1):
                val[self.curr_channel] = int(val[self.curr_channel]) | self.mask_or
            else:
                val[self.curr_channel] = int(val[self.curr_channel]) & self.mask_and

            self.image[x, y] = tuple(val)
            self.next_pos()

    def embed(self, path, output = None):
        key = self.key_input_text.text()
        mbit = self.bit_input_text.text()

        if (mbit == ''):
            mbit = 8
        else:
            mbit = int(mbit)

            if ((mbit < 1) or (mbit > 8)):
                mbit = 8

        print('mbit:', mbit)

        filename = path.split('/')[-1]
        filedata = len(filename)
        content = open(path, 'rb').read()
        data = len(content)

        if ((not self.randomized) and ((self.width * self.height * self.channels) < round(8 * (filedata + data + 96) / mbit))):
            return 'FAILED'
        elif ((self.randomized) and ((self.width * self.height * self.channels) < round(8 * (filedata + data + 128) / mbit))):
            return 'FAILED'

        if (self.encrypted):
            vig = Vigenere(key)
            content = vig.encryptFile(path)
            self.put_value(format(22, '08b'))
        else:
            self.put_value(format(11, '08b'))

        if (self.randomized):
            self.put_value(format(22, '08b'))
        else:
            self.put_value(format(11, '08b'))

        if (self.randomized):
            seed = sum(ord(k) for k in key)
            random.seed(seed)

            for i in range(16):
                self.map.pop(0)

            random.shuffle(self.map)

        self.put_value(format(filedata, '016b'))
        self.put_value(format(data, '064b'))

        for byte in filename:
            self.put_value(format(ord(byte), '08b'))

        for byte in content:
            self.put_value(format(int(byte), '08b'))

        old_filename = ntpath.basename(self.path).split('.')

        if (output == None):
            output = str(Path(self.path).parent) + '/' + old_filename[0] + '_embedded.' + old_filename[1]
            print('output', output)
            self.writeImage(output)
        else:
            output += '.' + old_filename[1]
            print('output', output)
            self.writeImage(output)

        return output

    def extract(self, output = None):
        key = self.key_input_text.text()

        encrypted = self.read_bits(8)
        randomized = self.read_bits(8)
        seed = sum(ord(k) for k in key)

        if (randomized == 22):
            random.seed(seed)

            for i in range(16):
                self.map.pop(0)

            random.shuffle(self.map)

        filedata = self.read_bits(16)
        filename = bytearray()

        data = self.read_bits(64)
        content = bytearray()

        for byte in range(filedata):
            filename.extend([self.read_bits(8)])

        for byte in range(data):
            content.extend([self.read_bits(8)])

        filename = filename.decode()
        old_filename = filename.split('.')

        if (output == None):
            output = str(Path(self.path).parent) + '/' + old_filename[0] + '_extracted.' + old_filename[1]

            with open(output, 'wb') as f:
                f.write(content)

            if (encrypted == 22):
                vig = Vigenere(key)
                vig.decryptFile(output, output)
        else:
            output += '.' + old_filename[1]

            with open(output, 'wb') as f:
                f.write(content)

            if (encrypted == 22):
                vig = Vigenere(key)
                vig.decryptFile(output, output)

        return output

    @staticmethod
    def psnr(image_one, image_two):
        real = cv2.imread(image_one)
        embedded = cv2.imread(image_two)

        mse = np.mean((real - embedded) ** 2)

        if (mse == 0):
            return 100

        max_pixel = 256.0
        psnr = 20 * math.log10(max_pixel / math.sqrt(mse))

        return psnr

    def render(self, window:Ui_MainWindow):
        self.image_lsb_widget = QtWidgets.QWidget(window.option_frame)
        self.image_lsb_widget.setObjectName("image_lsb_widget")
        self.verticalLayout_6 = QtWidgets.QVBoxLayout(self.image_lsb_widget)
        self.verticalLayout_6.setObjectName("verticalLayout_6")
        self.widget = QtWidgets.QWidget(self.image_lsb_widget)
        self.widget.setObjectName("widget")
        self.horizontalLayout_5 = QtWidgets.QHBoxLayout(self.widget)
        self.horizontalLayout_5.setObjectName("horizontalLayout_5")
        self.groupBox = QtWidgets.QGroupBox(self.widget)
        self.groupBox.setObjectName("groupBox")
        self.verticalLayout_2 = QtWidgets.QVBoxLayout(self.groupBox)
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.encryption_checkbox = QtWidgets.QCheckBox(self.groupBox)
        self.encryption_checkbox.setObjectName("encryption_checkbox")
        self.verticalLayout_2.addWidget(self.encryption_checkbox)
        self.horizontalLayout_5.addWidget(self.groupBox)
        self.groupBox_3 = QtWidgets.QGroupBox(self.widget)
        self.groupBox_3.setObjectName("groupBox_3")
        self.verticalLayout_4 = QtWidgets.QVBoxLayout(self.groupBox_3)
        self.verticalLayout_4.setObjectName("verticalLayout_4")
        self.randomized_checkbox = QtWidgets.QCheckBox(self.groupBox_3)
        self.randomized_checkbox.setObjectName("randomized_checkbox")
        self.verticalLayout_4.addWidget(self.randomized_checkbox)
        self.horizontalLayout_5.addWidget(self.groupBox_3)
        self.verticalLayout_6.addWidget(self.widget)
        self.groupBox_2 = QtWidgets.QGroupBox(self.image_lsb_widget)
        self.groupBox_2.setObjectName("groupBox_2")
        self.verticalLayout = QtWidgets.QVBoxLayout(self.groupBox_2)
        self.verticalLayout.setObjectName("verticalLayout")
        self.bit_input_text = QtWidgets.QLineEdit(self.groupBox_2)
        self.bit_input_text.setObjectName("bit_input_text")
        self.verticalLayout.addWidget(self.bit_input_text)
        self.verticalLayout_6.addWidget(self.groupBox_2)
        self.groupBox_4 = QtWidgets.QGroupBox(self.image_lsb_widget)
        self.groupBox_4.setObjectName("groupBox_4")
        self.horizontalLayout_2 = QtWidgets.QHBoxLayout(self.groupBox_4)
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.key_input_text = QtWidgets.QLineEdit(self.groupBox_4)
        self.key_input_text.setObjectName("key_input_text")
        self.horizontalLayout_2.addWidget(self.key_input_text)
        self.verticalLayout_6.addWidget(self.groupBox_4)
        window.horizontalLayout_4.addWidget(self.image_lsb_widget)

        self.retranslateUi()

        self.key_input_text.setMaxLength(25)
        self.onlyInt = QtGui.QIntValidator(1, 7)
        self.bit_input_text.setValidator(self.onlyInt)
        self.bit_input_text.setMaxLength(1)
        self.encryption_checkbox.stateChanged.connect(self.enable_encrypted)
        self.randomized_checkbox.stateChanged.connect(self.enable_randomized)

    def retranslateUi(self):
        _translate = QtCore.QCoreApplication.translate
        self.groupBox.setTitle(_translate("MainWindow", "Encryption"))
        self.encryption_checkbox.setText(_translate("MainWindow", "Enable"))
        self.groupBox_3.setTitle(_translate("MainWindow", "Random"))
        self.randomized_checkbox.setText(_translate("MainWindow", "Randomized Pixel"))
        self.groupBox_2.setTitle(_translate("MainWindow", "m-bit (1 <= m <= 8)"))
        self.groupBox_4.setTitle(_translate("MainWindow", "Key"))

    def enable_encrypted(self, state):
        self.encrypted = bool(state)

    def enable_randomized(self, state):
        self.randomized = bool(state)


if __name__ == '__main__':
    print('<<<<< embed >>>>>>')
    lsbe = imageLSB()
    lsbe.readImage('test/image/input.png')
    res_encode = lsbe.embed(path = 'test/image/test.txt', output = 'result/image/resLSB.png')
    # lsbe.readImage('test/image/input.bmp')
    # res_encode = lsbe.embed(path = 'test/image/test.txt', output = 'result/image/resLSB.bmp')
    # res_encode = lsbe.embed(path = 'test/image/mask.png', output = 'result/image/resLSB.bmp')
    print('embed filename :', res_encode)

    print('<<<<< extract >>>>>>')
    lsbd = imageLSB()
    lsbd.readImage('result/image/resLSB.png')
    # lsbd.readImage('result/image/resLSB.bmp')

    res_decode = lsbd.extract(output = 'result/image/test.txt')
    print('extract filename :', res_decode)

    print('<<<<< psnr >>>>>>')
    lsb = imageLSB()
    image_one = cv2.imread('test/image/input.png')
    image_two = cv2.imread('result/image/resLSB.png')
    # image_one = cv2.imread('test/image/input.bmp')
    # image_two = cv2.imread('result/image/resLSB.bmp')
    print('psnr :', lsb.psnr(image_one, image_two))