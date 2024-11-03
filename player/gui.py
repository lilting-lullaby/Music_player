import tkinter as tk
from tkinter import filedialog, Listbox
from .audio_player import AudioPlayer
from .draggable_button import DraggableButtonManager
from PIL import Image, ImageTk
from .wallpaper_manager import WallpaperManager
import os
from .slide import VolumeControl
from .playlist_manager import PlaylistManager

test_music_folder = "./resource/music"

class AudioPlayerGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Modern Music Player")
        self.root.geometry("1100x700")
        self.root.configure(bg="#2C3E50")  # 设置主窗口背景颜色

        # 初始化音频播放器
        self.player = AudioPlayer()

        # 初始化状态变量
        self.is_playing = False  # 用于跟踪播放状态
        self.play_mode = 0  # 0: 循环播放, 1: 单曲循环, 2: 随机播放
        self.after_id = None  # 用于存储 after 调用的 ID
        self.paused_position = 0  # 记录暂停位置
        self.wallpaper_manager = WallpaperManager(self.root,"wallpaper_config.json")
        self.volume_control = VolumeControl(root, initial_volume=50)
        self.button_manager = DraggableButtonManager(self.root, "button_config.json")
        self.playlist = PlaylistManager(self.root)
          # Adjust this path to your test music folder
        self.playlist.load_default_playlist(test_music_folder)

        # 使用按钮管理器创建按钮，不再手动写路径
        self.toggle_button = self.button_manager.create_button("toggle_button", "resource/image/list.png", self.playlist.toggle_playlist, 50, 50)
        self.play_pause_button = self.button_manager.create_button("play_pause_button", "resource/image/play.png", self.toggle_play_pause, 300, 50)
        self.prev_button = self.button_manager.create_button("prev_button", "resource/image/prev.png", self.play_previous, 200, 50)
        self.next_button = self.button_manager.create_button("next_button", "resource/image/next.png", self.play_next, 400, 50)
        self.play_mode_button = self.button_manager.create_button("play_mode_button", "resource/image/loop.png", self.change_play_mode, 500, 50)
        self.change_ui = self.button_manager.create_button("change_ui_button","resource/image/change_ui.png",self.wallpaper_manager.change_play_ground,60,60)
        self.add_background_buttion = self.button_manager.create_button("add_background","resource/image/add.png",self.wallpaper_manager.add_wallpaper,60,60)
        self.delete_button = self.button_manager.create_button("delete_background","resource/image/delete.png",self.wallpaper_manager.show_wallpaper_list,60,60)
        self.volume_button = self.button_manager.create_button("volume_button","resource/image/volume.png",lambda: self.volume_control.toggle_volume_slider(self.volume_button),60,60)

        # 控制按钮区域
        control_frame = tk.Frame(root, bg="#2C3E50")
        control_frame.pack(pady=10)

        # 进度条
        self.progress_var = tk.DoubleVar()
        self.progress_bar = tk.Scale(
            root,
            variable=self.progress_var,
            from_=0,
            to=100,
            orient="horizontal",
            length=300,
            showvalue=0,
            command=self.set_progress,
            bg="#2C3E50",
            fg="white",
            troughcolor="gray",
            sliderlength=15
        )
        self.progress_bar.place(relx=0.5, rely=0.9, anchor="center")

        # 绑定拖动开始和停止事件
        self.progress_bar.bind("<ButtonPress-1>", self.pause_during_drag)
        self.progress_bar.bind("<ButtonRelease-1>", self.resume_after_drag)

    def play_selected_track(self):
        """播放 PlaylistManager 中选中的歌曲"""
        selected_song = self.playlist.get_selected_track()
        print(selected_song)
        if selected_song:
            base_dir = os.path.dirname(os.path.abspath(__file__))
            song_path = os.path.join(base_dir, "..", "resource", "music", selected_song)
            self.player.load(song_path)
            self.player.play()
            print(f"Playing {selected_song}")
        else:
            print("No track selected.")

    def play_previous(self):
        """播放上一首歌曲"""
        self.update_progress_bar
        self.playlist.select_previous_track()
        self.play_selected_track()

    def play_next(self):
        """播放下一首歌曲"""
        self.update_progress_bar
        self.playlist.select_next_track()
        self.play_selected_track()

    def play_random_track(self):
        """随机播放一首歌曲"""
        self.update_progress_bar
        self.playlist.select_random_track()
        self.play_selected_track()

    def toggle_play_pause(self):
        """播放和暂停的切换功能"""
        
        if self.is_playing:
            # 当前正在播放，点击后暂停
            self.is_playing = False
            self.player.pause()
            self.button_manager.update_button_icon("play_pause_button", 0)  # 切换到播放图标
            if self.after_id:
                self.root.after_cancel(self.after_id)  # 停止进度条更新
                self.after_id = None  # 重置 after_id
        else:
            # 当前暂停，点击后开始播放
            print(self.player.paused_position)
            if self.player.paused_position:  # 如果有暂停位置，继续播放
                self.player.resume(self.player.paused_position)
            else:
                self.play_selected_track()  # 播放当前选中的歌曲
            
            self.button_manager.update_button_icon("play_pause_button", 1)  # 切换到暂停图标
            print("重启进度条更新")
            self.is_playing = True
            self.update_progress_bar()  # 恢复进度条更新
    
    def change_play_mode(self):
        """切换播放模式并更新图标"""
        # 循环切换播放模式
        self.play_mode = (self.play_mode + 1) % 3
        
        # 根据播放模式选择图标并更新显示
        if self.play_mode == 0:
            print("播放模式: 循环")
            self.button_manager.update_button_icon("play_mode_button", 0)
            # 在这里添加循环播放的逻辑
        elif self.play_mode == 1:
            print("播放模式: 单曲循环")
            self.button_manager.update_button_icon("play_mode_button", 1)
            # 在这里添加单曲循环的逻辑
        elif self.play_mode == 2:
            print("播放模式: 随机播放")
            self.button_manager.update_button_icon("play_mode_button", 2)
            # 在这里添加随机播放的逻辑
     
    def pause_during_drag(self, event):
        """拖动进度条开始时暂停播放，并禁止进度条自动更新"""
        if self.is_playing:
            self.player.pause()  # 暂停播放
            self.was_playing = True
            self.is_playing = False  # 设置为 False，停止进度条自动更新

            # 取消自动更新进度条的定时任务
            if self.after_id:
                self.root.after_cancel(self.after_id)
                self.after_id = None
        else:
            self.was_playing = False

    def resume_after_drag(self, event):
        """拖动停止时恢复播放，并允许进度条自动更新"""
        # 更新暂停位置为停止拖动时的进度条位置
        self.paused_position = (self.progress_var.get() / 100) * self.player.get_total_length()
        print(f"Updated paused_position to: {self.paused_position} seconds")  # 输出当前位置以便调试
        print(self.was_playing)

        # 只在之前正在播放的情况下恢复播放
        if self.was_playing:
            # print(self.was_playing)
            # print(self.paused_position)
            # position=self.paused_position
            self.player.resume(self.player.paused_position)  # 从新的暂停位置恢复播放
            self.is_playing = True  # 设置为 True，允许进度条自动更新
            self.update_progress_bar()  # 恢复进度条更新
            self.was_playing = False

    def set_progress(self, value):
        """根据用户拖动进度条设置播放进度"""
        if self.player.get_total_length() > 0:
            # 将拖动的位置转换为实际播放时间
            new_pos = (float(value) / 100) * self.player.get_total_length()
            self.player.set_position(new_pos)  # 设置新的播放位置
    
    def update_progress_bar(self):
        """更新进度条，显示当前歌曲进度"""
        # 检查播放状态
        if not self.is_playing:
            return  # 如果暂停或停止，不更新进度条
        
        # 获取当前播放时间和总时长
        current_pos = self.player.get_current_time()
        total_length = self.player.get_total_length()

        if total_length > 0:
            # 更新进度条位置
            self.progress_var.set((current_pos / total_length) * 100)
            
            # 检测是否接近歌曲结束（误差范围：0.5 秒内）
            if abs(total_length - current_pos) < 0.5:
                # 如果歌曲即将结束，根据播放模式进行处理
                self.on_song_end()
                return  # 停止进一步的进度条更新

        # 设置定时任务以继续更新进度条
        self.after_id = self.root.after(500, self.update_progress_bar)

    def on_song_end(self):
        """处理歌曲结束后的操作"""
        # 重置进度条到 0
        self.progress_var.set(0)
        print(self.is_playing)
        if self.play_mode == 0:  # 循环播放模式
            self.play_next()
            self.update_progress_bar()
        elif self.play_mode == 1:  # 单曲循环模式
            self.play_selected_track()  # 重新播放当前歌曲
            self.update_progress_bar()
        elif self.play_mode == 2:  # 随机播放模式
            self.play_random_track()
            self.update_progress_bar()


