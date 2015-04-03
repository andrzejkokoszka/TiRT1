#!/usr/bin/env python
# -*- coding: utf-8 -*-

import Tkinter as tk #import modułu biblioteki Tkinter -- okienka

class Application(tk.Frame):
    def __init__(self, master=None):
        tk.Frame.__init__(self, master)
        self.grid(sticky=tk.N+tk.S+tk.E+tk.W)

        # Widgety interfejsu graficznego
        self.checkbox_filterGray = None # checkbox filtra szarosci
        self.checkbox_resize = None # checbox do zmiany rozmiaru obrazu
        self.scale_resize = None # slider do zmiany wspolczynnika skalowania obrazu

        # Zmienne do obsługi widgetow
        self.var_checkbox_filterGray = tk.IntVar() # wartość checboxa od filtra szarosci
        self.var_checkbox_resize = tk.IntVar() # wartosć checkboxa do zmiany rozmiaru obrazu
        self.var_scale_resize = tk.DoubleVar() # wartosć slidera do wyboru współczynnika skalowania obrazu

        # Pola dotyczace serwisow
        self.service_controller = None # DevServiceController
        self.connection_video = None
        self.connection_settings = None

        self._createWidgets()

    def _createWidgets(self):

        top = self.winfo_toplevel()
        top.rowconfigure(0, weight=1)
        top.columnconfigure(0, weight=1)

        self.columnconfigure(0,weight=1)
        self.rowconfigure(0, weight=1)

        self.checkbox_filterGray = tk.Checkbutton(self, text="Filter Gray", variable=self.var_checkbox_filterGray)
        self.checkbox_filterGray.grid(column=0,row=0,columnspan=1)#,sticky=tk.N+tk.S+tk.E+tk.W)

        self.checkbox_resize = tk.Checkbutton(self, text="Resize Image",
                                              variable=self.var_checkbox_resize,
                                              command=self.cmd_checkbox_resize)
        self.checkbox_resize.grid(column=0,row=1,columnspan=1)

        # slider do zmiany wspolczynnika skalowania obrazu
        self.scale_resize = tk.Scale(self, from_=0.5, to=1, resolution=0.01, orient=tk.HORIZONTAL, tickinterval=0.1,
                                     length = 200, state=tk.DISABLED, label="Współczynnik skalowania",
                                     variable=self.var_scale_resize)
        self.scale_resize.grid(column=0,row=2,columnspan=1)
        self.var_scale_resize.set(1)

    def cmd_checkbox_resize(self):
        """ Metoda obsługująca checkbox do zmiany rozmiaru obrazu """
        if self.var_checkbox_resize.get():
            self.scale_resize.config(state=tk.NORMAL)
        else:
            self.scale_resize.config(state=tk.DISABLED)
            end_val = self.scale_resize.cget("to") # wartość końca przedziału slidera
            self.var_scale_resize.set(end_val)

if __name__=="__main__":
    app = Application()
    app.master.title('Input settings')
    app.mainloop()
