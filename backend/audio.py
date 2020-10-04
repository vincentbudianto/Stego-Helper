import wave
import random
import numpy as np
import math
import os

from .vigenere import Vigenere
from pathlib import Path
import ntpath

from main import Ui_MainWindow
from PyQt5 import QtCore, QtWidgets, QtGui

def save_file(path, content):
    print(path)
    new_file = open(path, "wb")
    new_file.write(content)
    new_file.close()

class Audio():
    def __init__(self):
        self.reset()
        self.counter = 0

        self.key = ""
        self.is_encrypted = False
        self.is_randomized = False
        self.last_bit_count = 1

    def reset(self):
        self.mask_one = [1, 2, 4, 8, 16]
        self.mask_or = self.mask_one.pop(0)
        self.mask_zero = [254, 253, 251, 247, 239]
        self.mask_and = self.mask_zero.pop(0)
        self.curr_byte = 0

    def read_container_file(self, container_file_path):
        self.reset()
        self.counter = 0
        self.container_file_path = container_file_path
        self.container_file_audio = wave.open(self.container_file_path, "r")
        self.container_file_params = self.container_file_audio.getparams()
        self.container_file_length = self.container_file_audio.getnframes()
        self.container_file_bytes = bytearray(list(self.container_file_audio.readframes(self.container_file_length)))
        self.container_file_length = len(self.container_file_bytes)
        print(self.container_file_length)

    def read_input_file(self, input_file_path):
        self.input_file_path = input_file_path
        self.input_file_name = ntpath.basename(input_file_path)
        self.input_file_bytes = open(self.input_file_path, "rb").read()

    def next_pos(self):
        if (self.curr_byte == (self.container_file_length - 1)):
            self.curr_byte = 0

            if (self.mask_or == 16):
                raise Exception("No available pixels remaining")
            else:
                self.mask_or = self.mask_one.pop(0)
                self.mask_and = self.mask_zero.pop(0)

        else:
            self.curr_byte += 1

    def read_bit(self):
        val = self.container_file_bytes[self.byte_map[self.curr_byte]]
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
            if (int(b) == 1):
                self.container_file_bytes[self.byte_map[self.curr_byte]] = self.container_file_bytes[self.byte_map[self.curr_byte]] | self.mask_or
            else:
                self.container_file_bytes[self.byte_map[self.curr_byte]] = self.container_file_bytes[self.byte_map[self.curr_byte]] & self.mask_and

            self.next_pos()

    def embedding(self, output_file_name=None):
        self.key = self.lineEdit.text()
        last_bit_count = self.lastBitEdit.text()

        if last_bit_count == '':
            last_bit_count = 1
        else:
            last_bit_count = int(last_bit_count)
            if (last_bit_count < 1) or (last_bit_count > 4):
                last_bit_count = 1

        inputfilename_size = len(self.input_file_name)
        inputfile_size = len(self.input_file_bytes)

        print("Preparing Byte Map")
        self.byte_map = list(range(self.container_file_length))

        filename = self.input_file_name
        content = self.input_file_bytes

        # Limiting LSB into last n bits
        if self.container_file_length < round(8 * (144 + inputfilename_size + inputfile_size) / last_bit_count):
            return 'FAILED'

        if self.is_encrypted:
            print("Encrypting")
            vig = Vigenere(self.key)
            content = vig.encryptFile(self.input_file_path)
            self.put_value(format(22, '08b'))
        else:
            self.put_value(format(11, '08b'))

        if self.is_randomized:
            self.put_value(format(22, '08b'))
        else:
            self.put_value(format(11, '08b'))

        # Randomizing bits
        if self.is_randomized:
            print("Randomizing bytes")
            total_ASCII = 0
            for word in self.key:
                total_ASCII += ord(word)
            for i in range(16):
                test = self.byte_map.pop(0)
            random.seed(total_ASCII)
            random.shuffle(self.byte_map)
            for i in range(15, -1, -1):
                self.byte_map.insert(0, i)

        self.put_value(format(inputfilename_size, '064b'))
        self.put_value(format(inputfile_size, '064b'))

        print("Embedding")

        for byte in filename:
            self.put_value(format(ord(byte), '08b'))

        for byte in content:
            self.put_value(format(int(byte), '08b'))

        ### WRITE FILES ###
        print("Writing output")
        output_file_path = output_file_name
        if output_file_path == None:
            old_filename = ntpath.basename(self.container_file_path).split('.')
            output_file_path = str(Path(self.container_file_path).parent) + '/' + old_filename[0] + '_embedded.' + old_filename[1]
        else:
            splitted_decoded = self.container_file_path.split('.')
            output_file_path = output_file_path + '.' + splitted_decoded[1]
        self.encrypted_file_path = output_file_path
        with wave.open(output_file_path, 'wb') as wav_file:
            wav_file.setparams(self.container_file_params)
            wav_file.writeframes(self.container_file_bytes)
            wav_file.close()

        return output_file_path

    def extract(self, output_file_name=None):
        self.key = self.lineEdit.text()

        print("Preparing Byte Map")
        self.byte_map = list(range(self.container_file_length))

        is_encrypted = self.read_bits(8)
        is_randomized = self.read_bits(8)

        print("Is encrypted:", is_encrypted)
        print("Is randomized:", is_randomized)

        if (is_randomized == 22):
            print("Randomizing bytes")
            total_ASCII = 0
            for word in self.key:
                total_ASCII += ord(word)
            for i in range(16):
                test = self.byte_map.pop(0)
            random.seed(total_ASCII)
            random.shuffle(self.byte_map)
            for i in range(15, -1, -1):
                self.byte_map.insert(0, i)

        filename_size = self.read_bits(64)
        content_size = self.read_bits(64)
        print('key', self.key)
        print('byte map', len(self.byte_map))
        print('filename_size', filename_size)
        print('content_size', content_size)

        print("Extracting")

        filename = bytearray()
        for i in range(filename_size):
            filename.extend([self.read_bits(8)])

        content = bytearray()
        for i in range(content_size):
            content.extend([self.read_bits(8)])

        ### WRITE FILES ###
        print("Writing output")
        if output_file_name == None:
            output_file_name = filename.decode()
            output_file_name = str(Path(self.container_file_path).parent) + '/' + output_file_name
        else:
            splitted_decoded = filename.decode().split('.')
            output_file_name = output_file_name + '.' + splitted_decoded[1]

        output_file_path = output_file_name
        save_file(output_file_path, content)

        if (is_encrypted == 22):
            print("Decrypting")
            vig = Vigenere(self.key)
            vig.decryptFile(output_file_path, output_file_path)

        return output_file_path

    # UI
    def render(self, window: Ui_MainWindow):
        self.widget_3 = QtWidgets.QWidget(window.option_frame)
        self.widget_3.setObjectName("widget_3")
        self.verticalLayout_6 = QtWidgets.QVBoxLayout(self.widget_3)
        self.verticalLayout_6.setObjectName("verticalLayout_6")
        self.widget = QtWidgets.QWidget(self.widget_3)
        self.widget.setObjectName("widget")
        self.horizontalLayout_5 = QtWidgets.QHBoxLayout(self.widget)
        self.horizontalLayout_5.setObjectName("horizontalLayout_5")
        self.groupBox = QtWidgets.QGroupBox(self.widget)
        self.groupBox.setObjectName("groupBox")
        self.verticalLayout_2 = QtWidgets.QVBoxLayout(self.groupBox)
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.checkBox = QtWidgets.QCheckBox(self.groupBox)
        self.checkBox.setObjectName("checkBox")
        self.verticalLayout_2.addWidget(self.checkBox)
        self.horizontalLayout_5.addWidget(self.groupBox)
        self.groupBox_3 = QtWidgets.QGroupBox(self.widget)
        self.groupBox_3.setObjectName("groupBox_3")
        self.verticalLayout_4 = QtWidgets.QVBoxLayout(self.groupBox_3)
        self.verticalLayout_4.setObjectName("verticalLayout_4")
        self.checkBox_2 = QtWidgets.QCheckBox(self.groupBox_3)
        self.checkBox_2.setObjectName("checkBox_2")
        self.verticalLayout_4.addWidget(self.checkBox_2)
        self.horizontalLayout_5.addWidget(self.groupBox_3)
        self.verticalLayout_6.addWidget(self.widget)
        self.groupBox_5 = QtWidgets.QGroupBox(self.widget_3)
        self.groupBox_5.setObjectName("groupBox_5")
        self.horizontalLayout_3 = QtWidgets.QHBoxLayout(self.groupBox_5)
        self.horizontalLayout_3.setObjectName("horizontalLayout_3")
        self.lastBitEdit = QtWidgets.QLineEdit(self.groupBox_5)
        self.lastBitEdit.setObjectName("lastBitEdit")
        self.horizontalLayout_3.addWidget(self.lastBitEdit)
        self.verticalLayout_6.addWidget(self.groupBox_5)
        self.groupBox_4 = QtWidgets.QGroupBox(self.widget_3)
        self.groupBox_4.setObjectName("groupBox_4")
        self.horizontalLayout_2 = QtWidgets.QHBoxLayout(self.groupBox_4)
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.lineEdit = QtWidgets.QLineEdit(self.groupBox_4)
        self.lineEdit.setObjectName("lineEdit")
        self.horizontalLayout_2.addWidget(self.lineEdit)
        self.verticalLayout_6.addWidget(self.groupBox_4)
        window.horizontalLayout_4.addWidget(self.widget_3)

        self.retranslateUi()
        self.checkBox.stateChanged.connect(self.encrypted_mode)
        self.checkBox_2.stateChanged.connect(self.randomized_mode)

        self.lineEdit.setMaxLength(25)
        self.lastBitEdit.setMaxLength(1)
        self.only_int = QtGui.QIntValidator(1, 4)
        self.lastBitEdit.setValidator(self.only_int)
        self.checkBox.stateChanged.connect(self.enable_encrypted)
        self.checkBox_2.stateChanged.connect(self.enable_randomized)

    def retranslateUi(self):
        _translate = QtCore.QCoreApplication.translate
        self.groupBox.setTitle(_translate("MainWindow", "Encryption"))
        self.checkBox.setText(_translate("MainWindow", "Enable"))
        self.groupBox_3.setTitle(_translate("MainWindow", "Random"))
        self.checkBox_2.setText(_translate("MainWindow", "Randomized"))
        self.groupBox_5.setTitle(_translate("MainWindow", "m-bit (1 <= m <= 4)"))
        self.groupBox_4.setTitle(_translate("MainWindow", "Key"))

    def encrypted_mode(self, state):
        self.is_encrypted = bool(state)

    def randomized_mode(self, state):
        self.is_randomized = bool(state)

    def enable_encrypted(self, state):
        self.is_encrypted = bool(state)

    def enable_randomized(self, state):
        self.is_randomized = bool(state)

    @staticmethod
    def audio_psnr(original_file, embedded_file):
        file_original = wave.open(original_file, 'rb')
        file_original_bytes = file_original.readframes(file_original.getnframes())
        file_original.close()

        file_embedded = wave.open(embedded_file, 'rb')
        file_embedded_bytes = file_embedded.readframes(file_embedded.getnframes())
        file_embedded.close()

        original_bytes_int = []
        embedded_bytes_int = []
        for i in range(0, len(file_original_bytes)):
            original_bytes_int.append(int(file_original_bytes[i]))
            embedded_bytes_int.append(int(file_embedded_bytes[i]))

        # print(original_bytes_int)
        original_bytes_int = np.array(original_bytes_int)
        embedded_bytes_int = np.array(embedded_bytes_int)

        delta = np.sum(pow((original_bytes_int - embedded_bytes_int),2))
        mse = delta / len(file_original_bytes)

        if mse == 0:
            mse = 100

        psnr = 20 * math.log10(255 / math.sqrt(mse))
        return psnr


if __name__ == "__main__":
    audio = Audio()
    audio_execute = 'extract'
    if audio_execute == 'embedding':
        audio.read_container_file("./audiostore/container/weebs.wav")
        audio.read_input_file("./audiostore/input/weed.wav")
        audio.embedding('FUSRODAH', True, True, 'fusrodah.wav')
        print("Counting PSNR")
        print("PSNR =", audio_psnr(audio.container_file_path, audio.encrypted_file_path))
    else:
        audio.read_container_file("./audiostore/encrypted/fusrodah.wav")
        audio.extract('FUSRODAH', None)
    print("Done")