import csv
from datetime import datetime

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QFileDialog, QAbstractItemView


def autoResizeColumnsWithStretch(tableViewWidget):
    """
    使表格的列宽自适应内容，并为每列增加额外宽度，避免文字被遮挡。
    :param tableViewWidget: QTableView对象
    """
    tableViewWidget.resizeColumnsToContents()  # 首先进行自适应宽度调整
    # 隐藏垂直表头
    tableViewWidget.verticalHeader().hide()
    extraSpace = 25  # 额外增加的宽度，可根据实际情况调整

    # 遍历每一列（除了最后一列），在自适应宽度的基础上增加额外宽度
    for column in range(tableViewWidget.model().columnCount() - 1):
        currentWidth = tableViewWidget.columnWidth(column)  # 获取当前列的宽度
        tableViewWidget.setColumnWidth(column, currentWidth + extraSpace)  # 增加额外宽度

    # 最后一列使用Stretch模式，填满剩余空间
    tableViewWidget.horizontalHeader().setStretchLastSection(True)
    # 设置为不可编辑
    tableViewWidget.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)


def immersingTableView(tableViewWidget):
    """
    自定义QTableView的外观，包括列头文字和表格中文字的区别。
    :param tableViewWidget: QTableView对象
    """
    # 设置样式表
    tableViewWidget.setStyleSheet("""
        QTableView {
            background-color: transparent;
            border: none;
        }
        QTableView::item {
            border-bottom: 1px solid #d6d9dc; /* 表格项之间的分割线 */
            padding: 5px;
            color: #2e3436; /* 表格中文字颜色 */
            font-size: 14px; /* 表格中文字大小 */
        }
        QHeaderView::section {
            background-color: #f0f0f0; /* 列头背景色 */
            padding: 5px;
            border: none;
            color: #2e3436; /* 列头文字颜色 */
            font-size: 14px; /* 列头文字大小 */
            font-weight: bold; /* 列头文字加粗 */
        }
        QHeaderView {
            background-color: transparent;
            border: none;
        }
        QTableView::item:selected {
            background-color: #a8d1f7; /* 选中项背景色 */
        }
    """)

    # 隐藏水平和垂直滚动条
    tableViewWidget.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
    tableViewWidget.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)

    # 关闭表格的默认网格线显示
    tableViewWidget.setShowGrid(False)

    # 设置为不可编辑
    tableViewWidget.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)


def immersing_TextEdit(textEditWidget):
    """
    自定义QTextEdit的外观，包括文字的颜色和大小。
    :param textEditWidget: QTextEdit对象
    """
    # 设置样式表
    textEditWidget.setStyleSheet("""
        QTextEdit#display_AI_prompt_TextEdit {
        background-color: transparent;
        border: 2px solid #cfcfcf; 
        border-radius: 10px; 
        }

        QTextEdit#display_AI_prompt_TextEdit QScrollBar:vertical {
            width: 0px;
        }
        
        QTextEdit#display_AI_prompt_TextEdit QScrollBar:horizontal {
        height: 0px;
        }""")


def user_select_save_file(parent, default_name):
    """
    弹出一个文件选择对话框，让用户选择保存文件的路径和文件名。

    Parameters:
        parent: 传递父窗口对象，通常是你的主窗口或当前窗口。
        default_name (str): 默认的文件名。

    Returns:
        str: 用户选择的文件路径。如果用户取消，则返回None。
    """
    default_name = datetime.now().strftime(
        '%Y-%m-%d_%H-%M-%S') + "_export.csv" if default_name is None else default_name
    options = QFileDialog.Option.DontUseNativeDialog
    file_path, _ = QFileDialog.getSaveFileName(
        parent,
        "导出任务报告",
        default_name,
        "CSV Files (*.csv)",
        options=options
    )
    return file_path if file_path else None


def export_model_to_csv(model, parent):
    """
    弹出文件保存对话框，让用户选择保存位置和文件名，然后将QStandardItemModel的内容导出为CSV文件。

    Parameters:
        model (QStandardItemModel): 要导出的模型。
        parent: 传递父窗口对象，通常是你的主窗口或当前窗口。
    """
    file_path = user_select_save_file(parent)  # 获取用户选择的文件路径
    if file_path:
        # 如果用户选择了文件路径，则执行导出操作
        with open(file_path, mode='w', newline='', encoding='utf-8-sig') as file:
            import csv
            writer = csv.writer(file)

            # 写入列标题
            headers = [model.headerData(i, Qt.Orientation.Horizontal) for i in range(model.columnCount())]
            writer.writerow(headers)

            # 遍历模型中的所有行
            for row in range(model.rowCount()):
                row_data = []
                for column in range(model.columnCount()):
                    item = model.item(row, column)
                    # 检查项是否存在
                    if item is not None:
                        row_data.append(item.text())
                    else:
                        row_data.append('')
                writer.writerow(row_data)
        print(f"Data exported to {file_path}")
    else:
        print("Export cancelled.")
