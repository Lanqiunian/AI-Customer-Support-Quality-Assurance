import qdarkstyle
from qdarkstyle import LightPalette

from PyQt6.QtWidgets import QApplication
from services.db.db_rule import init_db

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
    # apply_stylesheet(app, theme='light_cyan_500.xml',invert_secondary=True)
    # extra = {
    #
    #     # Button colors
    #     'danger': '#dc3545',
    #     'warning': '#ffc107',
    #     'success': '#17a2b8',
    #
    #     # Font
    #     'font_family': 'Roboto',
    # }
    #
    # apply_stylesheet(app, 'light_cyan.xml', invert_secondary=True, extra=extra)

    app.setStyleSheet(qdarkstyle.load_stylesheet(qt_api='pyqt6', palette=LightPalette()))

    # 显示窗口
    mainWindow.show()
    # 开始事件循环
    sys.exit(app.exec())
