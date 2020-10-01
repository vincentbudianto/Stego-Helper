import aviVideo
import math
import numpy as np
import random

from cv2 import cv2
from vigenere import Vigenere

class AviVideo:
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
        fourcc = cv2.VideoWriter_fourcc('M', 'P', 'N', 'G')     # 4-byte code used to specify the video codec.
        video_output = cv2.VideoWriter(filename_output, fourcc, self.fps, (self.width, self.height))
        for frame in self.frames:
            video_output.write(frame)
        video_output.release()
        return
    

class AviStegano():
    def __init__(self, filename_video, key, encryption=False, randomized=False):
        #Read aviVideo
        self.aviVideo = AviVideo()
        self.aviVideo.readVideo(filename_video)
        self.frames = self.aviVideo.getFrames()

        #Set AviStegano Metadata
        self.key = key
        self.seed = sum(ord(k) for k in key)
        self.encryption = encryption
        self.randomized = randomized
        
        self.mask_one = [1, 2, 4, 8, 16, 32, 64, 128]
        self.mask_or = self.mask_one.pop(0)

        self.mask_zero = [254, 253, 251, 247, 239, 223, 191, 127]
        self.mask_and = self.mask_zero.pop(0)

        #Video Data Size
        self.frame_size = len(self.aviVideo.getFrames())
        self.width_size = self.aviVideo.getWidth()
        self.height_size = self.aviVideo.getHeight()
        self.channel_size = 3   #RGB

        #Pointer Map
        self.frame_map = list(range(self.frame_size))
        self.height_map = list(range(self.height_size))
        self.width_map = list(range(self.width_size))

        self.curr_frame = 0
        self.curr_channel = 0
        self.curr_width = 0
        self.curr_height = 0

    def next_pos(self):
        if (self.curr_channel == (self.channel_size - 1)):
            self.curr_channel = 0

            if (self.curr_width == (self.width_size - 1)):
                self.curr_width = 0

                if (self.curr_height == (self.height_size - 1)):
                    self.curr_height = 0

                    if (self.curr_frame == (self.frame_size - 1)):
                        self.curr_frame = 0

                        if (self.mask_or == 128):
                            raise Exception('No available pixels remaining')
                        else:
                            self.mask_or = self.mask_one.pop(0)
                            self.mask_and = self.mask_zero.pop(0)
                    else:
                        self.curr_frame += 1
                else:
                    self.curr_height += 1
            else:
                self.curr_width += 1
        else:
            self.curr_channel += 1

    def read_bit(self):
        val = self.frames[self.frame_map[self.curr_frame]][self.height_map[self.curr_height], self.width_map[self.curr_width], self.curr_channel]
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
            val = list(self.frames[self.frame_map[self.curr_frame]][self.height_map[self.curr_height], self.width_map[self.curr_width]])

            if (int(b) == 1):
                val[self.curr_channel] = int(val[self.curr_channel]) | self.mask_or
            else:
                val[self.curr_channel] = int(val[self.curr_channel]) & self.mask_and

            self.frames[self.frame_map[self.curr_frame]][self.height_map[self.curr_height], self.width_map[self.curr_width]] = tuple(val)
            self.next_pos()

    def embeed(self, message_file_name, output_filename):
        filedata = len(message_file_name)
        content = open(message_file_name, "rb").read()
        data = len(content)

        if (self.frame_size * self.width_size * self.height_size * self.channel_size) < (filedata + data + 112):
            raise Exception('Image is smaller than payload')

        if (self.encryption):
            vig = Vigenere(self.key)
            content = vig.encryptFile(message_file_name)
            self.put_value(format(22, '08b'))
        else:
            self.put_value(format(11, '08b'))

        if (self.randomized):
            self.put_value(format(22, '08b'))
        else:
            self.put_value(format(11, '08b'))

        if (self.randomized):
            random.seed(self.seed)

            for i in range(24):
                self.frame_map.pop(0)
                self.height_map.pop(0)
                self.width_map.pop(0)

            random.shuffle(self.frame_map)
            random.shuffle(self.height_map)
            random.shuffle(self.width_map)

        self.put_value(format(filedata, '032b'))
        self.put_value(format(data, '064b'))

        for byte in message_file_name:
            self.put_value(format(ord(byte), '08b'))
        for byte in content:
            self.put_value(format(int(byte), '08b'))

        self.aviVideo.setFrames(self.frames)
        self.aviVideo.writeVideo(output_filename)

    def extract(self):
        encription = self.read_bits(8)
        randomized = self.read_bits(8)

        # print(encription)
        if (randomized == 22):
            print('randomized')
            random.seed(self.seed)

            for i in range(24):
                self.frame_map.pop(0)
                self.height_map.pop(0)
                self.width_map.pop(0)

            random.shuffle(self.frame_map)
            random.shuffle(self.height_map)
            random.shuffle(self.width_map)

        filedata = self.read_bits(32)
        filename = bytearray()

        data = self.read_bits(64)
        result = bytearray()

        for byte in range(filedata):
            filename.extend([self.read_bits(8)])

        for byte in range(data):
            result.extend([self.read_bits(8)])

        filename = 'extracted_' + filename.decode()

        with open(filename, "wb") as f:
            f.write(result)

        if (encription == 22):
            vig = Vigenere(self.key)
            vig.decryptFile(filename, ('decrypted' + filename))

        return filename, result


if __name__ == "__main__":
    # example = AviStegano('video/result2.avi', 'stegano', False, False)
    # print(format(example.frames[0][0,0,0], '08b'))
    # print(format(example.frames[0][0,0,1], '08b'))
    # print(format(example.frames[0][0,0,2], '08b'))
    # print(format(example.frames[0][0,1,0], '08b'))
    # print(format(example.frames[0][0,1,1], '08b'))
    # print(format(example.frames[0][0,1,2], '08b'))
    # print(format(example.frames[0][0,2,0], '08b'))
    # print(format(example.frames[0][0,2,1], '08b'))
    # print(format(example.frames[0][0,2,2], '08b'))
    # print(format(example.frames[0][0,3,0], '08b'))
    # print(format(example.frames[0][0,3,1], '08b'))
    # print(format(example.frames[0][0,3,2], '08b'))
    # print(format(example.frames[0][0,4,0], '08b'))
    # print(format(example.frames[0][0,4,1], '08b'))
    # print(format(example.frames[0][0,4,2], '08b'))
    # print(format(example.frames[0][0,5,0], '08b'))

    # print()
    # example.embeed('service.js', 'video/contoh.avi')
    # print(format(example.aviVideo.getFrames()[0][0,0,0], '08b'))
    # print(format(example.aviVideo.getFrames()[0][0,0,1], '08b'))
    # print(format(example.aviVideo.getFrames()[0][0,0,2], '08b'))
    # print(format(example.aviVideo.getFrames()[0][0,1,0], '08b'))
    # print(format(example.aviVideo.getFrames()[0][0,1,1], '08b'))
    # print(format(example.aviVideo.getFrames()[0][0,1,2], '08b'))
    # print(format(example.aviVideo.getFrames()[0][0,2,0], '08b'))
    # print(format(example.aviVideo.getFrames()[0][0,2,1], '08b'))
    # print(format(example.aviVideo.getFrames()[0][0,2,2], '08b'))
    # print(format(example.aviVideo.getFrames()[0][0,3,0], '08b'))
    # print(format(example.aviVideo.getFrames()[0][0,3,1], '08b'))
    # print(format(example.aviVideo.getFrames()[0][0,3,2], '08b'))
    # print(format(example.aviVideo.getFrames()[0][0,4,0], '08b'))
    # print(format(example.aviVideo.getFrames()[0][0,4,1], '08b'))
    # print(format(example.aviVideo.getFrames()[0][0,4,2], '08b'))
    # print(format(example.aviVideo.getFrames()[0][0,5,0], '08b'))

    # contoh = AviStegano('video/contoh.avi', 'stegano')
    # print(format(contoh.frames[0][0,0,0], '08b'))
    # print(format(contoh.frames[0][0,0,1], '08b'))
    # print(format(contoh.frames[0][0,0,2], '08b'))
    # print(format(contoh.frames[0][0,1,0], '08b'))
    # print(format(contoh.frames[0][0,1,1], '08b'))
    # print(format(contoh.frames[0][0,1,2], '08b'))
    # print(format(contoh.frames[0][0,2,0], '08b'))
    # print(format(contoh.frames[0][0,2,1], '08b'))
    # print(format(contoh.frames[0][0,2,2], '08b'))
    # print(format(contoh.frames[0][0,3,0], '08b'))
    # print(format(contoh.frames[0][0,3,1], '08b'))
    # print(format(contoh.frames[0][0,3,2], '08b'))
    # print(format(contoh.frames[0][0,4,0], '08b'))
    # print(format(contoh.frames[0][0,4,1], '08b'))
    # print(format(contoh.frames[0][0,4,2], '08b'))
    # print(format(contoh.frames[0][0,5,0], '08b'))
    # contoh.extract()