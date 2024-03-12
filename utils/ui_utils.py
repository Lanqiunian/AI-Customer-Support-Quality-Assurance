import csv
import html
import re
from datetime import datetime

from PyQt6.QtCore import Qt, QSortFilterProxyModel, QModelIndex
from PyQt6.QtWidgets import QFileDialog, QAbstractItemView

from services.db.db_dialogue_data import get_dialogue_by_datasetname_and_dialogueid
from services.db.db_task import get_comment_by_task_id_and_dialogue_id


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


def user_select_save_file(parent, default_name=None):
    """
    弹出一个文件选择对话框，让用户选择保存文件的路径和文件名。

    Parameters:
        parent: 传递父窗口对象，通常是你的主窗口或当前窗口。
        default_name (str): 默认的文件名。

    Returns:
        str: 用户选择的文件路径。如果用户取消，则返回None。
    """
    try:
        default_name = "质检报告-" + datetime.now().strftime(
            '%Y-%m-%d_%H-%M-%S') + ".csv" if default_name is None else default_name
        options = QFileDialog.Option.DontUseNativeDialog
        file_path, _ = QFileDialog.getSaveFileName(
            parent,
            "导出任务报告",
            default_name,
            "CSV Files (*.csv)",
            options=options
        )
    except Exception as e:
        print(f"选择文件路径: {e}")
        file_path = None
    return file_path if file_path else None


def convert_html_to_plain_text(html_content):
    # 处理HTML实体
    text = html.unescape(html_content)

    # 去除<style>标签及其内容
    text = re.sub(r'<style[^<]*?</style>', '', text, flags=re.DOTALL)

    # 将<p>, <br>, 和列表标签转换为换行符
    text = re.sub(r'(?i)<br\s*/?>', '\n', text)  # 处理<br>和<br/>
    text = re.sub(r'(?i)</p>', '\n', text)  # 处理</p>
    text = re.sub(r'(?i)<li>', '\n', text)  # 处理<li>
    # 注意: 可能需要更多替换以处理其他需要保留换行的情况

    # 去除其他HTML标签
    text = re.sub('<[^<]+?>', '', text)

    # 去除多余的空白字符，但保留换行
    text = re.sub('[ \t]+', ' ', text)  # 替换多余的空格和制表符为单个空格
    text = re.sub('(\n\s*)+\n', '\n\n', text)  # 压缩多个换行和空格为两个换行符

    return text.strip()


def export_model_to_csv(model, parent, task_id):
    print("导出操作开始。")
    file_path = user_select_save_file(parent)  # 获取用户选择的文件路径
    if file_path:
        # 如果用户选择了文件路径，则执行导出操作
        with open(file_path, mode='w', newline='', encoding='utf-8-sig') as file:
            import csv
            writer = csv.writer(file)

            # 写入列标题，忽略最后一列“操作”列，并添加"复检建议"列，以及“客服名”和“用户名”列
            headers = [model.headerData(i, Qt.Orientation.Horizontal) for i in range(model.columnCount() - 1)]
            # 在适当的位置插入新列标题
            headers.insert(4, "客服ID")  # 假设要插入为第5列
            headers.insert(5, "客户ID")  # 假设要插入为第6列
            headers.append("复检建议")  # 添加复检建议列标题
            writer.writerow(headers)

            # 遍历模型中的所有行
            for row in range(model.rowCount()):
                row_data = []
                for column in range(model.columnCount() - 1):  # 忽略最后一列
                    item = model.item(row, column)
                    if item is not None:
                        row_data.append(item.text())
                    else:
                        row_data.append('')

                # 在适当的位置插入客服ID和客户ID
                dialogue_id = model.item(row, 0).text()  # 假设对话ID位于第一列
                dataset_name = model.item(row, 3).text()  # 假设所属数据集位于第四列，根据实际情况调整

                dialogue_data = get_dialogue_by_datasetname_and_dialogueid(dataset_name, dialogue_id)
                service = dialogue_data.loc[0, "客服ID"]
                customer = dialogue_data.loc[0, "客户ID"]
                row_data.insert(4, service)  # 在第5列插入客服ID
                row_data.insert(5, customer)  # 在第6列插入客户ID

                # 获取复检建议并添加到行数据
                review_comment = get_comment_by_task_id_and_dialogue_id(task_id, dialogue_id)
                review_comment = convert_html_to_plain_text(
                    review_comment) if review_comment else "未给出复检建议"  # 如果返回None，则添加空字符串
                row_data.append(review_comment)

                writer.writerow(row_data)

        print(f"数据已导出到 {file_path}")
    else:
        print("导出操作被取消。")


class NumericSortProxyModel(QSortFilterProxyModel):
    """
    这个类用于定义一个可以比较字符串数字大小的托管模型，我的代码中在填入模型时不得不用str，而排序得用int，所以需要这个类。
    """

    def lessThan(self, left: QModelIndex, right: QModelIndex) -> bool:
        leftData = self.sourceModel().data(left)
        rightData = self.sourceModel().data(right)

        # Attempt to convert string data to integers for comparison
        try:
            leftNumber = int(leftData)
            rightNumber = int(rightData)
            return leftNumber < rightNumber
        except ValueError:
            # Fall back to default string comparison if conversion fails
            return leftData < rightData
