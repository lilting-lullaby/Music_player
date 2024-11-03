import tkinter as tk
from PIL import Image, ImageTk
from ctypes import cast, POINTER
from comtypes import CLSCTX_ALL
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume

class VolumeControl:
    def __init__(self, root, initial_volume=50):
        self.root = root
        self.volume_level = initial_volume
        self.is_slider_visible = False  # 控制音量条显示状态，初始为隐藏

        # 获取系统音量控制
        devices = AudioUtilities.GetSpeakers()
        interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
        self.volume = cast(interface, POINTER(IAudioEndpointVolume))

        # 设置初始音量
        self.set_system_volume(initial_volume / 100.0)

        # 创建音量条框架（包含自定义的音量条和标签）
        self.volume_slider_frame = tk.Frame(root, bg="white", bd=1, relief="solid")
        self.volume_slider_frame.place(x=root.winfo_width() - 70, y=20, anchor="ne")  # 固定在右上角位置

        # 创建一个Canvas作为自定义音量条
        self.volume_canvas = tk.Canvas(self.volume_slider_frame, width=10, height=120, bg="white", highlightthickness=0)
        self.volume_canvas.pack(pady=5)

        # 音量百分比标签，显示在音量条上方
        self.volume_label = tk.Label(self.volume_slider_frame, text=f"{self.volume_level}%", font=("Arial", 10), bg="white")
        self.volume_label.pack()

        # 绑定音量条的点击和拖动事件
        self.volume_canvas.bind("<Button-1>", self.set_volume_from_click)
        self.volume_canvas.bind("<B1-Motion>", self.set_volume_from_click)
        
        # 确保音量条初始隐藏
        self.volume_slider_frame.place_forget()

        # 更新音量条初始状态
        self.update_volume_display()

    def set_system_volume(self, volume_level):
        """设置系统音量"""
        # 设置系统音量（范围从 0.0 到 1.0）
        self.volume.SetMasterVolumeLevelScalar(volume_level, None)

    def toggle_volume_slider(self, button=None):
        """显示或隐藏音量条，固定在界面右上角"""
        if self.is_slider_visible:
            # 隐藏音量条
            self.volume_slider_frame.place_forget()
            self.is_slider_visible = False
        else:
            # 显示音量条
            self.volume_slider_frame.place(x=self.root.winfo_width(), y=0, anchor="ne")
            self.is_slider_visible = True
            self.update_volume_display()  # 更新音量条的显示

    def set_volume_from_click(self, event):
        """根据点击位置设置音量"""
        slider_height = 120
        # 计算音量百分比
        click_y = event.y
        self.volume_level = max(0, min(int((1 - click_y / slider_height) * 100), 100))
        self.update_volume_display()
        
        # 更新系统音量
        self.set_system_volume(self.volume_level / 100.0)

    def update_volume_display(self):
        """更新音量条和标签显示"""
        self.volume_label.config(text=f"{self.volume_level}%")
        self.volume_canvas.delete("slider")  # 删除之前的滑块图形

        # 计算滑块的位置并绘制
        slider_height = 120
        slider_position = slider_height * (1 - self.volume_level / 100)
        self.volume_canvas.create_line(5, 0, 5, slider_height, fill="gray", width=2, tags="slider")  # 背景条
        self.volume_canvas.create_line(5, slider_position, 5, slider_height, fill="green", width=2, tags="slider")  # 音量进度条
        self.volume_canvas.create_oval(0, slider_position - 5, 10, slider_position + 5, fill="green", outline="green", tags="slider")  # 滑块圆形

    def get_volume(self):
        """返回当前音量级别"""
        return self.volume_level

    def set_volume_level(self, volume):
        """通过代码设置音量（而非手动滑动）"""
        self.volume_level = volume
        self.update_volume_display()
        
        # 更新系统音量
        self.set_system_volume(volume / 100.0)
