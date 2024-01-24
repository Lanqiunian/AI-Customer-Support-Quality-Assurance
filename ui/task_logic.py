import sqlite3
from datetime import datetime

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QStandardItemModel, QStandardItem, QColor, QFont
from PyQt6.QtWidgets import QTableView, QMessageBox

from services.db_task import Task
from ui.ui_utils import autoResizeColumnsWithStretch
from utils.file_utils import TASK_DB_PATH, DIALOGUE_DB_PATH, SCHEME_DB_PATH


class TaskManager:
    def __init__(self, main_window, parent=None):

        self.selected_scheme = None
        self.selected_dataset = []
        self.main_window = main_window
        self.parent = parent
        self.main_window.task_tableView.clicked.connect(self.on_choosing_dataset_table_view_clicked)
        self.main_window.new_task_pushButton.clicked.connect(self.on_new_task_button_clicked)
        self.main_window.next_step_pushButton.clicked.connect(self.next_step)
        self.step_of_create_task = 1

    def setup_task_table_view(self):
        conn = sqlite3.connect(TASK_DB_PATH)
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM tasks")
        tasks = cursor.fetchall()

        self.model_setup_task_table_view = QStandardItemModel(len(tasks), 7)  # 根据列的实际数量调整

        self.model_setup_task_table_view.setHorizontalHeaderLabels(
            ["任务ID", "任务名称", "描述", "使用方案", "人工复检", "数据集名称", "操作"])

        for row_index, task in enumerate(tasks):
            task_id = task[0]
            # 查询当前任务绑定的所有数据集名称
            cursor.execute("SELECT data_name FROM datasets WHERE task_id=?", (task_id,))
            datasets = cursor.fetchall()
            datasets_names = ', '.join([dataset[0] for dataset in datasets])  # 将数据集名称合并成一个字符串

            for column_index, item in enumerate(task):
                if column_index == 4:  # 特别处理“人工复检”列
                    manual_check = "是" if item == 1 else "否"  # 根据布尔值显示“是”或“否”
                    print(manual_check)
                    item = QStandardItem(manual_check)
                else:
                    item = QStandardItem(str(item))
                item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)  # 设置文本居中
                self.model_setup_task_table_view.setItem(row_index, column_index, item)

            # 单独处理数据集名称列
            datasets_item = QStandardItem(datasets_names)
            datasets_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.model_setup_task_table_view.setItem(row_index, 5, datasets_item)

            # 在"操作"列添加"查看"文本与字体样式
            action_item = QStandardItem("查看")
            action_item.setForeground(QColor('blue'))
            font = QFont()
            font.setUnderline(True)
            action_item.setFont(font)
            action_item.setFlags(Qt.ItemFlag.ItemIsSelectable | Qt.ItemFlag.ItemIsEnabled)  # 设置为不可编辑但可选
            action_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.model_setup_task_table_view.setItem(row_index, 6, action_item)

        self.main_window.task_tableView.setModel(self.model_setup_task_table_view)
        self.main_window.task_tableView.verticalHeader().setVisible(False)
        autoResizeColumnsWithStretch(self.main_window.task_tableView)

        # 断开之前的连接
        try:
            self.main_window.task_tableView.clicked.disconnect()
        except Exception:
            pass  # 如果之前没有连接，则忽略错误

        # 重新连接信号
        self.main_window.task_tableView.clicked.connect(self.on_table_view_clicked)

        conn.close()

    def on_table_view_clicked(self, index):
        try:
            if index.column() == 6:
                task_name = self.model_setup_task_table_view.item(index.row(), 1).text()
                # self.main_window.show_task_detail(task_name)
                print(f"查看了{task_name}的详情")
        except Exception as e:
            print(f"点击表格视图时发生错误：{e}")

    def on_new_task_button_clicked(self):
        print("点击了新建任务按钮")
        self.main_window.stackedWidget.setCurrentIndex(9)
        self.setup_choosing_dataset_table_view()

    def setup_choosing_dataset_table_view(self):
        try:
            self.main_window.previous_step_pushButton.hide()
            self.main_window.task_name_lineEdit.hide()
            self.main_window.task_description_textEdit.hide()
            self.main_window.task_description_label.hide()
            self.main_window.task_name_label.hide()
            self.main_window.manual_check_checkBox.hide()
        except Exception as e:
            print(f"隐藏上一步按钮时发生错误：{e}")

        conn = sqlite3.connect(DIALOGUE_DB_PATH)
        cursor = conn.cursor()

        cursor.execute("SELECT id, data_name, import_time FROM meta_table")
        rows = cursor.fetchall()
        conn.close()

        # 假设有3列数据加上一列复选框
        self.model = QStandardItemModel(len(rows), 4)
        self.model.setHorizontalHeaderLabels(["选择", "ID", "数据集名称", "导入时间"])

        for row_index, row_data in enumerate(rows):
            # 在每行的开始添加复选框
            check_item = QStandardItem()
            check_item.setCheckable(True)
            check_item.setCheckState(Qt.CheckState.Unchecked)
            self.model.setItem(row_index, 0, check_item)

            # 添加其余的数据项
            for column_index, item_data in enumerate(row_data, 1):  # 注意，从1开始，因为0被复选框占用了
                item = QStandardItem(str(item_data))
                item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                self.model.setItem(row_index, column_index, item)

        self.main_window.choose_dataset_tableView.setModel(self.model)
        self.main_window.choose_dataset_tableView.verticalHeader().setVisible(False)
        autoResizeColumnsWithStretch(self.main_window.choose_dataset_tableView)

        # 断开之前的连接
        try:
            self.main_window.choose_dataset_tableView.clicked.disconnect()
        except Exception:
            pass  # 如果之前没有连接，则忽略错误

        # 重新连接信号到新的槽函数
        self.main_window.choose_dataset_tableView.clicked.connect(self.on_choosing_dataset_table_view_clicked)

    def on_choosing_dataset_table_view_clicked(self, index):
        # 如果点击的是复选框所在的列
        if index.column() == 0:
            item = self.model.itemFromIndex(index)
            # 切换复选框的状态
            new_state = Qt.CheckState.Checked if item.checkState() == Qt.CheckState.Unchecked else Qt.CheckState.Unchecked
            item.setCheckState(new_state)

    def setup_scheme_selection_table_view(self):

        conn = sqlite3.connect(SCHEME_DB_PATH)
        cursor = conn.cursor()
        cursor.execute("SELECT scheme_name, description FROM Schemes")
        schemes = cursor.fetchall()
        conn.close()

        # 创建模型
        self.scheme_model = QStandardItemModel(len(schemes), 2)

        self.scheme_model.setHorizontalHeaderLabels(["方案名称", "描述"])

        for row_index, (scheme_name, description) in enumerate(schemes):
            # 添加方案名称和描述
            scheme_item = QStandardItem(scheme_name)
            scheme_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            description_item = QStandardItem(description)
            description_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)

            self.scheme_model.setItem(row_index, 0, scheme_item)
            self.scheme_model.setItem(row_index, 1, description_item)

        # 设置模型和一些视图属性
        self.main_window.choose_dataset_tableView.setModel(self.scheme_model)
        self.main_window.choose_dataset_tableView.verticalHeader().setVisible(False)
        self.main_window.choose_dataset_tableView.setSelectionBehavior(QTableView.SelectionBehavior.SelectRows)
        self.main_window.choose_dataset_tableView.setSelectionMode(QTableView.SelectionMode.SingleSelection)

        # 连接表格选中信号到槽函数
        self.main_window.choose_dataset_tableView.selectionModel().selectionChanged.connect(
            self.on_scheme_selection_changed)

    def on_scheme_selection_changed(self, selected, deselected):
        # 获取当前选中的行
        try:
            indexes = selected.indexes()
            if indexes:
                selected_row = indexes[0].row()
                self.selected_scheme = self.scheme_model.item(selected_row, 0).text()  # 获取方案名称
                print(f"Selected Scheme: {self.selected_scheme}")
                # 在这里可以根据选择的方案进行进一步的操作
        except Exception as e:
            print(f"选择方案时发生错误：{e}")
            raise

    def next_step(self):
        if self.step_of_create_task == 1:

            for row in range(self.model.rowCount()):
                if self.model.item(row, 0).checkState() == Qt.CheckState.Checked:
                    self.selected_dataset.append(self.model.item(row, 2).text())

            # 如果没有选中任何数据集，则弹出警告对话框
            if not self.selected_dataset:
                self.main_window.show_warning_message("请选择数据集")
                return

            # print(f"选中的数据集为：{self.selected_dataset}")
            self.step_of_create_task = 2
            try:
                self.setup_scheme_selection_table_view()
                self.main_window.previous_step_pushButton.show()
            except Exception as e:
                print(f"设置方案选择表格视图时发生错误：{e}")
            return

        if self.step_of_create_task == 2:
            current_time_str = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
            default_task_name = "task-" + current_time_str

            # 切换到设置任务信息界面，把组件显示出来
            self.main_window.previous_step_pushButton.show()
            self.main_window.task_name_lineEdit.show()
            self.main_window.task_name_lineEdit.setText(default_task_name)
            self.main_window.task_description_textEdit.show()
            self.main_window.task_description_label.show()
            self.main_window.task_name_label.show()
            self.main_window.manual_check_checkBox.show()

            self.main_window.choose_dataset_tableView.hide()
            self.step_of_create_task = 3
            return

        if self.step_of_create_task == 3:
            # 把任务存进表格##############################################################
            task_name = self.main_window.task_name_lineEdit.text()
            task_description = self.main_window.task_description_textEdit.toPlainText()
            selected_scheme = self.selected_scheme
            manual_check = 1 if self.main_window.manual_check_checkBox.isChecked() else 0
            selected_dataset = self.selected_dataset
            new_task = Task(task_name, task_description, selected_scheme, manual_check)
            for dataset in selected_dataset:
                new_task.append_dataset(dataset)
            new_task.save_to_db()
            ##########################################################################

            QMessageBox.information(self.main_window, "成功", "任务创建成功！")
            self.main_window.stackedWidget.setCurrentIndex(3)

            return
