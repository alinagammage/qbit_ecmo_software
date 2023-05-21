## ====== Cottrell Lab Pixel Analysis Project Folder Creation Script
# Written by Daniel Kurtz

# Importing libraries
import shutil, os, tkinter.messagebox, numpy as np, random as rand, tkinter.font as tkfont#, xlsxwriter as xl, pandas as pd     #, sys, stat, re # pandas is used to make Threshold Excel File

#import tkinter as tk
from tkinter import filedialog
from tkinter import *
#import tkinter.ttk as ttk
#from tkinter.ttk import *

import win32com.client as win32
import customtkinter as ctk
from datetime import date
from PIL import ImageTk, Image

os. system('cls')

# Misc Variables (Defining them here lets you modify them inside of functions)

# Data Variables
arduino_Input = np.array([0,0,0,0,0,0]) ### Import values from arduino, stick in NP Array as Ints to simplify storage?
arduino_SysP = arduino_Input[0]
arduino_DiasP = arduino_Input[1]
arduino_BloodP = str(arduino_SysP) + "/" + str(arduino_DiasP) # Change Blood P's to string, only 2 that need conversion
arduino_OutT = arduino_Input[2]
arduino_FlowR = arduino_Input[3]
arduino_bO2 = arduino_Input[4]
arduino_bCO2 = arduino_Input[5]

# CTK App Settings
ctk.set_appearance_mode("Dark")  # Modes: "System" (standard), "Dark", "Light"
ctk.set_default_color_theme("dark-blue")  # Themes: "blue" (standard), "green", "dark-blue"

class App(ctk.CTk):

    WIDTH = 1000 # 2:1 Width:Height Aspect Ratio Used
    HEIGHT = 500

    def __init__(self):
        super().__init__()



        self.title("Ultraportable ECMO Data Visualization App")
        self.iconbitmap("Caduceus_icon_gold.ico")
        self.geometry(f"{App.WIDTH}x{App.HEIGHT}")
        # self.minsize(App.WIDTH, App.HEIGHT)

        self.protocol("WM_DELETE_WINDOW", self.on_closing)  # call .on_closing() when app gets closed

        # Creating fonts for use in the window
        fontData = ctk.CTkFont(family="Helvetica", size=12, weight="bold")
        fontTitle = ctk.CTkFont(family="Roboto Medium", size=16)
        fontAuthors = ctk.CTkFont(family="Roboto Medium", size=10)


        # ============ Creating Two Frames ============

        # configure grid layout (1x2) (row x col)
        self.grid_columnconfigure(1, weight=1) # Makes right side of window stretchy
        self.grid_rowconfigure(0, weight=1)

        self.frame_left = ctk.CTkFrame(master=self, width=300, corner_radius=0)
        self.frame_left.grid(row=0, column=0, sticky="nswe", padx=20, pady=20) # Pad and Sticky space out frames
        self.frame_left.grid_propagate(False)

        self.frame_right = ctk.CTkFrame(master=self,width=700)
        self.frame_right.grid(row=0, column=1, sticky="nswe", padx=20, pady=20) # Pad and Sticky space out frames
        self.frame_right.grid_propagate(False)

        # ============ Left Frame ============

        # Configure Grid Layout (15x3)
        self.frame_left.grid_rowconfigure(0, minsize=10)   # empty row with minsize as spacing
        self.frame_left.grid_rowconfigure(2, minsize=10)   # empty row with minsize as spacing
        self.frame_left.grid_rowconfigure(4, minsize=0)   # empty row with minsize as spacing
        self.frame_left.grid_rowconfigure(6, minsize=0)  # empty row with minsize as spacing
        self.frame_left.grid_rowconfigure(8, minsize=0)  # empty row with minsize as spacing
        self.frame_left.grid_rowconfigure(10, minsize=0)  # empty row with minsize as spacing
        self.frame_left.grid_rowconfigure(12, minsize=10)  # empty row with minsize as spacing
        self.frame_left.grid_rowconfigure(14, minsize=10)  # empty row with minsize as spacing
        self.frame_left.grid_columnconfigure(0, minsize=20)  # empty row with minsize as spacing
        self.frame_left.grid_columnconfigure(2, minsize=20)  # empty row with minsize as spacing

        # Title
        self.title_Label = ctk.CTkLabel(master=self.frame_left, text="Ultraportable ECMO DataVis", font=fontTitle)
        self.title_Label.grid(row=1, column=1, pady=10, padx=10)

        # Presentation of Values
        ## Blood P
        self.frame_BloodP = ctk.CTkFrame(master=self.frame_left)
        self.frame_BloodP.grid(row=3, column=1, columnspan=1, rowspan=1, sticky = "nswe")
        self.frame_BloodP.configure(border_width=1, border_color='#969696', # Hex Colour Code, Light Grey
                                    width=250, corner_radius=0)

        self.frame_BloodP.grid_rowconfigure(0, minsize=5)   # empty row with minsize as spacing
        self.sysP_Label = ctk.CTkLabel(master=self.frame_BloodP,
                                       text="Systolic/Diastolic Blood Pressure [mmHg]", font=fontData)
        self.sysP_Label.grid(row=1, column=0, padx=10)
        self.sysP_Data = ctk.CTkLabel(master=self.frame_BloodP, text=arduino_BloodP, font=fontData)
        self.sysP_Data.grid(row=2, column=0, padx=10)
        self.frame_BloodP.grid_rowconfigure(3, minsize=5)   # empty row with minsize as spacing


        ## Outlet Temperature
        self.frame_OutT = ctk.CTkFrame(master=self.frame_left)
        self.frame_OutT.grid(row=5, column=1, columnspan=1, rowspan=1, sticky = "nswe")
        self.frame_OutT.configure(border_width=1, border_color='#969696', # Hex Colour Code, Light Grey
                                    width=250, corner_radius=0)

        self.frame_OutT.grid_rowconfigure(0, minsize=5)   # empty row with minsize as spacing
        self.sysP_Label = ctk.CTkLabel(master=self.frame_OutT,
                                       text="Outlet Blood Temperature [\u2070C]", #Unicode Value for Deg symbol
                                       font=fontData)
        self.sysP_Label.grid(row=1, column=0, padx=10)
        self.sysP_Data = ctk.CTkLabel(master=self.frame_OutT, text=arduino_OutT, font=fontData)
        self.sysP_Data.grid(row=2, column=0, padx=10)
        self.frame_OutT.grid_rowconfigure(3, minsize=5)   # empty row with minsize as spacing


        ## Flow Rate
        self.frame_FlowR = ctk.CTkFrame(master=self.frame_left)
        self.frame_FlowR.grid(row=7, column=1, columnspan=1, rowspan=1, sticky = "nswe")
        self.frame_FlowR.configure(border_width=1, border_color='#969696', # Hex Colour Code, Light Grey
                                    width=250, corner_radius=0)

        self.sysP_Label = ctk.CTkLabel(master=self.frame_FlowR,
                                       text="Blood Flow Rate [L/min]", font=fontData)
        self.frame_FlowR.grid_rowconfigure(1, minsize=5)   # empty row with minsize as spacing
        self.sysP_Label.grid(row=1, column=0, padx=10)
        self.sysP_Data = ctk.CTkLabel(master=self.frame_FlowR, text=arduino_FlowR, font=fontData)
        self.sysP_Data.grid(row=2, column=0, padx=10)
        self.frame_FlowR.grid_rowconfigure(3, minsize=5)   # empty row with minsize as spacing


        ## Blood O2 Saturation
        self.frame_bO2 = ctk.CTkFrame(master=self.frame_left)
        self.frame_bO2.grid(row=9, column=1, columnspan=1, rowspan=1, sticky = "nswe")
        self.frame_bO2.configure(border_width=1, border_color='#969696', # Hex Colour Code, Light Grey
                                    width=250, corner_radius=0)

        self.sysP_Label = ctk.CTkLabel(master=self.frame_bO2,
                                       text="Blood Hb Saturation [%]", font=fontData)
        self.frame_bO2.grid_rowconfigure(1, minsize=5)  # empty row with minsize as spacing
        self.sysP_Label.grid(row=1, column=0, padx=10)
        self.sysP_Data = ctk.CTkLabel(master=self.frame_bO2, text=arduino_bO2, font=fontData)
        self.sysP_Data.grid(row=2, column=0, padx=10)
        self.frame_bO2.grid_rowconfigure(3, minsize=5)  # empty row with minsize as spacing

        ## Blood CO2 Saturation
        self.frame_bCO2 = ctk.CTkFrame(master=self.frame_left)
        self.frame_bCO2.grid(row=11, column=1, columnspan=1, rowspan=1, sticky = "nswe")
        self.frame_bCO2.configure(border_width=1, border_color='#969696', # Hex Colour Code, Light Grey
                                    width=250, corner_radius=0)

        self.sysP_Label = ctk.CTkLabel(master=self.frame_bCO2,
                                       text="Partial Pressure of Blood CO2 [mmHg]", font=fontData)
        self.frame_bCO2.grid_rowconfigure(1, minsize=5)  # empty row with minsize as spacing
        self.sysP_Label.grid(row=1, column=0, padx=10)
        self.sysP_Data = ctk.CTkLabel(master=self.frame_bCO2, text=arduino_bCO2, font=fontData)
        self.sysP_Data.grid(row=2, column=0, padx=10)
        self.frame_bCO2.grid_rowconfigure(3, minsize=5)  # empty row with minsize as spacing


        # Authorship Statement
        self.authors_Label = ctk.CTkLabel(master=self.frame_left,
                                          text="Created by Daniel Kurtz and Alina Gammage for QBiT", font=fontAuthors)
        self.authors_Label.grid(row=13, column=1, pady=20, padx=20,sticky="ew")

        # = Extra switch, left in code in case it's needed
        # self.switch_1 = ctk.CTkSwitch(master=self.frame_left)
        # self.switch_1.grid(row=8, column=0, pady=10, padx=20, sticky="w")


        # ============ Right Frame ============

        # configure grid layout (5x4)
        self.frame_right.grid_columnconfigure(0, weight=1)
        self.frame_right.grid_columnconfigure(1, weight=1)
        self.frame_right.grid_columnconfigure(2, weight=1)
        self.frame_right.grid_columnconfigure(3, weight=1)
        self.frame_right.grid_rowconfigure(0, weight=10)
        self.frame_right.grid_rowconfigure(2, weight=10)
        self.frame_right.grid_rowconfigure(4, weight=1)


        # ============ frame_left_top ============
        self.frameR_left_top = ctk.CTkFrame(master=self.frame_right)
        self.frameR_left_top.grid(row=0, column=0, columnspan=2, rowspan=2, sticky="nsew")
        self.frameR_left_top.configure(border_width=2, border_color='#969696',  # Hex Colour Code, Light Grey
                                  corner_radius=0)

        # configure grid layout (1x1)
        self.frameR_left_top.rowconfigure(0, weight=1)
        self.frameR_left_top.columnconfigure(0, weight=1)
        self.label_R_LT = ctk.CTkLabel(master=self.frameR_left_top, text="Blood Pressures", font=fontTitle)
        self.label_R_LT.grid(column=0, row=0, sticky="nswe", padx=15, pady=15)


        # ============ frame_right_top ============
        self.frameR_right_top = ctk.CTkFrame(master=self.frame_right)
        self.frameR_right_top.grid(row=0, column=2, columnspan=2, rowspan=2, sticky="nswe")
        self.frameR_right_top.configure(border_width=2, border_color='#969696',  # Hex Colour Code, Light Grey
                                       corner_radius=0)

        # configure grid layout (1x1)
        self.frameR_right_top.rowconfigure(0, weight=1)
        self.frameR_right_top.columnconfigure(0, weight=1)
        self.label_R_RT = ctk.CTkLabel(master=self.frameR_right_top, text="Flow Rate", font=fontTitle)
        self.label_R_RT.grid(column=0, row=0, sticky="nswe", padx=15, pady=15)


        # ============ frame_left_bot ============
        self.frameR_left_bot = ctk.CTkFrame(master=self.frame_right)
        self.frameR_left_bot.grid(row=2, column=0, columnspan=2, rowspan=2, sticky="nswe")
        self.frameR_left_bot.configure(border_width=2, border_color='#969696',  # Hex Colour Code, Light Grey
                                        corner_radius=0)

        # configure grid layout (1x1)
        self.frameR_left_bot.rowconfigure(0, weight=1)
        self.frameR_left_bot.columnconfigure(0, weight=1)
        self.label_R_LB = ctk.CTkLabel(master=self.frameR_left_bot, text="Blood [O2]", font=fontTitle)
        self.label_R_LB.grid(column=0, row=0, sticky="nswe", padx=15, pady=15)


        # ============ frame_right_bot ============
        self.frameR_right_bot = ctk.CTkFrame(master=self.frame_right)
        self.frameR_right_bot.grid(row=2, column=2, columnspan=2, rowspan=2, sticky="nswe")
        self.frameR_right_bot.configure(border_width=2, border_color='#969696',  # Hex Colour Code, Light Grey
                                       corner_radius=0)

        # configure grid layout (1x1)
        self.frameR_right_bot.rowconfigure(0, weight=1)
        self.frameR_right_bot.columnconfigure(0, weight=1)
        self.label_R_RB = ctk.CTkLabel(master=self.frameR_right_bot, text="Blood [CO2]", font=fontTitle)
        self.label_R_RB.grid(column=0, row=0, sticky="nswe", padx=15, pady=15)


        # ============ frame_Settings ============
        self.frameSettings = ctk.CTkFrame(master=self.frame_right)
        self.frameSettings.grid(row=4, column=0, columnspan=4, rowspan=1, sticky="nswe")
        self.frameSettings.configure(border_width=2, border_color='#969696',  # Hex Colour Code, Light Grey
                                        corner_radius=0)


## Functions

    # Dark/Light Mode Switch Function
    def change_mode(self):
        global pic_switch, init_Var

        if self.dark_light_switch.get() == 1:
            ctk.set_appearance_mode("dark")
            self.dlMode="Dark"

            # ====== Right frame pic, DARK mode (to fill the blank space)
            if pic_switch == 2: # If it was previously in Light mode
                if selection !=4:
                    self.pic_labelL.forget()
                    pixelImg = Image.open("MicrosoftTeams-image (2).png")
                    scale_w = 800  # / 461
                    scale_h = 300  # / 346
                    pixelImgLrg = pixelImg.resize((scale_w, scale_h), Image.ANTIALIAS)
                    pixelImgLarge = ImageTk.PhotoImage(image=pixelImgLrg)
                    self.pic_labelD = ctk.CTkLabel(self.frame_right, image=pixelImgLarge)
                    self.pic_labelD.image = pixelImgLarge
                    self.pic_labelD.grid(row=7, column=0, columnspan=3, rowspan=4, pady=0, padx=0, sticky="nswe")
                    pic_switch = 1

                else:
                    pixelImg = Image.open("MicrosoftTeams-image (2).png")
                    scale_w = 800  # / 461
                    scale_h = 300  # / 346
                    pixelImgLrg = pixelImg.resize((scale_w, scale_h), Image.ANTIALIAS)
                    pixelImgLarge = ImageTk.PhotoImage(image=pixelImgLrg)
                    self.pic_labelD = ctk.CTkLabel(self.frame_right, image=pixelImgLarge)
                    self.pic_labelD.image = pixelImgLarge
                    self.pic_labelD.grid(row=7, column=0, columnspan=3, rowspan=4, pady=0, padx=0, sticky="nswe")

                init_Var = "Swap"

            elif pic_switch == 0: # When it opens initially
                pixelImg = Image.open("MicrosoftTeams-image (2).png")
                scale_w = 800  # / 461
                scale_h = 300  # / 346
                pixelImgLrg = pixelImg.resize((scale_w, scale_h), Image.ANTIALIAS)
                pixelImgLarge = ImageTk.PhotoImage(image=pixelImgLrg)
                self.pic_labelD = ctk.CTkLabel(self.frame_right, image=pixelImgLarge)
                self.pic_labelD.image = pixelImgLarge
                self.pic_labelD.grid(row=7, column=0, columnspan=3, rowspan=4, pady=0, padx=0, sticky="nswe")
                pic_switch = 1 # ========= Dark mode set to open INITIALLY - "pic_switch = 2" must be set under
                                                    # identical elif for Light Mode if Light Mode is Default
                init_Var = "Start"

        elif self.dark_light_switch.get() == 0:
            ctk.set_appearance_mode("light")
            self.dlMode="Light"

            # ====== Right frame pic, LIGHT mode (to fill the blank space)
            if pic_switch == 1: # If it was previously in Dark mode
                if selection !=4:
                    self.pic_labelD.forget()
                    pixelImg = Image.open("MicrosoftTeams-image.png")
                    scale_w = 800  # / 461
                    scale_h = 300  # / 346
                    pixelImgLrg = pixelImg.resize((scale_w, scale_h), Image.ANTIALIAS)
                    pixelImgLarge = ImageTk.PhotoImage(image=pixelImgLrg)
                    self.pic_labelL = ctk.CTkLabel(self.frame_right, image=pixelImgLarge)
                    self.pic_labelL.image = pixelImgLarge
                    self.pic_labelL.grid(row=7, column=0, columnspan=3, rowspan=4, pady=0, padx=0, sticky="nswe")
                    pic_switch = 2
                init_Var = "Swap"

            elif pic_switch == 0: # When it opens initially - if it was initially Light Mode (Currently Not)
                pixelImg = Image.open("MicrosoftTeams-image.png")
                scale_w = 800  # / 461
                scale_h = 300  # / 346
                pixelImgLrg = pixelImg.resize((scale_w, scale_h), Image.ANTIALIAS)
                pixelImgLarge = ImageTk.PhotoImage(image=pixelImgLrg)
                self.pic_labelL = ctk.CTkLabel(self.frame_right, image=pixelImgLarge)
                self.pic_labelL.image = pixelImgLarge
                self.pic_labelL.grid(row=7, column=0, columnspan=3, rowspan=4, pady=0, padx=0, sticky="nswe")
                init_Var = "Swap"


    def button_event(self): # Extra function to show how buttons work
        print("Button pressed") # ======= Check

    def on_closing(self, event=0):
        self.destroy()

    def start(self):
        self.mainloop()


if __name__ == "__main__":
    app = App()
    app.start()