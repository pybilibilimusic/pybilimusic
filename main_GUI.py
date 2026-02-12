import sys
import threading
import download_mp4
from PyQt5.QtCore import pyqtSignal, QObject
from PyQt5.QtWidgets import QApplication, QMainWindow

from windows import Ui_MainWindow  # 导入自动生成的UI类


# 创建一个信号类用于线程与UI通信
class DownloadSignals(QObject):
    progress_updated = pyqtSignal(int)
    status_updated = pyqtSignal(str)
    finished = pyqtSignal()  # 完成后通知


class DownloadThread(threading.Thread):
    def __init__(self, url, signals):
        super().__init__()
        self.url = url
        self.signals = signals

    def run(self):
        # 定义回调函数
        def progress_callback(progress):
            self.signals.progress_updated.emit(progress)

        def status_callback(status):
            self.signals.status_updated.emit(status)

        # 调用外部模块
        download_mp4.download_video(self.url)
        self.signals.finished.emit()


class MusicPlayerApp(QMainWindow):
    def __init__(self):
        super().__init__()

        # 初始化UI
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        # 初始化变量
        self.user_input = ""  # 用于保存用户输入
        self.prompt_list = [
            "正在搜索歌曲，请稍后……",
            "搜索成功！请您选择歌曲，如不选择将于10秒后默认选择最优选项……",
            "正在解析并下载视频，请稍后（取决于视频时长，请耐心等待）……",
            "下载完成！"
        ]
        self.current_prompt_index = 0  # 当前提示索引

        # 创建信号对象
        self.download_signals = DownloadSignals()

        # 初始化界面状态
        self.init_ui()

        # 连接信号和槽
        self.connect_signals()

    def init_ui(self):
        """初始化界面状态"""
        # 隐藏user_info标签（初始不显示）
        self.ui.user_info.setVisible(False)

        # 隐藏name_list分组框（初始不显示）
        self.ui.name_list.setVisible(False)

        # 设置进度条初始值为0
        self.ui.progressBar.setValue(0)

    def connect_signals(self):
        """连接信号和槽函数"""
        # 连接提交按钮的点击事件
        self.ui.submitButton.clicked.connect(self.on_submit_clicked)

        # 连接下载信号
        self.download_signals.progress_updated.connect(self.update_progress)
        self.download_signals.status_updated.connect(self.update_user_info_text)
        self.download_signals.finished.connect(self.on_download_finished)

    def on_submit_clicked(self):
        """处理提交按钮点击事件"""
        # 1. 保存用户输入到变量user_input
        self.user_input = self.ui.lineEdit.text()
        print(f"用户输入: {self.user_input}")

        # 2. 显示user_info标签并设置初始文本
        self.ui.user_info.setVisible(True)
        self.update_user_info()

        # 3. 禁用提交按钮，防止重复提交
        self.ui.submitButton.setEnabled(False)

        # 4. 重置进度条
        self.ui.progressBar.setValue(0)

        # 5. 启动下载线程
        self.download_thread = DownloadThread(self.user_input, self.download_signals)
        self.download_thread.start()

    def update_user_info(self):
        """更新user_info标签的文本（使用预设的提示列表）"""
        if self.current_prompt_index < len(self.prompt_list):
            text = self.prompt_list[self.current_prompt_index]
            self.ui.user_info.setText(text)
            self.current_prompt_index += 1

    def update_user_info_text(self, text):
        """直接更新user_info标签的文本（用于回调）"""
        self.ui.user_info.setText(text)

    def update_progress(self, value):
        """更新进度条"""
        self.ui.progressBar.setValue(value)

    def on_download_finished(self):
        """下载完成后的处理"""
        # 启用提交按钮
        self.ui.submitButton.setEnabled(True)

        # 模拟传入列表到Group Box
        # 假设这是你的程序传出的列表
        name_list = ["歌曲A", "歌曲B", "歌曲C", "歌曲D", "歌曲E"]
        self.load_name_list(name_list)

        # 显示Group Box
        self.ui.name_list.setVisible(True)

        # 更新用户信息
        self.update_user_info()

    def load_name_list(self, name_list):
        """
        将列表加载到Group Box的单选按钮中

        参数:
            name_list: 包含5个元素的列表，将依次设置到单选按钮的文本
        """
        # 获取Group Box中的所有单选按钮
        radio_buttons = [
            self.ui.name_1,
            self.ui.name_2,
            self.ui.name_3,
            self.ui.name_4,
            self.ui.name_5
        ]

        # 确保列表不超过5个元素
        names = name_list[:5]

        # 更新每个单选按钮的文本
        for i, radio_button in enumerate(radio_buttons):
            if i < len(names):
                radio_button.setText(names[i])
                radio_button.setVisible(True)
            else:
                radio_button.setVisible(False)

        # 可选：默认选中第一个选项
        if names:
            radio_buttons[0].setChecked(True)

        # 在这里添加进一步开发的注释
        # [进一步开发位置]：可以在这里添加单选按钮的选择事件处理


# 程序入口
if __name__ == "__main__":
    app = QApplication(sys.argv)

    # 创建主窗口实例
    main_window = MusicPlayerApp()

    # 显示窗口
    main_window.show()

    # 进入应用程序的主循环
    sys.exit(app.exec_())