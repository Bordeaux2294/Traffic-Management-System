from ultralytics import YOLO
from email.mime.text import MIMEText
import smtplib
import numpy as np

class TrafficTracker():
    def __init__(self):
        self.model = YOLO('yolov8n.pt')
        self.dens_list = []
        self.sender = "TekSupport <software@teksupport.com>"
        self.receiver = "National Works Agency <ccs@nwa.gov.jm>"

    def eval(self):
        if np.min(self.dens_list) >= 1:
            msg = f"Traffic at {self.location} is at a critical level"
            self.send(msg)
        elif np.min(self.dens_list) >= 0.5:
            msg = f"Traffic at {self.location} is at a high level"
            self.send(msg)
        self.dens_list = self.dens_list[1:]


    def density(self,frame,location):
        self.location = location
        bounds = ((0,frame.shape[0]),(480,frame.shape[1]))
        y = bounds[0]
        x = bounds[1]
        frame = frame[y[0]:y[1], x[0]:x[1]]
        result = self.model(frame, verbose = False, classes=[2,3,5,7])
        area = ((y[1]-y[0])/200) * ((x[1]-x[0])/200)
        vehicles = len(result[0].boxes.cls)
        dens = vehicles/area
        self.dens_list.append(dens)
        if len(self.dens_list) >= 5:
           self.eval()
        return dens
    
    def send(self,msg):
        
        message = MIMEText(msg)
        message["Subject"] = "Alert!"
        message["From"] = self.sender
        message["To"] = self.receiver

        with smtplib.SMTP("sandbox.smtp.mailtrap.io", 2525) as server:
            server.starttls()
            server.login("e12deaf9906396", "bc33e62508b697")
            server.sendmail(self.sender, self.receiver, message.as_string())
            server.quit()


    

    