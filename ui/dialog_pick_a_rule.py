# Form implementation generated from reading ui file 'dialog_pick_a_rule.ui'
#
# Created by: PyQt6 UI code generator 6.4.2
#
# WARNING: Any manual changes made to this file will be lost when pyuic6 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt6 import QtCore, QtGui, QtWidgets


class Ui_add_rule_to_scheme_Dialog(object):
    def setupUi(self, add_rule_to_scheme_Dialog):
        add_rule_to_scheme_Dialog.setObjectName("add_rule_to_scheme_Dialog")
        add_rule_to_scheme_Dialog.resize(216, 75)
        self.pick_a_rule_buttonBox = QtWidgets.QDialogButtonBox(parent=add_rule_to_scheme_Dialog)
        self.pick_a_rule_buttonBox.setGeometry(QtCore.QRect(20, 40, 161, 32))
        self.pick_a_rule_buttonBox.setOrientation(QtCore.Qt.Orientation.Horizontal)
        self.pick_a_rule_buttonBox.setStandardButtons(QtWidgets.QDialogButtonBox.StandardButton.Cancel|QtWidgets.QDialogButtonBox.StandardButton.Ok)
        self.pick_a_rule_buttonBox.setObjectName("pick_a_rule_buttonBox")
        self.pick_a_rule_comboBox = QtWidgets.QComboBox(parent=add_rule_to_scheme_Dialog)
        self.pick_a_rule_comboBox.setGeometry(QtCore.QRect(20, 10, 171, 22))
        self.pick_a_rule_comboBox.setObjectName("pick_a_rule_comboBox")

        self.retranslateUi(add_rule_to_scheme_Dialog)
        self.pick_a_rule_buttonBox.accepted.connect(add_rule_to_scheme_Dialog.accept) # type: ignore
        self.pick_a_rule_buttonBox.rejected.connect(add_rule_to_scheme_Dialog.reject) # type: ignore
        QtCore.QMetaObject.connectSlotsByName(add_rule_to_scheme_Dialog)

    def retranslateUi(self, add_rule_to_scheme_Dialog):
        _translate = QtCore.QCoreApplication.translate
        add_rule_to_scheme_Dialog.setWindowTitle(_translate("add_rule_to_scheme_Dialog", "选择规则"))