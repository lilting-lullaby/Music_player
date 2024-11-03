import tkinter as tk
from tkinter import filedialog
from PIL import Image, ImageTk
import json
import os

class DraggableButtonManager:
    def __init__(self, root, config_file="D:/C++Projrct/Music_player/button_config.json"):
        self.root = root
        self.buttons = {}  # 存储按钮
        self.icons = {}    # 缓存图标
        self.config_file = config_file  # 配置文件路径
        self.config = self.load_button_config()  # 加载配置文件
        self.load_all_icons()  # 预加载所有图标

    def load_icons(self, icon_paths):
        """加载多个图标并缓存"""
        icon_list = []
        for path in icon_paths:
            if os.path.exists(path):
                try:
                    icon = ImageTk.PhotoImage(Image.open(path).resize((50, 50)))
                    icon_list.append(icon)
                except Exception as e:
                    print(f"[ERROR] Failed to load icon '{path}'. Exception: {e}")
            else:
                print(f"[ERROR] Icon file '{path}' does not exist.")
        return icon_list

    def load_all_icons(self):
        """加载配置文件中的所有图标"""
        for name, config in self.config.items():
            icon_paths = config.get("icons", [config.get("icon")])  # 支持单一图标或多图标
            self.icons[name] = self.load_icons(icon_paths)  # 缓存每个按钮的多图标

    def create_button(self, name, default_image_path, command, default_x, default_y, initial_icon_index=0):
        """创建可拖动的按钮，支持初始图标索引，并执行特定的点击操作"""
        config = self.config.get(name, {})
        icon_list = self.icons.get(name) or [ImageTk.PhotoImage(Image.open(default_image_path).resize((50, 50)))]
        
        # 限制初始图标索引范围
        initial_icon_index = min(initial_icon_index, len(icon_list) - 1)
        
        x = config.get("x", default_x)
        y = config.get("y", default_y)

        # 初始化按钮，使用图标列表中的指定图标
        button = tk.Button(self.root, image=icon_list[initial_icon_index], bg="#2C3E50", width=50, height=50)
        button.image_list = icon_list
        button.image_index = initial_icon_index  # 设置初始图标索引
        button.image = icon_list[initial_icon_index]
        button.place(x=x, y=y)

        # 绑定拖动事件
        button.bind("<Button-1>", self.start_drag)
        button.bind("<B1-Motion>", self.drag)

        # 保持左键释放时执行传入的 `command` 操作，仅在未拖动的情况下
        button.bind("<ButtonRelease-1>", lambda e, b=name: self.on_click_release(b, command))

        # 使用右键绑定新图标路径更新功能
        button.bind("<Button-3>", lambda e, b=button, n=name: self.switch_icon(b, n))

        self.buttons[name] = button  # 存储按钮对象
        return button




    def update_button_icon(self, button_name, icon_index):
        """动态更新指定按钮的图标为指定索引的图标"""
        button = self.buttons.get(button_name)
        if not button or icon_index >= len(button.image_list):
            print(f"[ERROR] Invalid icon index {icon_index} for button '{button_name}'.")
            return
        
        # 更新图标索引并配置按钮图标
        button.image_index = icon_index
        button.config(image=button.image_list[icon_index])
        button.image = button.image_list[icon_index]  # 更新图标引用
    def switch_icon(self, button, name):
        """右键点击更新按钮当前状态的图标路径"""
        new_icon_path = filedialog.askopenfilename(filetypes=[("Image Files", "*.png *.jpg *.jpeg")])
        if new_icon_path:
            # 加载并设置新图标
            new_icon = ImageTk.PhotoImage(Image.open(new_icon_path).resize((50, 50)))
            button.image_list[button.image_index] = new_icon
            button.config(image=new_icon)
            button.image = new_icon  # 保存新图标引用

            # 更新配置文件中的图标路径
            if "icons" in self.config[name]:
                self.config[name]["icons"][button.image_index] = new_icon_path
                self.write_config()  # 将新路径写入配置文件

    def start_drag(self, event):
        """开始拖动按钮"""
        widget = event.widget
        self.is_dragging = False  # 初始化为未拖动状态
        widget.startX = event.x
        widget.startY = event.y

    def drag(self, event):
        """拖动按钮并更新位置"""
        widget = event.widget
        dx = abs(event.x - widget.startX)
        dy = abs(event.y - widget.startY)
        
        # 判断是否移动超过阈值（比如5像素），如果是则视为拖动
        if dx > 5 or dy > 5:
            self.is_dragging = True
            x = widget.winfo_x() - widget.startX + event.x
            y = widget.winfo_y() - widget.startY + event.y
            widget.place(x=x, y=y)
            self.save_button_position(widget, x, y)  # 保存位置到配置


    def save_button_position(self, button, x, y):
        """将按钮位置保存到配置文件"""
        for name, btn in self.buttons.items():
            if btn == button:
                if name not in self.config:
                    self.config[name] = {}
                self.config[name]["x"] = x
                self.config[name]["y"] = y
                self.write_config()
                break
    def on_click_release(self, button_name, command):
        """在释放鼠标时处理点击事件，但仅在未拖动的情况下执行传入的操作"""
        if not self.is_dragging:
            # 未拖动才执行传入的操作
            if command:
                command()
        # 重置拖动标记
        self.is_dragging = False



    def save_button_config(self, name, icon_path, x, y):
        """保存按钮图标路径和位置到配置文件"""
        if name not in self.config:
            self.config[name] = {}
        if "icons" not in self.config[name]:
            self.config[name]["icons"] = []
        self.config[name]["icons"][self.buttons[name].image_index] = icon_path  # 更新当前图标路径
        self.config[name]["x"] = x
        self.config[name]["y"] = y
        self.write_config()

    def load_button_config(self):
        """加载配置文件"""
        if os.path.exists(self.config_file):
            with open(self.config_file, "r") as f:
                return json.load(f)
        print(f"[ERROR] Config file '{self.config_file}' not found.")
        return {}

    def write_config(self):
        """将配置写入文件"""
        with open(self.config_file, "w") as f:
            json.dump(self.config, f, indent=4)

    def get_icon(self, icon_name):
        """返回已缓存的图标，如果未缓存则尝试加载"""
        icon_list = self.icons.get(icon_name)
        if not icon_list:
            icon_paths = self.config.get(icon_name, {}).get("icons", [])
            icon_list = self.load_icons(icon_paths)
            self.icons[icon_name] = icon_list
        return icon_list[0] if icon_list else None  # 返回第一个图标作为默认图标
