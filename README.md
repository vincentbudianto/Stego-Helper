# Stego-Helper

## Audio Steganography
- read_container_file(real_audio)
- read_input_file(message)
- embedding(output: optional)
- extract(output: optional)
- audio_psnr(real_image, stego_object)

## Image Steganography
### Least Significant Bit (LSB)
- readImage(real_image)
- writeImage(stego_object)
- embed(message, output: optional)
- extract(output: optional)
- psnr(real_image, stego_object)

### Bit-Plane Complexity Segmentation (BPCS)
- readImage(real_image)
- writeImage(stego_object)
- embed(message, output: optional)
- extract(output: optional)
- psnr(real_image, stego_object)

## Video Steganography
- readVideo(real_video)
- writeVideo(stego_object)
- embeed(message, output: optional)
- extract(output: optional)
- calculatePSNR(real_video, stego_object)
