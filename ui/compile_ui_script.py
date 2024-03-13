import subprocess

# 将 .ui 文件转换为 .py 文件
ui_file = "main_window.ui"
py_file = "main_window.py"
subprocess.run(["pyuic6", "-o", py_file, ui_file], check=True)

# 向生成的 .py 文件添加 import 语句
with open(py_file, "r+", encoding='utf-8') as file:  # 指定文件编码为 UTF-8
    content = file.read()
    file.seek(0, 0)
    file.write("import resources\n" + content)
