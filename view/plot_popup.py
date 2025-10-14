# -*- coding: utf-8 -*-
"""
Created on Tue Oct 14 11:20:02 2025

@author: mitch
"""

# view/plot_popup.py
import customtkinter as ctk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

class PlotPopup(ctk.CTkToplevel):
    """
    A simple popup window (Toplevel) to display a matplotlib figure.
    """
    def __init__(self, figure, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.title("Analysis Summary Plot")
        self.geometry("800x600") # Set a default size for the popup

        # The FigureCanvasTkAgg is the bridge that embeds the plot
        canvas = FigureCanvasTkAgg(figure, master=self)
        canvas.draw()
        # Place the canvas widget, telling it to fill the entire popup window
        canvas.get_tk_widget().pack(side="top", fill="both", expand=True)