import cv2
import math
import numpy as np
import random

from .messageBPCS import messageBPCS
from .vigenere import Vigenere

from main import Ui_MainWindow
from PyQt5 import QtCore, QtWidgets

class imageBPCS():
    def __init__(self):
        self.block_size = 8

        self.encrypted = False
        self.randomized = False

    def readImage(self, filename):
        try:
            image = cv2.imread(filename)

            self.image = image
            self.height, self.width, self.channels = image.shape
        except Exception as exception:
            # print(exception)
            # print('Error while reading image file')
            return 'FAILED - Error while reading image file'

    def writeImage(self, filename):
        cv2.imwrite(filename, self.image)

    def complexity(self, block):
        count = 0
        height, width = block.shape

        for h in range(height - 1):
            for w in range(width - 1):
                if (block[h][w] != block[h + 1][w]):
                    count += 1

                if (block[h][w] != block[h][w + 1]):
                    count += 1

        return count / 112

    def to_bitplane(self, block):
        result = []

        for i in reversed(range(8)):
            bit = (block / (2 ** i)).astype(int) % 2
            result.append(bit)

        return result

    def to_byte(self, bit, plane):
        if (plane == 0):
            result = bit[plane]
        else:
            result = 2 * self.to_byte(bit, (plane - 1)) + bit[plane]

        return result

    def from_bitplane(self, bitplane):
        return self.to_byte(bitplane, (len(bitplane) - 1))

    def embed(self, path, output = ''):
        key = self.key_input_text.text()
        threshold = self.threshold_input_text.text()

        if (self.encrypted):
            vig = Vigenere(key)
            content = vig.encryptFile(path)
        else:
            content = open(path, 'rb').read()

        filename = path.split('/')[-1]

        msg = messageBPCS(filename = filename, content = content, key = key, threshold = threshold, encrypted = self.encrypted, randomized = self.randomized, block_size = self.block_size)

        message = msg.set_message()

        if (((self.width // self.block_size) * (self.height // self.block_size) * self.channels) < len(message)):
            # raise Exception('Image is smaller than payload')
            return 'FAILED - Image is smaller than payload'

        i = 0

        while (i < len(message)):
            h = 0

            while ((h < (self.height - self.block_size + 1)) and (i < len(message))):
                w = 0

                while ((w < (self.width - self.block_size + 1)) and (i < len(message))):
                    block = self.image[h:(h + self.block_size), w:(w + self.block_size)]
                    blocks = cv2.split(block)
                    bitplane = [self.to_bitplane(block) for block in blocks]
                    j = 0

                    while ((j < len(bitplane)) and (i < len(message))):
                        k = 0

                        while ((k < len(bitplane[j])) and (i < len(message))):
                            if (self.complexity(bitplane[j][k]) >= threshold):
                                bitplane[j][k] = message[i]
                                i += 1

                            k += 1

                        j += 1

                    channel = [self.from_bitplane(plane) for plane in bitplane]
                    new_blocks = cv2.merge(channel)
                    self.image[h:(h + self.block_size), w:(w + self.block_size)] = new_blocks
                    w += self.block_size

                h += self.block_size

        if (output == ''):
            self.writeImage('result/image/embed_' + filename)
        else:
            self.writeImage(output)

        return output

    def extract(self, output = ''):
        key = self.key_input_text.text()
        threshold = self.threshold_input_text.text()

        msg = messageBPCS(key = key, threshold = threshold, block_size = self.block_size)
        message = []

        h = 0

        while (h < (self.height - self.block_size + 1)):
            w = 0

            while (w < (self.width - self.block_size + 1)):
                block = self.image[h:(h + self.block_size), w:(w + self.block_size)]
                blocks = cv2.split(block)
                bitplane = [self.to_bitplane(block) for block in blocks]
                j = 0

                while (j < len(bitplane)):
                    k = 0

                    while (k < len(bitplane[j])):
                        if (self.complexity(bitplane[j][k]) >= threshold):
                            message.append(bitplane[j][k])

                        k += 1

                    j += 1

                w += self.block_size

            h += self.block_size

        filename, content, encrypted = msg.get_message(message)

        if (output == ''):
            with open(('result/image/extracted_' + filename), 'wb') as f:
                f.write(content)

            if (encrypted):
                vig = Vigenere(key)
                vig.decryptFile(('result/image/extracted_' + filename), ('result/image/extracted_' + filename))
        else:
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
        self.image_bpcs_widget = QtWidgets.QWidget(window.option_frame)
        self.image_bpcs_widget.setObjectName("image_bpcs_widget")
        self.verticalLayout_6 = QtWidgets.QVBoxLayout(self.image_bpcs_widget)
        self.verticalLayout_6.setObjectName("verticalLayout_6")
        self.widget = QtWidgets.QWidget(self.image_bpcs_widget)
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
        self.groupBox_2 = QtWidgets.QGroupBox(self.image_bpcs_widget)
        self.groupBox_2.setObjectName("groupBox_2")
        self.verticalLayout = QtWidgets.QVBoxLayout(self.groupBox_2)
        self.verticalLayout.setObjectName("verticalLayout")
        self.threshold_input_text = QtWidgets.QLineEdit(self.groupBox_2)
        self.threshold_input_text.setObjectName("threshold_input_text")
        self.verticalLayout.addWidget(self.threshold_input_text)
        self.verticalLayout_6.addWidget(self.groupBox_2)
        self.groupBox_4 = QtWidgets.QGroupBox(self.image_bpcs_widget)
        self.groupBox_4.setObjectName("groupBox_4")
        self.horizontalLayout_2 = QtWidgets.QHBoxLayout(self.groupBox_4)
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.key_input_text = QtWidgets.QLineEdit(self.groupBox_4)
        self.key_input_text.setObjectName("key_input_text")
        self.horizontalLayout_2.addWidget(self.key_input_text)
        self.verticalLayout_6.addWidget(self.groupBox_4)
        window.horizontalLayout_4.addWidget(self.image_bpcs_widget)

        self.retranslateUi()

        self.encryption_checkbox.stateChanged.connect(self.enable_encrypted)
        self.randomized_checkbox.stateChanged.connect(self.enable_randomized)

    def retranslateUi(self):
        _translate = QtCore.QCoreApplication.translate
        self.groupBox.setTitle(_translate("MainWindow", "Encryption"))
        self.encryption_checkbox.setText(_translate("MainWindow", "Enable"))
        self.groupBox_3.setTitle(_translate("MainWindow", "Random"))
        self.randomized_checkbox.setText(_translate("MainWindow", "Randomized Pixel"))
        self.groupBox_2.setTitle(_translate("MainWindow", "Threshold (0.1 - 0.5)"))
        self.groupBox_4.setTitle(_translate("MainWindow", "Key"))

    def enable_encrypted(self, state):
        self.encrypted = bool(state)

    def enable_randomized(self, state):
        self.randomized = bool(state)

if __name__ == '__main__':
    print('<<<<< embed >>>>>>')
    bpcse = imageBPCS()
    bpcse.readImage('test/image/input.png')
    res_encode = bpcse.embed(path = 'test/image/secret.txt', output = 'result/image/resBPCS.png')
    # res_encode = bpcse.embed(path = 'test/image/mask.png', output = 'result/image/resBPCS.png')
    # bpcse.readImage('test/image/input.bmp')
    # res_encode = bpcse.embed(path = 'test/image/secret.txt', output = 'result/image/resBPCS.bmp')
    # res_encode = bpcse.embed(path = 'test/image/mask.png', output = 'result/image/resBPCS.bmp')
    print('embed filename :', res_encode)

    print('<<<<< extract >>>>>>')
    bpcsd = imageBPCS()
    bpcsd.readImage('result/image/resBPCS.png')
    # bpcsd.readImage('result/image/resBPCS.bmp')

    res_decode = bpcsd.extract(output = 'result/image/secret.txt')
    print('extract filename :', res_decode)

    print('<<<<< psnr >>>>>>')
    bpcs = imageBPCS()
    image_one = cv2.imread('test/image/input.png')
    image_two = cv2.imread('result/image/resBPCS.png')
    # image_one = cv2.imread('test/image/input.bmp')
    # image_two = cv2.imread('result/image/resBPCS.bmp')
    print('psnr :', bpcs.psnr(image_one, image_two))