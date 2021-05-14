# --------------------------------------------------- Librerías ------------------------------------------------------
import matplotlib
matplotlib.use("TkAgg")
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
import matplotlib.animation as animation
from matplotlib import style
from matplotlib import pyplot as plt
from tkinter import *
import tkinter as tk
import serial
import time
import tkinter.font as font
import serial.tools.list_ports as lpuertos
from numpy import trapz as trapezoide

# -------------------------------------------- Comunicación Serial ---------------------------------------------------
# Búsqueda de puertos
ports = lpuertos.comports()
arport = 'None'
ncon = len(ports)

for p in range(0, ncon):
    puerto = ports[p]
    strpuerto = str(puerto)
    if 'Arduino' in strpuerto:
        p = strpuerto.split(' ')
        arport = p[0]

# Establecimiento de la comunicación serial
ser = serial.Serial(arport, baudrate=9600, timeout=1)
time.sleep(3)

# ----------------------------------- Inicialización de variables ----------------------------------------------------
LARGE_FONT = ("Verdana", 12)
style.use("ggplot")

x = []
y1 = []
y2 = []
y3 = []
global contador
contador = 0

# ---------------------- Función de obtener medidas mediante el puerto serial ----------------------------------------
def ObtVal():

    ser.write(b'A')
    leer = ser.readline().decode().split('\r\n')
    DA = int(leer.pop(0))

    ser.write(b'B')
    leer = ser.readline().decode().split('\r\n')
    DB = int(leer.pop(0))

    ser.write(b'C')
    leer = ser.readline().decode().split('\r\n')
    DC = int(leer.pop(0))

    return DA, DB, DC

# ----------------------------------- Definición de clases para interfaz gráfica ------------------------------------

class Proyecto(tk.Tk):
    def __init__(self, *args, **kwargs):
        tk.Tk.__init__(self, *args, **kwargs)

        tk.Tk.iconbitmap(self, default="./Icono.ico")
        tk.Tk.wm_title(self, "Medidor de consumo de energía")

        container = tk.Frame(self)
        container.pack(side="top", fill="both", expand=True)
        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)
        self.frames = {}

        for F in (Inicio, Grafica):
            frame = F(container, self)
            self.frames[F] = frame
            frame.grid(row=0, column=0, sticky="nsew")

        self.show_frame(Inicio)

    def show_frame(self, cont):
        frame = self.frames[cont]
        frame.tkraise()


class Inicio(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        pf = PhotoImage(file="uscorp.png")

        # ----------------------------------------- LABELS ---------------------------------------------------------
        #label = tk.Label(self, text="MEDIDOR DE CONSUMO DE ENERGÍA ELÉCTRICA", font=LARGE_FONT)
        #label.pack(pady=10)

        label2 = tk.Label(self, image=pf)
        label2.pf = pf
        label2.pack(pady=50)

        # ------------------------------------------- BUTTONS -----------------------------------------------------
        myfont = font.Font(family='Arial')
        button1 = tk.Button(self, text="Entrar", font=myfont, command=lambda: controller.show_frame(Grafica), width=20)
        button1.pack(pady=10)


class Grafica(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)

        self.es1 = IntVar()
        self.es2 = IntVar()
        self.es3 = IntVar()

        self.running = False
        self.ani = None

        # ------------------------------------------- LABELS -----------------------------------------------------

        label = tk.Label(self, text="GRÁFICA DE CONSUMO DE ENERGÍA ELÉCTRICA", font=LARGE_FONT)
        label.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

        # ------------------------------------------- FRAMES -----------------------------------------------------

        f1 = tk.Frame(self, height=500, width=300, borderwidth=2)
        f1.pack(side="left", fill="y")

        f2 = tk.Frame(self, height=500, width=300, borderwidth=2)
        f2.pack(side="right", fill="y")

        f3 = tk.Frame(self, height=200)
        f3.pack(side="bottom", fill="x")

        # ------------------------------------------ CHECKBOX ----------------------------------------------------

        self.ch1 = tk.Checkbutton(f1, text="Sensor 1", font=LARGE_FONT, variable=self.es1)
        self.ch1.grid(row=0, column=0, padx=60, pady=60)

        self.ch2 = tk.Checkbutton(f1, text="Sensor 2", font=LARGE_FONT, variable=self.es2)
        self.ch2.grid(row=1, column=0, padx=60, pady=60)

        self.ch3 = tk.Checkbutton(f1, text="Sensor 3", font=LARGE_FONT, variable=self.es3)
        self.ch3.grid(row=2, column=0, padx=60, pady=60)

        # ---------------------------------------- ENTRIES & LABELS ----------------------------------------------

        label2 = tk.Label(f2, text="Consumo Sensor 1 (kW)", font=LARGE_FONT)
        label2.grid(row=0, column=0, padx=30, pady=20)

        self.e1 = tk.Entry(f2, state="disable")
        self.e1.grid(row=1, column=0, padx=30, pady=20)

        label3 = tk.Label(f2, text="Consumo Sensor 2 (kW)", font=LARGE_FONT)
        label3.grid(row=3, column=0, padx=30, pady=20)

        self.e2 = tk.Entry(f2, state="disable")
        self.e2.grid(row=4, column=0, padx=30, pady=20)

        label4 = tk.Label(f2, text="Consumo Sensor 3 (kW)", font=LARGE_FONT)
        label4.grid(row=6, column=0, padx=30, pady=20)

        self.e3 = tk.Entry(f2, state="disable")
        self.e3.grid(row=7, column=0, padx=30, pady=20)

        label5 = tk.Label(f2, text="Tiempo (s)", font=LARGE_FONT)
        label5.grid(row=9, column=0, padx=30, pady=20)

        self.e4 = tk.Entry(f2, state="disable")
        self.e4.grid(row=10, column=0, padx=30, pady=20)

        # --------------------------------------- BUTTONS --------------------------------------------------------
        myfont = font.Font(family='Arial')

        self.button1 = tk.Button(f3, text="Volver", font=myfont, width=10,
                                 command=lambda: controller.show_frame(Inicio))
        self.button1.grid(row=0, column=0, padx=180, pady=20)

        self.button2 = tk.Button(f3, text="Iniciar", font=myfont, width=10, command=lambda: self.start())
        self.button2.grid(row=0, column=1, padx=180, pady=20)

        # ------------------------------------------ GRÁFICA ----------------------------------------------------

        self.fig = plt.Figure(figsize=(5, 5), dpi=100)
        self.a = self.fig.add_subplot(111)
        self.a.set_ylim(0, 1.5)
        self.a.set_xlabel('Tiempo (s)')
        self.a.set_ylabel('Potencia (kW)')
        self.canvas = FigureCanvasTkAgg(self.fig, master=self)
        self.canvas.draw()
        self.canvas.get_tk_widget().pack(side=tk.BOTTOM, fill=tk.BOTH, expand=True)

        toolbar = NavigationToolbar2Tk(self.canvas, self)
        toolbar.update()
        self.canvas._tkcanvas.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

    # -------------------------------------- Método Botón ----------------------------------------------------------

    def start(self):

        x.clear()
        y1.clear()
        y2.clear()
        y3.clear()

        self.contador = 0

        self.estadoch1=self.es1.get()
        self.estadoch2=self.es2.get()
        self.estadoch3=self.es3.get()

        if self.ani is None:
            # Si la animación no está corriendo entonces graficar
            self.a.cla()
            self.button2.config(text='Detener')

            self.ch1.config(state='disable')
            self.ch2.config(state='disable')
            self.ch3.config(state='disable')

            self.e1.config(state='normal')
            self.e2.config(state='normal')
            self.e3.config(state='normal')
            self.e4.config(state='normal')

            return self.graficar()

        if self.running:
            # Si la animación está corriendo, detener
            self.ani.event_source.stop()
            self.button2.config(text='Iniciar')

            self.ch1.config(state='normal')
            self.ch2.config(state='normal')
            self.ch3.config(state='normal')

            self.e1.config(state='disable')
            self.e2.config(state='disable')
            self.e3.config(state='disable')
            self.e4.config(state='disable')

        else:
            # Si la animación no está corriendo, reinicie
            self.ani.event_source.start()
            self.button2.config(text='Detener')

            self.ch1.config(state='disable')
            self.ch2.config(state='disable')
            self.ch3.config(state='disable')

            self.e1.config(state='normal')
            self.e2.config(state='normal')
            self.e3.config(state='normal')
            self.e4.config(state='normal')

        self.running = not self.running

    # --------------------------------- Función Animate para tomar datos y graficar ---------------------------------

    def graficar(self):

        self.ani = animation.FuncAnimation(self.fig, self.act_grafica, frames=10000, interval=1000)

        self.running = True
        self.button2.config(text='Detener')
        self.ani._start()


    def act_grafica(self, i):
        D1, D2, D3 = ObtVal()

        D1 = round((D1 * 1.2 / 1023), 3)
        D2 = round((D2 * 1.2 / 1023), 3)
        D3 = round((D3 * 1.2 / 1023), 3)

        x.append(self.contador)
        y1.append(D1)
        y2.append(D2)
        y3.append(D3)

        ay1 = trapezoide(y1)
        ay2 = trapezoide(y2)
        ay3 = trapezoide(y3)

        self.a.cla()

        self.a.set_ylim(0, 1.5, auto=False)

        if self.estadoch1 == 1 or self.estadoch2 == 1 or self.estadoch2 == 1:
            self.e4.delete(0, 20)
            self.e4.insert(0, str(self.contador))

        if self.estadoch1 == 1:
            self.e1.delete(0, 20)
            self.e1.insert(0, str(ay1))
            self.e1.delete(6, 20)
            self.a.plot(x, y1, 'r', label="Sensor 1")
            self.a.legend()

        if self.estadoch2 == 1:
            self.e2.delete(0, 20)
            self.e2.insert(0, str(ay2))
            self.e2.delete(6, 20)
            self.a.plot(x, y2, 'g', label="Sensor 2")
            self.a.legend()

        if self.estadoch3 == 1:
            self.e3.delete(0, 20)
            self.e3.insert(0, str(ay3))
            self.e3.delete(6, 20)
            self.a.plot(x, y3, 'b', label="Sensor 3")
            self.a.legend()


        self.a.set_xlabel('Tiempo (s)')
        self.a.set_ylabel('Potencia (kW)')
        self.contador += 1

app = Proyecto()
app.mainloop()