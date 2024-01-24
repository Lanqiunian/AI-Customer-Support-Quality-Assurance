from PyQt6 import QtWidgets


def autoResizeColumnsWithStretch(tableViewWidget):
    """
    使表格的列自动调整宽度，并且最后一列自动填充剩余空间, 使表格看起来更美观
    每个tableViewWidget都需要调用一次这个函数
    :param tableViewWidget:
    :return:
    """
    # 调整填充方式，前两列按照内容来填充，最后一列直接进行延申到末尾
    tableViewWidget.horizontalHeader().setSectionResizeMode(0,
                                                            QtWidgets.QHeaderView.ResizeMode.ResizeToContents)
    tableViewWidget.horizontalHeader().setSectionResizeMode(1,
                                                            QtWidgets.QHeaderView.ResizeMode.ResizeToContents)
    # 使最后一列自动扩展以填满表格剩余空间
    tableViewWidget.horizontalHeader().setStretchLastSection(True)
