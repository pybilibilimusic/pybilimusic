import tkinter as tk
from tkinter import filedialog
# noinspection PyUnresolvedReferences
import ctypes

# noinspection PyBroadException
def select_file(title="请选择文件", filetypes=None):
    """
    高清版文件选择器 - 解决tkinter模糊问题
    """
    try:
        # ========== 关键DPI设置 ==========
        # 告诉Windows这个程序是DPI感知的
        try:
            # Windows 8.1及以上
            ctypes.windll.shcore.SetProcessDpiAwareness(1)  # 系统DPI
        except:
            try:
                # Windows 8及以下
                ctypes.windll.user32.SetProcessDPIAware()
            except:
                pass

        # 创建主窗口
        root = tk.Tk()
        root.withdraw()

        # ========== 高清字体设置 ==========
        # 设置默认字体为系统清晰字体
        default_font = ("Microsoft YaHei UI", 9)  # Windows清晰字体
        root.option_add("*Font", default_font)

        # ========== 窗口缩放设置 ==========
        # 获取系统DPI缩放比例
        try:
            import ctypes
            from ctypes import wintypes

            user32 = ctypes.windll.user32
            user32.SetProcessDPIAware()

            # 获取屏幕DPI
            dc = user32.GetDC(0)
            DPI_SCALEX = ctypes.windll.gdi32.GetDeviceCaps(dc, 88)  # LOGPIXELSX
            DPI_SCALEY = ctypes.windll.gdi32.GetDeviceCaps(dc, 90)  # LOGPIXELSY
            user32.ReleaseDC(0, dc)

            # 计算缩放比例（相对于96 DPI）
            scale_x = DPI_SCALEX / 96.0
            scale_y = DPI_SCALEY / 96.0

            # 调整窗口缩放
            root.tk.call('tk', 'scaling', scale_x)
        except:
            # 如果获取DPI失败，使用默认值
            pass

        # ========== 优化窗口显示 ==========
        # 防止窗口被拉伸
        root.resizable(False, False)

        # 设置窗口风格为现代化
        root.option_add('*Dialog.msg.font', default_font)

        if filetypes is None:
            filetypes = [
            ("视频文件", "*.mp4 *.avi *.mkv *.mov *.wmv"),
            ("MP4文件", "*.mp4"),
            ("所有文件", "*.*")]

        # 创建文件对话框
        file_path = filedialog.askopenfilename(
            title=title,
            filetypes=filetypes
        )

        root.destroy()

        return file_path

    except Exception as e:
        print(f"高清对话框创建失败: {e}")
        # 回退到普通版本
        return None

if __name__ == "__main__":
    print(select_file())