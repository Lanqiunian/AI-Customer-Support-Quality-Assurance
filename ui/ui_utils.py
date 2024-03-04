from PyQt6 import QtWidgets


def autoResizeColumnsWithStretch(tableViewWidget):
    """
    使表格的列宽自适应内容，并为每列增加额外宽度，避免文字被遮挡。
    :param tableViewWidget: QTableView对象
    """
    tableViewWidget.resizeColumnsToContents()  # 首先进行自适应宽度调整
    #隐藏垂直表头
    tableViewWidget.verticalHeader().hide()
    extraSpace = 25  # 额外增加的宽度，可根据实际情况调整

    # 遍历每一列（除了最后一列），在自适应宽度的基础上增加额外宽度
    for column in range(tableViewWidget.model().columnCount() - 1):
        currentWidth = tableViewWidget.columnWidth(column)  # 获取当前列的宽度
        tableViewWidget.setColumnWidth(column, currentWidth + extraSpace)  # 增加额外宽度

    # 最后一列使用Stretch模式，填满剩余空间
    tableViewWidget.horizontalHeader().setStretchLastSection(True)


