import math
import numpy as np
import random
import sys

from cv2 import cv2
from .vigenere import Vigenere

from main import Ui_MainWindow
from PyQt5 import QtCore, QtWidgets, QtGui

FLAG_TRUE = 22
FLAG_FALSE = 11
TOTAL_FLAG_BITS = 24

class AviVideo():
    def __init__(self):
        self.filename = ''
        self.frames = []
        self.fps = 0
        self.width = 0
        self.height = 0

    def setFilename(self, filename):
        self.filename = filename

    def getFilename(self):
        return self.filename

    def setFrames(self, frames):
        self.frames = frames

    def getFrames(self):
        return self.frames

    def setFps(self, fps):
        self.fps = fps

    def getFps(self):
        return self.fps

    def setWidth(self, width):
        self.width = width

    def getWidth(self):
        return self.width

    def setHeight(self, height):
        self.height = height

    def getHeight(self):
        return self.height

    def readVideo(self, filename_input):
        try:
            video = cv2.VideoCapture(filename_input)

            self.filename = filename_input
            self.fps = int(video.get(cv2.CAP_PROP_FPS))
            self.width = int(video.get(cv2.CAP_PROP_FRAME_WIDTH))
            self.height = int(video.get(cv2.CAP_PROP_FRAME_HEIGHT))

            frames = []
            while(video.isOpened()):
                success, frame = video.read()
                if (success):
                    frames.append(frame)
                else:
                    break

            video.release()
            self.frames = frames

        except Exception as exception:
            print(exception)
            print("Error while reading video file")

    def writeVideo(self, filename_output):
        if sys.platform == "win32":
            fourcc = cv2.VideoWriter_fourcc('R', 'G', 'B', 'A')     # 4-byte code used to specify the video codec.
        else:
            fourcc = cv2.VideoWriter_fourcc('M', 'P', 'N', 'G')     # 4-byte code used to specify the video codec.
            
        video_output = cv2.VideoWriter(filename_output, fourcc, self.fps, (self.width, self.height))
        for frame in self.frames:
            video_output.write(frame)
        video_output.release()
        return

class AviStegano():
    def __init__(self):
        self.reset_init()

    def reset_init(self):
        #Read aviVideo
        self.aviVideo = None
        self.frames = 0

        self.mask_one = [1, 2, 4, 8, 16, 32, 64, 128]
        self.mask_or = self.mask_one.pop(0)

        self.mask_zero = [254, 253, 251, 247, 239, 223, 191, 127]
        self.mask_and = self.mask_zero.pop(0)

        #Video Data Size
        self.frame_size = 0
        self.height_size = 0
        self.width_size = 0
        self.channel_size = 0

        #Pointer Map
        self.frame_map = []
        self.map = []

        self.curr_frame = 0
        self.curr_pos = 0
        self.curr_channel = 0
        self.skipped_frame = 0

        #Save initial frame
        self.initial_frames = []

        #Flag
        self.encryption = False
        self.randomized_frame = False
        self.randomized_pixel = False

    def readVideo(self, video_filename):
        self.reset_init()
        #Read aviVideo
        self.aviVideo = AviVideo()
        self.aviVideo.readVideo(video_filename)
        self.frames = self.aviVideo.getFrames()

        #Video Data Size
        self.frame_size = len(self.aviVideo.getFrames())
        self.height_size = self.aviVideo.getHeight()
        self.width_size = self.aviVideo.getWidth()
        self.channel_size = 3   #RGB

        #Pointer Map
        self.frame_map = list(range(self.frame_size))
        self.map = list(range(self.height_size * self.width_size))

        #Save initial frame
        self.initial_frames = []
        for i in range (self.frame_size):
            self.initial_frames.append(np.copy(self.frames[0]))

    def get_index(self, position):
        height_idx = position // self.width_size
        width_idx = position % self.width_size

        return height_idx, width_idx

    def next_pos(self):
        if (self.curr_channel == (self.channel_size - 1)):
            self.curr_channel = 0

            if (self.curr_pos == (len(self.map) - 1)):
                self.curr_pos = 0

                if (self.curr_frame == (self.frame_size - self.skipped_frame - 1)):
                    self.curr_frame = self.skipped_frame

                    if (self.mask_or == 128):
                        return 'FAILED'
                    else:
                        self.mask_or = self.mask_one.pop(0)
                        self.mask_and = self.mask_zero.pop(0)

                else:
                    self.curr_frame += 1
            else:
                self.curr_pos += 1
        else:
            self.curr_channel += 1

    def read_bit(self):
        height_idx, width_idx = self.get_index(self.map[self.curr_pos])

        val = self.frames[self.frame_map[self.curr_frame]][height_idx, width_idx, self.curr_channel]
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
            height_idx, width_idx = self.get_index(self.map[self.curr_pos])
            val = list(self.frames[self.frame_map[self.curr_frame]][height_idx, width_idx])

            if (int(b) == 1):
                val[self.curr_channel] = int(val[self.curr_channel]) | self.mask_or
            else:
                val[self.curr_channel] = int(val[self.curr_channel]) & self.mask_and

            self.frames[self.frame_map[self.curr_frame]][height_idx, width_idx] = tuple(val)
            self.next_pos()

    def embeed(self, message_file_name, output_filename):
        #Set AviStegano Metadata
        key = self.lineEdit.text()
        seed = sum(ord(k) for k in key)
        mbit = self.bit_input_text.text()

        if (mbit == ''):
            mbit = 7
        else:
            mbit = int(mbit)

            if ((mbit < 1) or (mbit > 7)):
                mbit = 7

        filedata = len(message_file_name)
        content = open(message_file_name, "rb").read()
        data = len(content)

        #Add Encryption Flag Bits
        if (self.encryption):
            print('Encrypting Message File')
            vig = Vigenere(key)
            content = vig.encryptFile(message_file_name)
            self.put_value(format(FLAG_TRUE, '08b'))
        else:
            self.put_value(format(FLAG_FALSE, '08b'))

        #Add Randomized Frame Flag Bits
        if (self.randomized_frame):
            self.put_value(format(FLAG_TRUE, '08b'))
        else:
            self.put_value(format(FLAG_FALSE, '08b'))

        #Add Randomized Pixel Flag Bits
        if (self.randomized_pixel):
            self.put_value(format(FLAG_TRUE, '08b'))
        else:
            self.put_value(format(FLAG_FALSE, '08b'))

        #If any random skip early frame
        if (self.randomized_frame or self.randomized_pixel):
            random.seed(seed)
            self.skipped_frame = self.curr_frame + 1

            for i in range (self.skipped_frame):
                self.frame_map.pop(0)

            #Reset index pointer
            self.curr_frame = 0
            self.curr_pos = 0
            self.curr_channel = 0

            if (self.randomized_frame):
                print('Randomized Frame')
                random.shuffle(self.frame_map)

            if (self.randomized_pixel):
                print('Randomized Pixel')
                random.shuffle(self.map)

        if (self.randomized_frame or self.randomized_pixel):
            if (((self.frame_size - self.skipped_frame) * self.width_size * self.height_size * self.channel_size) < round((8 * (filedata + data)) / mbit)):
                return 'FAILED'
        else:
            if ((self.frame_size * self.width_size * self.height_size * self.channel_size) < round((8 * (filedata + data + 104)) / mbit)):
                return 'FAILED'

        self.put_value(format(filedata, '016b'))
        self.put_value(format(data, '064b'))

        for byte in message_file_name:
            self.put_value(format(ord(byte), '08b'))
        for byte in content:
            self.put_value(format(int(byte), '08b'))

        self.aviVideo.setFrames(self.frames)
        self.aviVideo.writeVideo(output_filename)

        return output_filename

    def extract(self, filename_message_output = ''):
        key = self.lineEdit.text()

        encription = self.read_bits(8)
        print('encription', encription)
        randomized_frame = self.read_bits(8)
        print('randomized_frame', randomized_frame)
        randomized_pixel = self.read_bits(8)
        print('randomized_pixel', randomized_pixel)

        if (randomized_frame == 22 or randomized_pixel == 22):
            seed = sum(ord(k) for k in key)
            random.seed(seed)

            self.skipped_frame = (24 // (self.width_size * self.height_size * self.channel_size)) + 1

            #Reset index pointer
            self.curr_pos = 0
            self.curr_channel = 0
            self.curr_frame = 0

            for i in range (self.skipped_frame):
                self.frame_map.pop(0)

            if (randomized_frame == 22):
                print('Randomized Frame')
                random.shuffle(self.frame_map)

            if (randomized_pixel == 22):
                print('Randomized Pixel')
                random.shuffle(self.map)

        filedata = self.read_bits(16)
        filename = bytearray()

        print('filedata',filedata)

        data = self.read_bits(64)
        result = bytearray()
        print('data',data)

        for byte in range(filedata):
            filename.extend([self.read_bits(8)])

        for byte in range(data):
            result.extend([self.read_bits(8)])

        filepath = filename.decode()
        print('filepath', filepath)
        original_filename = filepath.split('/')[-1]
        print('original_filename', original_filename)

        if filename_message_output == '':
            video_path = self.aviVideo.filename.split('/')
            filename =  '/'.join(video_path[:-1]) + '/' + original_filename
        else:
            filename = filename_message_output + '.' + original_filename.split('.')[-1]

        print('filename', filename)

        with open(filename, "wb") as f:
            f.write(result)

        if (encription == 22):
            vig = Vigenere(key)
            vig.decryptFile(filename, filename)

        return filename

    def psnr(self):
        result = 0

        for i in range (self.frame_size):
            result += self.calculatePSNR(self.frames[i], self.initial_frames[i])

        return result / self.frame_size

    @staticmethod
    def calculatePSNR(frame_one, frame_two):
        mse = np.mean((frame_one - frame_two) ** 2)

        if(mse == 0):
            return 100

        max_pixel = 256.0
        psnr = 20 * math.log10(max_pixel / math.sqrt(mse))

        return psnr

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
        self.checkBox_3 = QtWidgets.QCheckBox(self.groupBox_3)
        self.checkBox_3.setObjectName("checkBox_3")
        self.verticalLayout_4.addWidget(self.checkBox_3)
        self.checkBox_2 = QtWidgets.QCheckBox(self.groupBox_3)
        self.checkBox_2.setObjectName("checkBox_2")
        self.verticalLayout_4.addWidget(self.checkBox_2)
        self.horizontalLayout_5.addWidget(self.groupBox_3)
        self.verticalLayout_6.addWidget(self.widget)
        self.groupBox_2 = QtWidgets.QGroupBox(self.widget_3)
        self.groupBox_2.setObjectName("groupBox_2")
        self.verticalLayout = QtWidgets.QVBoxLayout(self.groupBox_2)
        self.verticalLayout.setObjectName("verticalLayout")
        self.bit_input_text = QtWidgets.QLineEdit(self.groupBox_2)
        self.bit_input_text.setObjectName("bit_input_text")
        self.verticalLayout.addWidget(self.bit_input_text)
        self.verticalLayout_6.addWidget(self.groupBox_2)
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

        self.lineEdit.setMaxLength(25)
        self.onlyInt = QtGui.QIntValidator(1, 7)
        self.bit_input_text.setValidator(self.onlyInt)
        self.bit_input_text.setMaxLength(1)
        self.checkBox.stateChanged.connect(self.enable_encryption)
        self.checkBox_3.stateChanged.connect(self.enable_randomized_frame)
        self.checkBox_2.stateChanged.connect(self.enable_randomized_pixel)

    def retranslateUi(self):
        _translate = QtCore.QCoreApplication.translate
        self.groupBox.setTitle(_translate("MainWindow", "Encryption"))
        self.checkBox.setText(_translate("MainWindow", "Enable"))
        self.groupBox_3.setTitle(_translate("MainWindow", "Random"))
        self.checkBox_3.setText(_translate("MainWindow", "Randomized Frame"))
        self.checkBox_2.setText(_translate("MainWindow", "Randomized Pixel"))
        self.groupBox_2.setTitle(_translate("MainWindow", "m-bit (0 < m < 8)"))
        self.groupBox_4.setTitle(_translate("MainWindow", "Key"))

    def enable_encryption(self, state):
        self.encryption = bool(state)

    def enable_randomized_frame(self, state):
        self.randomized_frame = bool(state)

    def enable_randomized_pixel(self, state):
        self.randomized_pixel = bool(state)

# if __name__ == "__main__":
    # Embeed
    # example = AviStegano()
    # example.readVideo('test/video/result2.avi')
    # print(len(example.frames), example.frames[0].shape)

    # example.embeed('api.py', 'test/video/contoh.avi', 'stegano')
    # print(format(example.aviVideo.getFrames()[0][0,0,0], '08b'))
    # print(format(example.aviVideo.getFrames()[0][0,0,1], '08b'))
    # print(format(example.aviVideo.getFrames()[0][0,0,2], '08b'))
    # print(format(example.aviVideo.getFrames()[0][0,1,0], '08b'))
    # print(format(example.aviVideo.getFrames()[0][0,1,1], '08b'))
    # print(format(example.aviVideo.getFrames()[0][0,1,2], '08b'))
    # print(format(example.aviVideo.getFrames()[0][0,2,0], '08b'))
    # print(format(example.aviVideo.getFrames()[0][0,2,1], '08b'))
    # print()
    # print(format(example.aviVideo.getFrames()[0][0,2,2], '08b'))
    # print(format(example.aviVideo.getFrames()[0][0,3,0], '08b'))
    # print(format(example.aviVideo.getFrames()[0][0,3,1], '08b'))
    # print(format(example.aviVideo.getFrames()[0][0,3,2], '08b'))
    # print(format(example.aviVideo.getFrames()[0][0,4,0], '08b'))
    # print(format(example.aviVideo.getFrames()[0][0,4,1], '08b'))
    # print(format(example.aviVideo.getFrames()[0][0,4,2], '08b'))
    # print(format(example.aviVideo.getFrames()[0][0,5,0], '08b'))
    # print()
    # print(format(example.aviVideo.getFrames()[0][0,5,1], '08b'))
    # print(format(example.aviVideo.getFrames()[0][0,5,2], '08b'))
    # print(format(example.aviVideo.getFrames()[0][0,6,0], '08b'))
    # print(format(example.aviVideo.getFrames()[0][0,6,1], '08b'))
    # print(format(example.aviVideo.getFrames()[0][0,6,2], '08b'))
    # print(format(example.aviVideo.getFrames()[0][0,7,0], '08b'))
    # print(format(example.aviVideo.getFrames()[0][0,7,1], '08b'))
    # print(format(example.aviVideo.getFrames()[0][0,7,2], '08b'))

    # print(example.psnr())

    # Extract
    # contoh = AviStegano()
    # contoh.readVideo('test/video/contoh.avi')
    # print(contoh.frames[0].shape)
    # print(format(contoh.frames[0][0,0,0], '08b'))
    # print(format(contoh.frames[0][0,0,1], '08b'))
    # print(format(contoh.frames[0][0,0,2], '08b'))
    # print(format(contoh.frames[0][0,1,0], '08b'))
    # print(format(contoh.frames[0][0,1,1], '08b'))
    # print(format(contoh.frames[0][0,1,2], '08b'))
    # print(format(contoh.frames[0][0,2,0], '08b'))
    # print(format(contoh.frames[0][0,2,1], '08b'))
    # print()
    # print(format(contoh.frames[0][0,2,2], '08b'))
    # print(format(contoh.frames[0][0,3,0], '08b'))
    # print(format(contoh.frames[0][0,3,1], '08b'))
    # print(format(contoh.frames[0][0,3,2], '08b'))
    # print(format(contoh.frames[0][0,4,0], '08b'))
    # print(format(contoh.frames[0][0,4,1], '08b'))
    # print(format(contoh.frames[0][0,4,2], '08b'))
    # print(format(contoh.frames[0][0,5,0], '08b'))
    # print()
    # print(format(contoh.frames[0][0,5,1], '08b'))
    # print(format(contoh.frames[0][0,5,2], '08b'))
    # print(format(contoh.frames[0][0,6,0], '08b'))
    # print(format(contoh.frames[0][0,6,1], '08b'))
    # print(format(contoh.frames[0][0,6,2], '08b'))
    # print(format(contoh.frames[0][0,7,0], '08b'))
    # print(format(contoh.frames[0][0,7,1], '08b'))
    # print(format(contoh.frames[0][0,7,2], '08b'))
    # contoh.extract('stegano')
    # pass