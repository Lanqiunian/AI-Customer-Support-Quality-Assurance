# 导入PyQt和自动生成的UI类

from PyQt6 import QtWidgets, QtCore
from PyQt6.QtGui import QStandardItemModel

from ui.dataset_logic import DataSetManager
from ui.main_window import Ui_MainWindow
from ui.rule_logic import RuleManager
from ui.scheme_logic import SchemeManager
from ui.task_logic import TaskManager


class CustomMainWindow(QtWidgets.QMainWindow, Ui_MainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setupUi(self)

        # 设置 TreeWidget 项与 StackedWidget 页面的映射
        self.setupTreeWidgetPageMapping()

        # 初始化 model_setup_scheme_table_view 实例变量
        self.model = QStandardItemModel(self)

        # 连接 TreeWidget 的项点击事件
        self.treeWidget_3.itemClicked.connect(self.onTreeItemClicked)

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
        self.Task_Manager = TaskManager(self)
        self.Task_Manager.setup_task_table_view()

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
