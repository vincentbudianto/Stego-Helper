import wave
import random
import numpy as np
import math

from vigenere import Vigenere

def save_file(path, content):
    print(path)
    new_file = open(path, "wb")
    new_file.write(content)
    new_file.close()

class Audio:
    def __init__(self, data, files=None, mode='embedding'):
        self.reset()
        self.counter = 0

        # Embedding
        if (mode == 'embedding'):
            # Processing input files
            self.key = data['key']
            self.audio_type = data['audioType']
            self.is_encrypted = bool(data['encrypted'])
            self.is_randomized = bool(data['randomized'])

            if files != None:
                print("Saving files")
                self.container_file = files['containerFile']
                self.input_file = files['inputFile']
                self.container_file_name = self.container_file.filename
                self.input_file_name = self.input_file.filename
                self.container_file_path = "./audiostore/container/" + self.container_file_name
                self.input_file_path = "./audiostore/input/" + self.input_file_name
                save_file(self.container_file_path, self.container_file.read())
                save_file(self.input_file_path, self.input_file.read())
            else:
                self.container_file_name = data['containerFileName']
                self.input_file_name = data['inputFileName']
                self.container_file_path = "./audiostore/container/" + self.container_file_name
                self.input_file_path = "./audiostore/input/" + self.input_file_name

            # Processing encrypted file (target)
            if not 'encryptedFileName' in data:
                temp = self.container_file_name.split('.')
                self.encrypted_file_name = temp[0] + "_encrypted." + temp[1]
            else:
                self.encrypted_file_name = data['encryptedFileName']
            self.encrypted_file_path = "./audiostore/encrypted/" + self.encrypted_file_name

            # Processing data files
            self.container_file_audio = wave.open(self.container_file_path, "r")
            self.container_file_params = self.container_file_audio.getparams()
            self.container_file_length = self.container_file_audio.getnframes()
            self.container_file_bytes = bytearray(list(self.container_file_audio.readframes(self.container_file_length)))
            self.container_file_length = len(self.container_file_bytes)
            self.input_file_bytes = open(self.input_file_path, "rb").read()

        else:
            # Get data files
            self.key = data['key']
            self.audio_type = data['audioType']

            # Save file
            if files != None:
                print("Saving files")
                self.encrypted_file = files['encryptedFile']
                self.encrypted_file_name = self.encrypted_file.filename
                self.encrypted_file_path = "./audiostore/encrypted/" + self.encrypted_file_name
                save_file(self.encrrypted_file_path, self.encrypted_file.read())
            else:
                self.encrypted_file_name = data['encryptedFileName']
                self.encrypted_file_path = "./audiostore/encrypted/" + self.encrypted_file_name

            # Processing encrypted file (target)
            if not 'containerFileName' in data:
                temp = self.encrypted_file_name.split('.')
                self.container_file_name = temp[0] + "_extracted." + temp[1]
            else:
                self.container_file_name = data['extractedFileName']
            self.container_file_path = "./audiostore/container/" + self.container_file_name

            # Processing data files
            self.container_file_audio = wave.open(self.encrypted_file_path, "r")
            self.container_file_params = self.container_file_audio.getparams()
            self.container_file_length = self.container_file_audio.getnframes()
            self.container_file_bytes = bytearray(list(self.container_file_audio.readframes(self.container_file_length)))
            self.container_file_length = len(self.container_file_bytes)

    def reset(self):
        self.mask_one = [1, 2, 4, 8, 16]
        self.mask_or = self.mask_one.pop(0)
        self.mask_zero = [254, 253, 251, 247, 239]
        self.mask_and = self.mask_zero.pop(0)
        self.curr_byte = 0

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

    def embedding(self):
        inputfilename_size = len(self.input_file_name)
        inputfile_size = len(self.input_file_bytes)

        print("Preparing Byte Map")
        self.byte_map = list(range(self.container_file_length))

        filename = self.input_file_name
        content = self.input_file_bytes

        # Limiting LSB into last 2 bits
        if self.container_file_length < 4 * (152 + inputfilename_size + inputfile_size):
            raise Exception('Audio is smaller than payload')

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

        if self.audio_type == 'stereo':
            self.put_value(format(22, '08b'))
        else:
            self.put_value(format(11, '08b'))

        # Randomizing bits
        if self.is_randomized:
            print("Randomizing bytes")
            total_ASCII = 0
            for word in self.key:
                total_ASCII += ord(word)
            for i in range(24):
                test = self.byte_map.pop(0)
            random.seed(total_ASCII)
            random.shuffle(self.byte_map)
            for i in range(23, -1, -1):
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
        with wave.open(self.encrypted_file_path, 'wb') as wav_file:
            wav_file.setparams(self.container_file_params)
            wav_file.writeframes(self.container_file_bytes)
            wav_file.close()

    def extract(self):
        print("Preparing Byte Map")
        self.byte_map = list(range(self.container_file_length))

        is_encrypted = self.read_bits(8)
        is_randomized = self.read_bits(8)
        audio_type = self.read_bits(8)

        if (is_randomized == 22):
            print("Randomizing bytes")
            total_ASCII = 0
            for word in self.key:
                total_ASCII += ord(word)
            for i in range(24):
                test = self.byte_map.pop(0)
            random.seed(total_ASCII)
            random.shuffle(self.byte_map)
            for i in range(23, -1, -1):
                self.byte_map.insert(0, i)
                
        filename_size = self.read_bits(64)
        content_size = self.read_bits(64)

        print("Extracting")

        filename = bytearray()
        for i in range(filename_size):
            filename.extend([self.read_bits(8)])

        content = bytearray()
        for i in range(content_size):
            content.extend([self.read_bits(8)])

        ### WRITE FILES ###
        print("Writing output")
        with wave.open(self.container_file_path, 'wb') as wav_file:
            wav_file.setparams(self.container_file_params)
            wav_file.writeframes(self.container_file_bytes)
            wav_file.close()

        new_filename = './audiostore/output/' + filename.decode()
        self.output_file_name = filename.decode()
        self.output_file_path = new_filename
        save_file(new_filename, content)

        if (is_encrypted == 22):
            print("Decrypting")
            vig = Vigenere(self.key)
            vig.decryptFile(new_filename, ('./audiostore/output/decrypted_' + filename.decode()))
            self.output_file_path = './audiostore/output/decrypted_' + filename.decode()

def audio_psnr(original_file, embedded_file):
    file_original = wave.open(original_file, 'rb')
    file_original_bytes = file_original.readframes(file_original.getnframes())
    file_original.close()

    file_embedded = wave.open(embedded_file, 'rb')
    file_embedded_bytes = file_embedded.readframes(file_embedded.getnframes())
    file_embedded.close()

    original_bytes_int = []
    embedded_bytes_int = []
    for i in range(1000, len(file_original_bytes)):
        original_bytes_int.append(int(file_original_bytes[i]))
        embedded_bytes_int.append(int(file_embedded_bytes[i]))

    # print(original_bytes_int)
    original_bytes_int = np.array(original_bytes_int)
    embedded_bytes_int = np.array(embedded_bytes_int)

    delta = np.sum(pow((original_bytes_int - embedded_bytes_int),2))
    mse = delta / len(file_original_bytes)

    psnr = 20 * math.log10(255 / math.sqrt(mse))
    return psnr


if __name__ == "__main__":
    audio_execute = 'embedding'
    if audio_execute == 'embedding':
        data = {'key':'FUSRODAH', 'encrypted':True, 'randomized':True, 'audioType':'stereo', 'containerFileName':'weebs.wav', 'inputFileName':'poke.mp3'}
        audio = Audio(data)
        audio.embedding()
        print("Counting PSNR")
        print("PSNR =", audio_psnr(audio.container_file_path, audio.encrypted_file_path))
    else:
        data = {'key':'FUSRODAH', 'audioType':'stereo', 'encryptedFileName':'weebs_encrypted.wav'}
        audio = Audio(data, mode='extract')
        audio.extract()
    print("Done")