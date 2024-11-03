import os
import json
import tkinter as tk
from tkinter import filedialog, Toplevel, Listbox, Button
from PIL import Image, ImageTk

class WallpaperManager:
    def __init__(self, root, config_file="wallpaper_config.json", wallpaper_dir="resource/background"):
        self.root = root
        self.config_file = config_file
        self.wallpaper_dir = wallpaper_dir
        self.wallpaper_list = []
        self.current_index = 0

        # 确保背景标签存在
        if not hasattr(self.root, "background_label"):
            self.root.background_label = tk.Label(self.root)
            self.root.background_label.place(relwidth=1, relheight=1)

        self.load_config()

    def load_config(self):
        """加载配置文件，初始化壁纸列表和当前索引"""
        if os.path.exists(self.config_file):
            with open(self.config_file, "r") as f:
                config = json.load(f)
                self.wallpaper_list = config.get("wallpapers", [])
                self.current_index = config.get("current_index", 0)
        else:
            self.wallpaper_list = []
            self.current_index = 0
            self.save_config()

    def save_config(self):
        """保存当前壁纸列表和索引到配置文件"""
        config = {
            "wallpapers": self.wallpaper_list,
            "current_index": self.current_index
        }
        with open(self.config_file, "w") as f:
            json.dump(config, f, indent=4)

    def add_wallpaper(self, wallpaper_path=None):
        """添加新的壁纸路径到列表并保存"""
        if not wallpaper_path:
            wallpaper_path = filedialog.askopenfilename(
                filetypes=[("Image Files", "*.png *.jpg *.jpeg")],
                initialdir=self.wallpaper_dir
            )
        if wallpaper_path and wallpaper_path not in self.wallpaper_list:
            self.wallpaper_list.append(wallpaper_path)
            self.save_config()
            print(f"Added wallpaper: {wallpaper_path}")
        else:
            print("Wallpaper already exists or invalid path.")

    def remove_wallpaper(self, wallpaper_path):
        """从列表中删除指定的壁纸路径并保存"""
        if wallpaper_path in self.wallpaper_list:
            self.wallpaper_list.remove(wallpaper_path)
            self.current_index = min(self.current_index, len(self.wallpaper_list) - 1)
            self.save_config()
            print(f"Removed wallpaper: {wallpaper_path}")
        else:
            print("Wallpaper not found in list.")

    def show_wallpaper_list(self):
        """显示壁纸列表供选择删除"""
        # 创建新窗口显示壁纸列表
        list_window = Toplevel(self.root)
        list_window.title("选择要删除的壁纸")
        list_window.geometry("300x400")

        # 创建 Listbox 列出所有壁纸
        wallpaper_listbox = Listbox(list_window, selectmode=tk.SINGLE, width=50, height=20)
        wallpaper_listbox.pack(pady=10)

        # 将所有壁纸路径添加到 Listbox
        for wallpaper in self.wallpaper_list:
            wallpaper_listbox.insert(tk.END, wallpaper)

        # 删除按钮，删除选中的壁纸
        delete_button = Button(list_window, text="删除选中壁纸", command=lambda: self.delete_selected_wallpaper(wallpaper_listbox, list_window))
        delete_button.pack(pady=10)

    def delete_selected_wallpaper(self, wallpaper_listbox, list_window):
        """删除 Listbox 中选中的壁纸"""
        selected_index = wallpaper_listbox.curselection()
        if selected_index:
            wallpaper_path = wallpaper_listbox.get(selected_index)
            self.remove_wallpaper(wallpaper_path)
            wallpaper_listbox.delete(selected_index)  # 从列表框中删除
            print(f"Deleted wallpaper: {wallpaper_path}")
            if not self.wallpaper_list:
                list_window.destroy()
        else:
            print("未选择要删除的壁纸")

    def change_play_ground(self):
        """循环切换壁纸，按列表顺序显示"""
        if not self.wallpaper_list:
            print("No wallpapers to display.")
            return

        # 切换到下一个壁纸
        self.current_index = (self.current_index + 1) % len(self.wallpaper_list)
        new_wallpaper = self.wallpaper_list[self.current_index]

        # 显示壁纸
        self.set_wallpaper(new_wallpaper)

        # 保存当前索引
        self.save_config()

    def set_wallpaper(self, wallpaper_path):
        """设置壁纸（实际应用于窗口背景）"""
        image = Image.open(wallpaper_path)
        bg_image = ImageTk.PhotoImage(image.resize((self.root.winfo_width(), self.root.winfo_height())))
        self.root.background_label.config(image=bg_image)
        self.root.background_label.image = bg_image
        print(f"Wallpaper changed to: {wallpaper_path}")
