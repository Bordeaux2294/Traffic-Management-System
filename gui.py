import tkinter as tk
import cv2
from PIL import Image, ImageTk
from traffictracker import density

class VideoPlayerApp:
    def __init__(self, window, video_source):
        self.window = window
        self.window.title("Video Player")

        self.video_source = video_source
        self.vid = cv2.VideoCapture(self.video_source)

        self.canvas = tk.Canvas(window, width=620, height=480)
        self.canvas.pack()

        self.text_label = tk.Label(window, bg="lightblue",font=("Arial", 16, "bold"),text="Calculating...")
        self.text_label.pack(pady=10) 
        self.count = 0

        self.update()

        self.window.mainloop()

    def update(self):
        ret, frame = self.vid.read()
        if ret:
            nframe = cv2.resize(frame, (620, 480))
            self.photo = ImageTk.PhotoImage(image=Image.fromarray(cv2.cvtColor(nframe, cv2.COLOR_BGR2RGB)))
            self.canvas.create_image(0, 0, image=self.photo, anchor=tk.NW)
            self.count += 1
        self.window.after(10, self.update)
        # Update text label
        if self.vid.isOpened() and self.count == 100:
            val = density(frame)
            if val > 1:
               self.text_label.config(bg = "red",text="Traffic Level: %.2f HIGH" % val)
            elif val > 0.5:
               self.text_label.config(bg = "yellow",text="Traffic Level: %.2f Danger" % val) 
            else:
               self.text_label.config(bg = "green", text="Traffic Level: %.2f" % val) 
            self.count = 0

def play_vid():
    app = VideoPlayerApp(tk.Toplevel(root), "traffic.mp4")

if __name__ == "__main__":
    root = tk.Tk()
    btn = tk.Button(root, text ="Traffic Watcher", command = play_vid)
    btn.pack(pady = 10)
    root.mainloop()
    
