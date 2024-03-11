# 导入PyQt和自动生成的UI类

from PyQt6 import QtWidgets, QtCore, uic
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QStandardItemModel
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QTextEdit, QLabel

from ui.logic.dataset_logic import DataSetManager
from ui.logic.global_setting_logic import GlobalSettingPageLogic
from ui.main_window import Ui_MainWindow
from ui.logic.rule_logic import RuleManager
from ui.logic.scheme_logic import SchemeManager
from ui.logic.summary_logic import SummaryManager
from ui.logic.task_logic import TaskManager
from ui.logic.undo_check_logic import UndoCheckManager
from utils.data_utils import generate_html


class CustomMainWindow(QtWidgets.QMainWindow, Ui_MainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setupUi(self)
        self.setWindowFlags(self.windowFlags() | Qt.WindowType.FramelessWindowHint)
        self._drag_pos = None

        # 将close_button_label转换为可点击的
        uic.loadUi("ui/main_window.ui", self)
        # 获取当前窗口的初始尺寸
        initialSize = self.size()

        # 设置窗口的最小和最大尺寸为当前尺寸，从而禁用尺寸调整
        self.setMinimumSize(initialSize)
        self.setMaximumSize(initialSize)

        # 连接点击事件
        self.minimize_button_label.mousePressEvent = self.minimize_window
        self.close_button_label.mousePressEvent = self.close_window

        # 设置 TreeWidget 项与 StackedWidget 页面的映射
        self.setupTreeWidgetPageMapping()

        # 初始化 model_setup_scheme_table_view 实例变量
        self.model = QStandardItemModel(self)

        # 连接 TreeWidget 的项点击事件
        self.treeWidget_3.itemClicked.connect(self.onTreeItemClicked)
        # 初始化 UndoCheckManager
        self.undo_check_manager = UndoCheckManager(self)
        self.undo_check_manager.setup_undo_check_tableView()
        # 初始化SummaryManager
        self.summary_manager = SummaryManager(self)
        self.summary_manager.reset_summary()

        # 初始化 RuleManager
        self.rule_manager = RuleManager(self)

        # 将规则管理相关的设置移动到 RuleManager 类中
        # 假设 RuleManager 类有一个方法来设置规则编辑页面
        self.rule_manager.setupRuleEditingPage()

        # 假设 RuleManager 类有一个方法来设置规则管理表格视图
        self.rule_manager.setupRuleManagerTableView()

        self.DataSet_Manager = DataSetManager(self)

        self.DataSet_Manager.setup_dataset_table_view()

        # 初始化 SchemeManager方案管理
        self.Scheme_Manager = SchemeManager(self, self.rule_manager)
        self.Scheme_Manager.setup_scheme_table_view()

        # 初始化 TaskManager任务管理
        self.Task_Manager = TaskManager(self, self.rule_manager)
        self.Task_Manager.setup_task_table_view()
        self.back_to_dialogue_detail_pushButton.hide()

        # 初始化设置
        self.GlobalSettingPage_manager = GlobalSettingPageLogic(self)
        self.GlobalSettingPage_manager.setup_global_setting()
        self.setting_save_Pushbutton.clicked.connect(self.GlobalSettingPage_manager.on_click_save_button)

        # 设置自定义开关
        self.minimize_button_label.setObjectName("minimize_button_label")
        self.close_button_label.setObjectName("close_button_label")

        # 为已定义的 QLabel 添加点击功能
        self._makeLabelClickable(self.close_button_label, self.close_window)
        self._makeLabelClickable(self.minimize_button_label, self.minimize_window)

    def _makeLabelClickable(self, label, function):
        # 动态添加点击功能
        def mousePressEvent(event):
            function()

        label.mousePressEvent = mousePressEvent

    def close_window(self):
        print("关闭窗口")
        self.close()

    def minimize_window(self):
        print("最小化窗口")
        self.showMinimized()

    # 重写鼠标事件，实现窗口拖动
    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self._drag_pos = event.position()

    def mouseMoveEvent(self, event):
        if event.buttons() & Qt.MouseButton.LeftButton and self._drag_pos:
            self.move(self.pos() + (event.position() - self._drag_pos).toPoint())

    def mouseReleaseEvent(self, event):
        self._drag_pos = None

    def setupDialogueDisplay(self, dialogue_df):
        """
        设置对话显示区域的内容。
        :param dialogue_df: 对话的df
        :return:
        """
        self.scrollArea = self.dialogue_scrollArea  # 假设dialogue_scrollArea是你的QScrollArea实例
        self.scrollArea.setWidgetResizable(True)

        self.scrollAreaWidgetContents = QWidget()
        self.scrollArea.setWidget(self.scrollAreaWidgetContents)

        layout = QVBoxLayout(self.scrollAreaWidgetContents)
        self.textEdit = QTextEdit()
        self.textEdit.setReadOnly(True)
        layout.addWidget(self.textEdit)

        # 根据DataFrame生成对话HTML内容
        dialogue_html = generate_html(dialogue_df)
        self.textEdit.setHtml(dialogue_html)

    def setupTreeWidgetPageMapping(self):
        # 映射项到StackedWidget的索引
        # 注意：只为具有对应页面的子项设置数据

        # 假设“概览”对应 page
        self.treeWidget_3.topLevelItem(0).setData(0, QtCore.Qt.ItemDataRole.UserRole, 0)

        # “质检规则和方案”子项映射
        self.treeWidget_3.topLevelItem(1).child(0).setData(0, QtCore.Qt.ItemDataRole.UserRole, 1)  # 质检规则配置 -> page_2
        self.treeWidget_3.topLevelItem(1).child(1).setData(0, QtCore.Qt.ItemDataRole.UserRole, 2)  # 质检方案管理 -> page_3

        # “质检任务”子项映射
        self.treeWidget_3.topLevelItem(2).child(0).setData(0, QtCore.Qt.ItemDataRole.UserRole, 3)  # 任务管理 -> page_4
        self.treeWidget_3.topLevelItem(2).child(1).setData(0, QtCore.Qt.ItemDataRole.UserRole, 4)  # 数据集管理 -> page_5

        # 假设“待办任务”对应 page_6
        self.treeWidget_3.topLevelItem(3).setData(0, QtCore.Qt.ItemDataRole.UserRole, 5)

        # 假设“系统管理”对应 page_7
        self.treeWidget_3.topLevelItem(4).setData(0, QtCore.Qt.ItemDataRole.UserRole, 6)

    def onTreeItemClicked(self, item, column):
        # 检查项是否设置了数据
        if item.data(0, QtCore.Qt.ItemDataRole.UserRole) is not None:
            # 根据点击的项获取对应的页面索引
            index = item.data(0, QtCore.Qt.ItemDataRole.UserRole)
            if item.data(0, QtCore.Qt.ItemDataRole.UserRole) == 1:
                # 每次回到质检规则配置页面都要重新设置一次，重新建立一次表格视图，因为重新保存后id会变
                self.rule_manager.setupRuleManagerTableView()

                # 切换到相应的StackedWidget页面
            self.stackedWidget.setCurrentIndex(index)


class ClickableLabel(QLabel):
    clicked = pyqtSignal()  # 定义信号

    def mousePressEvent(self, event):
        self.clicked.emit()  # 发射信号
