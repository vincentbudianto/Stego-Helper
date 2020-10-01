import imageLSB as lsb
import cv2

image_encode = cv2.imread('image/input.png')
lsbe = lsb.imageLSB(image = image_encode, key = 'STEGANOGRAPHY', encrypted = False, randomized = True)

res_encode = lsbe.embed('image/secret.txt')
# res_encode = lsbe.embed('image/mask.png')
cv2.imwrite('image/res.png', res_encode)

image_decode = cv2.imread('image/res.png')
lsbd = lsb.imageLSB(image = image_decode, key = 'STEGANOGRAPHY')

res_decode = lsbd.extract()
# with open(res_decode[0], "wb") as f:
# 	f.write(res_decode[1])

# image_encode = cv2.imread('input.png')
# print('psnr :', lsbd.psnr(image_encode))