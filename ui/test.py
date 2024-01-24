import sys
from PyQt6.QtWidgets import QApplication, QMainWindow, QTreeWidget, QTreeWidgetItem


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        # 设置窗口标题和大小
        self.setWindowTitle("侧边栏示例")
        self.setGeometry(100, 100, 800, 600)

        # 创建 QTreeWidget 对象
        self.tree = QTreeWidget(self)
        self.tree.setColumnCount(1)  # 设置列数
        self.tree.setHeaderLabel('选项')  # 设置头部标题

        # 添加选项
        options = ["选项1", "选项2", "选项3"]
        for option in options:
            parent = QTreeWidgetItem(self.tree)
            parent.setText(0, option)

            # 添加子选项
            for i in range(3):
                child = QTreeWidgetItem(parent)
                child.setText(0, f"{option} 子选项 {i + 1}")

        # 设置大小和位置
        self.tree.setGeometry(0, 0, 200, 600)


# 创建应用实例和窗口实例，然后运行
app = QApplication(sys.argv)
window = MainWindow()
window.show()
sys.exit(app.exec())
