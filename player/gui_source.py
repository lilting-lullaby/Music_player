import tkinter as tk
from tkinter import filedialog, Listbox
from .audio_player import AudioPlayer
from .draggable_button import DraggableButtonManager
from PIL import Image, ImageTk
import os

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

        self.button_manager = DraggableButtonManager(self.root, "button_config.json")



        # 使用 button_manager 加载图标并缓存
        self.play_icon = self.button_manager.get_icon("play_icon")
        self.pause_icon = self.button_manager.get_icon("pause_icon")
        self.next_icon = self.button_manager.get_icon("next_icon")
        self.prev_icon = self.button_manager.get_icon("prev_icon")
        self.loop_icon = self.button_manager.get_icon("loop_icon")
        self.single_loop_icon = self.button_manager.get_icon("single_loop_icon")
        self.shuffle_icon = self.button_manager.get_icon("shuffle_icon")
        self.list_icon = self.button_manager.get_icon("list_icon")
        self.volume_icon = self.button_manager.get_icon("volume_icon")


        # 使用按钮管理器创建按钮，不再手动写路径
        self.toggle_button = self.button_manager.create_button("toggle_button", "resource/image/list.png", self.toggle_playlist, 50, 50)
        self.play_pause_button = self.button_manager.create_button("play_pause_button", "resource/image/play.png", self.toggle_play_pause, 300, 50)
        self.prev_button = self.button_manager.create_button("prev_button", "resource/image/prev.png", self.play_previous, 200, 50)
        self.next_button = self.button_manager.create_button("next_button", "resource/image/next.png", self.play_next, 400, 50)
        self.play_mode_button = self.button_manager.create_button("play_mode_button", "resource/image/loop.png", self.change_play_mode, 500, 50)

        # 标题栏
        title_label = tk.Label(root, text="音乐播放器", font=("Helvetica", 18), bg="#2C3E50", fg="white")
        title_label.pack(pady=10)

        # 播放列表显示区域
        self.playlist_frame = tk.Frame(root, bg="#34495E", bd=2, relief=tk.GROOVE)
        self.playlist = Listbox(self.playlist_frame, selectmode=tk.SINGLE, bg="#34495E", fg="white", font=("Helvetica", 12))
        self.playlist.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # 默认隐藏播放列表框
        self.playlist_visible = False

        # 自动加载资源文件夹中的音乐
        self.load_default_playlist()

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

        # 音量控制滑块
        volume_frame = tk.Frame(root, bg="#2C3E50")
        volume_frame.pack(pady=10)

        volume_label = tk.Label(volume_frame, text="音量", bg="#2C3E50", fg="white", font=("Helvetica", 10))
        volume_label.pack(side=tk.LEFT)

        self.volume_slider = tk.Scale(volume_frame, from_=0, to=1, resolution=0.1, orient="horizontal", command=self.change_volume, bg="#2C3E50", fg="white", highlightthickness=0)
        self.volume_slider.set(0.5)
        self.volume_slider.pack(side=tk.LEFT, padx=10)



    def toggle_playlist(self):
        """显示或隐藏播放列表"""
        if self.playlist_visible:
            # 隐藏播放列表
            self.playlist_frame.pack_forget()
            #self.toggle_button.config(bg="#1ABC9C")  # 设置背景颜色以表示隐藏状态
        else:
            # 显示播放列表
            self.playlist_frame.pack(pady=10, padx=10, fill=tk.BOTH, expand=True)
            #self.toggle_button.config(bg="#E74C3C")  # 设置背景颜色以表示显示状态
        self.playlist_visible = not self.playlist_visible
   
    

    def load_default_playlist(self):
        """自动加载 resource/music 文件夹下的所有 MP3 文件到播放列表"""
        base_dir = os.path.dirname(os.path.abspath(__file__))
        songs_folder = os.path.join(base_dir, "..", "resource", "music")
        
        if os.path.exists(songs_folder):
            for file_name in os.listdir(songs_folder):
                if file_name.endswith(".mp3"):
                    self.playlist.insert(tk.END, file_name)
        else:
            print(f"Folder {songs_folder} not found.")

    def load_track(self):
        """打开文件选择器，加载音频文件"""
        track_path = filedialog.askopenfilename(filetypes=[("Audio Files", "*.mp3 *.wav")])
        if track_path:
            self.player.load(track_path)
            print(f"Loaded {track_path}")
            self.playlist.insert(tk.END, os.path.basename(track_path))

    def play_selected_track(self):
        """播放选中歌曲"""
        try:
            selected_index = self.playlist.curselection()[0]
            selected_song = self.playlist.get(selected_index)
            base_dir = os.path.dirname(os.path.abspath(__file__))
            song_path = os.path.join(base_dir, "..", "resource", "music", selected_song)
            self.player.load(song_path)
            self.player.play()
            print(f"Playing {selected_song}")
        except IndexError:
            print("No track selected.")

    def change_volume(self, volume):
        """调整音量"""
        self.player.set_volume(float(volume))


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
    

       


    def play_previous(self):
        """播放上一首歌曲"""
        self.update_progress_bar
        current_index = self.playlist.curselection()
        if current_index:
            prev_index = current_index[0] - 1 if current_index[0] > 0 else self.playlist.size() - 1
            self.playlist.selection_clear(0, tk.END)
            self.playlist.selection_set(prev_index)
            self.play_selected_track()

    def play_next(self):
        """播放下一首歌曲"""
        self.update_progress_bar
        current_index = self.playlist.curselection()
        if current_index:
            next_index = (current_index[0] + 1) % self.playlist.size()
            self.playlist.selection_clear(0, tk.END)
            self.playlist.selection_set(next_index)
            self.play_selected_track()


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

    def play_random_track(self):
        """随机播放一首歌曲"""
        self.update_progress_bar
        import random
        random_index = random.randint(0, self.playlist.size() - 1)
        self.playlist.selection_clear(0, tk.END)
        self.playlist.selection_set(random_index)
        self.play_selected_track()
        
