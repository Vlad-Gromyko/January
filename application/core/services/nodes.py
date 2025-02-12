import tkinter as tk
import customtkinter as ctk

from application.core.events import Service


class NodeCanvas(Service, ctk.CTkFrame):
    def __init__(self, master):
        Service.__init__(self)
        ctk.CTkFrame.__init__(self, master)
        self.name = 'NodeCanvas'

        frame_buttons = ctk.CTkFrame(self, height=25)
        frame_buttons.grid(row=0, column=0, sticky='nsew', pady=5)

        self.start_button = ctk.CTkButton(frame_buttons, text='\u2BC8', width=25, height=25)
        self.start_button.grid(row=0, column=0, padx=5, pady=5)

        ctk.CTkButton(frame_buttons, text='\u2BC0', width=25, height=25).grid(row=0, column=1, padx=5, pady=5)

        ctk.CTkButton(frame_buttons, text='Цветовая схема', width=25, height=25).grid(row=0, column=2, padx=5, pady=5)

        ctk.CTkButton(frame_buttons, text='Очистить Холст', width=25, height=25).grid(row=0, column=3, padx=5, pady=5)

        self.width = 1165
        self.height = 600
        self.canvas = tk.Canvas(master=self, width=self.width, height=self.height, relief='sunken', bg='#222222')
        self.canvas.grid(row=1, column=0, sticky='nsew')


        self.shift_x = 0
        self.shift_y = 0

        self.start_x = 0
        self.start_y = 0

        self.cage_dx = 25
        self.cage_dy = 25

        self.canvas_on_move = False

        self.canvas.bind("<ButtonPress-1>", self.start_move_canvas)
        self.canvas.bind("<Motion>", self.move_canvas)
        self.canvas.bind("<ButtonRelease-1>", self.end_move_canvas)

    def start_move_canvas(self, event):
        print(self.canvas.find_closest(event.x, event.y))
        self.canvas_on_move = True
        self.start_x = event.x
        self.start_y = event.y

    def move_canvas(self, event):
        if self.canvas_on_move:
            dx = event.x - self.start_x
            dy = event.y - self.start_y
            self.shift_x = dx
            self.shift_y = dy

            self.all_redraw()

    def end_move_canvas(self, event):
        self.canvas_on_move = False

    def all_redraw(self):
        pass

