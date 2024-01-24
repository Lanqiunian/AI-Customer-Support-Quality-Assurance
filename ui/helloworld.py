"""
第一个puqt6
"""
from PyQt6.QtWidgets import QApplication, QWidget, QLabel
import sys

app = QApplication(sys.argv)  # 创建一个应用

window = QWidget()
window.setWindowTitle("草泥马")
window.resize(400, 300)
window.move(960, 480)
window.show()

label = QLabel()
label.setText("CNM")
label.move(200, 20)
label.resize(150, 50)
label.setStyleSheet("background-color:yellow;padding:10px")
label.setParent(window)
label.show()

sys.exit(app.exec())  # 用这个，可以显示报错
