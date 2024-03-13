import sqlite3
from datetime import datetime

from PyQt6.QtCore import Qt, QThread, pyqtSignal
from PyQt6.QtGui import QStandardItemModel, QStandardItem, QColor, QFont, QBrush, QTextOption
from PyQt6.QtWidgets import QTableView, QMessageBox, QTextEdit, QDialog, QVBoxLayout, QLabel

from services.db.db_dialogue_data import get_dialogue_by_datasetname_and_dialogueid
from services.db.db_rule import get_score_by_name, rule_exists
from services.db.db_scheme import update_score_by_HitRulesList
from services.db.db_task import Task, delete_task, get_dialogue_count_by_task_id, get_average_score_by_task_id, \
    get_hit_times_by_task_id, get_hit_rate_by_task_id, remove_hit_rule, get_task_id_by_task_name, add_hit_rule, \
    get_score_by_task_id_and_dialogue_id, change_manual_check, get_manually_check_by_task_id_and_dialogue_id, \
    change_manual_review_corrected_errors, get_AI_prompt_by_task_id, insert_review_comment, check_review_exist
from services.model_api_client import AIAnalysisWorker
from ui.dialog_pick_a_rule import Ui_add_rule_to_scheme_Dialog
from utils.ui_utils import autoResizeColumnsWithStretch, export_model_to_csv
from utils.data_utils import text_to_list, get_score_info_by_name
from utils.global_utils import TASK_DB_PATH, DIALOGUE_DB_PATH, SCHEME_DB_PATH, RULE_DB_PATH, get_global_setting


class TaskManager:
    def __init__(self, main_window, RuleManager_instance, parent=None):

        self.model_task_detail_table_view = None
        self.model_setup_task_table_view = None

        self.hit_rule_model = None
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
        self.main_window.previous_step_pushButton.clicked.connect(self.previous_step)
        self.step_of_create_task = 1
        self.main_window.back_to_dialogue_detail_pushButton.clicked.connect(
            self.on_back_to_dialogue_detail_button_clicked)
        self.main_window.back_to_task_list_pushButton.clicked.connect(self.on_back_to_task_list_button_clicked)
        self.thread_ongoing = False
        self.review_correction = True  # 如果True，代表这个对话没有被人工纠正错误，是正确的

    def on_back_to_task_list_button_clicked(self):

        self.main_window.stackedWidget.setCurrentIndex(3)

    def on_back_to_dialogue_detail_button_clicked(self):

        self.main_window.stackedWidget.setCurrentIndex(11)
        self.main_window.back_to_dialogue_detail_pushButton.hide()

        print("返回对话详情")

    def setup_task_table_view(self):
        conn = sqlite3.connect(TASK_DB_PATH)
        cursor = conn.cursor()
        cursor.execute(
            "SELECT tasks.*, COALESCE(SUM(evaluation_results.manually_check = 1 AND "
            "evaluation_results.manual_review_completed = 0), 0) AS pending_reviews FROM tasks LEFT JOIN "
            "evaluation_results ON tasks.id = evaluation_results.task_id GROUP BY tasks.id")
        tasks = cursor.fetchall()

        self.model_setup_task_table_view = QStandardItemModel(len(tasks), 7)  # 根据列的实际数量调整

        self.model_setup_task_table_view.setHorizontalHeaderLabels(
            ["任务ID", "任务名称", "描述", "使用方案", "需要人工复检", "数据集名称", "操作"])

        for row_index, task in enumerate(tasks):
            task_id = task[0]
            # 查询当前任务绑定的所有数据集名称
            cursor.execute("SELECT data_name FROM datasets WHERE task_id=?", (task_id,))
            datasets = cursor.fetchall()
            datasets_names = ', '.join([dataset[0] for dataset in datasets])  # 将数据集名称合并成一个字符串

            for column_index in range(len(task) - 1):  # 最后一个额外的列是pending_reviews，不需要显示
                item = QStandardItem(str(task[column_index]))
                if column_index == 4:  # 特别处理“需要人工复检”列
                    needs_review = "是" if task[-1] > 0 else "否"  # 根据pending_reviews判断是否需要人工复检
                    item = QStandardItem(needs_review)
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

        # # 断开之前的连接
        # try:
        #     self.main_window.task_tableView.clicked.disconnect()
        # except Exception:
        #     pass  # 如果之前没有连接，则忽略错误

        # 重新连接信号
        self.main_window.task_tableView.clicked.connect(self.on_table_view_clicked)

        conn.close()

    def on_table_view_clicked(self, index):
        print("点击了表格视图")
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
                AI_prompt = get_AI_prompt_by_task_id(task_id) if get_AI_prompt_by_task_id(
                    task_id) else "你的任务是:\n1.识别客服在对话中的表现问题，\n2.给出改善建议。"
                task_description = self.model_setup_task_table_view.item(index.row(), 2).text()
                self.main_window.dialogue_count_label.setText(str(dialogue_count))
                self.main_window.average_score_label.setText(str(average_score))
                self.main_window.hit_times_label.setText(str(hit_times))
                self.main_window.hit_rate_label.setText(str(hit_rates))
                self.main_window.display_AI_prompt_TextEdit.setText(AI_prompt)

                # 设置任务基本信息
                self.main_window.the_task_name_label.setText(self.model_setup_task_table_view.item(0, 1).text())

                if task_description != "":
                    self.main_window.the_task_description_label.setText(
                        task_description)
                    print(f"任务描述：{task_description}")
                else:
                    self.main_window.the_task_description_label.setText("无")


        except Exception as e:
            print(f"点击表格视图时发生错误：{e}")

    def on_delete_task_button_clicked(self):
        task_id = self.model_setup_task_table_view.item(self.main_window.task_tableView.currentIndex().row(), 0).text()
        print(f"尝试删除任务 {task_id}")

        msgBox = QMessageBox(self.main_window)
        msgBox.setWindowTitle("删除任务")
        msgBox.setText(f"你确定要删除任务 {task_id} 吗?")
        msgBox.setIcon(QMessageBox.Icon.Question)

        # 创建自定义按钮
        confirmButton = msgBox.addButton("确认", QMessageBox.ButtonRole.AcceptRole)
        cancelButton = msgBox.addButton("取消", QMessageBox.ButtonRole.RejectRole)

        msgBox.exec()

        # 检查哪个按钮被点击
        if msgBox.clickedButton() == confirmButton:
            print(f"确认删除任务 {task_id}")
            try:
                # 调用删除任务的方法
                delete_task(task_id)
                self.main_window.stackedWidget.setCurrentIndex(3)

                # 刷新任务表格视图
                self.setup_task_table_view()
                # 刷新待办任务视图
                self.main_window.undo_check_manager.setup_undo_check_tableView()
                self.main_window.summary_manager.reset_summary()
            except Exception as e:
                print(f"删除任务后刷新任务表格视图时发生错误：{e}")
        else:
            print(f"取消删除任务 {task_id}")

    def setup_task_detail_table_view(self, task_id):
        # 用于展示任务详情，呈现某个任务所包含对话的列表
        try:
            self.main_window.delete_task_pushButton.clicked.disconnect()
        except Exception:
            pass
        self.main_window.delete_task_pushButton.clicked.connect(self.on_delete_task_button_clicked)
        conn = sqlite3.connect(TASK_DB_PATH)
        cursor = conn.cursor()

        # 获取每个对话的质检结果和命中的规则详情，确保只考虑了同一task_id下的相同dialogue_id
        cursor.execute("""
            SELECT 
                evaluation_results.dialogue_id, 
                evaluation_results.score, 
                evaluation_results.evaluation_time,
                GROUP_CONCAT(hit_rules_details.rule_name, ' ') AS hit_rules,
                evaluation_results.manually_check,
                evaluation_results.manual_review_completed
            FROM evaluation_results
            LEFT JOIN hit_rules_details 
                ON evaluation_results.dialogue_id = hit_rules_details.dialogue_id
                AND evaluation_results.task_id = hit_rules_details.task_id
            WHERE evaluation_results.task_id=?
            GROUP BY evaluation_results.dialogue_id
        """, (task_id,))
        evaluation_results = cursor.fetchall()

        # 设置模型和表格视图
        self.model_task_detail_table_view = QStandardItemModel(0, 9)  # 初始化时行数设置为0
        self.model_task_detail_table_view.setHorizontalHeaderLabels(
            ["对话ID", "任务名称", "质检方案", "所属数据集", "人工复检", "任务时间", "命中规则详情", "质检得分",
             "操作"])

        # 先获取任务基本信息，包括所属数据集
        cursor.execute("SELECT task_name, scheme FROM tasks WHERE id=?", (task_id,))
        task_info = cursor.fetchone()
        task_name, scheme = task_info

        cursor.execute("SELECT data_name FROM datasets WHERE task_id=?", (task_id,))
        datasets = cursor.fetchall()
        datasets_names = ', '.join([dataset[0] for dataset in datasets])  # 将数据集名称合并成一个字符串

        # 填充表格行
        for dialogue_id, score, evaluation_time, hit_rules, manually_check, manual_review_completed in evaluation_results:
            # 当manually_check为1且manual_review_completed为0时，人工复检状态为"是"
            manual_review_status = "是" if manually_check == 1 and manual_review_completed == 0 else "否"

            items = [
                QStandardItem(dialogue_id),
                QStandardItem(task_name),
                QStandardItem(scheme),
                QStandardItem(datasets_names),
                QStandardItem(manual_review_status),  # 使用新计算的人工复检状态
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

        # 设置可滚动视图的模型（保持原有代码不变）
        self.main_window.task_detail_tableView.setModel(self.model_task_detail_table_view)

        # 为固定视图设置相同的模型
        self.main_window.task_detail_tableView_fixed.setModel(self.model_task_detail_table_view)

        # 隐藏固定视图的垂直滚动条
        self.main_window.task_detail_tableView_fixed.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        # 隐藏固定视图的水平滚动条
        self.main_window.task_detail_tableView_fixed.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)

        # 隐藏可滚动视图的最后两列
        for column in range(self.model_task_detail_table_view.columnCount() - 2,
                            self.model_task_detail_table_view.columnCount()):
            self.main_window.task_detail_tableView.setColumnHidden(column, True)

        # 仅在固定视图中显示最后两列
        for column in range(self.model_task_detail_table_view.columnCount() - 2):
            self.main_window.task_detail_tableView_fixed.setColumnHidden(column, True)

        # 同步两个视图的垂直滚动
        self.main_window.task_detail_tableView.verticalScrollBar().valueChanged.connect(
            self.main_window.task_detail_tableView_fixed.verticalScrollBar().setValue
        )
        self.main_window.task_detail_tableView_fixed.verticalScrollBar().valueChanged.connect(
            self.main_window.task_detail_tableView.verticalScrollBar().setValue
        )

        # 配置视图（自适应列宽、隐藏垂直表头等）
        autoResizeColumnsWithStretch(self.main_window.task_detail_tableView)
        autoResizeColumnsWithStretch(self.main_window.task_detail_tableView_fixed)

        # 配置信号和槽（只需为主视图配置即可）
        try:
            self.main_window.task_detail_tableView_fixed.clicked.disconnect()
            self.main_window.export_task_report_pushButton.clicked.disconnect()
        except Exception:
            pass  # 如果之前没有连接，则忽略错误
        self.main_window.export_task_report_pushButton.clicked.connect(
            lambda: export_model_to_csv(self.model_task_detail_table_view, self.main_window, task_id))
        self.main_window.task_detail_tableView_fixed.clicked.connect(self.on_clicked_dialogue_detail)

    def on_click_save_new_comment(self, task_id, dataset_name, dialogue_id, new_comment):
        try:
            if self.main_window.ai_scrollArea.findChild(QTextEdit,
                                                        "Review_Comment").toPlainText() == "正在加载AI分析结果，请稍候...":
                QMessageBox.critical(self.main_window, "错误", "AI分析结果尚未加载完成，请稍后再试！")
                return

            insert_review_comment(task_id, dataset_name, dialogue_id, new_comment)
            self.main_window.stackedWidget.setCurrentIndex(11)
            self.setup_task_detail_table_view(task_id)
            QMessageBox.information(self.main_window, "提示", "保存成功！")
        except Exception as e:
            print(f"保存新的审核建议时发生错误：{e}")

    def on_click_regenerate_AI_pushButton(self, dialogue_data, AI_prompt):
        print("重新生成AI建议")
        self.display_ai_response(dialogue_data, AI_prompt)
        self.main_window.regenerate_AI_pushButton.hide()

    def on_clicked_dialogue_detail(self, index):
        """
        用于展示对话的详细信息，包括对话文本、命中规则详情等
        :param index:
        :return:
        """

        try:
            if index.column() == 8:
                self.review_correction = True
                self.main_window.stackedWidget.setCurrentIndex(11)
                # 获取对话ID和任务名称等基本信息
                dialogue_id = self.model_task_detail_table_view.item(index.row(), 0).text()
                task_name = self.model_task_detail_table_view.item(index.row(), 1).text()
                dataset_name = self.model_task_detail_table_view.item(index.row(), 3).text()
                manually_check = get_manually_check_by_task_id_and_dialogue_id(get_task_id_by_task_name(task_name),
                                                                               dialogue_id)
                self.main_window.regenerate_AI_pushButton.hide()

                try:
                    self.main_window.regenerate_AI_pushButton.clicked.disconnect()
                    self.main_window.save_new_comment_pushButton.clicked.disconnect()
                except Exception:
                    pass
                self.main_window.regenerate_AI_pushButton.clicked.connect(lambda:
                                                                          self.on_click_regenerate_AI_pushButton(
                                                                              dialogue_data, AI_prompt))
                self.main_window.save_new_comment_pushButton.clicked.connect(lambda:
                                                                             self.on_click_save_new_comment(
                                                                                 get_task_id_by_task_name(task_name),
                                                                                 dataset_name, dialogue_id,
                                                                                 self.main_window.ai_scrollArea.findChild(
                                                                                     QTextEdit,
                                                                                     "Review_Comment").toHtml()))
                self.main_window.manually_check_done_pushButton.hide()
                if manually_check == "1":
                    self.main_window.manually_check_pushButton.show()
                else:
                    self.main_window.manually_check_pushButton.hide()

                dialogue_id = int(dialogue_id)
                dialogue_data = get_dialogue_by_datasetname_and_dialogueid(dataset_name, dialogue_id)

                # 设置对话文本的显示
                self.main_window.setupDialogueDisplay(dialogue_data)
                AI_prompt = get_AI_prompt_by_task_id(get_task_id_by_task_name(task_name))
                print(f"AI_prompt: {AI_prompt}")
                # 创建一个线程来执行AI分析
                if check_review_exist(get_task_id_by_task_name(task_name), dialogue_id):
                    self.update_ai_scroll_area(check_review_exist(get_task_id_by_task_name(task_name), dialogue_id))
                    self.main_window.save_new_comment_pushButton.show()
                else:
                    self.display_ai_response(dialogue_data, AI_prompt)

                # 获取命中规则详情
                hit_rules = text_to_list(self.model_task_detail_table_view.item(index.row(), 6).text())
                self.main_window.score_label.setText(self.model_task_detail_table_view.item(index.row(), 7).text())
                self.main_window.dialogue_id_label.setText(str(dialogue_id))
                self.main_window.dataset_name_label.setText(dataset_name)
                self.main_window.manually_check_label.setText(("是" if manually_check == "1" else "否"))
                service = dialogue_data.loc[0, "客服ID"]
                customer = dialogue_data.loc[0, "客户ID"]
                self.main_window.service_id_label.setText(str(service))
                self.main_window.customer_label.setText(str(customer))
                try:
                    self.main_window.back_to_task_detail_pushButton.clicked.disconnect()
                except Exception:
                    pass
                self.main_window.back_to_task_detail_pushButton.clicked.connect(
                    lambda: self.on_clicked_back_to_task_detail(10))  # 返回任务详情

                if hit_rules == ['无']:
                    hit_rules = []
                print(f"命中规则：{hit_rules}")
                self.main_window.hit_rules_tableView.setModel(QStandardItemModel(0, 2))
                self.setup_hit_rules_table_view(hit_rules)
                task_name = self.model_task_detail_table_view.item(index.row(), 1).text()
                task_id = get_task_id_by_task_name(task_name)

                try:  # 把按钮全部解除连接
                    self.main_window.manually_remove_pushButton.clicked.disconnect()
                    self.main_window.manually_add_pushButton.clicked.disconnect()
                    self.main_window.manually_check_pushButton.clicked.disconnect()
                    self.main_window.manually_check_done_pushButton.clicked.disconnect()
                except Exception:
                    pass

                self.main_window.manually_remove_pushButton.clicked.connect(
                    lambda: self.on_clicked_manually_remove_hit_rule(task_id, dialogue_id, hit_rules))
                self.main_window.manually_add_pushButton.clicked.connect(
                    lambda: self.manually_add_hit_rule(task_id, dialogue_id, hit_rules))
                self.main_window.manually_check_pushButton.clicked.connect(
                    self.on_clicked_manually_check_pushButton)
                self.main_window.manually_check_done_pushButton.clicked.connect(
                    lambda: self.on_clicked_manually_check_done_pushButton(task_id, dialogue_id))


        except Exception as e:
            print(f"点击对话详情时发生错误：{e}")

    def on_clicked_manually_check_done_pushButton(self, task_id, dialogue_id):
        dataset_name = self.main_window.dataset_name_label.text()
        try:
            review_comment = self.main_window.ai_scrollArea.findChild(QTextEdit, "Review_Comment").toHtml()
        except Exception as e:
            print(f"获取审核建议时发生错误：{e}")
            review_comment = ""
        if self.main_window.ai_scrollArea.findChild(QTextEdit,
                                                    "Review_Comment").toPlainText() == "正在加载AI分析结果，请稍候...":
            QMessageBox.critical(self.main_window, "错误", "AI分析结果尚未加载完成，请稍后再试！")
            return
        print(f"toHtml()的结果为", self.main_window.ai_scrollArea.findChild(QTextEdit,
                                                                            "Review_Comment").toHtml())
        if get_global_setting().review_complete_inform == 0:
            self.complete_review(task_id, dataset_name, dialogue_id, review_comment)
        else:
            # 创建一个询问框
            reply = QMessageBox.question(self.main_window, '是否完成人工复检?',
                                         "此操作将会关闭人工复检功能，是否继续？",
                                         QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                                         QMessageBox.StandardButton.No)

            if reply == QMessageBox.StandardButton.Yes:

                self.complete_review(task_id, dataset_name, dialogue_id, review_comment)
            else:
                pass

    def complete_review(self, task_id, dataset_name, dialogue_id, review_comment):
        self.main_window.manually_check_done_pushButton.hide()
        self.main_window.manually_check_pushButton.hide()
        # 设置为已被检查
        change_manual_check(task_id, dialogue_id, 1)
        self.main_window.manually_check_label.setText("否")
        # 重设相关显示
        self.setup_task_detail_table_view(task_id)
        self.main_window.undo_check_manager.setup_undo_check_tableView()
        self.main_window.summary_manager.reset_summary()
        try:
            insert_review_comment(task_id, dataset_name, dialogue_id, review_comment)
        except Exception as e:
            print(f"插入审核建议时发生错误：{e}")
        try:
            if not self.review_correction:
                # 如果人工复检时发现了错误，需要修改是否出错的状态，然后回复到原来的状态
                change_manual_review_corrected_errors(task_id, dialogue_id)
                self.review_correction = True

            self.main_window.summary_manager.reset_summary()
            self.main_window.undo_check_manager.setup_undo_check_tableView()
        except Exception as e:
            print(f"完成人工复检时发生错误：{e}")

    def on_clicked_manually_check_pushButton(self):
        # 检查是否在设置中关闭了开始人工复检提示
        if get_global_setting().review_begin_inform == 0:
            self.main_window.manually_check_done_pushButton.show()
            self.main_window.manually_check_pushButton.hide()
            self.main_window.undo_check_manager.setup_undo_check_tableView()
        else:
            reply = QMessageBox.question(self.main_window, '是否进行人工复检',
                                         "进行人工复检，请编辑所命中的规则，然后单击“完成人工复检”。",
                                         QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                                         QMessageBox.StandardButton.No)

            # 根据用户的选择进行操作
            if reply == QMessageBox.StandardButton.Yes:
                # 如果用户点击“是”，则显示按钮

                self.main_window.manually_check_done_pushButton.show()
                self.main_window.manually_check_pushButton.hide()
                self.main_window.undo_check_manager.setup_undo_check_tableView()
            else:
                # 如果用户点击“否”，则不做任何操作（或者根据需要执行其他操作）
                pass

    def on_clicked_manually_remove_hit_rule(self, task_id, dialogue_id, hit_rules=None):
        # 获取当前选中的行对应的规则名称
        print(hit_rules)
        self.review_correction = False
        selected_index = self.main_window.hit_rules_tableView.currentIndex()
        print(f"selected_index: {selected_index}")
        try:
            if selected_index.isValid():
                model = self.main_window.hit_rules_tableView.model()
                rule_name = model.item(selected_index.row(), 0).text()
                print(f"手动移除规则：{rule_name}")
                hit_rules.remove(rule_name)
                remove_hit_rule(task_id, dialogue_id, rule_name)
                print(f"移除规则后的命中规则：{hit_rules}")
                self.setup_hit_rules_table_view(hit_rules)

                # 更新得分
                self.main_window.score_label.setText(str(update_score_by_HitRulesList(task_id, dialogue_id, hit_rules)))
                self.main_window.undo_check_manager.setup_undo_check_tableView()
            else:
                QMessageBox.information(self.main_window, "提示", "请选择要移除的规则")
        except Exception as e:
            print(f"手动移除规则时发生错误：{e}")

    def manually_add_hit_rule(self, task_id, dialogue_id, hit_rules=None):
        AppendHitRuleDialog(task_id, dialogue_id, self, hit_rules, self.main_window).exec()
        self.review_correction = False
        print("重新加载命中规则")
        self.setup_task_detail_table_view(task_id)
        # 更新得分显示
        try:
            self.main_window.score_label.setText(str(get_score_by_task_id_and_dialogue_id(task_id, dialogue_id)))
            self.main_window.undo_check_manager.setup_undo_check_tableView()
        except Exception as e:
            print(f"手动添加规则后更新得分时发生错误：{e}")

    def on_clicked_back_to_task_detail(self, index):
        try:
            self.main_window.stackedWidget.setCurrentIndex(index)
            # 检查AI分析线程是否存在并且正在运行
            if self.thread_ongoing:

                if self.thread.isRunning():
                    self.waitingDialog = WaitingDialog(self.main_window)
                    self.waitingDialog.show()
                    # 连接线程结束信号到槽函数，而不是在这里等待线程结束
                    self.thread.finished.connect(self.on_ai_thread_finished)
                    # 通知工作对象开始终止过程
                    self.worker.finished.emit()
                    # 请求线程退出
                    self.thread.quit()
        except Exception as e:
            print(f"返回对话列表时发生错误：{e}")

    # 修改display_ai_response方法，每次都创建新的线程和工作对象
    def display_ai_response(self, dialogue_data, AI_prompt=None):
        # 初始化显示正在加载的文本

        loadingText = "正在加载AI分析结果，请稍候..."
        self.update_ai_scroll_area(loadingText)

        # 创建新的线程和工作对象
        self.thread = QThread()
        self.worker = AIAnalysisWorker(dialogue_data, AI_prompt)
        self.worker.moveToThread(self.thread)
        # 连接信号
        self.worker.analysisCompleted.connect(self.update_ai_scroll_area)
        self.worker.finished.connect(self.thread.quit)  # 终止工作对象的处理
        self.thread.started.connect(self.worker.process)
        self.thread.finished.connect(self.on_ai_thread_finished)  # 线程结束时的清理
        # 启动线程
        self.thread.start()
        self.thread_ongoing = True

    def on_ai_thread_finished(self):
        # 关闭等待对话框
        if hasattr(self, 'waitingDialog'):
            self.waitingDialog.accept()
        # 清理线程和工作对象
        self.worker.deleteLater()
        if hasattr(self, 'thread'):
            self.thread.deleteLater()
        self.thread_ongoing = False
        # AI线程结束，显示刷新按钮
        self.main_window.regenerate_AI_pushButton.show()

    def update_ai_scroll_area(self, html_content):
        # 直接使用QTextEdit来展示文本内容
        textEdit = QTextEdit(self.main_window.ai_scrollArea)
        textEdit.setObjectName("Review_Comment")
        # textEdit.setReadOnly(True)  # 设置为只读模式
        textEdit.setWordWrapMode(QTextOption.WrapMode.WordWrap)  # 启用自动换行
        textEdit.setHtml(html_content)  # 设置HTML富文本内容

        # 应用样式
        textEdit.setStyleSheet("""
            QTextEdit {
                font-size: 12px;
                color: #333;
                padding: 10px;
                background-color: #f0f0f0;
                border-radius: 5px;
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
        if hit_rules is None:
            hit_rules = []  # 确保hit_rules不为None，避免后续操作引发错误

        hit_rule_model = QStandardItemModel(len(hit_rules), 2)
        hit_rule_model.setHorizontalHeaderLabels(["命中规则", "评分效果"])

        # 只有当hit_rules不为空时，才进行循环
        if hit_rules:  # 这个条件判断等同于 if len(hit_rules) > 0:
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
                if get_score_info_by_name(rule) is not None:
                    score_effect = get_score_info_by_name(rule)

                else:
                    score_effect = "规则已被删除"
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

            self.main_window.back_to_dialogue_detail_pushButton.show()
            if rule_exists(rule_name):
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
            else:
                QMessageBox.information(self.main_window, "提示", "规则已被删除")

    def on_new_task_button_clicked(self):
        self.highlight_step_title()
        self.main_window.stackedWidget.setCurrentIndex(9)
        self.main_window.choose_dataset_tableView.show()
        self.setup_choosing_dataset_table_view()

    def setup_choosing_dataset_table_view(self):
        try:
            self.main_window.previous_step_pushButton.hide()
            self.main_window.create_task_info_frame.hide()
            # 重置创建任务的步骤,解决打断时不重置导致问题。
            self.step_of_create_task = 1



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
        autoResizeColumnsWithStretch(self.main_window.choose_dataset_tableView)

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

            # 如果没有选中任何数据集，则弹出警告对话框
            if not selection_model.selectedRows():
                QMessageBox.warning(self.main_window, "警告", "请选择一个数据集！")
                return

            selected_indexes = selection_model.selectedRows()

            # 获取选中数据集的名称
            selected_index = selected_indexes[0]  # 由于是单选，所以取第一个选中的行
            selected_dataset_name = self.model.item(selected_index.row(), 1).text()  # 假设数据集名称在第二列
            self.selected_dataset = [selected_dataset_name]  # 更新self.selected_dataset为选中的数据集列表

            print(f"选中的数据集为：{self.selected_dataset}")
            self.step_of_create_task += 1  # 进入下一步
            self.highlight_step_title()
            try:
                self.setup_scheme_selection_table_view()  # 设置方案选择视图
                self.main_window.previous_step_pushButton.show()  # 显示上一步按钮
            except Exception as e:
                print(f"设置方案选择表格视图时发生错误：{e}")
            return

        if self.step_of_create_task == 2:
            current_time_str = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
            default_task_name = "质检任务_" + current_time_str

            # 切换到设置任务信息界面，把组件显示出来
            self.main_window.previous_step_pushButton.show()
            self.main_window.create_task_info_frame.show()

            self.main_window.task_name_lineEdit.setText(default_task_name)

            self.main_window.choose_dataset_tableView.hide()
            self.step_of_create_task = 3
            self.highlight_step_title()
            return

        if self.step_of_create_task == 3:

            try:
                # 把任务存进表格##############################################################
                task_name = self.main_window.task_name_lineEdit.text()
                task_description = self.main_window.task_description_textEdit.toPlainText()
                selected_scheme = self.selected_scheme
                print(f"选中的方案为：{selected_scheme}")
                manually_check = 1 if self.main_window.manual_check_checkBox.isChecked() else 0
                selected_dataset = self.selected_dataset
                AI_prompt = self.main_window.AI_prompt_textEdit.toPlainText()
                new_task = Task(task_name, task_description, selected_scheme, manually_check, AI_prompt)
                for dataset in selected_dataset:
                    new_task.append_dataset(dataset)
                print(f"任务名称：{task_name}")
                # 创建等待对话框
                wait_dialog = WaitingDialog()
                wait_dialog.show()

                # 使用 TaskThread 来执行耗时操作
                self.task_thread = TaskThread(new_task, self)
                self.task_thread.taskCompleted.connect(lambda: (wait_dialog.accept(),
                                                                QMessageBox.information(self.main_window, "成功",
                                                                                        "质检任务执行成功！"),
                                                                self.taskCompleted()))  # 任务完成时的其他操作
                self.task_thread.taskFailed.connect(lambda e: QMessageBox.critical(self.main_window, "错误", str(e)))
                # 任务完成时的其他操作
                self.task_thread.start()

                if manually_check == 1:
                    dialogue_count = get_dialogue_count_by_task_id(new_task.task_id)
                    print(f"需要人工复检,对话数：{dialogue_count}")
                else:
                    print("不需要人工复检")

                ##########################################################################


            except Exception as e:
                print(f"创建任务时发生错误：{e}")
                raise
            return

    def taskCompleted(self):
        print("执行任务完成")
        self.setup_task_table_view()

        self.main_window.undo_check_manager.setup_undo_check_tableView()
        self.step_of_create_task = 1
        self.main_window.summary_manager.reset_summary()
        self.main_window.stackedWidget.setCurrentIndex(3)  # 重设一下概览界面的任务基本信息

    def previous_step(self):
        if self.step_of_create_task == 2:
            try:
                # 从方案选择界面返回数据集选择界面
                self.setup_choosing_dataset_table_view()

                self.main_window.previous_step_pushButton.hide()  # 在第一步时隐藏上一步按钮
                self.step_of_create_task -= 1
                self.highlight_step_title()
                return
            except Exception as e:
                print(f"返回数据集选择界面时发生错误：{e}")

        if self.step_of_create_task == 3:
            # 从设置任务信息界面返回方案选择界面

            self.main_window.create_task_info_frame.hide()

            self.setup_scheme_selection_table_view()
            self.main_window.choose_dataset_tableView.show()
            self.step_of_create_task -= 1
            self.highlight_step_title()
            return

    def highlight_step_title(self):
        # 高亮显示当前步骤的标题
        for i in range(1, 4):
            label = getattr(self.main_window, f"step_{i}_label")
            if i == self.step_of_create_task:
                label.setStyleSheet("color: #000; font-weight: bold;")
                print(f"高亮显示步骤{i}的标题")
            else:
                label.setStyleSheet("color: #666; font-weight: normal;")


class WaitingDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent, Qt.WindowType.Dialog | Qt.WindowType.CustomizeWindowHint)
        self.initUI()

    def initUI(self):
        self.setWindowTitle("请稍候")
        layout = QVBoxLayout(self)
        label = QLabel("请稍后...", self)
        layout.addWidget(label)
        self.setLayout(layout)
        self.setModal(True)
        self.adjustSize()


class AppendHitRuleDialog(QDialog):
    def __init__(self, task_id, dialogue_id, task_manager, hit_rules=None, parent=None):  # 会用传递的scheme_name替换掉默认的空字符串
        super().__init__(parent)

        self.ui = Ui_add_rule_to_scheme_Dialog()
        self.ui.setupUi(self)
        self.task_id = task_id
        self.dialogue_id = dialogue_id
        self.task_manager = task_manager
        self.hit_rules = hit_rules

        try:
            self.load_rules_into_combobox()
            self.ui.pick_a_rule_buttonBox.accepted.connect(self.accept_override)

        except Exception as e:
            print(f"初始化发生异常：{e}")
        self.ui.pick_a_rule_comboBox.addItem("请选择规则", None)  # 添加默认选项

    def load_rules_into_combobox(self):
        """从数据库加载规则到下拉框"""
        conn = sqlite3.connect(RULE_DB_PATH)  # 使用正确的数据库路径
        cursor = conn.cursor()
        cursor.execute("SELECT rule_name FROM rule_index")
        for rule_name, in cursor.fetchall():
            self.ui.pick_a_rule_comboBox.addItem(rule_name, rule_name)
        conn.close()

    def accept_override(self):
        """处理确定按钮点击事件"""
        rule_name = self.ui.pick_a_rule_comboBox.currentData()  # 获取当前选中的规则名
        if rule_name is None:
            QMessageBox.warning(self, "错误", "请先选择一个规则")
        else:
            print("选中的规则是:", rule_name)
            # 在这里执行添加规则到方案的操作
            try:

                add_hit_rule(self.task_id, self.dialogue_id, rule_name)
                # 更新命中规则表格
                self.hit_rules.append(rule_name)
                self.task_manager.setup_hit_rules_table_view(self.hit_rules)

            except Exception as e:
                print(f"添加规则到方案时发生错误：{e}")
            # 假设有这样的函数可用
            self.accept()  # 关闭对话框


class TaskThread(QThread):
    taskCompleted = pyqtSignal()  # 任务完成时发出的信号
    taskFailed = pyqtSignal(Exception)  # 任务失败时发出的信号

    def __init__(self, task, Task_Manager):
        super().__init__()
        self.task = task
        self.TaskManager = Task_Manager

    def run(self):
        try:
            self.task.save_to_db()
            self.task.process_task()

            self.taskCompleted.emit()

        except Exception as e:
            self.taskFailed.emit(e)
