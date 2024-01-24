import sqlite3

from PyQt6 import QtWidgets
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QStandardItemModel, QStandardItem, QColor, QFont
from PyQt6.QtWidgets import QApplication, QMessageBox

from services.db_rule import delete_rule, add_rule, get_regex_by_name, get_keyword_by_name, get_script_by_name
from services.db_rule import rule_exists, \
    get_score_by_name
from services.db_scheme import get_scheme_by_rule_name
from services.rule_manager import Rule
from ui.ui_utils import autoResizeColumnsWithStretch
from utils.data_utils import list_to_text, format_score
from utils.file_utils import RULE_DB_PATH


class RuleManager:

    def __init__(self, main_window):
        self.main_window = main_window
        self.conditionsCounter = 0

    def setupRuleEditingPage(self):
        # 确保 scrollArea 设置为可以根据内容自动调整大小
        self.main_window.scrollArea_rule_edit.setWidgetResizable(True)

        # 为 widget_rule_edit 设置一个 QVBoxLayout
        self.verticalLayout = QtWidgets.QVBoxLayout(self.main_window.scrollAreaWidgetContents)
        self.verticalLayout.setAlignment(Qt.AlignmentFlag.AlignTop)  # 设置对齐方式为顶部对齐
        self.main_window.scrollAreaWidgetContents.setLayout(self.verticalLayout)
        self.main_window.NewRuleButton.clicked.connect(self.add_condition_layout)
        self.main_window.save_rule_pushButton.clicked.connect(self.save_rule)
        self.main_window.delete_rule_pushButton.clicked.connect(self.delete_rule)

        # 添加一个弹性空间以确保组件紧密排列在顶部
        self.verticalLayout.addStretch(1)

    def add_condition_layout(self, condition_type=None, condition_value=None, additional_info=None):
        # 移除弹性空间
        try:
            print("添加条件组件")
            stretch_index = self.verticalLayout.count() - 1
            if stretch_index >= 0:
                item = self.verticalLayout.takeAt(stretch_index)
                if item:
                    self.verticalLayout.removeItem(item)
                    del item  # 显式删除以避免内存泄漏

            self.conditionsCounter += 1  # 增加条件编号

            # 创建条件组件的布局
            condition_layout = QtWidgets.QHBoxLayout()

            # 创建并添加带编号的标签
            label = QtWidgets.QLabel(f"条件 {self.conditionsCounter}:")
            condition_layout.addWidget(label)

            # 创建并添加组合框
            condition_type_comboBox = QtWidgets.QComboBox()
            condition_type_comboBox.setObjectName(f"condition_type_comboBox_{self.conditionsCounter}")
            condition_type_comboBox.addItems(["正则表达式匹配", "关键词匹配", "话术匹配"])
            if condition_type:
                condition_type_comboBox.setCurrentText(condition_type)

            condition_layout.addWidget(condition_type_comboBox)

            # 创建并添加第一个文本编辑框
            textEdit_content = QtWidgets.QTextEdit()
            textEdit_content.setObjectName(f"textEdit_content_{self.conditionsCounter}")
            textEdit_content.setFixedHeight(50)
            # 如果有条件值，则将其填充到文本编辑框中
            if condition_value:
                textEdit_content.setPlainText(list_to_text((condition_value)))
            condition_layout.addWidget(textEdit_content)

            # 创建并添加相似度要求标签和 QLineEdit（默认隐藏）
            similarityLabel = QtWidgets.QLabel("相似度要求：")
            similarityLabel.setObjectName(f"similarityLabel_{self.conditionsCounter}")
            similarityLabel.hide()
            condition_layout.addWidget(similarityLabel)

            textEdit_similarity_threshold = QtWidgets.QLineEdit()
            textEdit_similarity_threshold.setObjectName(f"textEdit_similarity_threshold_{self.conditionsCounter}")
            textEdit_similarity_threshold.hide()
            textEdit_similarity_threshold.setFixedHeight(20)
            textEdit_similarity_threshold.setFixedWidth(50)
            condition_layout.addWidget(textEdit_similarity_threshold)

            # 创建并添加关键词检测类型组合框（默认隐藏）
            check_type = QtWidgets.QComboBox()
            check_type.addItems(["any", "all", "any_n", "none"])
            check_type.setObjectName(f"check_type_{self.conditionsCounter}")
            check_type.hide()
            condition_layout.addWidget(check_type)

            # 创建并添加数量输入框（默认隐藏）  # 用于关键词匹配类型为 any_n 时
            check_n = QtWidgets.QLineEdit()
            check_n_label = QtWidgets.QLabel("数量:")
            check_n.setObjectName(f"check_n_{self.conditionsCounter}")
            check_n.hide()
            check_n_label.hide()
            condition_layout.addWidget(check_n_label)
            condition_layout.addWidget(check_n)

            # 创建删除按钮
            deleteButton = QtWidgets.QPushButton("删除")
            deleteButton.setObjectName(f"deleteButton_{self.conditionsCounter}")
            deleteButton.clicked.connect(lambda: self.delete_condition(deleteButton))
            condition_layout.addWidget(deleteButton)

            # 创建一个容纳上述布局的QWidget
            condition_widget = QtWidgets.QWidget()
            condition_widget.setLayout(condition_layout)

            # 将QWidget添加到规则编辑页面的布局中
            self.verticalLayout.addWidget(condition_widget)

            # print(f"添加了条件组件 {self.conditionsCounter}")
            # print(f"条件类型：{condition_type}")

            # 根据条件类型显示或隐藏相应控件
            if condition_type == "正则表达式匹配":
                # print("正则表达式匹配开始填写")
                similarityLabel.hide()
                textEdit_similarity_threshold.hide()
                check_type.hide()
                # print("正则表达式匹配填写")
            elif condition_type == "关键词匹配":
                # print("关键词匹配开始填写")
                similarityLabel.setText("关键词匹配类型：")
                similarityLabel.show()
                # print("关键词匹配类型开始填写")
                # print("additional_info", additional_info)
                if additional_info:
                    check_type.setCurrentText(str(additional_info))
                # print("关键词匹配类型填写")
                check_type.show()
                textEdit_similarity_threshold.hide()
            elif condition_type == "话术匹配":
                similarityLabel.setText("相似度要求：")
                similarityLabel.show()
                textEdit_similarity_threshold.show()
                if additional_info:
                    textEdit_similarity_threshold.setText(str(additional_info))
                check_type.hide()

            # 连接信号到槽函数，以便在条件类型变化时更新界面
            condition_type_comboBox.currentTextChanged.connect(
                lambda text: self.handleComboboxSelection(condition_type_comboBox, similarityLabel,
                                                          textEdit_similarity_threshold,
                                                          check_type))
            check_type.currentTextChanged.connect(
                lambda text: self.handle_any_n_combo(check_type, check_n, check_n_label))

            # 重新添加弹性空间
            self.verticalLayout.addStretch(1)
            self.print_all_objectNames()
        except Exception as e:
            print(f"add发生异常：{e}")

    def handle_any_n_combo(self, comboBox, lineEdit, label):
        # 根据下拉菜单选择的值显示或隐藏相应的控件
        selectedText = comboBox.currentText()  # 获取当前选中的文本
        if selectedText == "any_n":
            lineEdit.show()
            label.show()

        else:
            lineEdit.hide()
            label.hide()

    def handleComboboxSelection(self, comboBox, similarityLabel, similarityThreshold, checkType=None):
        # 根据下拉菜单选择的值显示或隐藏相应的控件
        selectedText = comboBox.currentText()  # 获取当前选中的文本
        if selectedText == "话术匹配":
            similarityLabel.setText("阈值：")
            similarityLabel.show()
            similarityThreshold.show()
            if checkType: checkType.hide()  # 如果存在检测类型的控件，则隐藏它
        elif selectedText == "关键词匹配":
            similarityLabel.setText("检测类型：")
            similarityLabel.show()
            if checkType:
                checkType.show()  # 显示检测类型的控件
            similarityThreshold.hide()
        else:
            similarityLabel.hide()
            similarityThreshold.hide()
            if checkType:
                checkType.hide()

    def delete_condition(self, delete_button):
        # 删除对应的条件组件
        for i in range(self.verticalLayout.count()):
            layout_item = self.verticalLayout.itemAt(i)
            if layout_item is not None:
                widget = layout_item.widget()
                if widget and delete_button in widget.children():
                    self.verticalLayout.removeWidget(widget)
                    widget.deleteLater()
                    self.verticalLayout.update()  # 强制更新布局
                    break
        # 重新编号剩余的条件
        self.renumber_conditions()
        self.print_all_objectNames()

    def renumber_conditions(self):
        counter = 1
        # 遍历布局中的所有组件，并更新它们的编号和objectName
        for i in range(self.verticalLayout.count()):
            layout_item = self.verticalLayout.itemAt(i)
            if layout_item is not None:
                widget = layout_item.widget()
                if widget:
                    # 更新条件编号
                    label = next((child for child in widget.children() if
                                  isinstance(child, QtWidgets.QLabel) and child.text().startswith('条件')), None)
                    if label:
                        label.setText(f'条件 {counter}:')
                        label.setObjectName(f'label_{counter}')  # 更新标签的objectName
                    # 更新组件的objectName
                    for child in widget.children():

                        # 使用split函数将字符串分割成一个列表
                        parts = child.objectName().split('_')

                        # 提取最后一个下划线之前的部分
                        desired_part = '_'.join(parts[:-1])
                        base_name = desired_part
                        if isinstance(child, QtWidgets.QComboBox):
                            new_name = f'{base_name}_{counter}'
                            child.setObjectName(new_name)
                        elif isinstance(child, QtWidgets.QTextEdit) or isinstance(child, QtWidgets.QLineEdit):
                            new_name = f'{base_name}_{counter}'
                            child.setObjectName(new_name)
                        elif isinstance(child, QtWidgets.QPushButton):
                            # 断开并重新连接信号以防止多重连接
                            child.disconnect()
                            new_name = f'deleteButton_{counter}'
                            child.setObjectName(new_name)
                            child.clicked.connect(lambda _, b=child: self.delete_condition(b))
                        elif isinstance(child, QtWidgets.QLabel):
                            new_name = f'{base_name}_{counter}'
                            child.setObjectName(new_name)
                        elif isinstance(child, QtWidgets.QLineEdit):
                            new_name = f'{base_name}_{counter}'
                            child.setObjectName(new_name)
                    counter += 1
        # 更新条件计数器
        self.conditionsCounter = counter - 1
        # 如果存在，调用print_all_objectNames来打印所有子控件的objectName
        self.print_all_objectNames()

    def print_all_objectNames(self):
        for i in range(self.verticalLayout.count()):
            widget = self.verticalLayout.itemAt(i).widget()
            if widget:
                print(f"Widget {i}:")
                for child in widget.children():
                    if hasattr(child, 'objectName'):
                        print(f"  - {child.__class__.__name__} objectName: {child.objectName()}")

    def setupRuleManagerTableView(self):
        # 创建一个标准项模型
        self.model = QStandardItemModel(self.main_window)

        # 设置列头
        self.model.setHorizontalHeaderLabels(['ID', '规则名称', '评分标准', '质检方案'])

        # 将模型设置到 RuleManagerTableView
        self.main_window.RuleManagerTableView.setModel(self.model)
        self.main_window.RuleManagerTableView.verticalHeader().setVisible(False)
        autoResizeColumnsWithStretch(self.main_window.RuleManagerTableView)

        # 连接表格的clicked信号到onRuleClicked槽函数
        self.main_window.RuleManagerTableView.clicked.connect(self.onRuleClicked)
        self.main_window.AddRuleButton.clicked.connect(self.AddRule)

        # 在这里添加实例数据
        self.loadRuleFromDB()

    def AddRule(self):
        self.rule_editing_clear()

        self.main_window.stackedWidget.setCurrentIndex(7)

    def rule_editing_clear(self):
        """
        清除规则编辑页面的所有内容,编辑页面最全面的清除，都用这个
        :return:
        """
        self.clear_existing_conditions()
        self.main_window.RuleNameEditText.clear()
        self.main_window.score_type_comboBox.setCurrentIndex(0)
        self.main_window.score_value_line_edit.clear()
        self.conditionsCounter = 0

    def clear_existing_conditions(self):
        print("清除现有条件布局")
        # 遍历垂直布局中的所有项目
        try:
            for i in reversed(range(self.verticalLayout.count())):
                # 从布局中取出项目
                layout_item = self.verticalLayout.itemAt(i)

                # 如果项目是一个小部件，则从布局中移除并删除该小部件
                if layout_item.widget():
                    widget_to_remove = layout_item.widget()
                    self.verticalLayout.removeWidget(widget_to_remove)
                    widget_to_remove.deleteLater()
                # 如果项目是一个布局，则递归地清除这个布局中的所有小部件，并从父布局中移除
                elif layout_item.layout():
                    self.clear_layout(layout_item.layout())
                    self.verticalLayout.removeItem(layout_item)
        except Exception as e:
            print(f"发生异常：{e}")

        # 重置条件计数器
        self.conditionsCounter = 0
        print("清除了现有条件布局")

    def clear_layout(self, layout):
        # 递归清除布局中的所有项目
        while layout.count():
            item = layout.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()
            elif item.layout():
                self.clear_layout(item.layout())

    def loadRuleFromDB(self):
        """
        从数据库加载规则
        :return:
        """

        # 连接数据库
        conn = sqlite3.connect(RULE_DB_PATH)
        cursor = conn.cursor()

        # 查询所有规则名称及其对应的 ID
        cursor.execute('SELECT id, rule_name FROM rule_index')
        rules = cursor.fetchall()
        cursor.execute('SELECT score_type, score_value FROM score_rules')
        scores = cursor.fetchall()
        print(scores)

        # 为每个规则加载相关的数据
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

            score_item = QStandardItem(format_score(scores[rule_id - 1]))

            scheme_item = QStandardItem(get_scheme_by_rule_name(rule_name))
            # 将行添加到模型
            self.model.appendRow([id_item, name_item, score_item, scheme_item])

        # 关闭数据库连接
        conn.close()

        # 设置表格视图的光标为手形光标
        QApplication.setOverrideCursor(Qt.CursorShape.PointingHandCursor)  # 设置应用程序的默认光标样式

    def onRuleClicked(self, index):
        # 假设规则的ID存储在第一列
        rule_name = self.model.item(index.row(), 1).text()
        # print(f"规则名称为 {rule_name}")

        score_type = int(str(get_score_by_name(rule_name, 0)))
        score_value = str(get_score_by_name(rule_name, 1))
        try:
            self.main_window.score_type_comboBox.setCurrentIndex(score_type)
            self.main_window.score_value_line_edit.setText(score_value)
        except Exception as e:
            print(f"发生异常：{e}")

        self.loadRuleDetails(rule_name)

    def loadRuleDetails(self, rule_name):
        # 先清空现有条件布局
        self.rule_editing_clear()
        # 切换到规则编辑界面并加载规则详情
        self.main_window.stackedWidget.setCurrentIndex(7)  # 确保这是正确的页面索引
        self.main_window.RuleNameEditText.setText(rule_name)

        # print(f"数据库绝对路径", RULE_DB_PATH)
        # print(f"规则名称", rule_name)

        # 查询并加载规则的各项条件数据
        regex = get_regex_by_name(rule_name)
        print(f"获取了正则表达式匹配条件", regex)
        keyword = get_keyword_by_name(rule_name, 0)
        print(f"获取了关键词匹配条件", keyword)
        keyword_match_type = get_keyword_by_name(rule_name, 1)
        print(f"获取了关键词匹配类型", keyword_match_type)
        script = get_script_by_name(rule_name, 0)
        threshold = get_script_by_name(rule_name, 1)
        print(f"获取了话术匹配条件", script, threshold)
        if regex:
            print("添加正则表达式匹配条件")
            self.add_condition_layout("正则表达式匹配", regex)
        # 对于关键词匹配，我们可能同时需要关键词和匹配类型
        if keyword:
            print("添加关键词匹配条件")
            self.add_condition_layout("关键词匹配", keyword, additional_info=keyword_match_type)
        # 话术匹配可能包括话术本身和相应的阈值

        if script:
            print("添加话术匹配条件")
            self.add_condition_layout("话术匹配", script, additional_info=threshold)

    def save_rule(self):
        """
        点击规则保存按钮，保存规则
        :return:
        """
        try:
            rule_name = self.main_window.RuleNameEditText.toPlainText().strip()
            if not rule_name:
                QMessageBox.critical(self.main_window, "错误", "规则名称不能为空")
                return
            if self.conditionsCounter == 0:
                QMessageBox.critical(self.main_window, "错误", "规则至少需要一个条件")
                return

            if self.main_window.score_type_comboBox.currentText() == "一次打分为":
                new_score_type = 0
            else:
                new_score_type = 1
            new_score_value = int(self.main_window.score_value_line_edit.text())

            if rule_exists(rule_name):
                delete_rule(rule_name)

            new_rule = Rule(rule_name)
            new_rule.change_score_setting(new_score_type, new_score_value)

            for i in range(1, self.conditionsCounter + 1):
                comboBox = self.main_window.findChild(QtWidgets.QComboBox, f"condition_type_comboBox_{i}")
                condition_type = comboBox.currentText() if comboBox else None

                if condition_type == "正则表达式匹配":
                    regex_pattern = self.main_window.findChild(QtWidgets.QTextEdit,
                                                               f"textEdit_content_{i}").toPlainText()
                    new_rule.add_regex_rule(regex_pattern)

                elif condition_type == "关键词匹配":
                    keywords = self.main_window.findChild(QtWidgets.QTextEdit,
                                                          f"textEdit_content_{i}").toPlainText().split(' ')
                    check_type = self.main_window.findChild(QtWidgets.QComboBox, f"check_type_{i}").currentText()
                    if check_type == "any_n":
                        n = int(self.main_window.findChild(QtWidgets.QLineEdit, f"check_n_{i}").text())
                        new_rule.add_keyword_rule(keywords, check_type, n)
                    else:
                        new_rule.add_keyword_rule(keywords, check_type)

                elif condition_type == "话术匹配":
                    scripts = self.main_window.findChild(QtWidgets.QTextEdit,
                                                         f"textEdit_content_{i}").toPlainText().split(' ')
                    similarity_threshold = float(
                        self.main_window.findChild(QtWidgets.QLineEdit, f"textEdit_similarity_threshold_{i}").text())
                    new_rule.add_script_rule(scripts, similarity_threshold)

            add_rule(new_rule)
            print("规则保存成功")
            QMessageBox.information(self.main_window, "成功", f"规则 {rule_name} 已保存")

        except Exception as e:
            print(f"发生异常: {e}")

    def delete_rule(self):
        rule_name = self.main_window.RuleNameEditText.toPlainText().strip()
        if not rule_name or not rule_exists(rule_name):
            self.main_window.stackedWidget.setCurrentIndex(1)
            return
        reply = QMessageBox.question(self.main_window, "询问", "请确认是否删除此规则？？",
                                     QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                                     QMessageBox.StandardButton.No)

        if reply == QMessageBox.StandardButton.Yes:
            print("用户点击了'是'")
            delete_rule(rule_name)
            QMessageBox.information(self.main_window, "成功", f"规则 {rule_name} 已删除")
            self.main_window.stackedWidget.setCurrentIndex(1)

            self.rule_editing_clear()
            self.model.removeRow(self.main_window.RuleManagerTableView.currentIndex().row())
        else:
            print("用户点击了'否'")
