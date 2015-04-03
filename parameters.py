#!/usr/bin/env python
# -*- coding: utf-8 -*-

class ServicesParameters(object):
    """
    Służy do przechowywania informacji o serwisach, jakie podłączone są do serwisu MASTER.
    Dodając nowy serwis należy dopisać, informacje o nim i jego adresach do zmiennych statycznych klasy.
    Kolejność indeksowania serwisów numerami mówi o kolejności, w jakiej poszczególne serwisy będą przetwarzały obraz.
    """
    MASTER_SERVICE = "masterService"
    PREPROCESSING_SERVICE = "preprocessingService"
    RESIZE_SERVICE = "resizeService"
    FILTER_GRAY_SERVICE = "filterGrayService"

    SERVICES_ID = {
        "masterService": 0,
        "preprocessingService": 1,
        "resizeService": 2,
        "filterGrayService": 3
    }

    INPUT_VIDEO_CONNECTOR_NAMES = {
        0: "masterService_videoInput",
        1: "preprocessingService_videoInput",
        2: "resizeService_videoInput",
        3: "filterGrayService_videoInput"
    }

    INPUT_SETTINGS_CONNECTOR_NAMES = {
        0: "masterService_settingsInput",
        1: "preprocessingService_settingsInput",
        2: "resizeService_settingsInput",
        3: "filterGrayService_settingsInput"
    }

    OUTPUT_VIDEO_CONNECTOR_NAMES = {
        0: "masterService_videoOutput",
        1: "preprocessingService_videoOutput",
        2: "resizeService_videoOutput",
        3: "filterGrayService_videoOutput"
    }

    OUTPUT_SETTINGS_CONNECTOR_NAMES = {
        1: "preprocessingService_settingsOutput",
        2: "resizeService_settingsOutput",
        3: "filterGrayService_settingsOutput"
    }

    def getInputVideoConnectorName(self, serviceName):
        return self.INPUT_VIDEO_CONNECTOR_NAMES[self.SERVICES_ID[serviceName]]

    def getInputSettingsConnectorName(self, serviceName):
        return self.INPUT_SETTINGS_CONNECTOR_NAMES[self.SERVICES_ID[serviceName]]

    def getOutputVideoConnectorName(self, serviceName):
        return self.OUTPUT_VIDEO_CONNECTOR_NAMES[self.SERVICES_ID[serviceName]]

    def getOutputSettingsConnectorName(self, serviceName):
        return self.OUTPUT_SETTINGS_CONNECTOR_NAMES[self.SERVICES_ID[serviceName]]

    def getAllServiceNames(self):
        return self.SERVICES_ID.keys()

    def getServiceValue(self, serviceName):
        return self.SERVICES_ID[serviceName]

    def getServiceName(self, value):
        for serviceName, serviceValue in self.SERVICES_ID.iteritems():
            if serviceValue == value:
                return  serviceName
