import mimetypes

from backend import *
import os

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_MainWindow(object):
    def __init__(self):
        self.stego_list = [
            ("Image LSB", imageLSB()),
            ("Image BPCS", imageBPCS()),
            ("Video", AviStegano()),
            ("Audio", Audio())
        ]
        self.stego = self.stego_list[0]
        self.file_name = ''
        self.file_type = ''
        self.file_extension = ''
        self.result_file_path = ''

    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(600, 600)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.verticalLayout_5 = QtWidgets.QVBoxLayout(self.centralwidget)
        self.verticalLayout_5.setObjectName("verticalLayout_5")
        self.header_frame = QtWidgets.QFrame(self.centralwidget)
        self.header_frame.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.header_frame.setFrameShadow(QtWidgets.QFrame.Raised)
        self.header_frame.setObjectName("header_frame")
        self.horizontalLayout_3 = QtWidgets.QHBoxLayout(self.header_frame)
        self.horizontalLayout_3.setObjectName("horizontalLayout_3")
        self.choose_stego_dropdown = QtWidgets.QComboBox(self.header_frame)
        self.choose_stego_dropdown.setMinimumSize(QtCore.QSize(0, 50))
        font = QtGui.QFont()
        font.setPointSize(13)
        self.choose_stego_dropdown.setFont(font)
        self.choose_stego_dropdown.setObjectName("choose_stego_dropdown")
        self.choose_stego_dropdown.addItem("")
        self.choose_stego_dropdown.addItem("")
        self.choose_stego_dropdown.addItem("")
        self.choose_stego_dropdown.addItem("")
        self.horizontalLayout_3.addWidget(self.choose_stego_dropdown)
        self.open_media_button = QtWidgets.QPushButton(self.header_frame)
        self.open_media_button.setMinimumSize(QtCore.QSize(0, 50))
        font = QtGui.QFont()
        font.setPointSize(13)
        self.open_media_button.setFont(font)
        self.open_media_button.setObjectName("open_media_button")
        self.horizontalLayout_3.addWidget(self.open_media_button)
        self.verticalLayout_5.addWidget(self.header_frame)

        ### MULAI IMAGE LSB
        self.option_frame = QtWidgets.QFrame(self.centralwidget)
        self.option_frame.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.option_frame.setFrameShadow(QtWidgets.QFrame.Raised)
        self.option_frame.setObjectName("option_frame")
        self.horizontalLayout_4 = QtWidgets.QHBoxLayout(self.option_frame)
        self.horizontalLayout_4.setObjectName("horizontalLayout_4")

        # INSERT OPTIONS #

        self.verticalLayout_5.addWidget(self.option_frame)
        self.footer_frame = QtWidgets.QFrame(self.centralwidget)
        self.footer_frame.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.footer_frame.setFrameShadow(QtWidgets.QFrame.Raised)
        self.footer_frame.setObjectName("footer_frame")
        self.verticalLayout = QtWidgets.QVBoxLayout(self.footer_frame)
        self.verticalLayout.setObjectName("verticalLayout")
        self.widget_2 = QtWidgets.QWidget(self.footer_frame)
        self.widget_2.setObjectName("widget_2")
        self.horizontalLayout_6 = QtWidgets.QHBoxLayout(self.widget_2)
        self.horizontalLayout_6.setObjectName("horizontalLayout_6")
        self.embeed_button = QtWidgets.QPushButton(self.widget_2)
        font = QtGui.QFont()
        font.setPointSize(20)
        font.setBold(True)
        font.setWeight(75)
        self.embeed_button.setFont(font)
        self.embeed_button.setObjectName("embeed_button")
        self.horizontalLayout_6.addWidget(self.embeed_button)
        self.extract_button = QtWidgets.QPushButton(self.widget_2)
        font = QtGui.QFont()
        font.setPointSize(20)
        font.setBold(True)
        font.setWeight(75)
        self.extract_button.setFont(font)
        self.extract_button.setObjectName("extract_button")
        self.horizontalLayout_6.addWidget(self.extract_button)
        self.verticalLayout.addWidget(self.widget_2)
        self.groupBox_5 = QtWidgets.QGroupBox(self.footer_frame)
        self.groupBox_5.setObjectName("groupBox_5")
        self.horizontalLayout_8 = QtWidgets.QHBoxLayout(self.groupBox_5)
        self.horizontalLayout_8.setObjectName("horizontalLayout_8")
        self.open_initial_button = QtWidgets.QPushButton(self.groupBox_5)
        font = QtGui.QFont()
        font.setPointSize(15)
        self.open_initial_button.setFont(font)
        self.open_initial_button.setObjectName("open_initial_button")
        self.horizontalLayout_8.addWidget(self.open_initial_button)
        self.open_result_button = QtWidgets.QPushButton(self.groupBox_5)
        font = QtGui.QFont()
        font.setPointSize(15)
        self.open_result_button.setFont(font)
        self.open_result_button.setObjectName("open_result_button")
        self.horizontalLayout_8.addWidget(self.open_result_button)
        self.verticalLayout.addWidget(self.groupBox_5)
        self.info_text = QtWidgets.QPlainTextEdit(self.footer_frame)
        self.info_text.setObjectName("info_text")
        self.verticalLayout.addWidget(self.info_text)
        self.verticalLayout_5.addWidget(self.footer_frame)
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 600, 22))
        self.menubar.setObjectName("menubar")
        self.menuStegonya_Meyer = QtWidgets.QMenu(self.menubar)
        self.menuStegonya_Meyer.setObjectName("menuStegonya_Meyer")
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)
        self.menubar.addAction(self.menuStegonya_Meyer.menuAction())

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

        self.open_media_button.clicked.connect(self.openMediaFile)
        self.choose_stego_dropdown.currentIndexChanged.connect(self.change_stego)
        self.open_initial_button.clicked.connect(self.open_initial_file)
        self.open_result_button.clicked.connect(self.open_result_file)
        self.embeed_button.clicked.connect(self.embedding)
        self.extract_button.clicked.connect(self.extract)

        self.stego[1].render(self)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "MainWindow"))
        self.choose_stego_dropdown.setItemText(0, _translate("MainWindow", "Image (LSB)"))
        self.choose_stego_dropdown.setItemText(1, _translate("MainWindow", "Image (BPCS)"))
        self.choose_stego_dropdown.setItemText(2, _translate("MainWindow", "Video"))
        self.choose_stego_dropdown.setItemText(3, _translate("MainWindow", "Audio"))
        self.open_media_button.setText(_translate("MainWindow", "Open Media File"))
        self.embeed_button.setText(_translate("MainWindow", "Embeed"))
        self.extract_button.setText(_translate("MainWindow", "Extract"))
        self.groupBox_5.setTitle(_translate("MainWindow", "Open Media Viewer/Player"))
        self.open_initial_button.setText(_translate("MainWindow", "Initial"))
        self.open_result_button.setText(_translate("MainWindow", "Result"))
        self.menuStegonya_Meyer.setTitle(_translate("MainWindow", "Stegonya Meyer"))

    def open_initial_file(self):
        if self.file_name == "":
            self.info_text.setPlainText("Initial file is still empty")
        else:
            os.startfile(self.file_name)

    def open_result_file(self):
        if self.result_file_path == "":
            self.info_text.setPlainText("Result file is still empty")
        else:
            os.startfile(self.result_file_path)

    def clean(self, layout):
        for i in reversed(range(layout.count())):
            item = layout.takeAt(i)
            widget = item.widget()
            if widget is not None:
                widget.close()
            else:
                self.clean(item.layout())

    def change_stego(self, idx:int):
        self.clean(self.horizontalLayout_4)
        self.stego = self.stego_list[idx]
        self.stego[1].render(self)

    def openMediaFile(self):
        fileName, _ = QtWidgets.QFileDialog.getOpenFileName(
            None,
            "Select Media File",
            "",
            "All Files (*)",
        )
        if fileName:
            print(fileName)
            self.file_name = fileName
            self.appendInfoText("Media file : " + self.file_name)
            mime = mimetypes.guess_type(fileName)
            if mime[0]:
                print(mime)
                self.file_type = mime[0].split('/')[0]
                self.file_extension = mime[0].split('/')[1]

    def embedding(self):
        if self.stego[0] == 'Audio':
            if self.file_type != 'audio' or self.file_extension not in ['wav', '-wav', 'x-wav']:
                self.info_text.setPlainText("Container file extension has to be .wav or .x-wav")
                return -1

            inputFileName, _ = QtWidgets.QFileDialog.getOpenFileName(
                None,
                "Select Input File",
                "",
                "All Files (*)",
            )
            if inputFileName:
                self.info_text.setPlainText("Start Embedding Process")
                self.stego[1].read_container_file(self.file_name)
                self.appendInfoText("Container file read")
                self.stego[1].read_input_file(inputFileName)
                self.appendInfoText("Input file read")

                fileName, _ = QtWidgets.QFileDialog.getSaveFileName(
                    None,
                    "Select File to Save Output File",
                    "",
                    "All Files (*)",
                )
                result = 'FAILED'

                self.appendInfoText("Embedding")
                if fileName:
                    result = self.stego[1].embedding(fileName)
                else:
                    result = self.stego[1].embedding(None)

                if result == 'FAILED':
                    self.appendInfoText("Container file size is too small")
                else:
                    self.result_file_path = result
                    self.appendInfoText("Counting PSNR")
                    self.appendInfoText("PSNR = " + str(self.stego[1].audio_psnr(self.file_name, self.result_file_path)))
            else:
                self.appendInfoText("Error when reading input file")
                return -1

        elif self.stego[0] == 'Image LSB':
            if self.file_type != 'image' or self.file_extension not in ['bmp', 'png']:
                self.info_text.setPlainText("Container file extension has to be .bmp or .png")
                return -1

            inputFileName, _ = QtWidgets.QFileDialog.getOpenFileName(
                None,
                "Select Input File",
                "",
                "All Files (*)",
            )
            if inputFileName:
                self.stego[1].readImage(self.file_name)
                self.appendInfoText("Container file read")

                fileName, _ = QtWidgets.QFileDialog.getSaveFileName(
                    None,
                    "Select File to Save Output Text",
                    "",
                    "All Files (*)",
                )
                result = 'FAILED'

                self.appendInfoText("Embedding")

                if fileName:
                    result = self.stego[1].embed(path = inputFileName, output = fileName)
                else:
                    result = self.stego[1].embed(path = inputFileName)

                if result == 'FAILED':
                    self.appendInfoText("Container file size is too small")
                else:
                    self.result_file_path = result
                    self.appendInfoText("Counting PSNR")
                    self.appendInfoText("PSNR = " + str(self.stego[1].psnr(self.file_name, self.result_file_path)))
            else:
                self.appendInfoText("Error when reading input file")
                return -1

        elif self.stego[0] == 'Image BPCS':
            if self.file_type != 'image' or self.file_extension not in ['bmp', 'png']:
                self.info_text.setPlainText("Container file extension has to be .bmp or .png")
                return -1

            inputFileName, _ = QtWidgets.QFileDialog.getOpenFileName(
                None,
                "Select Input File",
                "",
                "All Files (*)",
            )
            if inputFileName:
                self.stego[1].readImage(self.file_name)
                self.appendInfoText("Container file read")

                fileName, _ = QtWidgets.QFileDialog.getSaveFileName(
                    None,
                    "Select File to Save Output Text",
                    "",
                    "All Files (*)",
                )
                result = 'FAILED'

                self.appendInfoText("Embedding")

                if fileName:
                    result = self.stego[1].embed(path = inputFileName, output = fileName)
                else:
                    result = self.stego[1].embed(path = inputFileName)

                if result == 'FAILED':
                    self.appendInfoText("Container file size is too small")
                else:
                    self.result_file_path = result
                    self.appendInfoText("Counting PSNR")
                    self.appendInfoText("PSNR = " + str(self.stego[1].psnr(self.file_name, self.result_file_path)))
            else:
                self.appendInfoText("Error when reading input file")
                return -1

        elif self.stego[0] == 'Video':
            print("IN")
            if self.file_type != 'video' or self.file_extension not in ['avi', 'x-msvideo']:
                self.info_text.setPlainText("Container file extension has to be .avi")
                return -1
            
            #Reading Video File
            self.appendInfoText("Reading Video File")
            self.stego[1].readVideo(self.file_name)

            input_message_filename, _ = QtWidgets.QFileDialog.getOpenFileName(
                None,
                "Select Message File",
                "",
                "All Files (*)",
            )
            if input_message_filename:
                print(input_message_filename)
                output_filename, _ = QtWidgets.QFileDialog.getSaveFileName(
                    None,
                    "Insert name to save file",
                    ".avi",
                    "All Files (*)",
                )

                self.appendInfoText("Embedding...")
                
                if output_filename:
                    output_name = output_filename.split('/')
                    if output_name[-1] == '' or output_name[-1] == '.avi':
                        output_name[-1] = 'embed_' + (self.file_name).split('/')[-1]
                        output_filename = '/'.join(output_name)
                else:
                    output_filename = 'embed_' + (self.file_name).split('/')[-1]

                print(output_filename)
                result = self.stego[1].embeed(input_message_filename, output_filename)

                if result == 'FAILED':
                    self.appendInfoText("Container file size is too small")
                else:
                    self.result_file_path = result
                    self.appendInfoText("Counting PSNR")
                    self.appendInfoText("PSNR = " + str(self.stego[1].psnr()))
            else:
                self.appendInfoText("Error when reading input file")
                return -1

    def extract(self):
        if self.stego[0] == 'Audio':
            if self.file_type != 'audio' or self.file_extension not in ['wav', '-wav', 'x-wav']:
                self.info_text.setPlainText("Container file extension has to be .wav or .x-wav")
                return -1

            self.info_text.setPlainText("Start Extraction Process")
            self.stego[1].read_container_file(self.file_name)
            self.appendInfoText("Container file read")

            fileName, _ = QtWidgets.QFileDialog.getSaveFileName(
                None,
                "Select File to Save Output File",
                "",
                "All Files (*)",
            )

            result = 'FAILED'
            self.appendInfoText("Extracting")
            if fileName:
                result = self.stego[1].extract(fileName)
            else:
                result = self.stego[1].extract(None)

            self.result_file_path = result
            self.appendInfoText("Finished extracting in " + result)

        elif self.stego[0] == 'Image LSB':
            if self.file_type != 'image' or self.file_extension not in ['bmp', 'png']:
                self.info_text.setPlainText("Container file extension has to be .bmp or .png")
                return -1

            self.info_text.setPlainText("Start Extraction Process")
            self.stego[1].readImage(self.file_name)
            self.appendInfoText("Container file read")

            fileName, _ = QtWidgets.QFileDialog.getSaveFileName(
                None,
                "Select File to Save Output File",
                "",
                "All Files (*)",
            )

            result = 'FAILED'
            self.appendInfoText("Extracting")
            if fileName:
                result = self.stego[1].extract(output = fileName)
            else:
                result = self.stego[1].extract()

            self.result_file_path = result
            self.appendInfoText("Finished extracting in " + result)

        elif self.stego[0] == 'Image BPCS':
            if self.file_type != 'image' or self.file_extension not in ['bmp', 'png']:
                self.info_text.setPlainText("Container file extension has to be .bmp or .png")
                return -1

            self.info_text.setPlainText("Start Extraction Process")
            self.stego[1].readImage(self.file_name)
            self.appendInfoText("Container file read")

            fileName, _ = QtWidgets.QFileDialog.getSaveFileName(
                None,
                "Select File to Save Output File",
                "",
                "All Files (*)",
            )

            result = 'FAILED'
            self.appendInfoText("Extracting")
            if fileName:
                result = self.stego[1].extract(output = fileName)
            else:
                result = self.stego[1].extract()

            self.result_file_path = result
            self.appendInfoText("Finished extracting in " + result)

        elif self.stego[0] == 'Video':
            if self.file_type != 'video' or self.file_extension not in ['avi', 'x-msvideo']:
                self.info_text.setPlainText("Container file extension has to be .avi")
                return -1

            self.info_text.setPlainText("Start Extraction Process")
            self.stego[1].readVideo(self.file_name)
            self.appendInfoText("Container file read")

            output_message_filename, _ = QtWidgets.QFileDialog.getSaveFileName(
                None,
                "Select File to Save Output File",
                "",
                "All Files (*)",
            )

            result = 'FAILED'
            self.appendInfoText("Extracting")
            if output_message_filename:
                result = self.stego[1].extract(output_message_filename)
            else:
                result = self.stego[1].extract()

            self.result_file_path = result
            self.appendInfoText("Finished extracting in " + result)

    def appendInfoText(self, text):
        self.info_text.appendPlainText(text)

if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    MainWindow = QtWidgets.QMainWindow()
    ui = Ui_MainWindow()
    ui.setupUi(MainWindow)
    MainWindow.show()
    sys.exit(app.exec_())
