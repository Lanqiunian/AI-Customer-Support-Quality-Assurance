import sqlite3

from PyQt6.QtWidgets import QMessageBox

from utils.global_utils import GLOBAL_DB_PATH, get_global_setting


class GlobalSettingPageLogic:
    def __init__(self, main_window):
        self.main_window = main_window

    def setup_global_setting(self):

        user_name = get_global_setting().user_name
        default_ai_prompt = get_global_setting().default_ai_prompt
        ai_api_key = get_global_setting().api_key
        self.main_window.user_name_lineEdit.setText(user_name)
        self.main_window.default_AI_prompt_textEdit.setText(default_ai_prompt)
        self.main_window.APIkey_lineEdit.setText(ai_api_key)
        print(f"开始提醒", get_global_setting().review_begin_inform)
        print(f"结束提醒", get_global_setting().review_complete_inform)
        self.main_window.review_begin_inform_checkBox.setChecked(get_global_setting().review_begin_inform)
        self.main_window.review_complete_inform_checkBox.setChecked(get_global_setting().review_complete_inform)

    def on_click_save_button(self):
        try:
            user_name = self.main_window.user_name_lineEdit.text()
            default_ai_prompt = self.main_window.default_AI_prompt_textEdit.toPlainText()
            ai_api_key = self.main_window.APIkey_lineEdit.text()
            review_begin_inform = 1 if self.main_window.review_begin_inform_checkBox.isChecked() else 0
            review_complete_inform = 1 if self.main_window.review_complete_inform_checkBox.isChecked() else 0

            conn = sqlite3.connect(GLOBAL_DB_PATH)
            cursor = conn.cursor()
            cursor.execute(
                "UPDATE global SET user_name = ?, default_ai_prompt = ?, API_KEY = ?,review_begin_inform = ?, review_complete_inform = ?",
                (user_name, default_ai_prompt, ai_api_key, review_begin_inform, review_complete_inform))
            conn.commit()
            conn.close()
            QMessageBox.information(self.main_window, "提示", "保存成功！")

            get_global_setting()
            self.setup_global_setting()

            self.main_window.summary_manager.setup_summary_basic_info()
        except Exception as e:
            QMessageBox.critical(self.main_window, "错误", "保存失败！")
            print(e)
