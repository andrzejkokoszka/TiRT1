#!/usr/bin/env python
# -*- coding: utf-8 -*-
import threading
from ComssServiceDevelopment.connectors.tcp.msg_stream_connector import OutputMessageConnector #import modułów konektora msg_stream_connector
from ComssServiceDevelopment.connectors.tcp.object_connector import OutputObjectConnector #import modułów konektora object_connector
from ComssServiceDevelopment.service import Service, ServiceController #import modułów klasy bazowej Service oraz kontrolera usługi
from parameters import ServicesParameters
from inputApp import Application
import os, signal

import cv2 #import modułu biblioteki OpenCV

class InputService(Service): #klasa usługi musi dziedziczyć po ComssServiceDevelopment.service.Service
    def __init__(self):			#"nie"konstruktor, inicjalizator obiektu usługi
        super(InputService, self).__init__() #wywołanie metody inicjalizatora klasy nadrzędnej

        self.service_params = ServicesParameters()
        self.webCam = cv2.VideoCapture(0) # strumien z kamery wideo
        self.service_lock = threading.RLock() #obiekt pozwalający na blokadę wątku

        # pola do określania, które serwisy zostały wybrane (domyślnie wyłączone)
        self.preprocessing_service = 1 # preprocessing service ma byc wykonywany zawsze
        self.resize_service = 0
        self.filter_gray_service = 0

        # parametry dla poszczególnych serwisów
        self.resize_coeff = 1 # wspołczynnik skalowania (resize service)

        self.app = Application()

    def declare_outputs(self):	#deklaracja wyjść
        self.declare_output("videoOutput", OutputMessageConnector(self))
        self.declare_output("settingsOutput", OutputObjectConnector(self))

    def declare_inputs(self): #deklaracja wejść
        pass

    def run_app_gui(self):
        self.app.master.title('Input settings')
        self.app.mainloop()
        os.kill(os.getpid(),signal.SIGTERM)

    def run(self):	#główna metoda usługi
        threading.Thread(target=self.run_app_gui).start() # W oddzielnym wątku uruchamiam aplikację z iterfejsem graficzynym

        settings_output = self.get_output("settingsOutput") # obiekt interfejsu wyjściowego dla ustawień
        video_output = self.get_output("videoOutput") # obiekt interfejsu wyjściowego dla obrazu

        while self.running():   # pętla główna usługi

            with self.service_lock:     #blokada wątku
                # pobieram wartości widgetów z interfejsu graficznego
                resize_service = self.app.var_checkbox_resize.get()
                filter_gray_service = self.app.var_checkbox_filterGray.get()
                resize_coeff = self.app.var_scale_resize.get()

            # Określam, które serwisy trzeba zastosować - dodaje do kolekcji numery ID poszczególnych serwisów, które należy wykonać
            services_applied = set()
            services_applied.add(self.service_params.getServiceValue(self.service_params.PREPROCESSING_SERVICE)) # serwis preprocessingu wykonywany jest zawsze
            if resize_service:
                services_applied.add(self.service_params.getServiceValue(self.service_params.RESIZE_SERVICE))
            if filter_gray_service:
                services_applied.add(self.service_params.getServiceValue(self.service_params.FILTER_GRAY_SERVICE))

            # Tworzę słownik z ustawieniami, który będzie przesłany do serwisu master
            settings = {'servicesApplied': list(services_applied),
                        'resizeCoeff': resize_coeff}

            _, frame = self.webCam.read() # odczyt obrazu z kamery
            frame_dump = frame.dumps() # zrzut ramki wideo do postaci ciągu bajtow

            settings_output.send(settings) # wysłanie ustawień do serwisu master
            video_output.send(frame_dump) # przesłanie ramki video do serwisu master

if __name__=="__main__":
    sc = ServiceController(InputService, "inputService.json") #utworzenie obiektu kontrolera usługi
    sc.start() #uruchomienie usługi