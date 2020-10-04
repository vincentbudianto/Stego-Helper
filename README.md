# Aplikasi Steganografi pada Berkas Citra, Audio, dan Video dengan Metode LSB dan Metode BPCS

Aplikasi steganografi sederhana yang dibangun dengan menggunakan bahasa pemrograman python.

### Requirement:
- python 3.*
- pip / conda
- ffmpeg

### Instalasi Environment
```
$ sudo apt install ffmpeg
$ conda env create -n stego-helper -f env.yml
```

### Run Program
```
$ python main.py
```

## Steganografi
Steganografi adalah proses penyembunyian file rahasia dalam file yang lebih besar sedemikian rupa sehingga orang lain tidak dapat mengetahui keberadaan atau isi pesan yang disembunyikan tersebut. Steganografi bertujuan untuk menjaga komunikasi rahasia antara dua pihak. Tidak seperti kriptografi yang menyembunyikan isi pesan rahasia, steganografi menyembunyikan fakta adanya pesan rahasia yang dikomunikasikan.

### Metode Steganografi
- __LSB__ <br>
  Metode Least Significant Bit (LSB) mengganti nilai bit terakhir dengan bit data informasi rahasia. Jika Most Significant Bit (MSB) diganti, maka akan menghasilkan dampak yang lebih besar pada nilai akhir tetapi jika Least Significant Bit (LSB) diganti, dampak yang dihasilkan minimal, sehingga digunakan least significant bit steganography.

- __BPCS__ <br>
  Metode Bit-Plane Complexity Segmentation (BPCS) mengganti bitplane pada file gambar dengan bitplane pada file atau pesan rahasia jika nilai kompleksitas bitplane gambar diatas threshold yang ditentukan.

### Media File :
- __Image__ <br>
  Image steganography menyembunyikan file dalam sebuah file citra yang bertipe .bmp atau .png. File .bmp atau .png dipakai karena file tersebut tidak mengalami kompresi sehingga penerapan steganografi pada bit-bit data tidak akan terlalu mempengaruhi objek stego yang dihasilkan.

- __Video__ <br>
  Video steganography menyembunyikan file dalam sebuah file video yang bertipe .avi. File .avi dipakai karena file tersebut tidak mengalami kompresi sehingga penerapan steganografi pada bit-bit data tidak akan terlalu mempengaruhi objek stego yang dihasilkan. <br>
  Cara melakukan steganografi pada file video dengan tipe .avi adalah dengan mengubah bit pada layer frame, khususnya frame gambar sehingga proses steganografi yang dilakukan mirip dengan steganografi gambar dengan jumlah frame yang banyak sehingga ukuran message yang dapat disisipkan pada file video jauh lebih besar dibandingkan dengan steganografi gambar.

- __Audio__ <br>
Audio steganography menyembunyikan file dalam sebuah file audio yang bertipe .wav. Alasan file .wav yang dibutuhkan dikarenakan file tersebut tidak mengalami kompresi sehingga metode LSB pada bit-bit data tidak akan terlalu mempengaruhi hasil audio yang dihasilkan. <br>
Cara melakukan steganografi pada file audio dengan tipe .wav adalah dengan memulai encoding pada byte ke-44 dengan metode LSB. Setelah itu, file hasil embedding akan dihubungkan kembali dengan 44 bit yang sebelumnya.

## Program Steganografi
Program steganografi yang dibuat dapat memproses media file gambar, video, maupun audio. Selain itu, untuk menambahkan tingkat kompeksitas penyisipan pesan, program memiliki 2 fitur, yaitu :
- __Enkripsi__ <br>
  program dapat melakukan enkripsi untuk file pesan dengan menggunakan metode vigenere cipher sebelum pesan disisipkan pada media file
- __Random__ <br>
  program dapat menyisipkan pesan secara acak untuk byte dari pesan, pada image dapat dilakukan random pada penyisipan dari posisi pixel, dan pada video juga dapat dilakukan random pada penyisipan dari posisi frame

### Opsi Aplikasi Steganografi
- __Image (LSB)__ <br>
  Steganografi melalui media gambar dengan metode LSB.
    - Acceptable file : .bmp, .png
    - Parameter input
      - stego key : key sebagai kunci enkripsi dan digunakan untuk membangkitkan nilai seed pada fungsi random
      - encryption : status enkripsi untuk file message
      - random pixel : metode pengacakan untuk penyisipan bit pada pixel gambar

- __Image (BPCS)__ <br>
  Steganografi melalui media gambar dengan metode LSB.
    - Acceptable file : .bmp, .png
    - Parameter input
      - stego key : key sebagai kunci enkripsi dan digunakan untuk membangkitkan nilai seed pada fungsi random
      - threshold : nilai batas untuk menentukan informative regions dan noise-like regions
      - encryption : status enkripsi untuk file message
      - random pixel : metode pengacakan untuk penyisipan bit pada pixel bitplane

- __Video__ <br>
  Steganografi melalui media gambar dengan metode LSB.
    - Acceptable file : .avi
    - Parameter input
      - stego key : key sebagai kunci enkripsi dan digunakan untuk membangkitkan nilai seed pada fungsi random
      - encryption : status enkripsi untuk file message
      - random frame : metode pengacakan untuk penyisipan bit pada frame video
      - random pixel : metode pengacakan untuk penyisipan bit pada pixel video

- __Audio__ <br>
  Steganografi melalui media gambar dengan metode LSB.
    - Acceptable file : 'wav', '-wav', 'x-wav'
    - Parameter input
      - stego key : key sebagai kunci enkripsi dan digunakan untuk membangkitkan nilai seed pada fungsi random
      - encryption : status enkripsi untuk file message
      - random : metode pengacakan untuk penyisipan bit pada byte video

### PSNR
Program juga dapat menghitung nilai PSNR atau Peak Signal-to-Noise Ratio yang menunjukkan perbandingan antara nilai maksimum dari sinyal yang diukur dengan besarnya dearu yang berpegaruh pada sinyal tersebut dan diukur dengan satuan desibel. Untuk menghitung PSNR gambar, dengan membandingkan perbedaan setiap pixel dari gambar, untuk video dengan menghitung rata-rata nilai PSNR setiap frame dengan menggunakan perhitungan PSNR gambar, sedangkan untuk menghitung PSNR audio dengan membandingkan setiap byte pada file audionya.

### Referensi
- [Image Steganography using Python. Understanding LSB Image Steganography… | by Rupali Roy](https://towardsdatascience.com/hiding-data-in-an-image-image-steganography-using-python-e491b68b1372)
- [least Significant Bit - an overview](https://www.sciencedirect.com/topics/computer-science/least-significant-bit)
- [Steganography — LSB Introduction with Python — Part 1 | by Juan Cortés](https://itnext.io/steganography-101-lsb-introduction-with-python-4c4803e08041)
- [Principle and applications of BPCS-Steganography](http://informatika.stei.itb.ac.id/~rinaldi.munir/Kriptografi/2015-2016/SPIE98.pdf)
- [OpenCV-Python Tutorials — OpenCV ](https://opencv-python-tutroals.readthedocs.io/en/latest/py_tutorials/py_tutorials.html)
- [OpenCV: Flags for video I/O](https://docs.opencv.org/3.4/d4/d15/group__videoio__flags__base.html)
- [How to Convert an RGB Image to Grayscale](https://e2eml.school/convert_rgb_to_grayscale.html)
- [AVI File Format](https://cdn.hackaday.io/files/274271173436768/avi.pdf)
- [Microsoft WAVE soundfile format](http://soundfile.sapp.org/doc/WaveFormat/)

### Author
- [13517066 | Willy Santoso](https://github.com/willysantoso05)
- [13517131 | Jan Meyer Saragih](https://github.com/Meyjan)
- [13517137 | Vincent Budianto](https://github.com/vincentbudianto)
