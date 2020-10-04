# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'video.ui'
#
# Created by: PyQt5 UI code generator 5.15.1
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_Form(object):
    def setupUi(self, Form):
        Form.setObjectName("Form")
        Form.resize(406, 318)
        self.horizontalLayout = QtWidgets.QHBoxLayout(Form)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.video_widget = QtWidgets.QWidget(Form)
        self.video_widget.setObjectName("video_widget")
        self.verticalLayout_6 = QtWidgets.QVBoxLayout(self.video_widget)
        self.verticalLayout_6.setObjectName("verticalLayout_6")
        self.widget = QtWidgets.QWidget(self.video_widget)
        self.widget.setObjectName("widget")
        self.horizontalLayout_5 = QtWidgets.QHBoxLayout(self.widget)
        self.horizontalLayout_5.setObjectName("horizontalLayout_5")
        self.groupBox = QtWidgets.QGroupBox(self.widget)
        self.groupBox.setObjectName("groupBox")
        self.verticalLayout_2 = QtWidgets.QVBoxLayout(self.groupBox)
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.encryption_checkbox = QtWidgets.QCheckBox(self.groupBox)
        self.encryption_checkbox.setObjectName("encryption_checkbox")
        self.verticalLayout_2.addWidget(self.encryption_checkbox)
        self.horizontalLayout_5.addWidget(self.groupBox)
        self.groupBox_3 = QtWidgets.QGroupBox(self.widget)
        self.groupBox_3.setObjectName("groupBox_3")
        self.verticalLayout_4 = QtWidgets.QVBoxLayout(self.groupBox_3)
        self.verticalLayout_4.setObjectName("verticalLayout_4")
        self.randomized_frame_button = QtWidgets.QCheckBox(self.groupBox_3)
        self.randomized_frame_button.setObjectName("randomized_frame_button")
        self.verticalLayout_4.addWidget(self.randomized_frame_button)
        self.randomized_pixel_button = QtWidgets.QCheckBox(self.groupBox_3)
        self.randomized_pixel_button.setObjectName("randomized_pixel_button")
        self.verticalLayout_4.addWidget(self.randomized_pixel_button)
        self.horizontalLayout_5.addWidget(self.groupBox_3)
        self.verticalLayout_6.addWidget(self.widget)
        self.widget_2 = QtWidgets.QWidget(self.video_widget)
        self.widget_2.setObjectName("widget_2")
        self.verticalLayout_3 = QtWidgets.QVBoxLayout(self.widget_2)
        self.verticalLayout_3.setObjectName("verticalLayout_3")
        self.groupBox_2 = QtWidgets.QGroupBox(self.widget_2)
        self.groupBox_2.setObjectName("groupBox_2")
        self.verticalLayout = QtWidgets.QVBoxLayout(self.groupBox_2)
        self.verticalLayout.setObjectName("verticalLayout")
        self.lineEdit = QtWidgets.QLineEdit(self.groupBox_2)
        self.lineEdit.setObjectName("lineEdit")
        self.verticalLayout.addWidget(self.lineEdit)
        self.verticalLayout_3.addWidget(self.groupBox_2)
        self.groupBox_4 = QtWidgets.QGroupBox(self.widget_2)
        self.groupBox_4.setObjectName("groupBox_4")
        self.horizontalLayout_2 = QtWidgets.QHBoxLayout(self.groupBox_4)
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.key_input_text = QtWidgets.QLineEdit(self.groupBox_4)
        self.key_input_text.setObjectName("key_input_text")
        self.horizontalLayout_2.addWidget(self.key_input_text)
        self.verticalLayout_3.addWidget(self.groupBox_4)
        self.verticalLayout_6.addWidget(self.widget_2)
        self.horizontalLayout.addWidget(self.video_widget)

        self.retranslateUi(Form)
        QtCore.QMetaObject.connectSlotsByName(Form)

    def retranslateUi(self, Form):
        _translate = QtCore.QCoreApplication.translate
        Form.setWindowTitle(_translate("Form", "Form"))
        self.groupBox.setTitle(_translate("Form", "Encryption"))
        self.encryption_checkbox.setText(_translate("Form", "Enable"))
        self.groupBox_3.setTitle(_translate("Form", "Random"))
        self.randomized_frame_button.setText(_translate("Form", "Randomized Frame"))
        self.randomized_pixel_button.setText(_translate("Form", "Randomized Pixel"))
        self.groupBox_2.setTitle(_translate("Form", "N - bit"))
        self.groupBox_4.setTitle(_translate("Form", "Key"))
