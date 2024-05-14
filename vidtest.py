from moviepy.editor import VideoFileClip
import tkinter as tk
import sv_ttk
import pygame

class App:
    def __init__(self, master,video):
        self.master = master
        self.video = video
        self.playing=True
        
    def play_video(self):
        
        clip = VideoFileClip(self.video)
        clip.preview()
        while self.playing:
            for event in pygame.event.get():
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:  # Example key: ESC
                        self.playing = False
        pygame.quit()
        #pygame.quit()



def main(window,video):
    root = window
    root.title("Traffic Watcha Footage Replay")
    sv_ttk.set_theme("dark")
    app = App(root, video)
    app.play_video()

    root.mainloop()