import tkinter
from tkinter import ttk
import sv_ttk
import os
from moviepy.editor import VideoFileClip  
from datetime import datetime
from PIL import Image, ImageTk
import tkinter.filedialog
import shutil  
import mysql.connector
from mysql.connector import Error
import random
from wrong_turn_model import detect_turn
import vidtest
from thumbnailgeneration import *

class SQLHandler():
    def __init__(self):      
        try:
            self.connection = mysql.connector.connect(host='localhost',
                                                      database='traffic_watcha',
                                                      user='root',
                                                      password='')
        except Error as e:
            print("Error while connecting to MySQL", e)

class ListVideos(ttk.Frame):
    def __init__(self, parent, thumbnail_callback):
        super().__init__(parent, style="Card.TFrame", padding=15)
        self.columnconfigure(0, weight=1)
        self.connection = SQLHandler().connection
        self.add_widgets()
        self.thumbnail_callback = thumbnail_callback

    def add_widgets(self):

        self.button = ttk.Button(self, text="Load Video", command=self.load_video)
        self.button.pack(fill=tkinter.X, pady=(20, 20))

        self.separator = ttk.Separator(self)
        self.separator.pack()

        self.scrollbar = ttk.Scrollbar(self)
        self.scrollbar.pack(side="right", fill="y")

        self.tree = ttk.Treeview(
            self,
            columns=("Name"),
            height=11,
            selectmode="browse",
            show=("headings",),
            yscrollcommand=self.scrollbar.set,
        )
        self.scrollbar.config(command=self.tree.yview)
        self.tree.pack(expand=True, fill="both")
        self.tree.heading("Name", text="Name")
        self.tree.column("Name", anchor="w", width=100)

        query = "SELECT title, file_path FROM sources"
        cursor = self.connection.cursor()
        cursor.execute(query)
        rows = cursor.fetchall()
        self.clips = {}  # Dictionary to store video titles and thumbnail paths

        for idx, row in enumerate(rows):
            video_name, video_path = row
            self.clips[video_name] = generate_thumbnail_for_video(video_path, "thumbnails")
            self.tree.insert("", "end", iid=idx, values=(video_name,))

        self.tree.bind("<<TreeviewSelect>>", self.on_video_selected)
    def on_video_selected(self, event):
        selected_item = self.tree.selection()[0]
        video_name = self.tree.item(selected_item, "values")[0]
        thumbnail_path = self.clips.get(video_name)
        self.thumbnail_callback(thumbnail_path)

    def add_video(self, video_path):
        video_name = os.path.splitext(os.path.basename(video_path))[0]
        creation_time = datetime.now()
        clip = VideoFileClip(video_path)
        duration = int(clip.duration)
        size = os.path.getsize(video_path) / (1024 * 1024) 
        insert_query = "INSERT INTO sources " \
                           "(title, location, creation_time, clip_length, file_path, size) " \
                           "VALUES (%s, %s, %s, %s, %s, %s)"
        cursor = self.connection.cursor()
        places = ['Kingston','Portmore','St. James', 'St Elizabeth']
        random_index = random.randint(0, len(places) - 1)
        query_items=[video_name,places[random_index],creation_time,duration,video_path,size]
        cursor.execute(insert_query,query_items)
        self.clips[video_name] = generate_thumbnail_for_video(video_path, "thumbnails")
        self.tree.insert("", "end", values=(video_name,))
        self.thumbnail_callback(self.clips[video_name])
        self.connection.commit()
        if self.tree.selection():
            self.tree.selection_set(self.tree.selection()[-1])
        else:
            self.tree.selection_set(self.tree.get_children()[-1])

    def load_video(self):
        file_path = tkinter.filedialog.askopenfilename(filetypes=[("Video Files", "*.mp4;*.avi;*.mkv")])
        if file_path:
            shutil.copy(file_path, "videos")
            new_file_name = os.path.basename(file_path)  # Get the filename
            new_file_path = os.path.abspath(os.path.join("videos", new_file_name))
            self.add_video(new_file_path)
            

class VideoThumbnail(ttk.LabelFrame):
    def __init__(self, parent, callback):
        super().__init__(parent, text="Video Thumbnail", padding=15)
        self.callback = callback
        self.thumbnail_label = ttk.Label(self)
        self.connection = SQLHandler().connection
        self.thumbnail_label.pack(fill="both", expand=True)
        self.add_widgets()

    def add_widgets(self):
        self.runbutton = ttk.Button(self, text="Run", style="Accent.TButton", command=self.runModel)
        self.runbutton.pack(side="right", padx=10, pady=10)


    def runModel(self):
        video = None
        video_files = [f for f in os.listdir(os.getcwd() + "\\" + "videos") if f.endswith((".mp4", ".avi", ".mkv"))]
        for video_file in video_files:
            if os.path.basename(self.video_path) == os.path.splitext(video_file)[0]:
                video = video_file
        if video is not None:
           
           results = detect_turn("videos\\"+video)
           for r in results:
                insert_query = f"INSERT INTO violations " \
                           "(title, type, location, creation_time, file_path) " \
                           "VALUES (%s, %s, %s, %s, %s)"
                cursor = self.connection.cursor()
                cursor.execute(insert_query,r)
                insert_query = f"INSERT INTO temp " \
                            "(title, type, location, creation_time, file_path) " \
                           "VALUES (%s, %s, %s, %s, %s)"
                cursor.execute(insert_query,r)
           self.connection.commit()
           self.callback()


    def update_thumbnail(self, thumbnail_path, max_size=(650, 650)):
        if os.path.exists(thumbnail_path):
            image = Image.open(thumbnail_path)
            # Calculate aspect ratio
            width, height = image.size
            aspect_ratio = width / height
            # Adjust size based on aspect ratio and maximum size
            target_width = min(width, max_size[0])
            target_height = int(target_width / aspect_ratio)
            if target_height > max_size[1]:
                target_height = max_size[1]
                target_width = int(target_height * aspect_ratio)
            # Resize image
            image = image.resize((target_width, target_height))
            photo = ImageTk.PhotoImage(image)
            self.thumbnail_label.configure(image=photo, anchor="center")
            self.thumbnail_label.image = photo
            self.video_path = "videos\\" + os.path.basename(os.path.splitext(thumbnail_path)[0])

class ModelResults(ttk.LabelFrame):
    def __init__(self, parent):
        super().__init__(parent, text="Model Results", padding=15)
        self.connection = SQLHandler().connection



    def update(self):
        self.scrollbar = ttk.Scrollbar(self)
        self.scrollbar.pack(side="right", fill="y")
        self.tree = ttk.Treeview(
            self,
            columns=("Title","Datetime"),
            height=11,
            selectmode="browse",
            show=("headings",),
            yscrollcommand=self.scrollbar.set,
        )
        self.scrollbar.config(command=self.tree.yview)
        
        self.tree.pack(expand=True, fill="both")
        self.tree.heading("Title", text="Title")
        self.tree.heading("Datetime", text="Datetime")

        self.tree.column("Title", anchor="w")
        self.tree.column("Datetime", anchor="w")
        query = "SELECT title, creation_time FROM temp"
        cursor = self.connection.cursor()
        cursor.execute(query)
        rows = cursor.fetchall()
        self.clips=[]
        for idx, row in enumerate(rows):
            title, time = row
            self.clips.append((title, time))
            self.tree.insert("", "end", iid=idx, values=(title,time))
        query = "DELETE FROM temp"
        cursor.execute(query)
        self.connection.commit()
        self.tree.bind("<Double-1>", self.play_video)
        
    def play_video(self, event):
        item = self.tree.selection()[0]
        idx = int(item)
        clip = self.clips[idx][0]
        print(clip)
        vidtest.main(tkinter.Toplevel(self),"violations\\"+clip)




class App(ttk.Frame):
    def __init__(self, parent):
        ttk.Frame.__init__(self, parent)

        for index in range(6):
            self.columnconfigure(index=index, weight=1)
            self.rowconfigure(index=index, weight=1)

        

        ListVideos(self, self.update_thumbnail).grid(row=0, column=0, rowspan=5, padx=10, pady=(10, 10), sticky="nsew")

        self.video_thumbnail_frame = VideoThumbnail(self,self.update_results)
        self.video_thumbnail_frame.grid(row=0, column=1, rowspan=5, columnspan=3, padx=10, pady=(10, 10), sticky="nsew")

        self.results = ModelResults(self)
        self.results.grid(row=0, column=4, rowspan=5, columnspan=2,padx=10, pady=(10, 10), sticky="nsew")

    def update_thumbnail(self, thumbnail_path):
        self.video_thumbnail_frame.update_thumbnail(thumbnail_path)

    def update_results(self):
        self.results.update()

def main(window):
    root = window
    root.title("Wrong Turn Detection Model")
    sv_ttk.set_theme("dark")
    App(root).pack(expand=True, fill="both")

    root.mainloop()


if __name__ == "__main__":
    main()

