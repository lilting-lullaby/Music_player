import vlc
import os
import time


class AudioPlayer:
    def __init__(self):
        self.instance = vlc.Instance()
        self.player = self.instance.media_player_new()
        self.current_track = None  # 当前正在播放的音轨
        self.volume = 0.5  # 默认音量（0.0 到 1.0 之间）
        self.total_length = 0  # 音频总时长
        self.paused_position = 0  # 记录暂停时的位置
        print("AudioPlayer initialized.")

    def load(self, track_path):
        """加载指定路径的音频文件"""
        if os.path.exists(track_path):
            self.current_track = track_path
            media = self.instance.media_new(track_path)
            self.player.set_media(media)
            self.player.play()
            time.sleep(0.1)  # 给 VLC 一些时间来加载媒体
            self.total_length = self.player.get_length() / 1000  # 获取音频总时长，单位为秒
            self.player.stop()
            print(f"Loaded track: {track_path}")
            print(f"Total length of the track: {self.total_length} seconds")
        else:
            print(f"File {track_path} not found.")

    def play(self):
        """播放音频文件"""
        if self.current_track:
            self.player.play()
            if self.paused_position > 0:
                self.player.set_time(int(self.paused_position * 1000))  # 从暂停位置继续播放
                print(f"Playing from paused position: {self.paused_position} seconds")
            else:
                print("Playing from the start")
            self.paused_position = 0  # 重置暂停位置
        else:
            print("No track loaded. Use the load() method to load a track.")

    def pause(self):
        """暂停音频播放"""
        if self.player.is_playing():
            self.paused_position = self.player.get_time() / 1000  # 获取当前播放时间（秒）
            self.player.pause()
            print(f"Paused at: {self.paused_position} seconds")

    def resume(self, position=None):
        """从指定的暂停位置继续播放"""
        if self.current_track:
            if position is not None:
                self.paused_position = position
            print(f"Resuming from position: {self.paused_position} seconds")
            self.play()  # 从 paused_position 播放
        else:
            print("No track loaded. Use the load() method to load a track.")

    def set_position(self, new_pos):
        """设置播放位置（秒）"""
        self.paused_position = new_pos
        self.player.set_time(int(new_pos * 1000))  # 设置播放时间，单位为毫秒
        print(f"Set position to: {new_pos} seconds")

    def stop(self):
        """停止音频播放"""
        self.player.stop()
        self.paused_position = 0
        print("Playback stopped")

    def get_current_time(self):
        """获取当前播放时间（秒）"""
        current_time = self.player.get_time() / 1000  # 返回当前播放时间，单位为秒
        print(f"Current playback time: {current_time} seconds")
        return current_time

    def get_total_length(self):
        """获取音频文件的总时长（秒）"""
        print(f"Total length of the track: {self.total_length} seconds")
        return self.total_length


