import os
import sqlite3
from datetime import datetime

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QStandardItemModel, QStandardItem, QColor, QFont
from PyQt6.QtWidgets import QFileDialog, QDialog, QMessageBox

from services.db_dialogue_data import import_dialogue_data, delete_dataset_by_name
from ui.dialog_new_dataset import Ui_Dialog_new_dataset
from ui.ui_utils import autoResizeColumnsWithStretch
from utils.file_utils import DIALOGUE_DB_PATH


class DataSetManager:
    def __init__(self, main_window, parent=None):

        self.main_window = main_window
        self.parent = parent
        self.main_window.new_dataset_pushButton.clicked.connect(self.show_file_dialog)

    def show_file_dialog(self):
        try:
            dialog = FileDialog(self.parent)
            default_name = "数据集_" + datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
            dialog.ui.new_dataset_name_lineEdit.setText(default_name)
            if dialog.exec() == QDialog.DialogCode.Accepted:
                # 在这里处理对话框的结果，比如获取文件名
                fileName = dialog.ui.new_dataset_name_lineEdit.text()  # 用户填写的数据集名称
                filePath = dialog.ui.new_dataset_path_lineEdit.text()  # 用户选择的文件路径

                if fileName and filePath:
                    # 检查文件是否存在
                    if os.path.exists(filePath):
                        print(f"选择的文件是: {filePath}")
                        import_dialogue_data(fileName, filePath, use_existing_db=False)
                        self.setup_dataset_table_view()
                    else:
                        QMessageBox.warning(self.parent, "文件不存在", "选择的文件不存在，请重新选择。",
                                            QMessageBox.StandardButton.Ok)
                else:
                    QMessageBox.information(self.parent, "信息不完整", "请填写完整的数据集名称和路径。",
                                            QMessageBox.StandardButton.Ok)

        except Exception as e:
            print(f"选择文件时发生错误: {e}")
            QMessageBox.critical(self.parent, "错误", f"选择文件时发生错误，请检查数据格式: {e}")

    def setup_dataset_table_view(self):
        conn = sqlite3.connect(DIALOGUE_DB_PATH)
        cursor = conn.cursor()

        cursor.execute("SELECT id, data_name, import_time FROM meta_table")
        rows = cursor.fetchall()

        conn.close()

        self.model = QStandardItemModel(len(rows), 4)  # 假设有4列，包括操作列

        self.model.setHorizontalHeaderLabels(["ID", "数据集名称", "导入时间", "操作"])

        if rows:
            for row_index, row in enumerate(rows):
                for column_index, item in enumerate(row):
                    item = QStandardItem(str(item))
                    item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)  # 设置文本居中
                    self.model.setItem(row_index, column_index, item)

                # 在"操作"列添加"删除"文本与字体样式#####################
                delete_item = QStandardItem("删除")
                delete_item.setForeground(QColor('blue'))  # 设置字体颜色为蓝色
                font = QFont()  # 创建一个新的字体对象
                font.setUnderline(True)  # 设置字体为下划线，模仿链接的外观
                delete_item.setFont(font)
                delete_item.setFlags(Qt.ItemFlag.ItemIsSelectable | Qt.ItemFlag.ItemIsEnabled)  # 设置为不可编辑但可选
                delete_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)  # 设置文本居中
                self.model.setItem(row_index, 3, delete_item)
                ###############################################################

        self.main_window.DataSetManagerTableView.setModel(self.model)
        self.main_window.DataSetManagerTableView.verticalHeader().setVisible(False)
        autoResizeColumnsWithStretch(self.main_window.DataSetManagerTableView)
        # 连接表格的clicked信号到槽函数
        # 断开之前的连接
        try:
            self.main_window.DataSetManagerTableView.clicked.disconnect()
        except Exception as e:
            pass  # 如果之前没有连接，则忽略错误
        # 重新连接信号
        self.main_window.DataSetManagerTableView.clicked.connect(self.on_table_view_clicked)

    def on_table_view_clicked(self, index):
        if index.column() == 3:  # 检查是否点击了“操作”列
            # 获取该行第二列（数据集名称）的内容
            data_name = self.model.item(index.row(), 1).text()
            reply = QMessageBox.question(self.main_window, '确认', '您确定要删除这条数据吗？',
                                         QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                                         QMessageBox.StandardButton.No)
            if reply == QMessageBox.StandardButton.Yes:
                self.delete_row(data_name)

    def delete_row(self, data_name):
        # 实现删除数据的逻辑
        print(f"正在删除名为 '{data_name}' 的数据集...")
        # 在这里添加从数据库删除记录的代码
        delete_dataset_by_name(data_name)
        # 删除后，可能需要刷新表格视图来反映更改
        self.setup_dataset_table_view()  # 重新加载数据显示

    def on_new_dataset_clicked(self):
        try:
            # 弹出文件选择对话框，让用户选择CSV文件
            dataPath, _ = QFileDialog.getOpenFileName(self.main_window, "选择CSV文件", "", "CSV files (*.csv)")
            print(f"选择的文件路径为：{dataPath}")
        except Exception as e:
            print(f"选择文件时发生错误: {e}")

        # 检查用户是否真的选择了文件
        if dataPath:
            dataName = self.main_window.dataset_name_lineEdit.text()  # 获取用户输入的数据集名称
            try:
                # 调用import_data_to_db函数，将CSV文件导入数据库
                import_dialogue_data(dataName, dataPath, use_existing_db=False)
                self.setup_dataset_table_view()  # 重新加载数据
                print("数据导入成功")
            except Exception as e:
                print(f"导入数据时发生错误: {e}")
        else:
            print("未选择文件")


class FileDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.ui = Ui_Dialog_new_dataset()
        self.ui.setupUi(self)
        self.ui.new_dataset_pushButton.clicked.connect(self.select_file)

    def select_file(self):
        # 使用 QFileDialog 让用户选择文件，并将选择的文件路径显示在 QLineEdit 中
        filePath, _ = QFileDialog.getOpenFileName(self, "选择文件", "", "CSV files (*.csv)")
        if filePath:
            self.ui.new_dataset_path_lineEdit.setText(filePath)
