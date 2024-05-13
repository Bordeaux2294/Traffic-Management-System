import tkinter
from tkinter import ttk
import sv_ttk
import os
from tkinter import messagebox
from moviepy.editor import VideoFileClip  
import datetime
import red_light
import speed_detection
import traffic_density
import wrong_turn
import crash_detection
from database import SQLHandler
import video_player


class PanedDemo(ttk.PanedWindow):
    def __init__(self, parent):
        super().__init__(parent)
        self.connection = SQLHandler().connection
        self.pane_1 = ttk.Frame(self, padding=(0, 0, 0, 10))
        self.pane_2 = ttk.Frame(self, padding=(0, 10, 5, 0))
        self.add(self.pane_1, weight=1)
        self.add(self.pane_2, weight=3)

        self.var = tkinter.IntVar(self, 47)

        self.add_widgets()

    def add_widgets(self):

        button_keys = ["Traffic Density", "Crash Detection", "Red Light Violation", "Speeding Detection", "Wrong Turn Detection"]
        for index, key in enumerate(button_keys):
            ttk.Button(
                self.pane_1,
                text=key,
                command = self.btncmd(index)
            ).grid(row=0, column=index, sticky="ew", padx=5, pady=5)

        self.switch = ttk.Checkbutton(
            self.pane_1, text="Dark theme", style="Switch.TCheckbutton", command=sv_ttk.toggle_theme
        )
        self.switch.grid(row=0, column=6, pady=10, sticky='e')


        self.scrollbar = ttk.Scrollbar(self.pane_2)
        self.scrollbar.pack(side="right", fill="y")


        self.tree = ttk.Treeview(
            self.pane_2,
            columns=("DateTime","Name","Type", "Location"),
            height=11,
            selectmode="browse",
            show=("headings",),
            yscrollcommand=self.scrollbar.set,
        )
        self.scrollbar.config(command=self.tree.yview)

        self.tree.pack(expand=True, fill="both")
        self.tree.heading("DateTime", text="DateTime")
        self.tree.heading("Name", text="Name")
        self.tree.heading("Type", text="Type")
        self.tree.heading("Location", text="Location")

        self.tree.column("DateTime", anchor="w", width=140)
        self.tree.column("Name", anchor="w", width=100)
        self.tree.column("Type", anchor="w", width=100)
        self.tree.column("Location", anchor="w", width=100)

        query = "SELECT title, type, creation_time, location FROM violations"
        cursor = self.connection.cursor()
        cursor.execute(query)
        rows = cursor.fetchall()
        self.clips = []

        for idx, row in enumerate(rows):
            title, type, creation_time, location = row
            self.clips.append((title, creation_time, location))
            self.tree.insert("", "end", iid=idx, values=(creation_time, title,type,location))
        self.tree.bind("<Double-1>", self.play_video)
    def btncmd(self,index):
        match index:
            case 0:
                return self.traffic
            case 1:
                return self.crash
            case 2:
                return self.redlight
            case 3:
                return self.speed
            case 4:
                return self.turn
            case _:
                return self.error

    def traffic(self):
        traffic_density.main(tkinter.Toplevel(self))

    def crash(self):
        crash_detection.main(tkinter.Toplevel(self))

    def redlight(self):
        red_light.main(tkinter.Toplevel(self))

    def speed(self):
        speed_detection.main(tkinter.Toplevel(self))

    def turn(self):
        wrong_turn.main(tkinter.Toplevel(self))

    def error(self):
        print("Error!")


        
    def play_video(self, event):
        item = self.tree.selection()[0]
        idx = int(item)
        clip = self.clips[idx][0]
        print(clip)
        video_player.main(tkinter.Toplevel(self),"violations\\"+clip+".mp4")
        # messagebox.showinfo("Playing Video", "Click OK to play the video.")
        
        # # Create a new window to play the video
        # play_window = tkinter.Toplevel(self.root)
        # player = tkinter.Label(play_window)
        # player.pack()
        
        # # Play the video
        # clip.preview(fps=25, audio=False, viewer=player)


       


class App(ttk.Frame):
    def __init__(self, parent):
        ttk.Frame.__init__(self, parent)

        # Make the app responsive
        for index in range(5):
            self.columnconfigure(index=index, weight=1)
            self.rowconfigure(index=index, weight=1)


        PanedDemo(self).grid(row=0, column=0, rowspan=6, columnspan = 6, padx=10, pady=(10, 0), sticky="nsew")





def main():
    root = tkinter.Tk()
    root.title("Traffic Watcha")
    sv_ttk.set_theme("dark")
    App(root).pack(expand=True, fill="both")

    root.mainloop()

if __name__ == "__main__":
    main()


