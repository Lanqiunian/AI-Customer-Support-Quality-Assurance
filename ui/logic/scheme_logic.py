import sqlite3

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QStandardItemModel, QStandardItem, QColor, QFont
from PyQt6.QtWidgets import QApplication, QMessageBox, QDialog

from services.db.db_rule import get_score_by_name
from services.db.db_scheme import query_scheme, Scheme, delete_scheme
from ui.dialog_pick_a_rule import Ui_add_rule_to_scheme_Dialog
from utils.ui_utils import autoResizeColumnsWithStretch
from utils.data_utils import format_score
from utils.global_utils import SCHEME_DB_PATH, RULE_DB_PATH


class SchemeManager:
    def __init__(self, MainWindow, RuleManager_instance, parent=None):

        self.main_window = MainWindow
        self.model_existing_rule_TableView = QStandardItemModel(self.main_window)
        self.rule_manager = RuleManager_instance if RuleManager_instance else None
        self.parent = parent
        self.main_window.new_scheme_pushButton.clicked.connect(self.create_new_scheme)
        self.main_window.add_rule_to_scheme_pushButton.clicked.connect(self.on_clicked_append_rule_to_scheme)
        self.main_window.delete_rule_from_scheme_pushButton.clicked.connect(self.delete_rule_from_scheme)
        self.main_window.save_scheme_pushButton.clicked.connect(self.on_Clicked_Save_Scheme)
        self.main_window.delete_scheme_pushButton.clicked.connect(self.on_Clicked_delete_scheme)
        self.main_window.delete_scheme_pushButton.hide()

        # 创建一个新的方案对象
        self.the_scheme = Scheme("sample_name", "sample_description")

    def create_new_scheme(self):
        """
        当点击“新建方案”按钮时触发
        :return:
        """
        self.the_scheme = Scheme("new_name", "new_description")
        self.main_window.stackedWidget.setCurrentIndex(8)
        self.main_window.scheme_name_lineEdit.setText("")  # 设置方案名称
        self.main_window.scheme_description_textEdit.setText("")  # 设置方案描述
        self.main_window.delete_scheme_pushButton.hide()
        self.setup_existing_rule_TableView([])

    def setup_scheme_table_view(self):
        conn = sqlite3.connect(SCHEME_DB_PATH)
        cursor = conn.cursor()

        cursor.execute("SELECT scheme_name, description FROM Schemes")
        rows = cursor.fetchall()

        conn.close()

        self.model_setup_scheme_table_view = QStandardItemModel(len(rows), 3)  # 假设有4列，包括操作列

        self.model_setup_scheme_table_view.setHorizontalHeaderLabels(["方案名称", "描述", "操作"])

        for row_index, row in enumerate(rows):
            for column_index, item in enumerate(row):
                item = QStandardItem(str(item))
                item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)  # 设置文本居中
                self.model_setup_scheme_table_view.setItem(row_index, column_index, item)

            # 在"操作"列添加"删除"文本与字体样式#####################
            delete_item = QStandardItem("查看")
            delete_item.setForeground(QColor('blue'))
            font = QFont()
            font.setUnderline(True)
            delete_item.setFont(font)
            delete_item.setFlags(Qt.ItemFlag.ItemIsSelectable | Qt.ItemFlag.ItemIsEnabled)  # 设置为不可编辑但可选
            delete_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)  # 设置文本居中
            self.model_setup_scheme_table_view.setItem(row_index, 2, delete_item)
            ###############################################################

        self.main_window.scheme_tableView.setModel(self.model_setup_scheme_table_view)
        self.main_window.scheme_tableView.verticalHeader().setVisible(False)

        # 连接表格的clicked信号到槽函数
        # 断开之前的连接
        try:
            self.main_window.scheme_tableView.clicked.disconnect()
        except Exception as e:
            pass  # 如果之前没有连接，则忽略错误
        # 重新连接信号
        self.main_window.scheme_tableView.clicked.connect(self.on_table_view_clicked)

    def on_table_view_clicked(self, index):
        """
        点击方案表格中的“操作”列时触发
        :param index:
        :return:
        """
        print("on_table_view_clicked")
        if index.column() == 2:  # 检查是否点击了“操作”列
            # 获取该行第二列（数据集名称）的内容
            scheme_name = self.model_setup_scheme_table_view.item(index.row(), 0).text()
            self.load_scheme_detail(scheme_name, "load_existing_scheme")
            try:
                self.the_scheme = query_scheme(scheme_name)
                print(f"the_scheme: {self.the_scheme.scheme_name}")
            except Exception as e:
                print(f"on_table_view_clicked发生异常：{e}")

    def load_scheme_detail(self, scheme_name="", type=None):
        """
        加载方案的详细信息
        :param scheme_name:
        :param type: 默认情况下是None，那么就从数据库中加载规则列表；如果是"fake_load"等非None，那么就从类的属性中加载
        :return:
        """

        if self.the_scheme.scheme_name != scheme_name:
            # 如果被初始化为已存在的Scheme，那么就将内存方案对象设置为此规则对象
            self.the_scheme = query_scheme(scheme_name)

        if type is not None:
            self.main_window.stackedWidget.setCurrentIndex(8)
            if self.the_scheme.scheme_name != "new_name":
                self.main_window.scheme_name_lineEdit.setText(scheme_name)  # 设置方案名称
                self.main_window.scheme_description_textEdit.setText(self.the_scheme.description)  # 设置方案描述
                self.main_window.delete_scheme_pushButton.show()
            # 读取scheme.db中scheme_name绑定的规则，将规则显示在dialog中

            rule_list = self.the_scheme.rules
        else:
            rule_list = self.get_rules_list(self.the_scheme)
        print(f"方案 '{scheme_name}' 包含的规则有：{rule_list}")
        self.setup_existing_rule_TableView(rule_list)

    def setup_existing_rule_TableView(self, rules_list):
        # 创建一个标准项模型
        self.model_existing_rule_TableView = QStandardItemModel()
        # 设置列头
        self.model_existing_rule_TableView.setHorizontalHeaderLabels(['ID', '规则名称', '评分标准'])

        # 将模型设置到 RuleManagerTableView
        self.main_window.existing_rules_in_scheme_tableView.setModel(self.model_existing_rule_TableView)
        self.main_window.existing_rules_in_scheme_tableView.verticalHeader().setVisible(False)
        try:
            autoResizeColumnsWithStretch(self.main_window.existing_rules_in_scheme_tableView)
        except Exception as e:
            print(f"setup_existing_rule_TableView发生异常：{e}")

        # 断开之前的连接
        try:
            self.main_window.existing_rules_in_scheme_tableView.clicked.disconnect()
        except Exception as e:
            pass  # 如果之前没有连接，则忽略错误
        # 重新连接信号
        # 连接表格的clicked信号到onRuleClicked槽函数
        self.main_window.existing_rules_in_scheme_tableView.clicked.connect(self.on_Clicked_Rule_Detail)
        # 在这里添加实例数据
        self.loadRuleFromDB(rules_list)

        for column in range(3):
            # 根据内容自动调整列宽
            self.main_window.existing_rules_in_scheme_tableView.resizeColumnToContents(column)

            # 获取当前列宽
            currentWidth = self.main_window.existing_rules_in_scheme_tableView.columnWidth(column)

            # 给当前列宽加上额外的宽度
            self.main_window.existing_rules_in_scheme_tableView.setColumnWidth(column, currentWidth + 20)

        print("setup_existing_rule_TableView加载规则完成")

    def loadRuleFromDB(self, rules_list):
        """
        从数据库加载对应方案所绑定的规则
        :param rules_list:
        :return:
        """
        # 连接数据库
        conn = sqlite3.connect(RULE_DB_PATH)
        cursor = conn.cursor()

        # 准备规则名称列表的 SQL 查询条件
        placeholders = ','.join('?' for unused in rules_list)
        query = f'SELECT id, rule_name FROM rule_index WHERE rule_name IN ({placeholders})'
        cursor.execute(query, rules_list)
        rules = cursor.fetchall()
        print(f"rules: {rules}")

        # 准备查询规则分数的 SQL
        score_query = f'SELECT rule_name, score_type, score_value FROM score_rules WHERE rule_name IN ({placeholders})'
        cursor.execute(score_query, rules_list)
        scores = cursor.fetchall()
        print(f"scores: {scores}")

        # 创建一个规则名到分数的映射，方便之后使用
        print(f"rules: {rules}")
        scores_dict = {rule_name: (score_type, score_value) for rule_name, score_type, score_value in scores}
        print(f"scores_dict: {scores_dict}")
        # 为每个查询到的规则加载相关的数据
        for rule_id, rule_name in rules:
            # 创建规则 ID 项
            id_item = QStandardItem(str(rule_id))
            id_item.setFlags(Qt.ItemFlag.ItemIsSelectable | Qt.ItemFlag.ItemIsEnabled)  # 设置为不可编辑但可选

            # 创建规则名称项
            name_item = QStandardItem(rule_name)
            name_item.setForeground(QColor('blue'))  # 设置字体颜色为蓝色
            font = QFont()  # 创建一个新的字体对象
            font.setUnderline(True)  # 设置字体为下划线，模仿链接的外观
            name_item.setFont(font)
            name_item.setFlags(Qt.ItemFlag.ItemIsSelectable | Qt.ItemFlag.ItemIsEnabled)  # 设置为不可编辑但可选

            # 根据规则名找到对应的分数信息
            score_type, score_value = scores_dict.get(rule_name, (None, None))
            score_item = QStandardItem(format_score((score_type, score_value)))

            # 将行添加到模型
            self.model_existing_rule_TableView.appendRow([id_item, name_item, score_item])
            # ID列设置文本居中
            self.model_existing_rule_TableView.item(0).setTextAlignment(Qt.AlignmentFlag.AlignCenter)

        # 关闭数据库连接
        conn.close()

        # 设置表格视图的光标为手形光标
        QApplication.setOverrideCursor(Qt.CursorShape.PointingHandCursor)  # 设置应用程序的默认光标样式

    def on_Clicked_Save_Scheme(self):
        """
        当点击“保存方案”按钮时触发
        :return:
        """
        # 获取方案名称和描述
        self.the_scheme.save()
        print(f"保存方案 '{self.the_scheme.scheme_name}'")
        new_scheme_name = self.main_window.scheme_name_lineEdit.text()
        new_scheme_description = self.main_window.scheme_description_textEdit.toPlainText()

        # 检查方案名称是否为空
        if not new_scheme_name:
            QMessageBox.warning(self.main_window, "方案名称为空", "请输入方案名称。")
            return

        self.the_scheme.update(new_scheme_name, new_scheme_description)

        self.load_scheme_detail(new_scheme_name)

        # 更新表格视图
        self.setup_scheme_table_view()

        QMessageBox.information(self.main_window, "保存成功", f"方案 '{new_scheme_name}' 已保存。")

    def on_Clicked_delete_scheme(self):
        """
        当点击“删除方案”按钮时触发
        :return:
        """
        # 获取方案名称
        scheme_name = self.the_scheme.scheme_name
        reply = QMessageBox.question(self.main_window, '确认', f'您确定要删除方案 "{scheme_name}" 吗？',
                                     QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        if reply == QMessageBox.StandardButton.No:
            return
        else:
            print(f"删除方案 '{scheme_name}'")
            delete_scheme(scheme_name)
            # 更新表格视图
            self.setup_scheme_table_view()
            self.main_window.stackedWidget.setCurrentIndex(2)
            self.setup_scheme_table_view()

    def on_Clicked_Rule_Detail(self, index):
        """
        当已有规则被点击，切换到此规则的编辑页面
        :param index:
        :return:
        """
        if index.column() == 1:
            print("on_Rule_Clicked")

            # 1.获取规则名称
            rule_name = self.model_existing_rule_TableView.item(index.row(), 1).text()
            print(f"rule_name获取成功: {rule_name}")

            print(f"成功设置页面")

            # 加载内容
            print(f"加载规则详情：{rule_name}")
            self.rule_manager.loadRuleDetails(rule_name)
            print(f"加载规则详情完成")
            # 加载评分类型和评分值
            score_type = int(str(get_score_by_name(rule_name, 0)))
            score_value = str(get_score_by_name(rule_name, 1))
            try:
                self.main_window.score_type_comboBox.setCurrentIndex(score_type)
                print(f"score_type: {score_type}")
                self.main_window.score_value_line_edit.setText(score_value)
                print(f"score_value: {score_value}")
            except Exception as e:
                print(f"on_Clicked_Rule_Detail发生异常：{e}")

    def on_clicked_append_rule_to_scheme(self):
        """
        当点击“添加规则”按钮时触发
        :return:
        """
        # 获取当前方案名称
        scheme_name = self.the_scheme.scheme_name
        # 创建一个添加规则的对话框
        dialog = AppendRuleDialog(self.parent, scheme_name, self.the_scheme)
        dialog.exec()
        # 重新加载规则列表
        try:
            self.load_scheme_detail(scheme_name, type="fake_load")
        except Exception as e:
            print(f"on_clicked_append_rule_to_scheme发生异常：{e}")

    def delete_rule_from_scheme(self):
        # 获取选中的行
        try:
            selected_indexes = self.main_window.existing_rules_in_scheme_tableView.selectedIndexes()
            if not selected_indexes:
                QMessageBox.warning(self.main_window, "未选择规则", "请在列表中选择一个规则进行删除。")
                return

            # 假设规则名称位于第二列（列索引从0开始计数）
            selected_row = selected_indexes[0].row()
            rule_id = self.model_existing_rule_TableView.item(selected_row, 0).text()
            rule_name = self.model_existing_rule_TableView.item(selected_row, 1).text()

            # 获取当前方案的名称
            scheme_name = self.main_window.scheme_name_lineEdit.text()

            # 从数据库中删除选中的规则与当前方案的关系
            self.delete_rule_from_scheme_db(scheme_name, rule_name)

            # 更新表格视图
            self.setup_existing_rule_TableView(self.get_rules_list(scheme_name))
        except Exception as e:
            print(f"delete_rule_from_scheme发生异常：{e}")

    def delete_rule_from_scheme_db(self, scheme_name, rule_name):
        conn = sqlite3.connect(SCHEME_DB_PATH)
        cursor = conn.cursor()
        # 删除方案与规则的关联
        cursor.execute("DELETE FROM Scheme_Rule_Relationship WHERE scheme_name = ? AND rule_name = ?",
                       (scheme_name, rule_name))
        conn.commit()
        conn.close()
        QMessageBox.information(self.main_window, "删除成功", f"规则 '{rule_name}' 已从方案 '{scheme_name}' 中删除。")

    def get_rules_list(self, scheme, type=None):
        # 此函数返回给定方案名称的所有规则名称列表
        conn = sqlite3.connect(SCHEME_DB_PATH)
        cursor = conn.cursor()
        scheme_name = scheme.scheme_name
        try:
            cursor.execute("SELECT rule_name FROM Scheme_Rule_Relationship WHERE scheme_name = ?", (scheme_name,))
            rules_data = cursor.fetchall()
            conn.close()
        except Exception as e:
            print(f"get_rules_list发生异常：{e}")
            pass
        rule_list = scheme.rules
        print(f"规则列表：{rule_list}")

        if type is not None:

            return rule_list

        else:
            return [rule[0] for rule in rules_data]

        # return [rule[0] for rule in rules_data]  # 返回规则名称列表


class AppendRuleDialog(QDialog):
    def __init__(self, parent=None, scheme_name="", the_scheme=None, rule_list=None):  # 会用传递的scheme_name替换掉默认的空字符串
        super().__init__(parent)

        self.ui = Ui_add_rule_to_scheme_Dialog()
        self.ui.setupUi(self)
        self.scheme_name = scheme_name  # 保存当前方案名称
        self.the_scheme = the_scheme  # 保存当前方案对象
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

                self.the_scheme.append(rule_name)
                print(f"添加规则 '{rule_name}' 到方案 '{self.scheme_name}'")
                print(f"方案 '{self.scheme_name}' 包含的规则有：{self.the_scheme.rules}")

                # self.the_scheme.save()
            except Exception as e:
                print(f"添加规则到方案时发生错误：{e}")
            # 假设有这样的函数可用
            self.accept()  # 关闭对话框
