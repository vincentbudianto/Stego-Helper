import cv2
import math
import numpy as np
import random

from vigenere import Vigenere

class imageLSB():
    def __init__(self):
        self.mask_one = [1, 2]
        self.mask_or = self.mask_one.pop(0)

        self.mask_zero = [254, 253]
        self.mask_and = self.mask_zero.pop(0)

        self.curr_pos = 0
        self.curr_channel = 0

    def readImage(self, filename):
        try:
            image = cv2.imread(filename)

            self.image = image
            self.height, self.width, self.channels = image.shape
            self.size = self.width * self.height
            self.map = list(range(self.size))
        except Exception as exception:
            print(exception)
            print('Error while reading image file')

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

                if (self.mask_or == 2):
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

    def embed(self, path, key, output = '', encrypted = False, randomized = False):
        filename = path.split('/')[-1]
        filedata = len(filename)
        content = open(path, 'rb').read()
        data = len(content)

        if ((not randomized) and ((self.width * self.height * self.channels) < (8 * (filedata + data + 96)))):
            raise Exception('Image is smaller than payload')
        elif ((randomized) and ((self.width * self.height * self.channels) < (8 * (filedata + data + 128)))):
            raise Exception('Image is smaller than payload')

        if (encrypted):
            vig = Vigenere(key)
            content = vig.encryptFile(path)
            self.put_value(format(22, '08b'))
        else:
            self.put_value(format(11, '08b'))

        if (randomized):
            self.put_value(format(22, '08b'))
        else:
            self.put_value(format(11, '08b'))

        if (randomized):
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

        if (output == ''):
            self.writeImage('result/image/embed_' + filename)
        else:
            self.writeImage(output)

        return output

    def extract(self, key, output = ''):
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

        if (output == ''):
            with open(('result/image/extracted_' + filename), 'wb') as f:
                f.write(content)

            if (encrypted == 22):
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
        mse = np.mean((image_one - image_two) ** 2)

        if (mse == 0):
            return 100

        max_pixel = 256.0
        psnr = 20 * math.log10(max_pixel / math.sqrt(mse))

        return psnr

if __name__ == '__main__':
    print('<<<<< embed >>>>>>')
    lsbe = imageLSB()
    lsbe.readImage('test/image/input.png')

    res_encode = lsbe.embed(path = 'test/image/test.txt', key = 'STEGANOGRAPHY', output = 'result/image/resLSB.png', encrypted = False, randomized = False)
    # res_encode = lsbe.embed(path = 'test/image/mask.png', key = 'STEGANOGRAPHY', output = 'result/image/resLSB.png', encrypted = False, randomized = False)

    print('<<<<< extract >>>>>>')
    lsbd = imageLSB()
    lsbd.readImage('result/image/resLSB.png')

    filename = lsbd.extract(key = 'STEGANOGRAPHY', output = 'result/image/test.txt')

    print('extract filename :', filename)

    print('<<<<< psnr >>>>>>')
    lsb = imageLSB()
    image_one = cv2.imread('test/image/input.png')
    image_two = cv2.imread('result/image/resLSB.png')
    print('psnr :', lsb.psnr(image_one, image_two))