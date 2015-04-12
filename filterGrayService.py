#!/usr/bin/env python
# -*- coding: utf-8 -*-
import threading
from ComssServiceDevelopment.connectors.tcp.msg_stream_connector import InputMessageConnector, OutputMessageConnector #import modułów konektora msg_stream_connector
from ComssServiceDevelopment.connectors.tcp.object_connector import InputObjectConnector, OutputObjectConnector #import modułów konektora object_connector
from ComssServiceDevelopment.service import Service, ServiceController #import modułów klasy bazowej Service oraz kontrolera usługi

import cv2 #import modułu biblioteki OpenCV
import numpy as np #import modułu biblioteki Numpy

class Filter1Service(Service): #klasa usługi musi dziedziczyć po ComssServiceDevelopment.service.Service
    def __init__(self):			#"nie"konstruktor, inicjalizator obiektu usługi
        super(Filter1Service, self).__init__() #wywołanie metody inicjalizatora klasy nadrzędnej
        self.settings = {}
        self.service_lock = threading.RLock() #obiekt pozwalający na blokadę wątku

    def declare_outputs(self):	#deklaracja wyjść
        self.declare_output("videoOutput", OutputMessageConnector(self))
        self.declare_output("settingsOutput", OutputObjectConnector(self))

    def declare_inputs(self): #deklaracja wejść
        self.declare_input("videoInput", InputMessageConnector(self))
        self.declare_input("settingsInput", InputObjectConnector(self))

    def watch_settings(self): #metoda obsługująca strumień sterujacy parametrem usługi
        settings_input = self.get_input("settingsInput") #obiekt interfejsu wejściowego
        settings_output = self.get_output("settingsOutput") #obiekt interfejsu wyjściowego
        while self.running(): #główna pętla wątku obsługującego strumień sterujący
            settings = settings_input.read() #odczyt danych z interfejsu wejściowego
            settings_output.send(settings) #przesłanie danych za pomocą interfejsu wyjściowego

    def run(self):	#główna metoda usługi
        threading.Thread(target=self.watch_settings).start() #uruchomienie wątku obsługującego strumień sterujący

        video_input = self.get_input("videoInput")	#obiekt interfejsu wejściowego
        video_output = self.get_output("videoOutput") #obiekt interfejsu wyjściowego1

        while self.running():   #pętla główna usługi
            frame_obj = video_input.read()  #odebranie danych z interfejsu wejściowegos
            frame = np.loads(frame_obj)     #załadowanie ramki do obiektu NumPy

            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY) # zastosowanie filtra

            video_output.send(frame.dumps()) #przesłanie ramki za pomocą interfejsu wyjściowego

if __name__=="__main__":
    sc = ServiceController(Filter1Service, "config/filterGrayService.json") #utworzenie obiektu kontrolera usługi
    sc.start() #uruchomienie usługi