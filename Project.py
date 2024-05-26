import os
import sys
import threading
import time
from os.path import basename

import pandas as pd
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QFileDialog, \
    QPushButton, QMessageBox
import torch
from npz import npz
from test import tuili
from txt import write_name
from DefectSegmentation import SegmentationResults

import sys
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QScrollArea
from PyQt5.QtGui import QPixmap, QImage, QPainter
from PyQt5.QtCore import Qt, QRectF
from PyQt5.QtWidgets import QGraphicsView, QGraphicsScene

base_dir = os.path.dirname(os.path.realpath(sys.argv[0]))

class ZoomableGraphicsView(QGraphicsView):
    def __init__(self):
        super().__init__()
        self.setScene(QGraphicsScene())
        self.setTransformationAnchor(QGraphicsView.AnchorUnderMouse)
        self.setRenderHint(QPainter.Antialiasing)
        self.setRenderHint(QPainter.SmoothPixmapTransform)

    def set_image(self, image_path):
        image = QImage(image_path)
        pixmap = QPixmap.fromImage(image)
        self.scene().addPixmap(pixmap)

    def wheelEvent(self, event):
        # Get the current zoom factor
        factor = 1.2 if event.angleDelta().y() > 0 else 0.8

        # Call the zoom method to perform zooming
        self.zoom(factor, event.pos())

    def zoom(self, factor, point=None):
        mouse_old = self.mapToScene(point) if point is not None else None

        # Calculate the new scale factor
        scale_factor = self.transform().scale(factor, factor)
        pix_widget = scale_factor.mapRect(QRectF(0, 0, 1, 1)).width()

        # Limit the zoom range
        if pix_widget > 30 and factor > 1:
            return
        if pix_widget < 0.01 and factor < 1:
            return

        # Apply the scale transformation
        self.scale(factor, factor)

        if point is not None:
            mouse_now = self.mapToScene(point)
            center_now = self.mapToScene(self.viewport().width() // 2, self.viewport().height() // 2)
            center_new = mouse_old - mouse_now + center_now
            self.centerOn(center_new)


class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.image_paths = []  # 存储图片路径
        self.image_paths_test = []  # 存储图片路径
        self.current_index = 0  # 当前显示图片的索引
        self.current_indexx = 0  # 当前显示图片的索引
        self.img2predict = None
        self.origin_shape = ()
        self.full_path = ""
        self.excel_path=None
        self.image_paths_test_xia = None
        self.image_paths_test_shang = None
        self.thread=False

        self.init_ui()


    def init_ui(self):
        self.setObjectName("Form")
        self.resize(1000, 800)
        self.setWindowTitle('缺陷分割系统')
        # 设置窗口标志位以启用最小化、最大化和关闭按钮
        self.setWindowFlags(
            Qt.Window | Qt.WindowMinimizeButtonHint | Qt.WindowMaximizeButtonHint | Qt.WindowCloseButtonHint)
        self.setWindowIcon(QIcon(os.path.join(base_dir, "images/UI/tb.png")))

        # Central widget  整体垂直布局*******************************************
        central_layout = QVBoxLayout()

        self.title=QLabel()
        self.title.setFixedHeight(10)
        central_layout.addWidget(self.title)

        # ************************左右显示屏水平布局******************************************************************************************************
        # Horizontal layout for image labels
        image_layout_rf = QHBoxLayout()

        self.label_right = ZoomableGraphicsView()

        image_layout_rf.addWidget(self.label_right,1)

        # ***************右边显示屏垂直布局****************************************************

        left_layout = QVBoxLayout()

        self.label_left1 = QLabel()
        self.label_left1.setAlignment(Qt.AlignCenter)
        self.label_left1.setStyleSheet("background-color: black;")
        left_layout.addWidget(self.label_left1)

        self.label_left2 = QLabel()
        self.label_left2.setAlignment(Qt.AlignCenter)
        self.label_left2.setStyleSheet("background-color: black;")
        left_layout.addWidget(self.label_left2)

        image_layout_rf.addLayout(left_layout,1)

        central_layout.addLayout(image_layout_rf)
        # ******************************************************************************************************************
        button_layout = QHBoxLayout()

        self.pushButton1 = QPushButton("<")
        self.pushButton1.setFixedWidth(80)
        # self.pushButtonn.clicked.connect(self.show_previous_right_image)
        button_layout.addWidget(self.pushButton1)

        # button_layout.addStretch(1)

        self.file_name_label1 = QLabel()
        self.file_name_label1.setFixedHeight(35)
        # self.file_name_label1.clicked.connect(self.show_file_name1)
        button_layout.addWidget(self.file_name_label1)
        self.file_name_label1.setStyleSheet("font-size: 30px;font-weight: bold;border: 1px solid gray;")

        self.pushButton2 = QPushButton(">")
        self.pushButton2.setFixedWidth(80)
        # self.pushButtonn_2.clicked.connect(self.show_next_right_image)
        button_layout.addWidget(self.pushButton2)

        self.pushButton3 = QPushButton("<")
        self.pushButton3.setFixedWidth(80)
        # self.pushButtonn_3.clicked.connect(self.show_previous_right_image)
        button_layout.addWidget(self.pushButton3)

        self.file_name_label2 = QLabel()
        self.file_name_label2.setFixedHeight(35)
        # self.file_name_label2.clicked.connect(self.show_file_name2)
        button_layout.addWidget(self.file_name_label2)
        self.file_name_label2.setStyleSheet("font-size: 30px;font-weight: bold;border: 1px solid gray;")

        self.pushButton4 = QPushButton(">")
        self.pushButton4.setFixedWidth(80)
        # self.pushButtonn_4.clicked.connect(self.show_next_right_image)
        button_layout.addWidget(self.pushButton4)


        self.pushButton1.clicked.connect(self.show_previous_right_image)
        self.pushButton2.clicked.connect(self.show_next_right_image)
        self.pushButton3.clicked.connect(self.show_previous_image)
        self.pushButton4.clicked.connect(self.show_next_image)

        central_layout.addLayout(button_layout)

        # ***********************************************************************************************************************
        self.title1 = QLabel()
        self.title1.setFixedHeight(10)
        # self.title.setAlignment(Qt.AlignCenter)
        central_layout.addWidget(self.title1)
# *************************************************************************************************************
        # Action buttons
        anjian_layoutt = QHBoxLayout()
        self.pushButton_5 = QPushButton("上传图片")
        self.pushButton_5.setFixedHeight(60)
        self.pushButton_5.setStyleSheet("font-size: 40px;font-weight: bold")
        self.pushButton_5.clicked.connect(self.upload_img)
        anjian_layoutt.addWidget(self.pushButton_5)

        self.pushButton_6 = QPushButton("缺陷分割")
        self.pushButton_6.setFixedHeight(60)
        self.pushButton_6.setStyleSheet("font-size: 40px;font-weight: bold")
        self.pushButton_6.clicked.connect(self.detect_img_thread)
        anjian_layoutt.addWidget(self.pushButton_6)

        # **************************显示OK,NG的控件*****************************************
        self.file_name_label3 = QLabel()
        self.file_name_label3.setFixedHeight(58)
        self.file_name_label3.setStyleSheet("background-color: red; color: white; font-size: 48px; font-weight: bold;border: 1px solid gray;border-radius: 4px;")
        anjian_layoutt.addWidget(self.file_name_label3)
        # **************************显示OK,NG的控件*****************************************

        self.pushButton_6o = QPushButton("OK")
        self.pushButton_6o.setFixedHeight(60)
        self.pushButton_6o.setStyleSheet("font-size: 40px;font-weight: bold")
        self.pushButton_6o.clicked.connect(self.ok_excel)
        anjian_layoutt.addWidget(self.pushButton_6o)

        self.pushButton_6n = QPushButton("NG")
        self.pushButton_6n.setFixedHeight(60)
        self.pushButton_6n.setStyleSheet("font-size: 40px;font-weight: bold")
        self.pushButton_6n.clicked.connect(self.ng_excel)
        anjian_layoutt.addWidget(self.pushButton_6n)

        central_layout.addLayout(anjian_layoutt)

        self.setLayout(central_layout)

# ***************************************************************************************************

    def upload_img(self):
        folder_path = QFileDialog.getExistingDirectory(None, "选择文件夹")
        self.img2predict = folder_path
        if folder_path:
            self.label_left1.clear()
            self.label_left2.clear()
            self.file_name_label3.clear()
            self.file_name_label2.clear()

            self.image_paths_test_xia = None
            self.image_paths_test_shang = None
            self.excel_path=None
            image_files = [os.path.join(folder_path, filename) for filename in os.listdir(folder_path)
                           if filename.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp', '.gif'))]
            if image_files:
                self.image_paths = image_files
                self.show_image(0)

    def detect_img(self):
        # 进行图片检测的操作
        if self.img2predict and self.image_paths_test_xia==None and self.thread==False:
            self.thread = True
            if self.img2predict:
                source = self.img2predict

                current_time = time.strftime("%Y-%m-%d_%H-%M-%S")
                result_folder = os.path.join(base_dir, 'Result_' + current_time)
                # 检查并创建所需的文件夹

                npz_folder = os.path.join(result_folder, 'npz')
                txt_folder = os.path.join(result_folder, 'txt')
                prediction_folder = os.path.join(result_folder, 'prediction')
                display_folder = os.path.join(result_folder, 'display')

                display_folder_shang = os.path.join(result_folder, 'display_shang')

                for folder in [npz_folder, txt_folder, prediction_folder, display_folder,
                               display_folder_shang]:
                    if not os.path.exists(folder):
                        os.makedirs(folder)

                npz(source, npz_folder)
                write_name(npz_folder, txt_folder)

                tuili(npz_folder, txt_folder, prediction_folder)

                self.full_path = prediction_folder
                display_path = display_folder
                display_path_shang = display_folder_shang
                excel_folder = os.path.join(result_folder, 'excel')
                if not os.path.exists(excel_folder):
                    os.makedirs(excel_folder)
                self.excel_path = os.path.join(excel_folder, 'output.xlsx')

                print("--------------Process segmentation results--------------------")
                SegmentationResults(source, self.full_path, display_path, display_path_shang, self.excel_path)

                self.image_paths_test_shang = [os.path.join(display_path_shang, filename) for filename in
                                               os.listdir(display_path_shang)]
                self.image_paths_test_xia = [os.path.join(display_path, filename) for filename in
                                             os.listdir(display_path)]

                self.show_image_test(0)
                self.thread = False

            else:
                # 创建一个提示框
                msgBox = QMessageBox()
                msgBox.setIcon(QMessageBox.Information)
                msgBox.setText("请先上传图片")
                msgBox.setWindowTitle("提示")
                msgBox.exec_()
        else:
            pass

    def detect_img_thread(self):
        thread = threading.Thread(target=self.detect_img)
        thread.start()

    def show_image(self, index):
        if index >= 0 and index < len(self.image_paths):
            self.label_right.set_image(self.image_paths[index])

            file_name = basename(self.image_paths[index])
            self.file_name_label1.setText(file_name)
            self.file_name_label1.setAlignment(Qt.AlignCenter)

    def show_image_test(self, index):
        if index >= 0 and index < len(self.image_paths_test_shang):
            pixmap = QPixmap(self.image_paths_test_shang[index])
            scale_factor = min(self.label_left1.width() / pixmap.width(), self.label_left1.height() / pixmap.height())
            scaled_pixmap = pixmap.scaled(pixmap.width() * scale_factor, pixmap.height() * scale_factor)
            self.label_left1.setPixmap(scaled_pixmap)

            file_name = basename(self.image_paths_test_shang[index])
            self.file_name_label2.setText(file_name)
            self.file_name_label2.setAlignment(Qt.AlignCenter)

            # *************显示OK.NG****************
            file_name = self.file_name_label2.text()

            if self.excel_path:
                excel_path = self.excel_path
                df = pd.read_excel(excel_path)

                indexx = df.index[df['FileName'] == file_name].tolist()

                if indexx:
                    self.file_name_label3.setText(df.at[indexx[0], 'Result'])
                    self.file_name_label3.setAlignment(Qt.AlignCenter)
            # ********************************************************

        if index >= 0 and index < len(self.image_paths_test_xia):
            pixmap = QPixmap(self.image_paths_test_xia[index])
            scale_factor = min(self.label_left2.width() / pixmap.width(), self.label_left2.height() / pixmap.height())
            scaled_pixmap = pixmap.scaled(pixmap.width() * scale_factor, pixmap.height() * scale_factor)
            self.label_left2.setPixmap(scaled_pixmap)

            file_name = basename(self.image_paths_test_xia[index])

        if index >= 0 and index < len(self.image_paths):

            self.label_right.set_image(self.image_paths[index])

            file_name = basename(self.image_paths[index])
            self.file_name_label1.setText(file_name)
            self.file_name_label1.setAlignment(Qt.AlignCenter)

    def show_previous_image(self):
        if self.file_name_label2.text():
            if self.current_indexx > 0:
                self.current_indexx -= 1
                self.show_image_test(self.current_indexx)
        else:
            msgBox = QMessageBox()
            msgBox.setIcon(QMessageBox.Information)
            msgBox.setText("请先进行缺陷分割")
            msgBox.setWindowTitle("提示")
            msgBox.exec_()

    def show_next_image(self):
        if self.file_name_label2.text():
            if self.current_indexx < len(self.image_paths) - 1:
                self.current_indexx += 1
                self.show_image_test(self.current_indexx)
        else:
            msgBox = QMessageBox()
            msgBox.setIcon(QMessageBox.Information)
            msgBox.setText("请先进行缺陷分割")
            msgBox.setWindowTitle("提示")
            msgBox.exec_()

    def show_previous_right_image(self):
        if self.current_index > 0:
            self.current_index -= 1
            self.show_image(self.current_index)

    def show_next_right_image(self):
        if self.current_index < len(self.image_paths) - 1:
            self.current_index += 1
            self.show_image(self.current_index)

    def ok_excel(self):
        if self.excel_path and self.file_name_label2.text():
            file_name = self.file_name_label2.text()
            excel_path = self.excel_path
            df = pd.read_excel(excel_path)

            index = df.index[df['FileName'] == file_name].tolist()

            if index:
                self.file_name_label3.setText('OK')
                self.file_name_label3.setAlignment(Qt.AlignCenter)
                df.at[index[0], 'Result'] = 'OK'
                df.at[index[0], 'Mark'] = '1'

                df.to_excel(excel_path, index=False)
        else:
            msgBox = QMessageBox()
            msgBox.setIcon(QMessageBox.Information)
            msgBox.setText("请先进行缺陷分割")
            msgBox.setWindowTitle("提示")
            msgBox.exec_()

    def ng_excel(self):
        if self.excel_path and self.file_name_label2.text():
            file_name = self.file_name_label2.text()
            excel_path = self.excel_path

            df = pd.read_excel(excel_path)

            index = df.index[df['FileName'] == file_name].tolist()

            if index:
                self.file_name_label3.setText('NG')
                self.file_name_label3.setAlignment(Qt.AlignCenter)
                df.at[index[0], 'Result'] = 'NG'
                df.at[index[0], 'Mark'] = '2'
                df.to_excel(excel_path, index=False)
        else:
            msgBox = QMessageBox()
            msgBox.setIcon(QMessageBox.Information)
            msgBox.setText("请先进行缺陷分割")
            msgBox.setWindowTitle("提示")
            msgBox.exec_()

    def keyPressEvent(self, event):
        print(event.key())
        if event.key() == Qt.Key_A:
            self.pushButton3.click()
        elif event.key() == Qt.Key_D:
            self.pushButton4.click()
        else:
            super().keyPressEvent(event)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
