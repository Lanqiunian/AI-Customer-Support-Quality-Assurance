from PyQt6.QtGui import QStandardItemModel
from PyQt6.QtWidgets import QApplication
from services.db_rule import init_db
from ui.main_window_logic import CustomMainWindow

# 在程序开始时初始化数据库
if __name__ == "__main__":
    import sys

    init_db()
    # 加载数据
    # 创建 QApplication 实例
    app = QApplication(sys.argv)
    # 创建自定义窗口实例
    mainWindow = CustomMainWindow()

    # 显示窗口
    mainWindow.show()
    # 开始事件循环
    sys.exit(app.exec())
