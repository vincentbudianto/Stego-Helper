import cv2
import math
import numpy as np
import random

from vigenere import Vigenere

class imageLSB():
    def __init__(self, image, key, encrypted = False, randomized = False):
        self.image = image
        self.key = key
        self.seed = sum(ord(k) for k in key)
        self.encrypted = encrypted
        self.randomized = randomized
        self.height, self.width, self.channels = image.shape
        self.size = self.width * self.height

        self.map = list(range(self.height * self.width))

        self.mask_one = [1, 2, 4, 8, 16, 32, 64, 128]
        self.mask_or = self.mask_one.pop(0)

        self.mask_zero = [254, 253, 251, 247, 239, 223, 191, 127]
        self.mask_and = self.mask_zero.pop(0)

        self.curr_pos = 0
        self.curr_channel = 0

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
                    raise Exception('No available pixels remaining')
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

    def embed(self, filename):
        filedata = len(filename)
        content = open(filename, "rb").read()
        data = len(content)

        if (not self.randomized) and ((self.width * self.height * self.channels) < (filedata + data + 96)):
            raise Exception('Image is smaller than payload')
        elif (self.randomized) and ((self.width * self.height * self.channels) < (filedata + data + 128)):
            raise Exception('Image is smaller than payload')

        if (self.encrypted):
            vig = Vigenere(self.key)
            content = vig.encryptFile(filename)
            self.put_value(format(22, '08b'))
        else:
            self.put_value(format(11, '08b'))

        if (self.randomized):
            self.put_value(format(22, '08b'))
        else:
            self.put_value(format(11, '08b'))

        if (self.randomized):
            random.seed(self.seed)

            for i in range(16):
                self.map.pop(0)

            random.shuffle(self.map)

        self.put_value(format(filedata, '016b'))
        self.put_value(format(data, '064b'))

        for byte in filename:
            self.put_value(format(ord(byte), '08b'))

        for byte in content:
            self.put_value(format(int(byte), '08b'))

        return self.image

    def extract(self):
        encrypted = self.read_bits(8)
        randomized = self.read_bits(8)

        if (randomized == 22):
            random.seed(self.seed)

            for i in range(16):
                self.map.pop(0)

            random.shuffle(self.map)

        filedata = self.read_bits(16)
        filename = bytearray()

        data = self.read_bits(64)
        result = bytearray()

        for byte in range(filedata):
            filename.extend([self.read_bits(8)])

        for byte in range(data):
            result.extend([self.read_bits(8)])

        filename = filename.decode()

        with open(filename, "wb") as f:
            f.write(result)

        if (encrypted == 22):
            vig = Vigenere(self.key)
            vig.decryptFile(filename, ('image/decrypted' + filename))

        return filename, result

    def psnr(self, image):
        mse = np.mean((image - self.image) ** 2)

        if (mse == 0):
            return 100

        max_pixel = 256.0
        psnr = 20 * math.log10(max_pixel / math.sqrt(mse))

        return psnr