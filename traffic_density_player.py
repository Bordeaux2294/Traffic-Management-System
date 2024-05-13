import tkinter as tk
from tkinter import ttk
import cv2
import sv_ttk
import random
from PIL import Image, ImageTk
from datetime import datetime
import mysql.connector
from mysql.connector import Error
from traffictracker import density

class SQLHandler():
    def __init__(self):      
        try:
            self.connection = mysql.connector.connect(host='localhost',
                                                      database='traffic_watcha',
                                                      user='root',
                                                      password='')
        except Error as e:
            print("Error while connecting to MySQL", e)

class TrafficApp(ttk.Frame):
    def __init__(self, parent, video_source):
        super().__init__(parent, padding=15)
        self.connection = SQLHandler().connection

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
        if self.vid.isOpened() and self.count == 100:
            val = density(frame)
            if val > 1:
               self.text_label.config(background = "red",text="Traffic Level: %.2f HIGH" % val)
               cls = 'high'
            elif val > 0.5:
               self.text_label.config(background = "yellow",text="Traffic Level: %.2f Danger" % val) 
               cls = 'danger'
            else:
               self.text_label.config(background = "green", text="Traffic Level: %.2f" % val)
               cls = 'safe'
            insert_query = f"INSERT INTO density " \
                            "(density, classification, location, intersection, creation_time) " \
                           "VALUES (%s, %s, %s, %s, %s)"
            insert_query2 = f"INSERT INTO temp2 " \
                            "(density, classification, location, intersection, creation_time) " \
                           "VALUES (%s, %s, %s, %s, %s)"
            cursor = self.connection.cursor()
            vals = [val,cls,places[random_index],random.randint(0, 10),datetime.now()]
            cursor.execute(insert_query,vals)
            cursor.execute(insert_query2,vals)
            self.connection.commit()
            if val > 1:
               self.text_label.config(background = "red",text="Traffic Level: %.2f HIGH" % val)
            elif val > 0.5:
               self.text_label.config(background = "yellow",text="Traffic Level: %.2f Danger" % val) 
            else:
               self.text_label.config(background = "green", text="Traffic Level: %.2f" % val) 
            self.count = 0

def main(window,video):
    root = window
    root.title("Traffic Density Results")
    sv_ttk.set_theme("dark")
    TrafficApp(root, video).pack(expand=True, fill="both")

    root.mainloop()
