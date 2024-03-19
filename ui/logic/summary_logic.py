import sqlite3

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QStandardItemModel, QStandardItem
from PyQt6.QtWidgets import QMessageBox

from services.db.db_task import get_overall_info, get_review_statistics
from utils.ui_utils import immersingTableView, autoResizeColumnsWithStretch
from utils.data_utils import create_service_id_avg_score_table, analyzeResponseTime
from utils.global_utils import TASK_DB_PATH, get_global_setting


class SummaryManager:
    def __init__(self, main_window):

        self.main_window = main_window
        self.summary = None
        self.columnsAdjusted = False

    def setup_summary_basic_info(self):
        # 绑定按键点击事件
        self.setup_button_click_event()
        # 设置任务基本信息
        total_dialogue_count, average_score, hit_times, hit_rate = get_overall_info()
        self.main_window.summary_total_dialogues_label.setText(str(total_dialogue_count))
        self.main_window.summary_average_score_label.setText(str(average_score))
        self.main_window.summary_hit_times_label.setText(str(hit_times))
        self.main_window.summary_hit_rate_label.setText(str(hit_rate))

        review_count, review_completion_count, review_mistake_count = get_review_statistics()
        print(review_count, review_completion_count, review_mistake_count)
        if review_count == 0:
            review_completion_rate = '0%'
        else:
            review_completion_rate = str(round(100 * int(review_completion_count) / review_count, 2)) + '%'
        if review_completion_count == 0:
            review_accuracy = '0%'
        else:
            review_accuracy = str(
                round(100 * (review_completion_count - review_mistake_count) / review_completion_count, 2)) + '%'
        self.main_window.summary_dialogue_count_label.setText(str(review_count))
        self.main_window.summary_review_completion_rate_label.setText(review_completion_rate)
        self.main_window.summary_review_accuracy_label.setText(review_accuracy)

        uncompleted_review_count = str(self.main_window.undo_check_manager.model_undo_check_table_view.rowCount())
        print(get_global_setting().user_name)
        user_name = get_global_setting().user_name
        if uncompleted_review_count == '0':
            welcome = '欢迎回来！' + user_name + '，当前没有待办任务😘'
            self.main_window.go_check_commandLinkButton.hide()
        else:
            welcome = '欢迎回来！' + user_name + '，当前有' + uncompleted_review_count + '个待办任务🤣'
            self.main_window.go_check_commandLinkButton.show()
        self.main_window.welcome_label.setText(welcome)

    def setup_button_click_event(self):
        # 设置按钮点击事件
        """
        go_check_commandLinkButton,
        go_rule_pushButton,
        go_scheme_pushButton,
        go_task_pushButton,
        go_check_pushButton,
        go_export_pushButton
        """
        print('setup_button_click_event')
        try:
            self.main_window.go_check_commandLinkButton.clicked.disconnect()
            self.main_window.go_rule_pushButton.clicked.disconnect()
            self.main_window.go_scheme_pushButton.clicked.disconnect()
            self.main_window.go_task_pushButton.clicked.disconnect()
            self.main_window.go_check_pushButton.clicked.disconnect()
            self.main_window.go_export_pushButton.clicked.disconnect()
            self.main_window.reset_pushButton.clicked.disconnect()
        except TypeError:
            pass

        self.main_window.go_check_commandLinkButton.clicked.connect(
            lambda: self.main_window.stackedWidget.setCurrentIndex(5))
        self.main_window.go_rule_pushButton.clicked.connect(
            lambda: self.main_window.stackedWidget.setCurrentIndex(1))
        self.main_window.go_scheme_pushButton.clicked.connect(
            lambda: self.main_window.stackedWidget.setCurrentIndex(2))
        self.main_window.go_task_pushButton.clicked.connect(
            lambda: self.main_window.stackedWidget.setCurrentIndex(3))
        self.main_window.go_check_pushButton.clicked.connect(
            lambda: self.main_window.stackedWidget.setCurrentIndex(5))
        self.main_window.go_export_pushButton.clicked.connect(
            lambda: QMessageBox.information(self.main_window, '提示',
                                            '导出报告，步骤为：\n质检任务→任务管理→查看→导出报告',
                                            QMessageBox.StandardButton.Ok))
        self.main_window.reset_pushButton.clicked.connect(self.reset_summary)

    def setup_tableview_top5_hit_rules(self):
        # 连接到数据库
        conn = sqlite3.connect(TASK_DB_PATH)
        cursor = conn.cursor()

        # 查询每条规则的命中次数，并按命中次数降序排序，只取前5条
        cursor.execute('''
            SELECT rule_name, COUNT(*) AS hit_count
            FROM hit_rules_details
            GROUP BY rule_name
            ORDER BY hit_count DESC
            LIMIT 5
        ''')

        top5_rules = cursor.fetchall()
        conn.close()

        # 设置模型以填充到表格视图
        model = QStandardItemModel(0, 2)  # 0行开始，2列（规则名称和命中次数）
        model.setHorizontalHeaderLabels(['规则名称', '命中次数'])
        # 设置表头居中
        model.setHeaderData(0, Qt.Orientation.Horizontal, Qt.ItemDataRole.TextAlignmentRole,
                            Qt.AlignmentFlag.AlignCenter)

        for row_index, (rule_name, hit_count) in enumerate(top5_rules):
            # 将规则名称和命中次数转化为标准项并添加到模型中
            model.setItem(row_index, 0, QStandardItem(rule_name))
            model.setItem(row_index, 1, QStandardItem(str(hit_count)))
            # 设置居中
            model.item(row_index, 0).setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            model.item(row_index, 1).setTextAlignment(Qt.AlignmentFlag.AlignCenter)

        self.main_window.top_5_hit_tableView.setModel(model)
        self.main_window.top_5_hit_tableView.verticalHeader().setVisible(False)
        if not self.columnsAdjusted:
            autoResizeColumnsWithStretch(self.main_window.top_5_hit_tableView)
        else:
            pass
        immersingTableView(self.main_window.top_5_hit_tableView)

    def setup_tableview_summary_service(self):
        # 获取客服ID和平均得分的字典
        service_avg_scores = create_service_id_avg_score_table()

        # 初始化表格模型
        self.model_summary_service = QStandardItemModel()
        self.model_summary_service.setHorizontalHeaderLabels(['客服ID', '平均得分', '平均响应时间(分钟)'])
        # 设置表头居中
        self.model_summary_service.setHeaderData(0, Qt.Orientation.Horizontal, Qt.ItemDataRole.TextAlignmentRole,
                                                 Qt.AlignmentFlag.AlignCenter)

        for service_id, avg_score in service_avg_scores.items():
            # 获取客服的平均响应时间
            avg_response_time = analyzeResponseTime(service_id)

            # 创建条目
            id_item = QStandardItem(service_id)
            score_item = QStandardItem(str(round(avg_score, 2)))
            response_time_item = QStandardItem(str(avg_response_time))

            # 设置文本居中
            id_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            score_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            response_time_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)

            # 添加行到模型
            self.model_summary_service.appendRow([id_item, score_item, response_time_item])

        # 设置表格视图的模型
        self.main_window.summary_service_tableView.setModel(self.model_summary_service)

        # 配置视图样式和行为
        if not self.columnsAdjusted:
            autoResizeColumnsWithStretch(self.main_window.summary_service_tableView)
            self.columnsAdjusted = True
        else:
            pass

        self.main_window.summary_service_tableView.verticalHeader().setVisible(False)
        immersingTableView(self.main_window.summary_service_tableView)

    def reset_summary(self):
        self.setup_summary_basic_info()
        self.setup_tableview_top5_hit_rules()
        self.setup_tableview_summary_service()
        self.setup_button_click_event()
