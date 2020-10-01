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

        self.height_map = list(range(self.height))
        self.width_map = list(range(self.width))

        self.mask_one = [1, 2, 4, 8, 16, 32, 64, 128]
        self.mask_or = self.mask_one.pop(0)

        self.mask_zero = [254, 253, 251, 247, 239, 223, 191, 127]
        self.mask_and = self.mask_zero.pop(0)

        self.curr_width = 0
        self.curr_height = 0
        self.curr_channel = 0

    def next_pos(self):
        if (self.curr_channel == (self.channels - 1)):
            self.curr_channel = 0

            if (self.curr_width == (len(self.width_map) - 1)):
                self.curr_width = 0

                if (self.curr_height == (len(self.height_map) - 1)):
                    self.curr_height = 0

                    if (self.mask_or == 128):
                        raise Exception('No available pixels remaining')
                    else:
                        self.mask_or = self.mask_one.pop(0)
                        self.mask_and = self.mask_zero.pop(0)
                else:
                    self.curr_height += 1
            else:
                self.curr_width += 1
        else:
            self.curr_channel += 1

    def read_bit(self):
        val = self.image[self.height_map[self.curr_height], self.width_map[self.curr_width]][self.curr_channel]
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
            val = list(self.image[self.height_map[self.curr_height], self.width_map[self.curr_width]])

            if (int(b) == 1):
                val[self.curr_channel] = int(val[self.curr_channel]) | self.mask_or
            else:
                val[self.curr_channel] = int(val[self.curr_channel]) & self.mask_and

            self.image[self.height_map[self.curr_height], self.width_map[self.curr_width]] = tuple(val)
            self.next_pos()

    def embed(self, filename):
        filedata = len(filename)
        content = open(filename, "rb").read()
        data = len(content)

        if (self.width * self.height * self.channels) < (filedata + data + 112):
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
                self.height_map.pop(0)
                self.width_map.pop(0)

            random.shuffle(self.height_map)
            random.shuffle(self.width_map)

        self.put_value(format(filedata, '032b'))
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
                self.height_map.pop(0)
                self.width_map.pop(0)

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

        if (encrypted == 22):
            vig = Vigenere(self.key)
            vig.decryptFile(filename, ('decrypted' + filename))

        return filename, result

    def psnr(self, image):
        mse = np.mean((image - self.image) ** 2)

        if(mse == 0):
            return 100

        max_pixel = 256.0
        psnr = 20 * math.log10(max_pixel / math.sqrt(mse))

        return psnr