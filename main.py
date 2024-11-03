import tkinter as tk

from player.gui import AudioPlayerGUI

if __name__ == "__main__":
    root = tk.Tk()
    app = AudioPlayerGUI(root)
    root.mainloop()
