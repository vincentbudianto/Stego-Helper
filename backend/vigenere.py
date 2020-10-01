from itertools import cycle
from random import shuffle
from typing import List, Union

import re
import numpy as np

class Vigenere():
    def __init__(self, key):
        self.key = key
        self.auto_key = False
        self.random = False
        self.base = 0
        self.set_matrix()

    def encrypt(self, plain_text: str, *args, **kwargs) -> str:
        key_now = self.key
        list_int_plain_text = self.str_to_list_int(plain_text, base=self.base)
        list_int_cipher_text = self._int_encrypt_(list_int_plain_text, key_now)
        return self.list_int_to_str(list_int_cipher_text, base=self.base)

    def _int_encrypt_(self, list_int_plain_text: List[int], key_now: str) -> str:
        list_int_key = self.str_to_list_int(key_now, base=self.base)

        if (self.auto_key):
            list_int_key += list_int_plain_text

        list_int_cipher_text = [
            (num + key) % 256
            for key, num in zip(cycle(list_int_key), list_int_plain_text)
        ]

        return list_int_cipher_text

    def decrypt(self, cipher_text: str, *args, **kwargs) -> str:
        key_now = self.key

        list_int_cipher_text = self.str_to_list_int(cipher_text, base=self.base)
        list_int_plain_text = self._int_decrypt_(list_int_cipher_text, key_now)
        return self.list_int_to_str(list_int_plain_text, base=self.base)

    def _int_decrypt_(self, list_int_cipher_text: List[int], key_now: str) -> str:
        list_int_key = self.str_to_list_int(key_now, base=self.base)
        if self.auto_key:
            if key_now == '':
                return ''

            list_int_plain_text = []
            for idx, num in enumerate(list_int_cipher_text):
                key = list_int_key[idx]
                plain_int = (num - key) % 256
                list_int_plain_text.append(plain_int)
                list_int_key.append(plain_int)
        else:
            list_int_plain_text = [(num - key) % 256 for key, num in zip(
                cycle(list_int_key), list_int_cipher_text)]

        return list_int_plain_text

    def set_matrix(self, shift: int = 1):
        '''Generate Vigenere Matrix
        if random is True then shift will not be used
        '''
        temp_matrix = list()

        char_count = 256

        for i in range(char_count):
            temp_row = [j for j in range(i, char_count + i)]

            if self.random:
                shuffle(temp_row)

            temp_row = [j % char_count for j in temp_row]
            temp_matrix.append(temp_row)

        self.matrix = temp_matrix

    def full_mode(self, state):
        self.random = bool(state)
        self.set_matrix()

    def auto_key_mode(self, state):
        self.auto_key = bool(state)

    def encryptFile(self, fileName):
        if fileName:
            # if outputFile:
                # fileSize = os.stat(fileName).st_size
                # nLoop = ceil(fileSize / OFFSET)
                binary = np.fromfile(fileName, dtype=np.uint8)
                cipher_list_int = self._int_encrypt_(binary, self.key)
                arr = np.asarray(cipher_list_int, dtype=np.uint8)
                # arr.tofile(outputFile)
                # print('done encrypt')
                return arr.tobytes()

    def decryptFile(self, fileName, outputFile):
        if fileName:
            if outputFile:
                # fileSize = os.stat(fileName).st_size
                # nLoop = ceil(fileSize / OFFSET)
                binary = np.fromfile(fileName, dtype=np.uint8)
                plain_list_int = self._int_decrypt_(binary, self.key)
                arr = np.asarray(plain_list_int, dtype=np.uint8)
                arr.tofile(outputFile)
                # print('done decrypt')
                # return arr.tobytes()

    @staticmethod
    def str_to_list_int(
        text: Union[str, List[str]], base: int = ord('a')) -> List[int]:
        '''Convert str to list of int

        Convertion done by substract each char by base,
        so the smallest char will have int = 0
        '''
        return [(ord(char) - base) for char in text]

    @staticmethod
    def list_int_to_str(list_int: List[int], base: int = ord('a')) -> str:
        '''Convert list of int to str
        Convertion done by adding each num with base,
        so the number 0 will have char = chr(base)
        '''
        return ''.join([chr(num + base) for num in list_int])

    @staticmethod
    def remove_punctuation(text: str, filter: str = '[^a-zA-Z]') -> str:
        '''Remove punctuation from the text using re.sub()
        '''
        return re.sub(filter, '', text)
