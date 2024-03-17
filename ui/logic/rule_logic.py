import json
import sqlite3

from PyQt6 import QtWidgets
from PyQt6.QtCore import Qt, QDateTime
from PyQt6.QtGui import QStandardItemModel, QStandardItem, QColor, QFont
from PyQt6.QtWidgets import QApplication, QMessageBox, QFileDialog

from services.db.db_rule import delete_rule, add_rule, get_script_by_name, \
    query_rule, import_rules_from_json, export_rules_to_json, get_condition_count
from services.db.db_rule import rule_exists, \
    get_score_by_name
from services.db.db_scheme import get_scheme_by_rule_name
from services.model_api_client import AISuggestionThread
from services.rule_manager import Rule
from ui.logic.task_logic import WaitingDialog
from utils.data_utils import list_to_text, format_score, is_valid_logic_expression
from utils.global_utils import RULE_DB_PATH
from utils.ui_utils import NumericSortProxyModel


class RuleManager:

    def __init__(self, main_window):

        self.main_window = main_window
        self.conditionsCounter = 0  # 用于记录条件的数量，在加载和定位组件时计数用
        self.conditionsCounter_for_check_logic_expression = 0  # 用于记录条件的数量，检测逻辑表达式时用

    def setupRuleEditingPage(self):
        # 确保 scrollArea 设置为可以根据内容自动调整大小
        self.main_window.scrollArea_rule_edit.setWidgetResizable(True)

        # 为 widget_rule_edit 设置一个 QVBoxLayout
        self.verticalLayout = QtWidgets.QVBoxLayout(self.main_window.scrollAreaWidgetContents)
        self.verticalLayout.setAlignment(Qt.AlignmentFlag.AlignTop)  # 设置对齐方式为顶部对齐
        self.main_window.scrollAreaWidgetContents.setLayout(self.verticalLayout)
        self.main_window.new_condition_Pushbutton.clicked.connect(self.on_new_condition_button_clicked)  # 增加条件编号)
        self.main_window.save_rule_pushButton.clicked.connect(self.save_rule)
        self.main_window.delete_rule_pushButton.clicked.connect(self.delete_rule)
        self.main_window.generate_ai_suggestion_pushButton.clicked.connect(self.on_click_generate_ai_rule_suggestion)

        # 添加一个弹性空间以确保组件紧密排列在顶部
        self.verticalLayout.addStretch(1)

    def on_new_condition_button_clicked(self):
        self.add_condition_layout()
        self.conditionsCounter_for_check_logic_expression += 1
        self.check_logic_expression()

    def add_condition_layout(self, condition_type=None, target_role=None, condition_value=None, additional_info=None):

        try:
            stretch_index = self.verticalLayout.count() - 1
            if stretch_index >= 0:
                item = self.verticalLayout.takeAt(stretch_index)
                if item:
                    self.verticalLayout.removeItem(item)
                    del item  # 显式删除以避免内存泄漏

            self.conditionsCounter += 1  # 增加条件编号

            # 创建条件组件的布局
            condition_layout = QtWidgets.QHBoxLayout()

            # 创建并添加组合框
            condition_type_comboBox = QtWidgets.QComboBox()
            condition_type_comboBox.setObjectName(f"condition_type_comboBox_{self.conditionsCounter}")
            condition_type_comboBox.addItems(["正则表达式匹配", "关键词匹配", "话术匹配"])

            # 创建并添加带编号的标签
            label = QtWidgets.QLabel(f"条件 {self.conditionsCounter}:")
            condition_layout.addWidget(label)

            if condition_type:
                condition_type_comboBox.setCurrentText(condition_type)

            condition_layout.addWidget(condition_type_comboBox)

            # 创建并添加目标角色组合框
            label = QtWidgets.QLabel("目标角色：")
            target_role_comboBox = QtWidgets.QComboBox()
            target_role_comboBox.setObjectName(f"target_role_comboBox_{self.conditionsCounter}")
            target_role_comboBox.addItems(["客服", "客户"])
            condition_layout.addWidget(label)
            condition_layout.addWidget(target_role_comboBox)

            if target_role:
                target_role_comboBox.setCurrentIndex(int(target_role))

            # 创建并添加第一个文本编辑框
            textEdit_content = QtWidgets.QTextEdit()
            textEdit_content.setObjectName(f"textEdit_content_{self.conditionsCounter}")
            textEdit_content.setFixedHeight(50)
            # 如果有条件值，则将其填充到文本编辑框中
            if condition_value:
                if condition_type == "正则表达式匹配":
                    textEdit_content.setPlainText(condition_value)
                else:
                    textEdit_content.setPlainText(list_to_text(condition_value))
                    # 正则表达式不要用这个list_to_text，因为它会让正则表达式有一堆空格

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
                    check_type.setCurrentText(str(additional_info[0]))
                    if additional_info[1] is not None:
                        check_n.show()
                        check_n.setText(str(additional_info[1]))
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
        self.conditionsCounter_for_check_logic_expression -= 1
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
        self.setup_condition_selection_combo()
        self.check_logic_expression()

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

        # 创建一个代理模型用于排序
        self.proxyModel = NumericSortProxyModel(self.main_window)
        self.proxyModel.setSourceModel(self.model)
        # 设置排序时不区分大小写
        self.proxyModel.setSortCaseSensitivity(Qt.CaseSensitivity.CaseInsensitive)

        # 配置代理模型进行排序，此处0代表ID列
        self.proxyModel.sort(0)

        # 将代理模型设置到 RuleManagerTableView
        self.main_window.RuleManagerTableView.setModel(self.proxyModel)
        self.main_window.RuleManagerTableView.verticalHeader().setVisible(False)

        # 连接信号和槽
        self.main_window.AddRuleButton.clicked.connect(self.AddRule)
        try:
            # 断开之前的连接（如果存在）
            self.main_window.import_rules_pushButton.clicked.disconnect()
            self.main_window.export_rules_pushButton.clicked.disconnect()
            self.main_window.RuleManagerTableView.clicked.disconnect()
        except TypeError:
            # 如果之前没有连接，则忽略这个错误
            pass
        self.main_window.import_rules_pushButton.clicked.connect(self.on_clicked_import_rules)
        self.main_window.export_rules_pushButton.clicked.connect(self.on_clicked_export_rules)
        self.main_window.RuleManagerTableView.clicked.connect(self.onRuleClicked)

        # 在这里添加实例数据
        self.loadRuleFromDB()
        for column in range(3):
            # 根据内容自动调整列宽
            self.main_window.RuleManagerTableView.resizeColumnToContents(column)

            # 获取当前列宽
            currentWidth = self.main_window.RuleManagerTableView.columnWidth(column)

            # 给当前列宽加上额外的宽度
            self.main_window.RuleManagerTableView.setColumnWidth(column, currentWidth + 20)

    def AddRule(self):
        """
        添加规则
        """
        self.rule_editing_clear()
        self.conditionsCounter_for_check_logic_expression = 0
        self.main_window.RuleNameEditText.setReadOnly(False)
        self.main_window.stackedWidget.setCurrentIndex(7)
        self.main_window.logic_expression_lineEdit.textChanged.connect(self.check_logic_expression)
        self.check_logic_expression()
        self.setup_logic_expression_event()

    def rule_editing_clear(self):
        """
        清除规则编辑页面的所有内容,编辑页面最全面的清除，都用这个
        :return:
        """
        self.clear_existing_conditions()
        self.main_window.RuleNameEditText.clear()
        self.main_window.score_type_comboBox.setCurrentIndex(0)
        self.main_window.score_value_line_edit.clear()
        self.main_window.logic_expression_lineEdit.clear()
        # 清除add_condition_to_logic_expression_comboBox中的选项
        self.main_window.add_condition_to_logic_expression_comboBox.clear()
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

        conn = sqlite3.connect(RULE_DB_PATH)
        cursor = conn.cursor()

        # 查询所有规则名称及其对应的 ID
        cursor.execute('SELECT id, rule_name FROM rule_index')
        rules = cursor.fetchall()
        cursor.execute('SELECT score_type, score_value FROM score_rules ')
        scores = cursor.fetchall()

        # 为每个规则加载相关的数据
        for rule_id, rule_name in rules:
            # 创建规则 ID 项
            id_item = QStandardItem(str(rule_id))
            id_item.setFlags(Qt.ItemFlag.ItemIsSelectable | Qt.ItemFlag.ItemIsEnabled)  # 设置为不可编辑但可选
            # 设置居中
            id_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)

            # 创建规则名称项
            name_item = QStandardItem(rule_name)
            name_item.setForeground(QColor('blue'))  # 设置字体颜色为蓝色
            font = QFont()  # 创建一个新的字体对象
            font.setUnderline(True)  # 设置字体为下划线，模仿链接的外观
            name_item.setFont(font)
            name_item.setFlags(Qt.ItemFlag.ItemIsSelectable | Qt.ItemFlag.ItemIsEnabled)  # 设置为不可编辑但可选
            cursor.execute('SELECT score_type, score_value FROM score_rules WHERE rule_name=?', (rule_name,))
            scores_info = cursor.fetchall()
            # print(f"获取了评分信息", scores_info)
            score_item = QStandardItem(format_score(scores_info[0]))

            scheme_item = QStandardItem(get_scheme_by_rule_name(rule_name))
            # 将行添加到模型
            self.model.appendRow([id_item, name_item, score_item, scheme_item])

        conn.close()

        # 设置表格视图的光标
        QApplication.setOverrideCursor(Qt.CursorShape.PointingHandCursor)  # 设置应用程序的默认光标样式

    def onRuleClicked(self, index):
        # 使用mapToSource将代理模型的索引映射回原始模型的索引
        sourceIndex = self.proxyModel.mapToSource(index)

        # 规则的ID存储在第一列
        rule_name = self.model.item(sourceIndex.row(), 1).text()
        # 加载规则的详细信息
        self.loadRuleDetails(rule_name)

    def loadRuleDetails(self, rule_name):
        try:
            # 先清空现有条件布局
            self.rule_editing_clear()
            self.conditionsCounter_for_check_logic_expression = get_condition_count(rule_name)

            score_type = int(str(get_score_by_name(rule_name, 0)))
            score_value = str(get_score_by_name(rule_name, 1))
            logic_expression = str(query_rule(rule_name).logic_expression)
            print(f"加载规则详情：{rule_name}，评分类型：{score_type}，评分值：{score_value}，逻辑表达式：{logic_expression}")
            try:
                self.main_window.score_type_comboBox.setCurrentIndex(score_type)
                self.main_window.score_value_line_edit.setText(score_value)
                print(f"设置了评分类型和评分值", score_type, score_value)
            except Exception as e:
                print(f"发生异常：{e}")
            # 切换到规则编辑界面并加载规则详情
            self.main_window.stackedWidget.setCurrentIndex(7)  # 确保这是正确的页面索引
            self.main_window.RuleNameEditText.setText(rule_name)

            self.main_window.RuleNameEditText.setReadOnly(True)  # 设置规则名称不可编辑

            # print(f"数据库绝对路径", RULE_DB_PATH)
            # print(f"规则名称", rule_name)
            selected_rule = query_rule(rule_name)
            # 查询并加载规则的各项条件数据
            regex = selected_rule.regex_rules

            keyword = selected_rule.keyword_rules

            script = selected_rule.script_rules
            threshold = get_script_by_name(rule_name, 1)

            if regex:
                print("添加正则表达式匹配条件")
                for regex_condition in regex:
                    self.add_condition_layout("正则表达式匹配", regex_condition['target_role'],
                                              regex_condition['pattern'])
            # 对于关键词匹配，我们可能同时需要关键词和匹配类型
            if keyword:
                print("添加关键词匹配条件")
                for keyword_condition in keyword:
                    keyword_match_type = keyword_condition['check_type']
                    keyword_n = keyword_condition['n']
                    additional_information = [keyword_match_type, keyword_n]
                    print(f"传递了检测类型：", additional_information)
                    self.add_condition_layout("关键词匹配", keyword_condition['target_role'],
                                              keyword_condition['keywords'],
                                              additional_info=additional_information)

            # 话术匹配可能包括话术本身和相应的阈值

            if script:
                print("添加话术匹配条件")
                for script_condition in script:
                    self.add_condition_layout("话术匹配", script_condition['target_role'], script_condition['scripts'],
                                              additional_info=threshold)
            self.setup_logic_expression_event()

            try:
                self.main_window.logic_expression_lineEdit.textChanged.disconnect()
            except TypeError:
                pass
            self.main_window.logic_expression_lineEdit.textChanged.connect(self.check_logic_expression)

            self.main_window.logic_expression_lineEdit.setText(logic_expression)
        except Exception as e:
            print(f"加载规则详情发生异常：{e}")

    def insert_text_to_logic_expression(self, text):
        try:
            # 在当前光标位置插入文本
            self.main_window.logic_expression_lineEdit.insert(text)
        except Exception as e:
            print(f"插入文字发生异常：{e}")

    def setup_logic_expression_event(self):
        try:
            self.main_window.add_and.clicked.disconnect()
            self.main_window.add_or.clicked.disconnect()
            self.main_window.add_not.clicked.disconnect()
            self.main_window.add_open_bracket.clicked.disconnect()
            self.main_window.add_close_bracket.clicked.disconnect()
            self.main_window.add_condition.clicked.disconnect()

        except TypeError:
            print("没有连接到任何事件")
            pass
        try:
            self.main_window.add_and.clicked.connect(lambda: self.insert_text_to_logic_expression(" and"))
            self.main_window.add_or.clicked.connect(lambda: self.insert_text_to_logic_expression(" or"))
            self.main_window.add_not.clicked.connect(lambda: self.insert_text_to_logic_expression(" not"))
            self.main_window.add_open_bracket.clicked.connect(lambda: self.insert_text_to_logic_expression(" ("))
            self.main_window.add_close_bracket.clicked.connect(lambda: self.insert_text_to_logic_expression(") "))
            self.main_window.add_condition.clicked.connect(
                self.on_click_add_condition_to_logic_expression)
            self.setup_condition_selection_combo()

        except Exception as e:
            print(f"设定logic_expression_event发生异常：{e}")

    def setup_condition_selection_combo(self):
        self.main_window.add_condition_to_logic_expression_comboBox.clear()
        for i in range(1, self.conditionsCounter + 1):
            print(f"为条件 {i} 添加事件")
            self.main_window.add_condition_to_logic_expression_comboBox.addItem(" " + str(i))

    def check_logic_expression(self):
        try:
            print("检查逻辑表达式")
            # 获取编辑器内容
            text = self.main_window.logic_expression_lineEdit.text()
            # 0. 如果条件数目为0，则直接判定正确
            if self.conditionsCounter_for_check_logic_expression == 0:
                self.main_window.logic_detect_label.setText("逻辑表达式正确")
                self.main_window.logic_detect_label.setStyleSheet("color: green;background-color:transparent")
                return

            # 1. 检查是否包含所有逻辑命题编号

            missing_numbers = [str(i) for i in range(1, self.conditionsCounter_for_check_logic_expression + 1) if
                               str(i) not in text]

            if missing_numbers:
                # 如果有缺失，则更新提示标签
                self.main_window.logic_detect_label.setText(f"缺少条件: {', '.join(missing_numbers)}")
                self.main_window.logic_detect_label.setStyleSheet(
                    "color: orange;background-color:transparent")  # 使提示标签醒目
                return

            # 2. 检查是否是正确的逻辑表达式
            if not is_valid_logic_expression(text, self.conditionsCounter_for_check_logic_expression):
                # 如果表达式不正确，则更新提示标签
                self.main_window.logic_detect_label.setText("逻辑表达式错误")
                self.main_window.logic_detect_label.setStyleSheet("color: red;background-color:transparent")
                return

            # 如果都没有问题，则提示正确
            self.main_window.logic_detect_label.setText("逻辑表达式正确")
            self.main_window.logic_detect_label.setStyleSheet("color: green;background-color:transparent")
        except Exception as e:
            print(f"检查逻辑表达式发生异常：{e}")

    def on_click_add_condition_to_logic_expression(self):

        selected_condition = self.main_window.add_condition_to_logic_expression_comboBox.currentText()
        self.insert_text_to_logic_expression(selected_condition)

    def save_rule(self):
        """
        点击规则保存按钮，保存规则
        :return:
        """
        # 检测各个文本框是否填写完整
        # 检测各个文本框是否填写完整
        for i in range(self.verticalLayout.count()):
            widget = self.verticalLayout.itemAt(i).widget()
            if widget:
                for child in widget.children():
                    # 确保 child 是 QWidget 的实例，，，，想了好久这里怎么搞的
                    if isinstance(child, QtWidgets.QWidget):
                        if not child.isVisible():
                            continue  # 如果控件不可见，则跳过后续的检查
                    if isinstance(child, QtWidgets.QTextEdit):
                        if not child.toPlainText():
                            QtWidgets.QMessageBox.critical(self.main_window, "错误", "条件内容不能为空")
                            return
                    if isinstance(child, QtWidgets.QLineEdit):
                        if not child.text():
                            print(f"相似度阈值{child.text()}，objectName{child.objectName()}")
                            QtWidgets.QMessageBox.critical(self.main_window, "错误", "相似度阈值不能为空")
                            return

        if is_valid_logic_expression(self.main_window.logic_expression_lineEdit.text(),
                                     self.conditionsCounter) is False:
            QMessageBox.critical(self.main_window, "错误", "逻辑表达式不正确,请修改后重试！")
            return

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
            new_rule = Rule(rule_name)

            # 更改评分设置
            new_rule.change_score_setting(new_score_type, new_score_value)

            # 保存逻辑表达式
            new_rule.logic_expression = self.main_window.logic_expression_lineEdit.text()

            # 保存条件
            for i in range(1, self.conditionsCounter + 1):
                comboBox = self.main_window.findChild(QtWidgets.QComboBox, f"condition_type_comboBox_{i}")
                condition_type = comboBox.currentText() if comboBox else None
                target_role = self.main_window.findChild(QtWidgets.QComboBox,
                                                         f"target_role_comboBox_{i}").currentIndex()
                if condition_type == "正则表达式匹配":
                    regex_pattern = self.main_window.findChild(QtWidgets.QTextEdit,
                                                               f"textEdit_content_{i}").toPlainText()

                    new_rule.add_regex_rule(regex_pattern, target_role, i)

                elif condition_type == "关键词匹配":
                    keywords = self.main_window.findChild(QtWidgets.QTextEdit,
                                                          f"textEdit_content_{i}").toPlainText().split(' ')
                    print(f"从规则设置中添加的关键词为：{keywords}")
                    check_type = self.main_window.findChild(QtWidgets.QComboBox, f"check_type_{i}").currentText()
                    if check_type == "any_n":
                        n = int(self.main_window.findChild(QtWidgets.QLineEdit, f"check_n_{i}").text())
                        new_rule.add_keyword_rule(keywords, check_type, target_role, i, n)
                    else:
                        new_rule.add_keyword_rule(keywords, check_type, target_role, i)

                elif condition_type == "话术匹配":
                    scripts = self.main_window.findChild(QtWidgets.QTextEdit,
                                                         f"textEdit_content_{i}").toPlainText().split(' ')
                    similarity_threshold = float(
                        self.main_window.findChild(QtWidgets.QLineEdit, f"textEdit_similarity_threshold_{i}").text())
                    new_rule.add_script_rule(scripts, similarity_threshold, target_role, i)

            add_rule(new_rule)
            print("规则保存成功")
            QMessageBox.information(self.main_window, "成功", f"规则 {rule_name} 已保存")
            # 更新规则页面
            self.setupRuleManagerTableView()
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

    def on_clicked_import_rules(self):
        """
        打开文件选择器来选择JSON文件，并调用import_rules_from_json函数来导入规则。
        """
        file_path, _ = QFileDialog.getOpenFileName(self.main_window, "选择规则配置文件", "",
                                                   "JSON Files (*.json)",
                                                   options=QFileDialog.Option.DontUseNativeDialog)
        if file_path:
            try:
                import_rules_from_json(file_path)
                QMessageBox.information(self.main_window, "导入成功", "规则成功导入数据库。")
                self.setupRuleManagerTableView()
            except Exception as e:
                QMessageBox.critical(self.main_window, "导入失败", f"导入过程中发生错误：{e}")

    def on_clicked_export_rules(self):
        """
        打开文件选择器来选择保存位置和文件名，并调用export_rules_to_json函数来导出规则。
        """
        date_str = QDateTime.currentDateTime().toString("yyyy-MM-dd_HH-mm-ss")
        default_name = "rules_config_" + date_str + ".json"
        file_path, _ = QFileDialog.getSaveFileName(self.main_window, "导出规则配置文件", default_name,
                                                   "JSON Files (*.json)",
                                                   options=QFileDialog.Option.DontUseNativeDialog)
        if file_path:
            try:
                export_rules_to_json(RULE_DB_PATH, file_path)
                QMessageBox.information(self.main_window, "导出成功", "规则成功导出到文件。")
            except Exception as e:
                QMessageBox.critical(self.main_window, "导出失败", f"导出过程中发生错误：{e}")

    def on_click_generate_ai_rule_suggestion(self):
        direction = self.main_window.ai_direction_textEdit.toPlainText()
        if not direction:
            QMessageBox.critical(self.main_window, "错误", "请提供一个方向描述。")
            return

        # 显示等待窗口
        self.waitingDialog = WaitingDialog(self.main_window)
        self.waitingDialog.setModal(True)
        self.waitingDialog.setWindowTitle("请稍候")
        self.waitingDialog.show()
        self.conditionsCounter_for_check_logic_expression = 0

        # 创建并启动AI线程
        self.ai_thread = AISuggestionThread(direction)
        self.ai_thread.finished.connect(self.on_ai_suggestion_received)
        self.ai_thread.start()

    def on_ai_suggestion_received(self, rule_json, error):
        self.waitingDialog.accept()  # 关闭等待窗口

        if error is not None:  # 检查是否有错误
            QMessageBox.critical(self.main_window, "错误", f"AI建议获取错误:生成规则的AI建议时发生错误：{error}")
            return
        print(f"AI建议的规则JSON：{rule_json}")

        if rule_json == "处理超时，请检查网络连接并重试":
            QMessageBox.critical(self.main_window, "错误", f"AI建议获取错误:{rule_json}")
            return
        try:
            self.add_conditions_from_json(rule_json)
        except Exception as e:
            QMessageBox.critical(self.main_window, "错误", f"处理AI建议时发生错误：{e}")

    def add_conditions_from_json(self, json_data):
        """
        从JSON格式的字符串中读取规则信息，并使用add_condition_layout添加到布局中。

        Parameters:
            json_data (str): 包含规则定义的JSON字符串。
        """
        self.rule_editing_clear()
        self.main_window.logic_expression_lineEdit.textChanged.connect(self.check_logic_expression)
        # 解析JSON字符串
        try:
            rule_data = json.loads(json_data)
        except json.JSONDecodeError as e:
            QMessageBox.critical(self.main_window, "错误", f"返回值发生错误，请尝试重新获取：{e}")
            return

        self.main_window.RuleNameEditText.setText(rule_data['rule_name'])
        self.main_window.score_type_comboBox.setCurrentIndex(int(rule_data['score_type']))
        self.main_window.score_value_line_edit.setText(str(rule_data['score_value']))

        # 添加话术匹配规则
        for script_rule in rule_data['script_rules']:
            self.add_condition_layout(condition_type="话术匹配",
                                      target_role=int(script_rule['target_role']),
                                      condition_value=script_rule['scripts'],  # 直接传递列表
                                      additional_info=script_rule['similarity_threshold'])
            self.conditionsCounter_for_check_logic_expression += 1

        # 添加关键词匹配规则
        for keyword_rule in rule_data['keyword_rules']:
            self.add_condition_layout(condition_type="关键词匹配",
                                      target_role=int(keyword_rule['target_role']),
                                      condition_value=keyword_rule['keywords'],  # 直接传递列表
                                      additional_info=(keyword_rule['check_type'], keyword_rule.get('n')))
            self.conditionsCounter_for_check_logic_expression += 1

        # 添加正则表达式匹配规则
        for regex_rule in rule_data['regex_rules']:
            self.add_condition_layout(condition_type="正则表达式匹配",
                                      target_role=int(regex_rule['target_role']),
                                      condition_value=regex_rule['pattern'])  # 传递字符串，因为正则是单个字符串
            self.conditionsCounter_for_check_logic_expression += 1
        self.main_window.logic_expression_lineEdit.setText(rule_data['logic_expression'])
        self.setup_condition_selection_combo()
