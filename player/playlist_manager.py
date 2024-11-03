# playlist_manager.py
import tkinter as tk
import os
import random

class PlaylistManager:
    def __init__(self, parent_frame):
        """初始化播放列表管理器"""
        self.frame = tk.Frame(parent_frame, bg="#34495E", bd=2, relief=tk.GROOVE)
        self.playlist = tk.Listbox(self.frame, selectmode=tk.SINGLE, bg="#34495E", fg="white", font=("Helvetica", 12))
        self.playlist.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        self.playlist_visible = False

    def toggle_playlist(self):
        """显示或隐藏播放列表"""
        if self.playlist_visible:
            self.frame.pack_forget()
        else:
            self.frame.pack(pady=10, padx=10, fill=tk.BOTH, expand=True)
        self.playlist_visible = not self.playlist_visible

    def load_default_playlist(self, folder_path):
        """加载文件夹中的所有 MP3 文件到播放列表"""
        self.playlist.delete(0, tk.END)  # 清空当前播放列表
        if os.path.exists(folder_path):
            for file_name in os.listdir(folder_path):
                if file_name.endswith(".mp3"):
                    self.playlist.insert(tk.END, file_name)
        else:
            print(f"Folder {folder_path} not found.")

    def add_track(self, track_name):
        """向播放列表添加新轨道"""
        self.playlist.insert(tk.END, track_name)

    def get_selected_track(self):
        """获取选中的歌曲名称"""
        try:
            selected_index = self.playlist.curselection()[0]
            return self.playlist.get(selected_index)
        except IndexError:
            return None

    def select_next_track(self):
        """选中下一首歌曲"""
        current_index = self.playlist.curselection()
        if current_index:
            next_index = (current_index[0] + 1) % self.playlist.size()
            self.playlist.selection_clear(0, tk.END)
            self.playlist.selection_set(next_index)
            return self.get_selected_track()
        return None

    def select_previous_track(self):
        """选中上一首歌曲"""
        current_index = self.playlist.curselection()
        if current_index:
            prev_index = current_index[0] - 1 if current_index[0] > 0 else self.playlist.size() - 1
            self.playlist.selection_clear(0, tk.END)
            self.playlist.selection_set(prev_index)
            return self.get_selected_track()
        return None

    def select_random_track(self):
        """随机选中一首歌曲"""
        random_index = random.randint(0, self.playlist.size() - 1)
        self.playlist.selection_clear(0, tk.END)
        self.playlist.selection_set(random_index)
        return self.get_selected_track()
