import cv2
import math
import numpy as np
import random

from vigenere import Vigenere

class imageBPCS():
	def __init__(self, image, key, encrypted = False, randomized = False, threshold = 0.3):
		self.image = image
		self.key = key
		self.seed = sum(ord(k) for k in key)
		self.encrypted = encrypted
		self.randomized = randomized
		self.threshold = threshold
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

	def embed(self, filename):
		filedata = len(filename)
		content = open(filename, "rb").read()
		data = len(content)

	def extract(self):
		encrypted = self.read_bits(8)
		randomized = self.read_bits(8)

	def psnr(self, image):
		mse = np.mean((image - self.image) ** 2)

		if(mse == 0):
			return 100

		max_pixel = 256.0
		psnr = 20 * math.log10(max_pixel / math.sqrt(mse))

		return psnr