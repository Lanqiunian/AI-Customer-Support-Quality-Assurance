# Form implementation generated from reading ui file 'main_window.ui'
#
# Created by: PyQt6 UI code generator 6.4.2
#
# WARNING: Any manual changes made to this file will be lost when pyuic6 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt6 import QtCore, QtGui, QtWidgets


class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.setWindowModality(QtCore.Qt.WindowModality.NonModal)
        MainWindow.resize(1008, 610)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Policy.Preferred, QtWidgets.QSizePolicy.Policy.Preferred)
        sizePolicy.setHorizontalStretch(4)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(MainWindow.sizePolicy().hasHeightForWidth())
        MainWindow.setSizePolicy(sizePolicy)
        MainWindow.setContextMenuPolicy(QtCore.Qt.ContextMenuPolicy.PreventContextMenu)
        MainWindow.setStyleSheet("")
        self.centralwidget = QtWidgets.QWidget(parent=MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.treeWidget_3 = QtWidgets.QTreeWidget(parent=self.centralwidget)
        self.treeWidget_3.setGeometry(QtCore.QRect(0, 0, 151, 591))
        self.treeWidget_3.setStyleSheet("QTreeView::item {\n"
"    border-bottom: 1px solid #d6d6d6; /* Add a bottom border to each item */\n"
"    padding: 5px; /* Add padding to make item taller */\n"
"    \n"
"\n"
"    \n"
"}\n"
"QTreeWidget {\n"
"   \n"
"}")
        self.treeWidget_3.setObjectName("treeWidget_3")
        font = QtGui.QFont()
        font.setBold(True)
        font.setUnderline(False)
        font.setStrikeOut(False)
        self.treeWidget_3.headerItem().setFont(0, font)
        item_0 = QtWidgets.QTreeWidgetItem(self.treeWidget_3)
        item_0 = QtWidgets.QTreeWidgetItem(self.treeWidget_3)
        brush = QtGui.QBrush(QtGui.QColor(0, 0, 0))
        brush.setStyle(QtCore.Qt.BrushStyle.Dense4Pattern)
        item_0.setForeground(0, brush)
        item_1 = QtWidgets.QTreeWidgetItem(item_0)
        item_1 = QtWidgets.QTreeWidgetItem(item_0)
        item_0 = QtWidgets.QTreeWidgetItem(self.treeWidget_3)
        item_1 = QtWidgets.QTreeWidgetItem(item_0)
        item_1 = QtWidgets.QTreeWidgetItem(item_0)
        item_0 = QtWidgets.QTreeWidgetItem(self.treeWidget_3)
        item_0 = QtWidgets.QTreeWidgetItem(self.treeWidget_3)
        self.stackedWidget = QtWidgets.QStackedWidget(parent=self.centralwidget)
        self.stackedWidget.setGeometry(QtCore.QRect(150, 0, 861, 591))
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Policy.Preferred, QtWidgets.QSizePolicy.Policy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.stackedWidget.sizePolicy().hasHeightForWidth())
        self.stackedWidget.setSizePolicy(sizePolicy)
        self.stackedWidget.setWhatsThis("")
        self.stackedWidget.setLayoutDirection(QtCore.Qt.LayoutDirection.LeftToRight)
        self.stackedWidget.setStyleSheet("")
        self.stackedWidget.setObjectName("stackedWidget")
        self.page = QtWidgets.QWidget()
        self.page.setObjectName("page")
        self.label = QtWidgets.QLabel(parent=self.page)
        self.label.setGeometry(QtCore.QRect(40, 60, 54, 16))
        self.label.setText("")
        self.label.setObjectName("label")
        self.label_2 = QtWidgets.QLabel(parent=self.page)
        self.label_2.setGeometry(QtCore.QRect(10, 10, 54, 16))
        self.label_2.setObjectName("label_2")
        self.stackedWidget.addWidget(self.page)
        self.page_2 = QtWidgets.QWidget()
        self.page_2.setObjectName("page_2")
        self.label_3 = QtWidgets.QLabel(parent=self.page_2)
        self.label_3.setGeometry(QtCore.QRect(10, 20, 81, 16))
        self.label_3.setFrameShape(QtWidgets.QFrame.Shape.NoFrame)
        self.label_3.setScaledContents(False)
        self.label_3.setObjectName("label_3")
        self.RuleManagerTableView = QtWidgets.QTableView(parent=self.page_2)
        self.RuleManagerTableView.setGeometry(QtCore.QRect(0, 60, 841, 421))
        self.RuleManagerTableView.setFocusPolicy(QtCore.Qt.FocusPolicy.ClickFocus)
        self.RuleManagerTableView.setSelectionMode(QtWidgets.QAbstractItemView.SelectionMode.NoSelection)
        self.RuleManagerTableView.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectionBehavior.SelectRows)
        self.RuleManagerTableView.setIconSize(QtCore.QSize(0, 0))
        self.RuleManagerTableView.setShowGrid(True)
        self.RuleManagerTableView.setObjectName("RuleManagerTableView")
        self.RuleManagerTableView.horizontalHeader().setVisible(True)
        self.RuleManagerTableView.horizontalHeader().setCascadingSectionResizes(False)
        self.RuleManagerTableView.horizontalHeader().setStretchLastSection(True)
        self.AddRuleButton = QtWidgets.QPushButton(parent=self.page_2)
        self.AddRuleButton.setGeometry(QtCore.QRect(760, 20, 81, 31))
        self.AddRuleButton.setObjectName("AddRuleButton")
        self.stackedWidget.addWidget(self.page_2)
        self.page_3 = QtWidgets.QWidget()
        self.page_3.setObjectName("page_3")
        self.label_4 = QtWidgets.QLabel(parent=self.page_3)
        self.label_4.setGeometry(QtCore.QRect(10, 20, 151, 16))
        self.label_4.setObjectName("label_4")
        self.scheme_tableView = QtWidgets.QTableView(parent=self.page_3)
        self.scheme_tableView.setGeometry(QtCore.QRect(0, 40, 841, 451))
        self.scheme_tableView.setObjectName("scheme_tableView")
        self.new_scheme_pushButton = QtWidgets.QPushButton(parent=self.page_3)
        self.new_scheme_pushButton.setGeometry(QtCore.QRect(760, 10, 75, 24))
        self.new_scheme_pushButton.setObjectName("new_scheme_pushButton")
        self.stackedWidget.addWidget(self.page_3)
        self.page_4 = QtWidgets.QWidget()
        self.page_4.setObjectName("page_4")
        self.label_5 = QtWidgets.QLabel(parent=self.page_4)
        self.label_5.setGeometry(QtCore.QRect(10, 10, 61, 16))
        self.label_5.setObjectName("label_5")
        self.task_tableView = QtWidgets.QTableView(parent=self.page_4)
        self.task_tableView.setGeometry(QtCore.QRect(0, 50, 841, 441))
        self.task_tableView.setObjectName("task_tableView")
        self.new_task_pushButton = QtWidgets.QPushButton(parent=self.page_4)
        self.new_task_pushButton.setGeometry(QtCore.QRect(760, 10, 81, 31))
        self.new_task_pushButton.setObjectName("new_task_pushButton")
        self.stackedWidget.addWidget(self.page_4)
        self.page_5 = QtWidgets.QWidget()
        self.page_5.setObjectName("page_5")
        self.label_6 = QtWidgets.QLabel(parent=self.page_5)
        self.label_6.setGeometry(QtCore.QRect(0, 10, 71, 16))
        self.label_6.setObjectName("label_6")
        self.DataSetManagerTableView = QtWidgets.QTableView(parent=self.page_5)
        self.DataSetManagerTableView.setGeometry(QtCore.QRect(10, 50, 831, 441))
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Policy.Fixed, QtWidgets.QSizePolicy.Policy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.DataSetManagerTableView.sizePolicy().hasHeightForWidth())
        self.DataSetManagerTableView.setSizePolicy(sizePolicy)
        self.DataSetManagerTableView.setFocusPolicy(QtCore.Qt.FocusPolicy.ClickFocus)
        self.DataSetManagerTableView.setSelectionMode(QtWidgets.QAbstractItemView.SelectionMode.NoSelection)
        self.DataSetManagerTableView.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectionBehavior.SelectRows)
        self.DataSetManagerTableView.setIconSize(QtCore.QSize(0, 0))
        self.DataSetManagerTableView.setShowGrid(True)
        self.DataSetManagerTableView.setObjectName("DataSetManagerTableView")
        self.DataSetManagerTableView.horizontalHeader().setVisible(True)
        self.DataSetManagerTableView.horizontalHeader().setCascadingSectionResizes(False)
        self.DataSetManagerTableView.horizontalHeader().setStretchLastSection(True)
        self.new_dataset_pushButton = QtWidgets.QPushButton(parent=self.page_5)
        self.new_dataset_pushButton.setGeometry(QtCore.QRect(750, 10, 91, 31))
        self.new_dataset_pushButton.setObjectName("new_dataset_pushButton")
        self.stackedWidget.addWidget(self.page_5)
        self.page_6 = QtWidgets.QWidget()
        self.page_6.setObjectName("page_6")
        self.label_7 = QtWidgets.QLabel(parent=self.page_6)
        self.label_7.setGeometry(QtCore.QRect(10, 20, 54, 16))
        self.label_7.setObjectName("label_7")
        self.stackedWidget.addWidget(self.page_6)
        self.page_7 = QtWidgets.QWidget()
        self.page_7.setObjectName("page_7")
        self.label_8 = QtWidgets.QLabel(parent=self.page_7)
        self.label_8.setGeometry(QtCore.QRect(10, 10, 54, 16))
        self.label_8.setObjectName("label_8")
        self.stackedWidget.addWidget(self.page_7)
        self.page_8 = QtWidgets.QWidget()
        self.page_8.setObjectName("page_8")
        self.label_9 = QtWidgets.QLabel(parent=self.page_8)
        self.label_9.setGeometry(QtCore.QRect(60, 10, 51, 21))
        self.label_9.setObjectName("label_9")
        self.scrollArea_rule_edit = QtWidgets.QScrollArea(parent=self.page_8)
        self.scrollArea_rule_edit.setGeometry(QtCore.QRect(10, 110, 831, 371))
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Policy.Expanding, QtWidgets.QSizePolicy.Policy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.scrollArea_rule_edit.sizePolicy().hasHeightForWidth())
        self.scrollArea_rule_edit.setSizePolicy(sizePolicy)
        self.scrollArea_rule_edit.setWhatsThis("")
        self.scrollArea_rule_edit.setWidgetResizable(True)
        self.scrollArea_rule_edit.setAlignment(QtCore.Qt.AlignmentFlag.AlignLeading|QtCore.Qt.AlignmentFlag.AlignLeft|QtCore.Qt.AlignmentFlag.AlignTop)
        self.scrollArea_rule_edit.setObjectName("scrollArea_rule_edit")
        self.scrollAreaWidgetContents = QtWidgets.QWidget()
        self.scrollAreaWidgetContents.setGeometry(QtCore.QRect(0, 0, 829, 16))
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Policy.Preferred, QtWidgets.QSizePolicy.Policy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.scrollAreaWidgetContents.sizePolicy().hasHeightForWidth())
        self.scrollAreaWidgetContents.setSizePolicy(sizePolicy)
        self.scrollAreaWidgetContents.setAutoFillBackground(True)
        self.scrollAreaWidgetContents.setObjectName("scrollAreaWidgetContents")
        self.scrollArea_rule_edit.setWidget(self.scrollAreaWidgetContents)
        self.label_10 = QtWidgets.QLabel(parent=self.page_8)
        self.label_10.setGeometry(QtCore.QRect(10, 30, 61, 31))
        self.label_10.setObjectName("label_10")
        self.RuleNameEditText = QtWidgets.QTextEdit(parent=self.page_8)
        self.RuleNameEditText.setGeometry(QtCore.QRect(70, 30, 111, 31))
        self.RuleNameEditText.setObjectName("RuleNameEditText")
        self.save_rule_pushButton = QtWidgets.QPushButton(parent=self.page_8)
        self.save_rule_pushButton.setGeometry(QtCore.QRect(190, 30, 71, 31))
        self.save_rule_pushButton.setObjectName("save_rule_pushButton")
        self.NewRuleButton = QtWidgets.QPushButton(parent=self.page_8)
        self.NewRuleButton.setGeometry(QtCore.QRect(270, 70, 71, 31))
        self.NewRuleButton.setObjectName("NewRuleButton")
        self.delete_rule_pushButton = QtWidgets.QPushButton(parent=self.page_8)
        self.delete_rule_pushButton.setGeometry(QtCore.QRect(270, 30, 71, 31))
        self.delete_rule_pushButton.setObjectName("delete_rule_pushButton")
        self.score_type_comboBox = QtWidgets.QComboBox(parent=self.page_8)
        self.score_type_comboBox.setGeometry(QtCore.QRect(70, 70, 111, 31))
        self.score_type_comboBox.setObjectName("score_type_comboBox")
        self.score_type_comboBox.addItem("")
        self.score_type_comboBox.addItem("")
        self.label_score_standard = QtWidgets.QLabel(parent=self.page_8)
        self.label_score_standard.setGeometry(QtCore.QRect(10, 70, 51, 31))
        self.label_score_standard.setObjectName("label_score_standard")
        self.score_value_Label = QtWidgets.QLabel(parent=self.page_8)
        self.score_value_Label.setGeometry(QtCore.QRect(240, 70, 31, 31))
        self.score_value_Label.setObjectName("score_value_Label")
        self.score_value_line_edit = QtWidgets.QLineEdit(parent=self.page_8)
        self.score_value_line_edit.setGeometry(QtCore.QRect(190, 70, 41, 31))
        self.score_value_line_edit.setObjectName("score_value_line_edit")
        self.back_to_dialogue_detail_pushButton = QtWidgets.QPushButton(parent=self.page_8)
        self.back_to_dialogue_detail_pushButton.setGeometry(QtCore.QRect(10, 5, 41, 24))
        self.back_to_dialogue_detail_pushButton.setObjectName("back_to_dialogue_detail_pushButton")
        self.stackedWidget.addWidget(self.page_8)
        self.page_9 = QtWidgets.QWidget()
        self.page_9.setObjectName("page_9")
        self.label_11 = QtWidgets.QLabel(parent=self.page_9)
        self.label_11.setGeometry(QtCore.QRect(10, 10, 91, 16))
        self.label_11.setObjectName("label_11")
        self.save_scheme_pushButton = QtWidgets.QPushButton(parent=self.page_9)
        self.save_scheme_pushButton.setGeometry(QtCore.QRect(480, 20, 75, 24))
        self.save_scheme_pushButton.setObjectName("save_scheme_pushButton")
        self.delete_scheme_pushButton = QtWidgets.QPushButton(parent=self.page_9)
        self.delete_scheme_pushButton.setGeometry(QtCore.QRect(570, 20, 75, 24))
        self.delete_scheme_pushButton.setObjectName("delete_scheme_pushButton")
        self.label_12 = QtWidgets.QLabel(parent=self.page_9)
        self.label_12.setGeometry(QtCore.QRect(20, 150, 71, 16))
        self.label_12.setObjectName("label_12")
        self.label_13 = QtWidgets.QLabel(parent=self.page_9)
        self.label_13.setGeometry(QtCore.QRect(20, 50, 54, 16))
        self.label_13.setObjectName("label_13")
        self.scheme_name_lineEdit = QtWidgets.QLineEdit(parent=self.page_9)
        self.scheme_name_lineEdit.setGeometry(QtCore.QRect(80, 50, 291, 21))
        self.scheme_name_lineEdit.setObjectName("scheme_name_lineEdit")
        self.existing_rules_in_scheme_tableView = QtWidgets.QTableView(parent=self.page_9)
        self.existing_rules_in_scheme_tableView.setGeometry(QtCore.QRect(20, 170, 821, 201))
        self.existing_rules_in_scheme_tableView.setObjectName("existing_rules_in_scheme_tableView")
        self.add_rule_to_scheme_pushButton = QtWidgets.QPushButton(parent=self.page_9)
        self.add_rule_to_scheme_pushButton.setGeometry(QtCore.QRect(800, 140, 21, 24))
        self.add_rule_to_scheme_pushButton.setObjectName("add_rule_to_scheme_pushButton")
        self.delete_rule_from_scheme_pushButton = QtWidgets.QPushButton(parent=self.page_9)
        self.delete_rule_from_scheme_pushButton.setGeometry(QtCore.QRect(820, 140, 21, 24))
        self.delete_rule_from_scheme_pushButton.setObjectName("delete_rule_from_scheme_pushButton")
        self.label_14 = QtWidgets.QLabel(parent=self.page_9)
        self.label_14.setGeometry(QtCore.QRect(20, 80, 54, 16))
        self.label_14.setObjectName("label_14")
        self.scheme_description_textEdit = QtWidgets.QTextEdit(parent=self.page_9)
        self.scheme_description_textEdit.setGeometry(QtCore.QRect(80, 80, 291, 51))
        self.scheme_description_textEdit.setObjectName("scheme_description_textEdit")
        self.stackedWidget.addWidget(self.page_9)
        self.page_10 = QtWidgets.QWidget()
        self.page_10.setObjectName("page_10")
        self.label_15 = QtWidgets.QLabel(parent=self.page_10)
        self.label_15.setGeometry(QtCore.QRect(10, 0, 81, 16))
        self.label_15.setObjectName("label_15")
        self.choose_dataset_tableView = QtWidgets.QTableView(parent=self.page_10)
        self.choose_dataset_tableView.setGeometry(QtCore.QRect(0, 110, 811, 211))
        self.choose_dataset_tableView.setObjectName("choose_dataset_tableView")
        self.pick_dataset_label = QtWidgets.QLabel(parent=self.page_10)
        self.pick_dataset_label.setGeometry(QtCore.QRect(80, 40, 161, 51))
        font = QtGui.QFont()
        font.setFamily("微软雅黑")
        font.setPointSize(24)
        self.pick_dataset_label.setFont(font)
        self.pick_dataset_label.setObjectName("pick_dataset_label")
        self.label_16 = QtWidgets.QLabel(parent=self.page_10)
        self.label_16.setGeometry(QtCore.QRect(270, 60, 41, 16))
        font = QtGui.QFont()
        font.setPointSize(26)
        self.label_16.setFont(font)
        self.label_16.setObjectName("label_16")
        self.pick_scheme_label_2 = QtWidgets.QLabel(parent=self.page_10)
        self.pick_scheme_label_2.setGeometry(QtCore.QRect(340, 40, 131, 51))
        font = QtGui.QFont()
        font.setFamily("微软雅黑")
        font.setPointSize(24)
        self.pick_scheme_label_2.setFont(font)
        self.pick_scheme_label_2.setObjectName("pick_scheme_label_2")
        self.start_analyze_label = QtWidgets.QLabel(parent=self.page_10)
        self.start_analyze_label.setGeometry(QtCore.QRect(600, 40, 131, 51))
        font = QtGui.QFont()
        font.setFamily("微软雅黑")
        font.setPointSize(24)
        self.start_analyze_label.setFont(font)
        self.start_analyze_label.setObjectName("start_analyze_label")
        self.label_17 = QtWidgets.QLabel(parent=self.page_10)
        self.label_17.setGeometry(QtCore.QRect(510, 60, 41, 16))
        font = QtGui.QFont()
        font.setPointSize(26)
        self.label_17.setFont(font)
        self.label_17.setObjectName("label_17")
        self.next_step_pushButton = QtWidgets.QPushButton(parent=self.page_10)
        self.next_step_pushButton.setGeometry(QtCore.QRect(570, 350, 75, 31))
        self.next_step_pushButton.setObjectName("next_step_pushButton")
        self.previous_step_pushButton = QtWidgets.QPushButton(parent=self.page_10)
        self.previous_step_pushButton.setGeometry(QtCore.QRect(480, 350, 81, 31))
        self.previous_step_pushButton.setObjectName("previous_step_pushButton")
        self.task_name_label = QtWidgets.QLabel(parent=self.page_10)
        self.task_name_label.setGeometry(QtCore.QRect(40, 130, 91, 16))
        self.task_name_label.setObjectName("task_name_label")
        self.task_name_lineEdit = QtWidgets.QLineEdit(parent=self.page_10)
        self.task_name_lineEdit.setGeometry(QtCore.QRect(130, 130, 411, 21))
        self.task_name_lineEdit.setObjectName("task_name_lineEdit")
        self.task_description_textEdit = QtWidgets.QTextEdit(parent=self.page_10)
        self.task_description_textEdit.setGeometry(QtCore.QRect(130, 160, 411, 61))
        self.task_description_textEdit.setObjectName("task_description_textEdit")
        self.task_description_label = QtWidgets.QLabel(parent=self.page_10)
        self.task_description_label.setGeometry(QtCore.QRect(40, 160, 91, 16))
        self.task_description_label.setObjectName("task_description_label")
        self.manual_check_checkBox = QtWidgets.QCheckBox(parent=self.page_10)
        self.manual_check_checkBox.setGeometry(QtCore.QRect(40, 230, 101, 16))
        self.manual_check_checkBox.setObjectName("manual_check_checkBox")
        self.stackedWidget.addWidget(self.page_10)
        self.page_11 = QtWidgets.QWidget()
        self.page_11.setObjectName("page_11")
        self.task_detail_tableView = QtWidgets.QTableView(parent=self.page_11)
        self.task_detail_tableView.setGeometry(QtCore.QRect(10, 110, 661, 481))
        self.task_detail_tableView.setObjectName("task_detail_tableView")
        self.delete_task_pushButton = QtWidgets.QPushButton(parent=self.page_11)
        self.delete_task_pushButton.setGeometry(QtCore.QRect(760, 0, 75, 24))
        self.delete_task_pushButton.setObjectName("delete_task_pushButton")
        self.label_46 = QtWidgets.QLabel(parent=self.page_11)
        self.label_46.setGeometry(QtCore.QRect(40, 36, 61, 20))
        self.label_46.setObjectName("label_46")
        self.the_task_description_label = QtWidgets.QLabel(parent=self.page_11)
        self.the_task_description_label.setGeometry(QtCore.QRect(100, 36, 121, 21))
        self.the_task_description_label.setObjectName("the_task_description_label")
        self.label_18 = QtWidgets.QLabel(parent=self.page_11)
        self.label_18.setGeometry(QtCore.QRect(40, 60, 61, 16))
        self.label_18.setObjectName("label_18")
        self.label_50 = QtWidgets.QLabel(parent=self.page_11)
        self.label_50.setGeometry(QtCore.QRect(170, 60, 61, 16))
        self.label_50.setObjectName("label_50")
        self.label_51 = QtWidgets.QLabel(parent=self.page_11)
        self.label_51.setGeometry(QtCore.QRect(100, 60, 71, 16))
        self.label_51.setObjectName("label_51")
        self.label_52 = QtWidgets.QLabel(parent=self.page_11)
        self.label_52.setGeometry(QtCore.QRect(230, 60, 71, 16))
        self.label_52.setObjectName("label_52")
        self.dialogue_count_label = QtWidgets.QLabel(parent=self.page_11)
        self.dialogue_count_label.setGeometry(QtCore.QRect(40, 80, 51, 21))
        font = QtGui.QFont()
        font.setPointSize(14)
        self.dialogue_count_label.setFont(font)
        self.dialogue_count_label.setObjectName("dialogue_count_label")
        self.average_score_label = QtWidgets.QLabel(parent=self.page_11)
        self.average_score_label.setGeometry(QtCore.QRect(100, 80, 61, 21))
        font = QtGui.QFont()
        font.setPointSize(14)
        self.average_score_label.setFont(font)
        self.average_score_label.setObjectName("average_score_label")
        self.hit_rate_label = QtWidgets.QLabel(parent=self.page_11)
        self.hit_rate_label.setGeometry(QtCore.QRect(230, 80, 121, 21))
        font = QtGui.QFont()
        font.setPointSize(12)
        self.hit_rate_label.setFont(font)
        self.hit_rate_label.setObjectName("hit_rate_label")
        self.hit_times_label = QtWidgets.QLabel(parent=self.page_11)
        self.hit_times_label.setGeometry(QtCore.QRect(170, 80, 51, 21))
        font = QtGui.QFont()
        font.setPointSize(14)
        self.hit_times_label.setFont(font)
        self.hit_times_label.setObjectName("hit_times_label")
        self.back_to_task_list_pushButton = QtWidgets.QPushButton(parent=self.page_11)
        self.back_to_task_list_pushButton.setGeometry(QtCore.QRect(0, 0, 31, 31))
        self.back_to_task_list_pushButton.setObjectName("back_to_task_list_pushButton")
        self.the_task_name_label = QtWidgets.QLabel(parent=self.page_11)
        self.the_task_name_label.setGeometry(QtCore.QRect(40, 0, 641, 31))
        font = QtGui.QFont()
        font.setPointSize(16)
        self.the_task_name_label.setFont(font)
        self.the_task_name_label.setObjectName("the_task_name_label")
        self.task_detail_tableView_fixed = QtWidgets.QTableView(parent=self.page_11)
        self.task_detail_tableView_fixed.setGeometry(QtCore.QRect(670, 110, 181, 481))
        self.task_detail_tableView_fixed.setObjectName("task_detail_tableView_fixed")
        self.stackedWidget.addWidget(self.page_11)
        self.page_12 = QtWidgets.QWidget()
        self.page_12.setObjectName("page_12")
        self.label_19 = QtWidgets.QLabel(parent=self.page_12)
        self.label_19.setGeometry(QtCore.QRect(30, 10, 54, 16))
        self.label_19.setObjectName("label_19")
        self.dialogue_scrollArea = QtWidgets.QScrollArea(parent=self.page_12)
        self.dialogue_scrollArea.setGeometry(QtCore.QRect(20, 90, 451, 461))
        self.dialogue_scrollArea.setWidgetResizable(True)
        self.dialogue_scrollArea.setObjectName("dialogue_scrollArea")
        self.scrollAreaWidgetContents_2 = QtWidgets.QWidget()
        self.scrollAreaWidgetContents_2.setGeometry(QtCore.QRect(0, 0, 449, 459))
        self.scrollAreaWidgetContents_2.setObjectName("scrollAreaWidgetContents_2")
        self.dialogue_scrollArea.setWidget(self.scrollAreaWidgetContents_2)
        self.hit_rules_tableView = QtWidgets.QTableView(parent=self.page_12)
        self.hit_rules_tableView.setGeometry(QtCore.QRect(480, 110, 371, 161))
        self.hit_rules_tableView.setObjectName("hit_rules_tableView")
        self.label_39 = QtWidgets.QLabel(parent=self.page_12)
        self.label_39.setGeometry(QtCore.QRect(20, 30, 61, 16))
        self.label_39.setObjectName("label_39")
        self.label_40 = QtWidgets.QLabel(parent=self.page_12)
        self.label_40.setGeometry(QtCore.QRect(130, 30, 54, 16))
        self.label_40.setObjectName("label_40")
        self.label_41 = QtWidgets.QLabel(parent=self.page_12)
        self.label_41.setGeometry(QtCore.QRect(20, 50, 54, 16))
        self.label_41.setObjectName("label_41")
        self.label_42 = QtWidgets.QLabel(parent=self.page_12)
        self.label_42.setGeometry(QtCore.QRect(20, 70, 54, 16))
        self.label_42.setObjectName("label_42")
        self.label_43 = QtWidgets.QLabel(parent=self.page_12)
        self.label_43.setGeometry(QtCore.QRect(520, 10, 151, 41))
        font = QtGui.QFont()
        font.setPointSize(24)
        self.label_43.setFont(font)
        self.label_43.setObjectName("label_43")
        self.dialogue_id_label = QtWidgets.QLabel(parent=self.page_12)
        self.dialogue_id_label.setGeometry(QtCore.QRect(80, 30, 54, 16))
        self.dialogue_id_label.setObjectName("dialogue_id_label")
        self.dataset_name_label = QtWidgets.QLabel(parent=self.page_12)
        self.dataset_name_label.setGeometry(QtCore.QRect(180, 30, 291, 16))
        self.dataset_name_label.setObjectName("dataset_name_label")
        self.service_id_label = QtWidgets.QLabel(parent=self.page_12)
        self.service_id_label.setGeometry(QtCore.QRect(60, 50, 411, 16))
        self.service_id_label.setObjectName("service_id_label")
        self.customer_label = QtWidgets.QLabel(parent=self.page_12)
        self.customer_label.setGeometry(QtCore.QRect(60, 70, 411, 16))
        self.customer_label.setObjectName("customer_label")
        self.score_label = QtWidgets.QLabel(parent=self.page_12)
        self.score_label.setGeometry(QtCore.QRect(670, 10, 71, 41))
        font = QtGui.QFont()
        font.setPointSize(24)
        self.score_label.setFont(font)
        self.score_label.setObjectName("score_label")
        self.back_to_task_detail_pushButton = QtWidgets.QPushButton(parent=self.page_12)
        self.back_to_task_detail_pushButton.setGeometry(QtCore.QRect(0, 0, 31, 31))
        self.back_to_task_detail_pushButton.setObjectName("back_to_task_detail_pushButton")
        self.ai_scrollArea = QtWidgets.QScrollArea(parent=self.page_12)
        self.ai_scrollArea.setGeometry(QtCore.QRect(480, 300, 371, 251))
        self.ai_scrollArea.setWidgetResizable(True)
        self.ai_scrollArea.setObjectName("ai_scrollArea")
        self.scrollAreaWidgetContents_10 = QtWidgets.QWidget()
        self.scrollAreaWidgetContents_10.setGeometry(QtCore.QRect(0, 0, 369, 249))
        self.scrollAreaWidgetContents_10.setObjectName("scrollAreaWidgetContents_10")
        self.ai_scrollArea.setWidget(self.scrollAreaWidgetContents_10)
        self.label_119 = QtWidgets.QLabel(parent=self.page_12)
        self.label_119.setGeometry(QtCore.QRect(480, 280, 61, 16))
        self.label_119.setObjectName("label_119")
        self.label_120 = QtWidgets.QLabel(parent=self.page_12)
        self.label_120.setGeometry(QtCore.QRect(480, 90, 61, 16))
        self.label_120.setObjectName("label_120")
        self.manually_add_pushButton = QtWidgets.QPushButton(parent=self.page_12)
        self.manually_add_pushButton.setGeometry(QtCore.QRect(810, 85, 21, 21))
        self.manually_add_pushButton.setObjectName("manually_add_pushButton")
        self.manually_remove_pushButton = QtWidgets.QPushButton(parent=self.page_12)
        self.manually_remove_pushButton.setGeometry(QtCore.QRect(830, 85, 21, 21))
        self.manually_remove_pushButton.setObjectName("manually_remove_pushButton")
        self.manually_check_pushButton = QtWidgets.QPushButton(parent=self.page_12)
        self.manually_check_pushButton.setGeometry(QtCore.QRect(730, 50, 81, 31))
        self.manually_check_pushButton.setObjectName("manually_check_pushButton")
        self.manually_check_done_pushButton = QtWidgets.QPushButton(parent=self.page_12)
        self.manually_check_done_pushButton.setGeometry(QtCore.QRect(730, 85, 81, 21))
        self.manually_check_done_pushButton.setObjectName("manually_check_done_pushButton")
        self.label_20 = QtWidgets.QLabel(parent=self.page_12)
        self.label_20.setGeometry(QtCore.QRect(510, 60, 111, 21))
        self.label_20.setObjectName("label_20")
        self.manually_check_label = QtWidgets.QLabel(parent=self.page_12)
        self.manually_check_label.setGeometry(QtCore.QRect(620, 60, 101, 21))
        self.manually_check_label.setObjectName("manually_check_label")
        self.stackedWidget.addWidget(self.page_12)
        MainWindow.setCentralWidget(self.centralwidget)
        self.statusbar = QtWidgets.QStatusBar(parent=MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)

        self.retranslateUi(MainWindow)
        self.stackedWidget.setCurrentIndex(11)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)
        MainWindow.setTabOrder(self.scrollArea_rule_edit, self.treeWidget_3)
        MainWindow.setTabOrder(self.treeWidget_3, self.RuleManagerTableView)
        MainWindow.setTabOrder(self.RuleManagerTableView, self.NewRuleButton)
        MainWindow.setTabOrder(self.NewRuleButton, self.save_rule_pushButton)
        MainWindow.setTabOrder(self.save_rule_pushButton, self.RuleNameEditText)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "智能客服质检"))
        self.treeWidget_3.headerItem().setText(0, _translate("MainWindow", "客服质检"))
        __sortingEnabled = self.treeWidget_3.isSortingEnabled()
        self.treeWidget_3.setSortingEnabled(False)
        self.treeWidget_3.topLevelItem(0).setText(0, _translate("MainWindow", "概览"))
        self.treeWidget_3.topLevelItem(1).setText(0, _translate("MainWindow", "质检规则和方案"))
        self.treeWidget_3.topLevelItem(1).child(0).setText(0, _translate("MainWindow", "质检规则配置"))
        self.treeWidget_3.topLevelItem(1).child(1).setText(0, _translate("MainWindow", "质检方案管理"))
        self.treeWidget_3.topLevelItem(2).setText(0, _translate("MainWindow", "质检任务"))
        self.treeWidget_3.topLevelItem(2).child(0).setText(0, _translate("MainWindow", "任务管理"))
        self.treeWidget_3.topLevelItem(2).child(1).setText(0, _translate("MainWindow", "数据集管理"))
        self.treeWidget_3.topLevelItem(3).setText(0, _translate("MainWindow", "待办任务"))
        self.treeWidget_3.topLevelItem(4).setText(0, _translate("MainWindow", "系统管理"))
        self.treeWidget_3.setSortingEnabled(__sortingEnabled)
        self.label_2.setText(_translate("MainWindow", "概览"))
        self.label_3.setText(_translate("MainWindow", "质检规则配置"))
        self.AddRuleButton.setText(_translate("MainWindow", "+ 新建规则"))
        self.label_4.setText(_translate("MainWindow", "质检方案管理"))
        self.new_scheme_pushButton.setText(_translate("MainWindow", "新建方案"))
        self.label_5.setText(_translate("MainWindow", "任务管理"))
        self.new_task_pushButton.setText(_translate("MainWindow", "+新质检任务"))
        self.label_6.setText(_translate("MainWindow", "数据集管理"))
        self.new_dataset_pushButton.setText(_translate("MainWindow", "+ 导入数据集"))
        self.label_7.setText(_translate("MainWindow", "待办任务"))
        self.label_8.setText(_translate("MainWindow", "系统管理"))
        self.label_9.setText(_translate("MainWindow", "规则编辑"))
        self.label_10.setText(_translate("MainWindow", "规则名称："))
        self.save_rule_pushButton.setText(_translate("MainWindow", "保存"))
        self.NewRuleButton.setText(_translate("MainWindow", "+ 新条件"))
        self.delete_rule_pushButton.setText(_translate("MainWindow", "删除"))
        self.score_type_comboBox.setItemText(0, _translate("MainWindow", "一次打分为"))
        self.score_type_comboBox.setItemText(1, _translate("MainWindow", "加减总得分"))
        self.label_score_standard.setText(_translate("MainWindow", "评分规则："))
        self.score_value_Label.setText(_translate("MainWindow", "分"))
        self.back_to_dialogue_detail_pushButton.setText(_translate("MainWindow", "返回"))
        self.label_11.setText(_translate("MainWindow", "方案编辑页面"))
        self.save_scheme_pushButton.setText(_translate("MainWindow", "保存方案"))
        self.delete_scheme_pushButton.setText(_translate("MainWindow", "删除方案"))
        self.label_12.setText(_translate("MainWindow", "已包含规则："))
        self.label_13.setText(_translate("MainWindow", "方案名称："))
        self.add_rule_to_scheme_pushButton.setText(_translate("MainWindow", "+"))
        self.delete_rule_from_scheme_pushButton.setText(_translate("MainWindow", "-"))
        self.label_14.setText(_translate("MainWindow", "方案描述："))
        self.label_15.setText(_translate("MainWindow", "新建质检任务"))
        self.pick_dataset_label.setText(_translate("MainWindow", "选择数据集"))
        self.label_16.setText(_translate("MainWindow", "→"))
        self.pick_scheme_label_2.setText(_translate("MainWindow", "选择方案"))
        self.start_analyze_label.setText(_translate("MainWindow", "开始质检"))
        self.label_17.setText(_translate("MainWindow", "→"))
        self.next_step_pushButton.setText(_translate("MainWindow", "下一步"))
        self.previous_step_pushButton.setText(_translate("MainWindow", "上一步"))
        self.task_name_label.setText(_translate("MainWindow", "质检任务名称*："))
        self.task_description_label.setText(_translate("MainWindow", "质检任务描述*："))
        self.manual_check_checkBox.setText(_translate("MainWindow", "需要人工复检"))
        self.delete_task_pushButton.setText(_translate("MainWindow", "删除任务"))
        self.label_46.setText(_translate("MainWindow", "任务描述："))
        self.the_task_description_label.setText(_translate("MainWindow", "无描述"))
        self.label_18.setText(_translate("MainWindow", "总会话数"))
        self.label_50.setText(_translate("MainWindow", "命中数"))
        self.label_51.setText(_translate("MainWindow", "平均得分"))
        self.label_52.setText(_translate("MainWindow", "命中率"))
        self.dialogue_count_label.setText(_translate("MainWindow", "0"))
        self.average_score_label.setText(_translate("MainWindow", "0"))
        self.hit_rate_label.setText(_translate("MainWindow", "0"))
        self.hit_times_label.setText(_translate("MainWindow", "0"))
        self.back_to_task_list_pushButton.setText(_translate("MainWindow", "←"))
        self.the_task_name_label.setText(_translate("MainWindow", "task_name"))
        self.label_19.setText(_translate("MainWindow", "对话详情"))
        self.label_39.setText(_translate("MainWindow", "对话序号："))
        self.label_40.setText(_translate("MainWindow", "数据集："))
        self.label_41.setText(_translate("MainWindow", "客服："))
        self.label_42.setText(_translate("MainWindow", "用户："))
        self.label_43.setText(_translate("MainWindow", "质检得分："))
        self.dialogue_id_label.setText(_translate("MainWindow", "default"))
        self.dataset_name_label.setText(_translate("MainWindow", "default"))
        self.service_id_label.setText(_translate("MainWindow", "default"))
        self.customer_label.setText(_translate("MainWindow", "default"))
        self.score_label.setText(_translate("MainWindow", "100"))
        self.back_to_task_detail_pushButton.setText(_translate("MainWindow", "←"))
        self.label_119.setText(_translate("MainWindow", "AI分析"))
        self.label_120.setText(_translate("MainWindow", "命中规则"))
        self.manually_add_pushButton.setText(_translate("MainWindow", "+"))
        self.manually_remove_pushButton.setText(_translate("MainWindow", "-"))
        self.manually_check_pushButton.setText(_translate("MainWindow", "进行人工复检"))
        self.manually_check_done_pushButton.setText(_translate("MainWindow", "人工复检完成"))
        self.label_20.setText(_translate("MainWindow", "是否需要人工复检："))
        self.manually_check_label.setText(_translate("MainWindow", "manually_check"))
