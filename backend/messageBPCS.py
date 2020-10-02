import math
import numpy as np
import os

Wc = np.array([[0, 1, 0, 1, 0, 1, 0, 1],
               [1, 0, 1, 0, 1, 0, 1, 0],
               [0, 1, 0, 1, 0, 1, 0, 1],
               [1, 0, 1, 0, 1, 0, 1, 0],
               [0, 1, 0, 1, 0, 1, 0, 1],
               [1, 0, 1, 0, 1, 0, 1, 0],
               [0, 1, 0, 1, 0, 1, 0, 1],
               [1, 0, 1, 0, 1, 0, 1, 0]])

class messageBPCS():
    def __init__(self, filename = None, content = None, key = None, threshold = 0.3, encrypted = False, randomized = False, block_size = 8):
        self.filename = filename
        self.content = content
        self.key = key
        self.threshold = threshold
        self.encrypted = encrypted
        self.randomized = randomized
        self.block_size = block_size
        self.bitplane = []

        if (self.filename != None):
            self.filedata = len(self.filename)
        else:
            self.filedata = None

        if (self.content != None):
            self.data = len(self.content)
        else:
            self.data = None

        self.header = None
        self.header_bitplane = []
        self.content_bitplane = []
        self.conjugation_map = []

    def to_binary(self, message):
        binary = [format(byte, '08b') for byte in message]

        while((len(binary) % self.block_size) != 0):
            binary.append('01010101')

        return binary

    def to_bitplane(self, binary):
        block = np.array([list(bit) for bit in binary])
        height, width = block.shape
        bitplane = []

        for h in range(0, (height - self.block_size + 1), self.block_size):
            for w in range(0, (width - self.block_size + 1), self.block_size):
                bitplane.append(block[h:(h + self.block_size), w:(w + self.block_size)].astype(int))

        return bitplane

    def complexity(self, bitplane):
        count = 0

        for h in range(self.block_size - 1):
            for w in range(self.block_size - 1):
                if(bitplane[h][w] != bitplane[h + 1][w]):
                    count += 1

                if(bitplane[h][w] != bitplane[h][w + 1]):
                    count += 1

        return count / 112

    def conjugate(self, plane):
        return plane ^ Wc

    def int_bitplane(self, x):
        bitplane = []

        byte = format(x, '064b')
        plane = np.array([list(byte[b:(b + self.block_size)]) for b in range(0, len(byte), self.block_size)])
        plane = self.conjugate(plane.astype(int))
        bitplane.append(plane)

        return bitplane

    def get_int(self, bitplane):
        bitplane = self.conjugate(bitplane)
        binary = ''.join([''.join(bit) for bit in bitplane.astype(str)])
        result = int(binary, 2)

        return result

    def create_header(self):
        header = ''

        if (self.encrypted):
            header += '22|'
        else:
            header += '11|'

        if (self.randomized):
            header += '22|'
        else:
            header += '11|'

        header += str(self.filedata) + '|'
        header += str(self.data) + '|'
        header += self.filename

        self.header = header.encode('utf-8')
        binary = self.to_binary(self.header)
        self.header_bitplane = self.to_bitplane(binary)

        return self.header_bitplane

    def create_content(self):
        content = self.to_binary(self.content)
        self.content_bitplane = self.to_bitplane(content)

    def conjugate_content(self):
        for i in range(len(self.content_bitplane)):
            if (self.complexity(self.content_bitplane[i]) < self.threshold):
                self.content_bitplane[i] = self.conjugate(self.content_bitplane[i])
                self.conjugation_map.append(i)

    def conjugation_mapping(self):
        conjugation_map = ['0' for i in range(len(self.bitplane))]

        for i in self.conjugation_map:
            conjugation_map[i] = '1'

        while((len(conjugation_map) % self.block_size) != 0):
            conjugation_map.append('0')

        binary = [''.join(conjugation_map[j:(j + self.block_size)]) for j in range(0, len(conjugation_map), self.block_size)]

        while((len(binary) % self.block_size) != 0):
            binary.append('01010101')

        self.conjugation_map = self.to_bitplane(binary)

        for j in range(len(self.conjugation_map)):
            self.conjugation_map[j] = self.conjugate(self.conjugation_map[j])

        return self.conjugation_map

    def get_byte(self, bitplane):
        result = bytearray()

        for plane in bitplane:
            for bit in plane:
                byte = int(''.join(bit.astype(str)), 2)
                result.append(byte)

        return result

    def from_bitplane(self, bitplane):
        cmap = []

        for i in range(len(self.conjugation_map)):
            self.conjugation_map[i] = self.conjugate(self.conjugation_map[i])

        for plane in self.conjugation_map:
            cmap.append(''.join([''.join(bit) for bit in plane.astype(str)]))

        cmap = ''.join(cmap)

        for i in range(len(bitplane)):
            if (cmap[i] == '1'):
                bitplane[i] = self.conjugate(bitplane[i])

        return bitplane

    def get_header(self):
        self.header = self.get_byte(self.header_bitplane)
        self.header = self.header.decode('utf-8', errors='ignore')

        headers = self.header.split('|')

        if (int(headers[0]) == 22):
            self.encrypted = True
        elif (int(headers[0]) == 11):
            self.encrypted = False

        if (int(headers[1]) == 22):
            self.randomized = True
        elif (int(headers[1]) == 11):
            self.randomized = False

        self.filedata = int(headers[2])
        self.data = int(headers[3])

        return headers[4][:self.filedata]

    def get_content(self):
        return self.get_byte(self.content_bitplane)[:self.data]

    def set_message(self):
        self.create_header()
        self.create_content()
        self.conjugate_content()

        self.bitplane += self.int_bitplane(len(self.header_bitplane))
        self.bitplane += self.header_bitplane
        self.bitplane += self.content_bitplane

        cmap = self.conjugation_mapping()
        cbitplane = self.int_bitplane(len(cmap))
        cbitplane += cmap

        self.bitplane = cbitplane + self.bitplane

        return self.bitplane

    def get_message(self, bitplane):
        cmap_length = self.get_int(bitplane.pop(0))

        for i in range(cmap_length):
            self.conjugation_map.append(bitplane.pop(0))

        header_length = self.get_int(bitplane.pop(0))

        for j in range(header_length):
            self.header_bitplane.append(bitplane.pop(0))

        bitplane = self.from_bitplane(bitplane)
        self.content_bitplane = bitplane
        self.filename = self.get_header()
        self.content = self.get_content()

        return self.filename, self.content

if __name__ == '__main__':
    print('<<<<< message to bitplane >>>>>>')
    path = 'image/secret.txt'
    # path = 'image/mask.png'
    name = path.split('/')[-1]
    contents = open(path, 'rb').read()
    smsg = messageBPCS(filename = name, content = contents)
    bitplane = smsg.set_message()
    print('bitplane :', len(bitplane))

    print('\nmessage complexity :')
    for i in range(len(bitplane)):
        c = smsg.complexity(bitplane[i])

        if (c <= 0.3):
            print('complexity', i, ':', c)
            print(bitplane[i])

    print('\n\n<<<<< bitplane to message >>>>>>')
    gmsg = messageBPCS()
    filename, content = gmsg.get_message(bitplane)
    print('filename :', filename)
    print(' content :', len(content))
    # with open('image/test.png', 'wb') as fout:
    with open('result/message/' + filename, 'wb') as fout:
        fout.write(content)
