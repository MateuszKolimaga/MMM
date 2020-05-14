import tkinter as tk
from tkinter import ttk
from scipy import signal
import math

class Impuls:
    def __init__(self, impulsFrame, num_a, num_b, settings, radSelected, resolution):
        self.impulsFrame = impulsFrame

        self.a = self.convert(num_a)
        self.b = self.convert(num_b)
        self.settings = self.convert_dict(settings)
        self.radSelected = radSelected
        self.resolution = float(resolution.get())

        self.input_singal = []
        self.output_signal = []
        self.time = [0]
        self.max_ab = max(self.a + self.b)

        self.calculations()

        self.s1 = signal.lti([self.b[3], self.b[2], self.b[1], self.b[0]], [1, self.a[2], self.a[1], self.a[0]])
        self.w, self.wzm, self.faza = signal.bode(self.s1)


    

    def calculations(self):
        # wyznaczanie czasu
        sum = 0
        for _ in range(int(self.settings['duration'])*(int(1.0/self.resolution))-1):
            sum += self.resolution
            self.time.append(sum)

        # wyznaczanie sygnału wejściowego 
        if self.radSelected == 1: # prostokatny
            self.input_singal = [self.settings["amplitude"] * signal.square(2 * math.pi * (1 / self.settings["period"]) * i, 
                                     self.settings["fulfillment"] / 100.) for i in self.time]

        elif self.radSelected == 2: # skok
            self.input_singal = [self.settings["amplitude"] if i >= self.settings["start"] else 0 for i in self.time]

        elif self.radSelected == 3: # sinusoida
            self.input_singal = [self.settings["amplitude"] * math.sin(2 * math.pi * (1 / self.settings["period"]) * i) for i in self.time]

        elif self.radSelected == 4: # trojkatny
            self.input_singal = [2 * self.settings["amplitude"] * signal.square(2 * math.pi * (1 / self.settings["period"]) * i, 0.5) for i in self.time]
            self.input_singal = self.calkowanie(self.input_singal)

        # wyznaczanie sygnału wyjściowego
        self.output_signal = [0 for _ in range(len(self.input_singal))]
        v = [0, 0, 0, 0]
        v[3] = self.input_singal
        for _ in range(math.ceil(self.max_ab / 3.5) *100):
            v[2] = self.calkowanie(v[3])
            v[1] = self.calkowanie(v[2])
            v[0] = self.calkowanie(v[1])
            v = self.wzmocnienie(0, v)
            v[3] = self.odejmowanie(v[2], v[1], v[0])
        i = len(v) - 1
        while i >= 0 :
            if i != 3 : v[i] = self.calkowanie(v[i + 1])
            i -= 1
        v = self.wzmocnienie(1, v)
        self.output_signal = self.dodawanie(self.output_signal, v[3], v[2], v[1], v[0])

                  

    def calkowanie(self, data):
        sum = 0
        integral = [0,0]
        for i in range(1,len(data)-1):
            sum += (data[i] + data[i+1]) * (self.time[i+1] - self.time[i])/ 2.
            integral.append(sum)
        return integral
    
    def odejmowanie(self, v2, v1, v0):
        wynik = [0]
        for i in range(len(self.input_singal)-1) :
            wynik.append(self.input_singal[i] - v2[i] - v1[i] - v0[i])
        return wynik

    def dodawanie(self, wyjscie, v3, v2, v1, v0):
        wynik = []
        for i in range(len(wyjscie)) :
            wynik.append(wyjscie[i] + v3[i] + v2[i] + v1[i] + v0[i])
        return wynik

    def mnozenie(self, p, v):
        wynik = []
        for i in range(len(v)) :
            wynik.append(p * v[i])
        return wynik

    def wzmocnienie(self, wejscie_czy_wyjscie, v):
        if wejscie_czy_wyjscie == 0 :
            for i in range(len(self.a)) :
                v[i] = self.mnozenie(self.a[i], v[i])
        else :
            for i in range(len(self.b)) :
                v[i] = self.mnozenie(self.b[i], v[i])
        return v

    # funkcja zwracajaca czy uklad jest stabilny 
    def is_stable(self):
        if any(self.a) < 0:
             print("Układ jest niestabilny")
             return False
        elif self.a[2] > 0 and self.a[2]*self.a[1] - self.a[0] > 0: 
            print("Układ jest stabilny")
            return True

    # funkcja konwertujaca StringVar to int
    def convert(self, num_x):
        a = []
        for x in num_x:
            if self.is_number(x.get()):
                a.append(float(x.get()))
            else:
                a.append(0)
        return a

    # funkcja konwertujaca StringVar to int w słowniku
    def convert_dict(self, set):
        d = {}
        for k,v in set.items():
            if self.is_number(v.get()):
                d[k] = float(v.get())
            else:
                d[k] = 0
        return d
    
    def wyswietl_wspolczynniki(self):
        print("Oto lista wspolczynnikow a: ")
        print(self.a)
        print("Oto lista wspolczynnikow b: ")
        print(self.b)
        print("Ustawienia")
        print(self.settings['amplitude'])
        print(self.settings['period'])
        print(self.settings['duration'])
        print(self.settings['fulfillment'])
        print(self.settings['start'])

    def is_number(self, s):
        try:
            float(s)
            return True
        except ValueError:
            return False