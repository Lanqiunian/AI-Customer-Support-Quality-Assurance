import sqlite3
from datetime import datetime

from PyQt6.QtCore import Qt, QThread
from PyQt6.QtGui import QStandardItemModel, QStandardItem, QColor, QFont, QBrush, QTextOption
from PyQt6.QtWidgets import QTableView, QMessageBox, QTextEdit

from services.db_dialogue_data import get_dialogue_by_datasetname_and_dialogueid
from services.db_rule import get_score_by_name
from services.db_task import Task, delete_task, get_dialogue_count_by_task_id, get_average_score_by_task_id, \
    get_hit_times_by_task_id, get_hit_rate_by_task_id
from services.model_api_client import AIAnalysisWorker
from ui.ui_utils import autoResizeColumnsWithStretch
from utils.data_utils import text_to_list, get_score_info_by_name
from utils.file_utils import TASK_DB_PATH, DIALOGUE_DB_PATH, SCHEME_DB_PATH


class TaskManager:
    def __init__(self, main_window, RuleManager_instance, parent=None):

        self.aiAnalysisThread = None
        self.rule_manager = None
        self.selected_scheme = None
        self.selected_dataset = []
        self.rule_manager = RuleManager_instance if RuleManager_instance else None
        self.main_window = main_window
        self.parent = parent
        self.main_window.task_tableView.clicked.connect(self.on_choosing_dataset_table_view_clicked)
        self.main_window.new_task_pushButton.clicked.connect(self.on_new_task_button_clicked)
        self.main_window.next_step_pushButton.clicked.connect(self.next_step)
        self.step_of_create_task = 1
        self.main_window.back_to_dialogue_detail_pushButton.clicked.connect(
            self.on_back_to_dialogue_detail_button_clicked)

    def on_back_to_dialogue_detail_button_clicked(self):
        self.main_window.stackedWidget.setCurrentIndex(11)
        self.main_window.back_to_dialogue_detail_pushButton.hide()

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
                task_id = self.model_setup_task_table_view.item(index.row(), 0).text()
                print(f"查看了{task_id}的详情")
                self.main_window.stackedWidget.setCurrentIndex(10)
                self.setup_task_detail_table_view(task_id)

                # 填写质检指标
                dialogue_count = get_dialogue_count_by_task_id(task_id)
                average_score = get_average_score_by_task_id(task_id)
                hit_times = get_hit_times_by_task_id(task_id)
                hit_rates = get_hit_rate_by_task_id(task_id)
                self.main_window.dialogue_count_label.setText(str(dialogue_count))
                self.main_window.average_score_label.setText(str(average_score))
                self.main_window.hit_times_label.setText(str(hit_times))
                self.main_window.hit_rate_label.setText(str(hit_rates))
        except Exception as e:
            print(f"点击表格视图时发生错误：{e}")

    def on_delete_task_button_clicked(self):
        task_id = self.model_setup_task_table_view.item(self.main_window.task_tableView.currentIndex().row(), 0).text()
        print(f"删除了任务 {task_id}")
        try:
            delete_task(task_id)
            self.main_window.stackedWidget.setCurrentIndex(3)

            self.setup_task_table_view()
        except Exception as e:
            print(f"删除任务后刷新任务表格视图时发生错误：{e}")

    def setup_task_detail_table_view(self, task_id):
        # 用于展示任务详情，将每个对话的结果展示
        try:
            self.main_window.delete_task_pushButton.clicked.disconnect()
        except Exception:
            pass
        self.main_window.delete_task_pushButton.clicked.connect(self.on_delete_task_button_clicked)
        conn = sqlite3.connect(TASK_DB_PATH)
        cursor = conn.cursor()

        # 获取每个对话的质检结果和命中的规则详情，确保只考虑了同一task_id下的相同dialogue_id
        cursor.execute("""
            SELECT evaluation_results.dialogue_id, evaluation_results.score, evaluation_results.evaluation_time,
            GROUP_CONCAT(hit_rules_details.rule_name, ' ') AS hit_rules
            FROM evaluation_results
            LEFT JOIN hit_rules_details ON evaluation_results.dialogue_id = hit_rules_details.dialogue_id
            AND evaluation_results.task_id = hit_rules_details.task_id
            WHERE evaluation_results.task_id=?
            GROUP BY evaluation_results.dialogue_id
        """, (task_id,))
        evaluation_results = cursor.fetchall()

        # 设置任务基本信息
        self.main_window.task_id_label.setText(task_id)
        self.main_window.the_task_name_label.setText(self.model_setup_task_table_view.item(0, 1).text())
        # print(f"任务名称：{self.model_setup_task_table_view.item(0, 1).text()}")
        self.main_window.the_task_description_label.setText(self.model_setup_task_table_view.item(0, 2).text())
        # print(f"任务描述：{self.model_setup_task_table_view.item(0, 2).text()}")
        self.main_window.scheme_label.setText(self.model_setup_task_table_view.item(0, 3).text())

        self.main_window.manual_check_label.setText(self.model_setup_task_table_view.item(0, 4).text())
        self.main_window.dataset_label.setText(self.model_setup_task_table_view.item(0, 5).text())

        # 设置模型和表格视图
        self.model_task_detail_table_view = QStandardItemModel(0, 9)  # 初始化时行数设置为0
        self.model_task_detail_table_view.setHorizontalHeaderLabels(
            ["对话ID", "任务名称", "质检方案", "所属数据集", "人工复检", "任务时间", "命中规则详情", "质检得分",
             "操作"])

        # 先获取任务基本信息，包括所属数据集
        cursor.execute("SELECT task_name, scheme, manual_check FROM tasks WHERE id=?", (task_id,))
        task_info = cursor.fetchone()
        task_name, scheme, manual_check = task_info
        manual_check_text = "是" if manual_check else "否"

        cursor.execute("SELECT data_name FROM datasets WHERE task_id=?", (task_id,))
        datasets = cursor.fetchall()
        datasets_names = ', '.join([dataset[0] for dataset in datasets])  # 将数据集名称合并成一个字符串

        # 填充表格行
        for dialogue_id, score, evaluation_time, hit_rules in evaluation_results:
            items = [
                QStandardItem(dialogue_id),
                QStandardItem(task_name),
                QStandardItem(scheme),
                QStandardItem(datasets_names),
                QStandardItem(manual_check_text),
                QStandardItem(evaluation_time),
                QStandardItem(hit_rules if hit_rules else "无"),
                QStandardItem(str(score)),
                QStandardItem("查看")
            ]
            for item in items[:-1]:  # 设置文本居中，除了操作列
                item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            action_item = items[-1]
            action_item.setForeground(QColor('blue'))
            font = QFont()
            font.setUnderline(True)
            action_item.setFont(font)
            action_item.setFlags(Qt.ItemFlag.ItemIsSelectable | Qt.ItemFlag.ItemIsEnabled)
            action_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.model_task_detail_table_view.appendRow(items)

        self.main_window.task_detail_tableView.setModel(self.model_task_detail_table_view)
        self.main_window.task_detail_tableView.verticalHeader().setVisible(False)
        autoResizeColumnsWithStretch(self.main_window.task_detail_tableView)

        # 断开之前的连接
        try:
            self.main_window.task_detail_tableView.clicked.disconnect()
        except Exception:
            pass  # 如果之前没有连接，则忽略错误

        # 重新连接信号
        self.main_window.task_detail_tableView.clicked.connect(self.on_clicked_dialogue_detail)

        conn.close()

    def on_clicked_dialogue_detail(self, index):
        """
        用于展示对话的详细信息，包括对话文本、命中规则详情等
        :param index:
        :return:
        """
        try:
            if index.column() == 8:
                self.main_window.stackedWidget.setCurrentIndex(11)
                # 获取对话ID和任务名称等基本信息
                dialogue_id = self.model_task_detail_table_view.item(index.row(), 0).text()
                task_name = self.model_task_detail_table_view.item(index.row(), 1).text()
                dataset_name = self.model_task_detail_table_view.item(index.row(), 3).text()
                dialogue_id = int(dialogue_id)
                dialogue_data = get_dialogue_by_datasetname_and_dialogueid(dataset_name, dialogue_id)

                # 设置对话文本的显示
                self.main_window.setupDialogueDisplay(dialogue_data)

                # 创建一个线程来执行AI分析
                self.display_ai_response(dialogue_data)

                # 获取命中规则详情
                hit_rules = text_to_list(self.model_task_detail_table_view.item(index.row(), 6).text())
                self.main_window.score_label.setText(self.model_task_detail_table_view.item(index.row(), 7).text())
                self.main_window.dialogue_id_label.setText(str(dialogue_id))
                self.main_window.dataset_name_label.setText(dataset_name)
                service = dialogue_data.loc[0, "客服ID"]
                customer = dialogue_data.loc[0, "客户ID"]
                self.main_window.service_id_label.setText(str(service))
                self.main_window.customer_label.setText(str(customer))
                try:
                    self.main_window.back_to_task_detail_pushButton.clicked.disconnect()
                except Exception:
                    pass
                self.main_window.back_to_task_detail_pushButton.clicked.connect(
                    lambda: self.main_window.stackedWidget.setCurrentIndex(10))  # 返回任务详情

                print(f"命中规则：{hit_rules}")
                self.setup_hit_rules_table_view(hit_rules)
        except Exception as e:
            print(f"点击对话详情时发生错误：{e}")

    def display_ai_response(self, dialogue_data):
        # 初始化显示正在加载的文本
        loadingText = "正在加载AI分析结果，请稍候..."
        self.update_ai_scroll_area(loadingText)

        # 创建线程和工作对象
        self.thread = QThread()
        self.worker = AIAnalysisWorker(dialogue_data)
        self.worker.moveToThread(self.thread)

        # 连接信号
        self.worker.analysisCompleted.connect(self.update_ai_scroll_area)
        self.worker.analysisCompleted.connect(self.thread.quit)  # 分析完成后请求线程退出
        self.thread.started.connect(self.worker.process)
        self.thread.finished.connect(self.thread.deleteLater)  # 线程结束后删除线程对象
        self.worker.analysisCompleted.connect(self.worker.deleteLater)  # 工作完成后删除工作对象

        # 启动线程
        self.thread.start()

    def update_ai_scroll_area(self, text):
        # 直接使用QTextEdit来展示文本内容
        textEdit = QTextEdit(self.main_window.ai_scrollArea)
        textEdit.setReadOnly(True)  # 设置为只读模式
        textEdit.setWordWrapMode(QTextOption.WrapMode.WordWrap)  # 启用自动换行
        textEdit.setText(text)  # 设置文本内容

        # 应用样式
        textEdit.setStyleSheet("""
            QTextEdit {
                font-size: 16px;
                color: #333;
                padding: 10px;
                background-color: #f0f0f0;
                border-radius: 10px;
            }
        """)

        # 将QTextEdit设置为滚动区域的widget
        self.main_window.ai_scrollArea.setWidget(textEdit)

        # 配置QTextEdit的最大宽度，确保内容不会超出滚动区域的宽度
        margin = 20  # 边距大小，可以根据需要调整
        textEdit.setMaximumWidth(self.main_window.ai_scrollArea.width() - margin)

        # 隐藏滚动条
        self.main_window.ai_scrollArea.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.main_window.ai_scrollArea.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)

    def setup_hit_rules_table_view(self, hit_rules=None):

        hit_rule_model = QStandardItemModel(len(hit_rules), 2)
        hit_rule_model.setHorizontalHeaderLabels(["命中规则", "评分效果"])
        if hit_rules[0] is not None:
            for row_index, rule in enumerate(hit_rules):
                # 创建规则名项
                rule_item = QStandardItem(rule)
                rule_item.setForeground(QBrush(QColor('blue')))  # 设置字体颜色为蓝色
                font = QFont()  # 创建字体实例
                font.setUnderline(True)  # 设置字体为带下划线
                rule_item.setFont(font)  # 应用字体
                rule_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                hit_rule_model.setItem(row_index, 0, rule_item)

                # 假设 get_score_info_by_name 函数返回评分效果的文本描述
                score_effect = get_score_info_by_name(rule)
                score_effect_item = QStandardItem(score_effect)
                score_effect_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                hit_rule_model.setItem(row_index, 1, score_effect_item)

        self.main_window.hit_rules_tableView.setModel(hit_rule_model)
        self.main_window.hit_rules_tableView.verticalHeader().setVisible(False)
        autoResizeColumnsWithStretch(self.main_window.hit_rules_tableView)
        self.main_window.hit_rules_tableView.setSelectionBehavior(QTableView.SelectionBehavior.SelectRows)
        self.main_window.hit_rules_tableView.setSelectionMode(QTableView.SelectionMode.SingleSelection)

        # 连接点击信号到槽函数
        self.main_window.hit_rules_tableView.clicked.connect(self.on_hit_rule_clicked)

    def on_hit_rule_clicked(self, index):
        # 确认点击的是命中规则列
        if index.column() == 0:
            rule_name = index.model().item(index.row(), 0).text()
            print(f"Clicked on rule: {rule_name}")
            self.main_window.back_to_dialogue_detail_pushButton.show()

            self.rule_manager.loadRuleDetails(rule_name)
            score_type = int(str(get_score_by_name(rule_name, 0)))
            score_value = str(get_score_by_name(rule_name, 1))
            try:
                self.main_window.score_type_comboBox.setCurrentIndex(score_type)
                print(f"score_type: {score_type}")
                self.main_window.score_value_line_edit.setText(score_value)
                print(f"score_value: {score_value}")
            except Exception as e:
                print(f"on_Clicked_Rule_Detail发生异常：{e}")

    def on_new_task_button_clicked(self):
        print("点击了新建任务按钮")
        self.main_window.stackedWidget.setCurrentIndex(9)
        self.main_window.choose_dataset_tableView.show()
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

        # 假设有3列数据
        self.model = QStandardItemModel(len(rows), 3)
        self.model.setHorizontalHeaderLabels(["ID", "数据集名称", "导入时间"])

        for row_index, row_data in enumerate(rows):
            # 添加数据项
            for column_index, item_data in enumerate(row_data):
                item = QStandardItem(str(item_data))
                item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                self.model.setItem(row_index, column_index, item)

        self.main_window.choose_dataset_tableView.setModel(self.model)
        self.main_window.choose_dataset_tableView.verticalHeader().setVisible(False)
        autoResizeColumnsWithStretch(self.main_window.choose_dataset_tableView)

        # 设置选择模式为单选
        self.main_window.choose_dataset_tableView.setSelectionMode(QTableView.SelectionMode.SingleSelection)
        # 设置选择行为为选择整行
        self.main_window.choose_dataset_tableView.setSelectionBehavior(QTableView.SelectionBehavior.SelectRows)

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
            # 获取当前选中的行
            selection_model = self.main_window.choose_dataset_tableView.selectionModel()
            selected_indexes = selection_model.selectedRows()

            # 如果没有选中任何数据集，则弹出警告对话框
            if not selected_indexes:
                self.main_window.show_warning_message("请选择数据集")
                return

            # 获取选中数据集的名称
            selected_index = selected_indexes[0]  # 由于是单选，所以取第一个选中的行
            selected_dataset_name = self.model.item(selected_index.row(), 1).text()  # 假设数据集名称在第二列
            self.selected_dataset = [selected_dataset_name]  # 更新self.selected_dataset为选中的数据集列表

            print(f"选中的数据集为：{self.selected_dataset}")
            self.step_of_create_task += 1  # 进入下一步
            try:
                self.setup_scheme_selection_table_view()  # 设置方案选择视图
                self.main_window.previous_step_pushButton.show()  # 显示上一步按钮
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
            try:
                # 把任务存进表格##############################################################
                task_name = self.main_window.task_name_lineEdit.text()
                task_description = self.main_window.task_description_textEdit.toPlainText()
                selected_scheme = self.selected_scheme
                manual_check = 1 if self.main_window.manual_check_checkBox.isChecked() else 0
                selected_dataset = self.selected_dataset
                new_task = Task(task_name, task_description, selected_scheme, manual_check)
                for dataset in selected_dataset:
                    new_task.append_dataset(dataset)
                print(f"任务名称：{task_name}")
                new_task.save_to_db()
                print(f"任务描述：{task_description}")
                new_task.process_task()
                ##########################################################################

                QMessageBox.information(self.main_window, "成功", "任务创建成功！")

                self.main_window.stackedWidget.setCurrentIndex(3)
                self.setup_task_table_view()
                self.step_of_create_task = 1
            except Exception as e:
                print(f"创建任务时发生错误：{e}")
                raise
            return
