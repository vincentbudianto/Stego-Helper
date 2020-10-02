import cv2
import math
import numpy as np
import random

from messageBPCS import messageBPCS
from vigenere import Vigenere

class imageBPCS():
    def __init__(self):
        self.block_size = 8

    def readImage(self, filename):
        try:
            image = cv2.imread(filename)

            self.image = image
            self.height, self.width, self.channels = image.shape
            self.size = self.width * self.height
            self.map = list(range(self.size))
        except Exception as exception:
            print(exception)
            print("Error while reading image file")

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

    def embed(self, path, key, threshold, encrypted, randomized):
        if (encrypted):
            vig = Vigenere(key)
            content = vig.encryptFile(path)
        else:
            content = open(path, "rb").read()

        filename = path.split('/')[-1]

        msg = messageBPCS(filename = filename, content = content, key = key, threshold = threshold, encrypted = encrypted, randomized = randomized, block_size = self.block_size)

        message = msg.set_message()

        if ((self.width * self.height * self.channels) < len(message)):
            raise Exception('Image is smaller than payload')

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

        return self.image

    def extract(self, key, threshold):
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

        with open('result/image/' + filename, "wb") as f:
            f.write(content)

        if (encrypted):
            vig = Vigenere(key)
            vig.decryptFile('result/image/' + filename, ('result/image/decrypted_' + filename))

        return filename, content

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
    bpcse = imageBPCS()
    bpcse.readImage('image/input.png')
    res_encode = bpcse.embed(path = 'image/test.txt', key = 'STEGANOGRAPHY', threshold = 0.3, encrypted = False, randomized = False)
    # res_encode = bpcse.embed(path = 'image/mask.png', key = 'STEGANOGRAPHY', threshold = 0.3, encrypted = False, randomized = False)
    bpcse.writeImage('result/image/resBPCS.png')

    print('<<<<< extract >>>>>>')
    bpcsd = imageBPCS()
    bpcsd.readImage('result/image/resBPCS.png')

    filename, content = bpcsd.extract(key = 'STEGANOGRAPHY', threshold = 0.3)

    print('res_decode filename :', filename)
    print(' res_decode content :', len(content))

    # with open(filename, "wb") as f:
    # 	f.write(content)

    print('<<<<< psnr >>>>>>')
    bpcs = imageBPCS()
    image_one = cv2.imread('image/input.png')
    image_two = cv2.imread('result/image/resBPCS.png')
    print('psnr :', bpcs.psnr(image_one, image_two))