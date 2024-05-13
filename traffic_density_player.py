import tkinter as tk
from tkinter import ttk
import cv2
import sv_ttk
import random
from PIL import Image, ImageTk
from datetime import datetime
from traffictracker import TrafficTracker
from database import SQLHandler

class TrafficApp(ttk.Frame):
    def __init__(self, parent, video_source):
        super().__init__(parent, padding=15)
        self.connection = SQLHandler()
        self.track = TrafficTracker()

        self.video_source = video_source
        self.vid = cv2.VideoCapture(self.video_source)

        self.canvas = tk.Canvas(self, width=620, height=480)
        self.canvas.pack()

        self.text_label = ttk.Label(self, background="lightblue",font=("Arial", 16, "bold"),text="Calculating...")
        self.text_label.pack(pady=10) 
        self.count = 0

        self.update()


    def update(self):
        ret, frame = self.vid.read()
        if ret:
            nframe = cv2.resize(frame, (620, 480))
            self.photo = ImageTk.PhotoImage(image=Image.fromarray(cv2.cvtColor(nframe, cv2.COLOR_BGR2RGB)))
            self.canvas.create_image(0, 0, image=self.photo, anchor=tk.NW)
            self.count += 1
        self.after(10, self.update)
        # Update text label
        places = ['Kingston','Portmore','St. James', 'St Elizabeth']
        random_index = random.randint(0, len(places) - 1)
        location = places[random_index]
        intersection = random.randint(0, 10)
        if self.vid.isOpened() and self.count == 100:
            val = self.track.density(frame,location+" " +str(intersection))
            if val > 1:
               self.text_label.config(background = "red",text="Traffic Level: %.2f Critical" % val)
               cls = 'high'
            elif val > 0.5:
               self.text_label.config(background = "yellow",text="Traffic Level: %.2f High" % val) 
               cls = 'danger'
            else:
               self.text_label.config(background = "green", text="Traffic Level: %.2f" % val)
               cls = 'safe'
               vals = [val,cls,location,intersection,datetime.now()]
               self.connection.add_density(vals)
            self.count = 0

def main(window,video):
    root = window
    root.title("Traffic Density Results")
    sv_ttk.set_theme("dark")
    TrafficApp(root, video).pack(expand=True, fill="both")

    root.mainloop()
