import tkinter as tk
from pynput import mouse

class MousePositionTracker:
    def __init__(self, root):
        self.root = root
        self.label = tk.Label(root, text="坐标: (0, 0)", font=("Helvetica", 16))
        self.label.pack(pady=20)

        # 添加置顶按钮
        self.topmost_button = tk.Button(root, text="置顶窗口", command=self.toggle_topmost, bg="lightgray")
        self.topmost_button.pack(pady=10)

        # Set up the mouse listener
        self.listener = mouse.Listener(on_move=self.on_move)
        self.listener.start()

    def on_move(self, x, y):
        self.label.config(text=f"坐标: ({x}, {y})")

    def toggle_topmost(self):
        is_topmost = self.root.attributes('-topmost')
        self.root.attributes('-topmost', not is_topmost)
        if is_topmost:
            self.topmost_button.config(bg="lightgray")
        else:
            self.topmost_button.config(bg="lightblue")

if __name__ == "__main__":
    root = tk.Tk()
    root.title("Mouse Position Tracker")
    root.geometry("250x150")  # 调整窗口大小以适应按钮

    tracker = MousePositionTracker(root)

    root.mainloop()