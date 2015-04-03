#!/usr/bin/env python
# -*- coding: utf-8 -*-
import threading
from ComssServiceDevelopment.connectors.tcp.msg_stream_connector import InputMessageConnector #import modułów konektora msg_stream_connector
from ComssServiceDevelopment.connectors.tcp.object_connector import InputObjectConnector #import modułów konektora object_connector
from ComssServiceDevelopment.service import Service, ServiceController #import modułów klasy bazowej Service oraz kontrolera usługi
from parameters import ServicesParameters
from outputApp import Application
import os, signal
from PIL import Image, ImageTk

import cv2 #import modułu biblioteki OpenCV
import numpy as np #import modułu biblioteki Numpy

class OutputService(Service): #klasa usługi musi dziedziczyć po ComssServiceDevelopment.service.Service
    def __init__(self):			#"nie"konstruktor, inicjalizator obiektu usługi
        super(OutputService, self).__init__() #wywołanie metody inicjalizatora klasy nadrzędnej
        self.service_lock = threading.RLock() #obiekt pozwalający na blokadę wątku
        self.app = Application()

    def declare_outputs(self):	#deklaracja wyjść
        pass

    def declare_inputs(self): #deklaracja wejść
        self.declare_input("videoInputOrigin", InputMessageConnector(self))
        self.declare_input("videoInputModified", InputMessageConnector(self))

    def run_app_gui(self):
        self.app.master.title('Output service')
        self.app.mainloop()
        os.kill(os.getpid(), signal.SIGTERM)

    def show_frame(self, input_connector, video_frame_label):
        obj = input_connector.read()
        frame = np.loads(obj) # załadownaie ramki do obiektu NumPy
        img = Image.fromarray(frame)
        imgTk = ImageTk.PhotoImage(image=img)
        video_frame_label.imgTk = imgTk
        video_frame_label.configure(image=imgTk)

    def run(self):	#główna metoda usługi
        threading.Thread(target=self.run_app_gui).start() # uruchomienie wątku obsługującego panel GUI

        video_input_origin = self.get_input("videoInputOrigin") # obiekt interfejsu wyjściowego dla obrazu oryginalnego
        video_input_modified = self.get_input("videoInputModified") # obiekt interfejsu wyjściowego dla obrazu zmodyfikowanego


        while self.running(): # pętla główna usługi
            try:
                self.show_frame(video_input_modified, self.app.label_videoModified) # wyświetlenie obrazu przetworzonego
                self.show_frame(video_input_origin, self.app.label_videoOrigin) # wyświetlenie obrazu zmodyfikowanego
            except:
                pass

if __name__=="__main__":
    sc = ServiceController(OutputService, "outputService.json") #utworzenie obiektu kontrolera usługi
    sc.start() #uruchomienie usługi