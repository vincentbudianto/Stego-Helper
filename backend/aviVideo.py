import aviVideo
import math
import numpy as np
import random

from cv2 import cv2
from vigenere import Vigenere

FLAG_TRUE = 22
FLAG_FALSE = 11
TOTAL_FLAG_BITS = 24

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
    def __init__(self):
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

    def readVideo(self, video_filename):
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
                        raise Exception('No available pixels remaining')
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

    def embeed(self, message_file_name, output_filename, key, encryption=False, randomized_frame=False, randomized_pixel=False):
        #Set AviStegano Metadata
        seed = sum(ord(k) for k in key)

        filedata = len(message_file_name)
        content = open(message_file_name, "rb").read()
        data = len(content)

        #Add Encryption Flag Bits
        if (encryption):
            print('Encrypting Message File')
            vig = Vigenere(key)
            content = vig.encryptFile(message_file_name)
            self.put_value(format(FLAG_TRUE, '08b'))
        else:
            self.put_value(format(FLAG_FALSE, '08b'))

        #Add Randomized Frame Flag Bits
        if (randomized_frame):
            self.put_value(format(FLAG_TRUE, '08b'))
        else:
            self.put_value(format(FLAG_FALSE, '08b'))

        #Add Randomized Pixel Flag Bits
        if (randomized_pixel):
            self.put_value(format(FLAG_TRUE, '08b'))
        else:
            self.put_value(format(FLAG_FALSE, '08b'))

        #If any random skip early frame
        if (randomized_frame or randomized_pixel):
            random.seed(seed)
            self.skipped_frame = self.curr_frame + 1

            for i in range (self.skipped_frame):
                self.frame_map.pop(0)

            #Reset index pointer
            self.curr_frame = 0
            self.curr_pos = 0
            self.curr_channel = 0

            if (randomized_frame):
                print('Randomized Frame')
                random.shuffle(self.frame_map)

            if (randomized_pixel):
                print('Randomized Pixel')
                random.shuffle(self.map)

        if (randomized_frame or randomized_pixel):
            if (((self.frame_size - self.skipped_frame) * self.width_size * self.height_size * self.channel_size) < (filedata + data + 136)):
                raise Exception('Video is smaller than payload')
        else:
            if ((self.frame_size * self.width_size * self.height_size * self.channel_size) < (filedata + data + 104)):
                raise Exception('Video is smaller than payload')

        self.put_value(format(filedata, '032b'))
        self.put_value(format(data, '064b'))

        for byte in message_file_name:
            self.put_value(format(ord(byte), '08b'))
        for byte in content:
            self.put_value(format(int(byte), '08b'))

        self.aviVideo.setFrames(self.frames)
        self.aviVideo.writeVideo(output_filename)

    def extract(self, key, filename_message_output = ''):
        encription = self.read_bits(8)
        randomized_frame = self.read_bits(8)
        randomized_pixel = self.read_bits(8)

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

        filedata = self.read_bits(32)
        filename = bytearray()

        data = self.read_bits(64)
        result = bytearray()

        for byte in range(filedata):
            filename.extend([self.read_bits(8)])

        for byte in range(data):
            result.extend([self.read_bits(8)])

        if (filename_message_output == ''):
            filename = filename.decode()
        else:
            filename = filename_message_output

        with open(filename, "wb") as f:
            f.write(result)

        if (encription == 22):
            vig = Vigenere(key)
            vig.decryptFile(filename, filename)

        return filename, result

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

if __name__ == "__main__":
    # Embeed
    # example = AviStegano()
    # example.readVideo('video/result2.avi')
    # print(len(example.frames), example.frames[0].shape)

    # example.embeed('secret.txt', 'video/contoh.avi', 'stegano', True, True, True)
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
    contoh = AviStegano()
    contoh.readVideo('video/contoh.avi')
    print(contoh.frames[0].shape)
    print(format(contoh.frames[0][0,0,0], '08b'))
    print(format(contoh.frames[0][0,0,1], '08b'))
    print(format(contoh.frames[0][0,0,2], '08b'))
    print(format(contoh.frames[0][0,1,0], '08b'))
    print(format(contoh.frames[0][0,1,1], '08b'))
    print(format(contoh.frames[0][0,1,2], '08b'))
    print(format(contoh.frames[0][0,2,0], '08b'))
    print(format(contoh.frames[0][0,2,1], '08b'))
    print()
    print(format(contoh.frames[0][0,2,2], '08b'))
    print(format(contoh.frames[0][0,3,0], '08b'))
    print(format(contoh.frames[0][0,3,1], '08b'))
    print(format(contoh.frames[0][0,3,2], '08b'))
    print(format(contoh.frames[0][0,4,0], '08b'))
    print(format(contoh.frames[0][0,4,1], '08b'))
    print(format(contoh.frames[0][0,4,2], '08b'))
    print(format(contoh.frames[0][0,5,0], '08b'))
    print()
    print(format(contoh.frames[0][0,5,1], '08b'))
    print(format(contoh.frames[0][0,5,2], '08b'))
    print(format(contoh.frames[0][0,6,0], '08b'))
    print(format(contoh.frames[0][0,6,1], '08b'))
    print(format(contoh.frames[0][0,6,2], '08b'))
    print(format(contoh.frames[0][0,7,0], '08b'))
    print(format(contoh.frames[0][0,7,1], '08b'))
    print(format(contoh.frames[0][0,7,2], '08b'))
    contoh.extract('stegano')
    pass