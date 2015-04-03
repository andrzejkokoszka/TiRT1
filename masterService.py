#!/usr/bin/env python
# -*- coding: utf-8 -*-
import threading
from ComssServiceDevelopment.connectors.tcp.msg_stream_connector import InputMessageConnector, OutputMessageConnector #import modułów konektora msg_stream_connector
from ComssServiceDevelopment.connectors.tcp.object_connector import InputObjectConnector, OutputObjectConnector #import modułów konektora object_connector
from ComssServiceDevelopment.service import Service, ServiceController #import modułów klasy bazowej Service oraz kontrolera usługi
from parameters import ServicesParameters

import numpy as np #import modułu biblioteki Numpy

class MasterService(Service):
    def __init__(self): # "nie"konstruktor, inicjalizator obiektu usługi
        super(MasterService, self).__init__() # wywołanie metody inicjalizatora klasy nadrzędnej
        self.service_lock = threading.RLock() # obiekt pozwalający na blokadę wątku
        self.service_params = ServicesParameters() # obiekt do pobierania nazw serwisów, które podłączone są do serwisu master i ich konektorów

    def declare_outputs(self):	# deklaracja wyjść
        service_names = self.service_params.getAllServiceNames() # pobieram nazwy wszystkich serwisów, jakie będą podłączone do serwisu master (na ich podstawie są pobierane nazy konektorów)
        for service in service_names:
            connector_name = self.service_params.getOutputVideoConnectorName(service) # pobieram nazwę konektora wyjściowego dla obrazu video
            self.declare_output(connector_name, OutputMessageConnector(self)) # deklaracja konektora
            if service != self.service_params.MASTER_SERVICE: # wszystkie serwisy oprócz samego serwisu master mają konektor wyjściowy z ustawieniami
                connector_name = self.service_params.getOutputSettingsConnectorName(service) # pobieram nazwę konektora wyjściowego dla ustawień przetwarzania
                self.declare_output(connector_name, OutputObjectConnector(self)) # deklaracja konektora

    def declare_inputs(self): #deklaracja wejść
        service_names = self.service_params.getAllServiceNames() # pobieram nazwy wszystkich serwisów, jakie będą podłączone do serwisu master (na ich podstawie są pobierane nazy konektorów)
        for service in service_names:
            connector_name = self.service_params.getInputVideoConnectorName(service) # pobieram nazwę konektora wejściowego dla obrazu video
            self.declare_input(connector_name, InputMessageConnector(self)) # deklaracja konektora
            connector_name = self.service_params.getInputSettingsConnectorName(service) # pobieram nazwę konektora wejściowego dla ustawień przetwarzania
            self.declare_input(connector_name, InputObjectConnector(self)) # deklaracja konektora

    def watch_services(self, str_settingsInput, str_videoInput): # metoda obsługująca wejścia i wyjścia poszczególnych serwisów podrzędnych, które podłączone są do mastera
        # Bezpośrednio deklaruje tylko interfejsy wejściowe, bo to jaki będzie inerefejs wyjściowy (czyli jaki serwis podrzędny przetwarzający obraz będzie wykonwany jako kolejny) zależy od przesłanych ustawień. Więc program musi sam wybrać, gdzie dalej przesłać obraz i dalsze ustawienia
        settings_input = self.get_input(str_settingsInput) # obiekt interfejsu wejściowego
        video_input = self.get_input(str_videoInput)

        while self.running(): #główna pętla wątku

            try:
                settings = settings_input.read() #odczyt danych z interfejsu wejściowego
            except:
                # jeśli nie da się odczytać danych to prawdopodobnie połączenie na sockecie zostało przerwane, więc je zamykam. Połączenie zostaje odtworzone przy kolejnej próbie odczytu danych (wynika z implementacji konektorów
                settings_input.close()

            current_services = settings.get('servicesApplied',{}) # lista serwisów, które należy wykorzystać. Zawiera numery ID, które określone są w klasie ServiceParameters, zmiennej SERVICES_ID

            if current_services: # jeśli lista serwisów nie jest pusta, to trzeba przekazac dane do kolejnego serwisu
                service_value = current_services.pop(0) # biorę pierwszy element z listy serwisow - ta usługa będzie aktualnie zastosowana
                settings['servicesApplied'] = current_services # aktualizuję ogólne ustawienia z usuniętym pierwszym elementem

                service_name = self.service_params.getServiceName(service_value) # pobieram nazwę serwisu, jaki ma być teraz wykonany
                output_settings_connector = self.service_params.getOutputSettingsConnectorName(service_name) # pobieram nazwę konektora wyjściowego dla ustawień przetwarzania
                settings_output = self.get_output(output_settings_connector) # pobieram obiekt interfejsu wyjściowego dla ustawień
                try:
                    settings_output.send(settings) # przesłanie danych za pomocą interfejsu wyjściowego
                except:
                    settings_output.close() # zamknięcie socketa - będzie odtworzone w kolejnej próbie (jak wyżej)
            else: # jeśli lista serwisów jest pusta, to znaczy ze wszystkie operacje przetwarzania obrazu zostały wykonane i można przesłac obraz na wyjście, więc aktualnym konektorem wyjściowym będzie konektor mastera
                service_name = self.service_params.MASTER_SERVICE

            try:
                frame_obj = video_input.read()  # odebranie danych z interfejsu wejściowego dla obrazu
            except:
                video_input.close() # zamknięcie socketa - będzie odtworzone w kolejnej próbie (jak wyżej)

            frame = np.loads(frame_obj) # załadowanie ramki do obiektu NumPy
            output_video_connector = self.service_params.getOutputVideoConnectorName(service_name) # pobieram nazwę konektora wyjściowego dla obrazu
            video_output = self.get_output(output_video_connector) # pobieram obiekt interfejsu wyjściowego dla obrazu
            try:
                video_output.send(frame.dumps()) # przesłanie danych za pomocą interfejsu wyjściowego
            except:
                video_output.close() # zamknięcie socketa - będzie odtworzone w kolejnej próbie (jak wyżej)


    def run(self):	# główna metoda usługi
        # Uruchamiam w odzielnych wątkach metody obsługujące wejścia i wyjścia serwisów podrzędnych, które podłączone są do mastera
        for service_name in self.service_params.getAllServiceNames():
            input_settings_connector = self.service_params.getInputSettingsConnectorName(service_name) # pobieram nazwę konektora wejściowego serwisu podrzędnego (wejście ustawień)
            input_video_connector = self.service_params.getInputVideoConnectorName(service_name) # pobieram nazwę konektora wejściowego serwisu podrzędnego (wejście obrazu)
            threading.Thread(target=lambda: self.watch_services(input_settings_connector,input_video_connector)).start() #uruchomienie wątku obsługującego wejścia i wyjścia dla serwisu podrzędnego

        while self.running():
            None

if __name__=="__main__":
    sc = ServiceController(MasterService, "masterService.json") #utworzenie obiektu kontrolera usługi
    sc.start() #uruchomienie usługi