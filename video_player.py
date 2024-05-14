import tkinter as tk
from tkinter import ttk
import cv2
import sv_ttk
from PIL import Image, ImageTk



class TrafficApp(ttk.Frame):
    def __init__(self, parent, video_source):
        super().__init__(parent, padding=15)

        self.video_source = video_source
        self.vid = cv2.VideoCapture(self.video_source)

        self.canvas = tk.Canvas(self, width=800, height=500)
        self.canvas.pack()
        self.count = 0
        self.update()


    def update(self,max_size=(800, 800)):
        ret, frame = self.vid.read()
        if ret:
            height, width, _ = frame.shape
            aspect_ratio = width / height
            # Adjust size based on aspect ratio and maximum size
            target_width = min(width, max_size[0])
            target_height = int(target_width / aspect_ratio)
            if target_height > max_size[1]:
                target_height = max_size[1]
                target_width = int(target_height * aspect_ratio)
            nframe = cv2.resize(frame, (target_width, target_height))
            self.photo = ImageTk.PhotoImage(image=Image.fromarray(cv2.cvtColor(nframe, cv2.COLOR_BGR2RGB)))
            self.canvas.create_image(0, 0, image=self.photo, anchor=tk.NW)
            self.count += 1
        self.after(10, self.update)
        if self.vid.isOpened() and self.count == 100:
            self.count = 0
        

def main(window,video):
    root = window
    root.title("Traffic Watcha Footage Replay")
    sv_ttk.set_theme("dark")
    TrafficApp(root, video).pack(expand=True, fill="both")

    root.mainloop()
