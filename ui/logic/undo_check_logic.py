import sqlite3

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QColor, QFont, QStandardItem, QStandardItemModel

from services.db.db_dialogue_data import get_dialogue_by_datasetname_and_dialogueid
from services.db.db_task import get_manually_check_by_task_id_and_dialogue_id, get_AI_prompt_by_task_id
from utils.ui_utils import autoResizeColumnsWithStretch
from utils.data_utils import text_to_list
from utils.global_utils import TASK_DB_PATH


class UndoCheckManager:
    def __init__(self, main_window):

        self.main_window = main_window

    def setup_undo_check_tableView(self):
        # 用于展示需要人工复查的对话详情
        try:
            conn = sqlite3.connect(TASK_DB_PATH)
            cursor = conn.cursor()

            cursor.execute("""
                        SELECT tasks.id AS task_id, tasks.task_name, datasets.data_name, tasks.scheme, 
                        evaluation_results.dialogue_id, evaluation_results.score, 
                        evaluation_results.evaluation_time, GROUP_CONCAT(hit_rules_details.rule_name, ' ') AS hit_rules,
                        evaluation_results.manually_check, evaluation_results.manual_review_completed
                        FROM evaluation_results
                        JOIN tasks ON evaluation_results.task_id = tasks.id
                        JOIN datasets ON tasks.id = datasets.task_id
                        LEFT JOIN hit_rules_details ON evaluation_results.dialogue_id = hit_rules_details.dialogue_id
                               AND evaluation_results.task_id = hit_rules_details.task_id
                        WHERE evaluation_results.manually_check = 1 AND evaluation_results.manual_review_completed = 0
                        GROUP BY evaluation_results.task_id, evaluation_results.dialogue_id
                        ORDER BY evaluation_results.evaluation_time DESC
                    """)
            evaluation_results = cursor.fetchall()

            self.model_undo_check_table_view = QStandardItemModel(0, 9)
            self.model_undo_check_table_view.setHorizontalHeaderLabels(
                ["任务ID", "任务名称", "所属数据集", "质检方案", "对话ID", "任务时间", "命中规则详情", "质检得分",
                 "操作"])

            # 填充表格行
            for task_id, task_name, data_name, scheme, dialogue_id, score, evaluation_time, hit_rules, manually_check, manual_review_completed in evaluation_results:
                manual_review_status = "复核"

                items = [
                    QStandardItem(str(task_id)),
                    QStandardItem(task_name),
                    QStandardItem(data_name),
                    QStandardItem(scheme),
                    QStandardItem(str(dialogue_id)),
                    QStandardItem(evaluation_time),
                    QStandardItem(hit_rules if hit_rules else "无"),
                    QStandardItem(str(score)),
                    QStandardItem(manual_review_status)  # 显示复核状态而非简单的复核操作
                ]
                for item in items[:-1]:  # 除了质检得分和操作列外，设置文本居中
                    item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                action_item = items[-1]
                action_item.setForeground(QColor('blue'))
                font = QFont()
                font.setUnderline(True)
                action_item.setFont(font)
                action_item.setFlags(Qt.ItemFlag.ItemIsSelectable | Qt.ItemFlag.ItemIsEnabled)
                action_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                self.model_undo_check_table_view.appendRow(items)

            # 设置滚动视图的模型
            self.main_window.undo_check_tableView.setModel(self.model_undo_check_table_view)
            # 设置固定视图的模型
            self.main_window.undo_check_tableView_fixed.setModel(self.model_undo_check_table_view)

            # 隐藏可动视图的垂直和水平滚动条
            self.main_window.undo_check_tableView.setVerticalScrollBarPolicy(
                Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
            # 在滚动视图中隐藏最后两列
            self.main_window.undo_check_tableView.setColumnHidden(self.model_undo_check_table_view.columnCount() - 2,
                                                                  True)
            self.main_window.undo_check_tableView.setColumnHidden(self.model_undo_check_table_view.columnCount() - 1,
                                                                  True)

            # 在固定视图中仅显示最后两列
            for column in range(self.model_undo_check_table_view.columnCount() - 2):
                self.main_window.undo_check_tableView_fixed.setColumnHidden(column, True)

            # 同步两个视图的垂直滚动
            self.main_window.undo_check_tableView.verticalScrollBar().valueChanged.connect(
                self.main_window.undo_check_tableView_fixed.verticalScrollBar().setValue
            )
            self.main_window.undo_check_tableView_fixed.verticalScrollBar().valueChanged.connect(
                self.main_window.undo_check_tableView.verticalScrollBar().setValue
            )

            # 配置视图（自适应列宽、隐藏垂直表头等）
            autoResizeColumnsWithStretch(self.main_window.undo_check_tableView)
            autoResizeColumnsWithStretch(self.main_window.undo_check_tableView_fixed)

            try:
                self.main_window.undo_check_tableView.clicked.disconnect()
            except Exception:
                pass  # 如果之前没有连接，则忽略错误
            self.main_window.undo_check_tableView.clicked.connect(self.on_clicked_dialogue_detail)

            try:
                self.main_window.undo_check_tableView_fixed.clicked.disconnect()
            except Exception:
                pass  # 如果之前没有连接，则忽略错误
            self.main_window.undo_check_tableView_fixed.clicked.connect(self.on_clicked_dialogue_detail)

            conn.close()
        except Exception as e:
            print(f"加载需要人工复查的对话时发生错误：{e}")

    def on_clicked_dialogue_detail(self, index):
        """
        展示对话的详细信息，包括对话文本、命中规则详情等
        :param index: 索引
        :return: None
        """
        try:
            if index.column() == 8:  # 如果点击的是操作列
                self.main_window.stackedWidget.setCurrentIndex(11)  # 切换到详细信息视图

                # 获取选中行的任务ID、任务名称、数据集名称、对话ID
                task_id_item = self.model_undo_check_table_view.item(index.row(), 0)
                task_name_item = self.model_undo_check_table_view.item(index.row(), 1)
                data_name_item = self.model_undo_check_table_view.item(index.row(), 2)
                dialogue_id_item = self.model_undo_check_table_view.item(index.row(), 4)

                # 获取对应的文本
                task_id = task_id_item.text()
                task_name = task_name_item.text()
                data_name = data_name_item.text()
                dialogue_id = dialogue_id_item.text()

                # 根据任务ID和对话ID获取是否需要人工复查的状态
                manually_check = get_manually_check_by_task_id_and_dialogue_id(task_id, dialogue_id)
                self.main_window.manually_check_done_pushButton.hide()
                # 根据人工复查状态显示或隐藏按钮
                if manually_check == "1":
                    self.main_window.manually_check_pushButton.show()
                else:
                    self.main_window.manually_check_pushButton.hide()

                # 获取对话数据
                dialogue_data = get_dialogue_by_datasetname_and_dialogueid(data_name, dialogue_id)

                # 显示对话数据
                self.main_window.setupDialogueDisplay(dialogue_data)

                # 执行AI分析
                AI_prompt = get_AI_prompt_by_task_id(task_id)
                self.main_window.Task_Manager.display_ai_response(dialogue_data, AI_prompt)

                # 获取命中规则详情

                hit_rules = text_to_list(self.model_undo_check_table_view.item(index.row(), 6).text())
                print(hit_rules)
                self.main_window.score_label.setText(
                    self.model_undo_check_table_view.item(index.row(), 7).text())  # 质检得分
                self.main_window.dialogue_id_label.setText(dialogue_id)
                self.main_window.dataset_name_label.setText(data_name)
                self.main_window.manually_check_label.setText("是" if manually_check == "1" else "否")
                service = dialogue_data.loc[0, "客服ID"]
                customer = dialogue_data.loc[0, "客户ID"]
                self.main_window.service_id_label.setText(str(service))
                self.main_window.customer_label.setText(str(customer))

                # 清除旧的信号连接
                try:
                    self.main_window.back_to_task_detail_pushButton.clicked.disconnect()
                except Exception:
                    pass  # 如果之前没有连接，则忽略错误

                # 设置返回按钮的新连接
                self.main_window.back_to_task_detail_pushButton.clicked.connect(
                    lambda: self.main_window.Task_Manager.on_clicked_back_to_task_detail(5))

                # 清除并设置命中规则表格
                if hit_rules == ['无']:
                    hit_rules = []
                self.main_window.Task_Manager.setup_hit_rules_table_view(hit_rules)

                # 设置人工复查按钮的信号连接
                try:
                    self.main_window.manually_remove_pushButton.clicked.disconnect()
                    self.main_window.manually_add_pushButton.clicked.disconnect()
                    self.main_window.manually_check_pushButton.clicked.disconnect()
                    self.main_window.manually_check_done_pushButton.clicked.disconnect()
                except Exception:
                    pass  # 如果之前没有连接，则忽略错误

                # 连接人工复查按钮的新信号
                self.main_window.manually_remove_pushButton.clicked.connect(
                    lambda: self.main_window.Task_Manager.on_clicked_manually_remove_hit_rule(task_id, dialogue_id,
                                                                                              hit_rules))
                self.main_window.manually_add_pushButton.clicked.connect(
                    lambda: self.main_window.Task_Manager.manually_add_hit_rule(task_id, dialogue_id, hit_rules))
                self.main_window.manually_check_pushButton.clicked.connect(
                    self.main_window.Task_Manager.on_clicked_manually_check_pushButton)
                self.main_window.manually_check_done_pushButton.clicked.connect(
                    lambda: self.main_window.Task_Manager.on_clicked_manually_check_done_pushButton(task_id,
                                                                                                    dialogue_id))

        except Exception as e:
            print(f"从待办任务点击对话详情时发生错误：{e}")

    def on_clicked_back_to_undo(self):
        """
        返回到待办任务列表
        :return: None
        """
        self.main_window.stackedWidget.setCurrentIndex(5)
        self.main_window.undo_check_manager.setup_undo_check_tableView()
