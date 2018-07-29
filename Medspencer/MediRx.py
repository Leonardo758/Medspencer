''' Created on Jul 23, 2018 @author: Ivan '''
#!usr/bin/python

#import modules
try:
    import Tkinter as tk
    from Tkinter import *
    from pathlib2 import Path
except  ImportError:
    import tkinter as tk
    from tkinter import *
    from pathlib import Path

import sys
import time
from time import gmtime, strftime
import os
import sqlite3
import MediDB
# from PIL import Image
from MediDB import *
from Queries import *


TITLE_FONT = ("Verdana", 12, "bold")
LARGE_FONT = ("Arial", 12)
LABEL_FONT = ("Time New Roman", 12, "bold")
ERROR_FONT = ("Verdana", 24, "bold")
BW_SIZE = "5"
BH_SIZE = "2"
W_BOX = "12"
W_BOX_LENGTH = "22"
H_BOX = "1"


fingerprint_index = 6
query = 0

# import smbus
# i2c = smbus.SMBus(1)
I2C_ADDRESS = 0x18
NO_DATA = 0xff
ERR = 0xfe
FPID = NO_DATA
SCAN_FINGERPRINT = 0x01
REGISTER_FINGERPRINT = 0x02
DISPENSE = 0x03
PLAY_ALARM = 0x04

db_name = 'Medespenser.db'
createTable()
createData()


# I2C Functions
def FingerprintReader():
    #print("Reading fingerprint...")
    # FPID = NO_DATA

    I2CWrite(SCAN_FINGERPRINT)

    # Loop if no data ready
    while(FPID == NO_DATA):
        #print("NO DATA")
        FPID = I2CRead()
        time.sleep(1)
    #print("Fingerprint read! " + str(FPID))
    # return an int less than 128 (Registered User)
    # return ERR (Print not found, Access Denied)
    return FPID


def FingerprintAdder():
    #print("Registering fingerprint...")
    FPID = NO_DATA
    fingerprint_index

    I2CWrite(REGISTER_FINGERPRINT, fingerprint_index)
    fingerprint_index = fingerprint_index + 1

    # Loop if no data ready
    while(FPID == NO_DATA):
        #print("NO DATA")
        FPID = I2CRead()
        time.sleep(1)

    #print("Fingerprint registered!")
    # return an int less than 128 (Registered User)
    # return ERR (Print not found, Access Denied)
    return FPID


def Dispense1():
    I2CWrite(DISPENSE, 1)


def Dispense2():
    I2CWrite(DISPENSE, 2)


def Dispense3():
    I2CWrite(DISPENSE, 3)


def I2CRead():
    byte = ERR
    while byte == ERR:
        #print("READING")
        try:
            byte = i2c.read_byte(I2C_ADDRESS)
        except:
            byte = ERR
    return byte


def I2CWrite(cmd, dat=-1):
    # Write a single register
    byte = 0
    while True:
        #print("WRITING")
        try:
            if dat == -1:
                i2c.write_byte(I2C_ADDRESS, cmd)
            else:
                i2c.write_byte_data(I2C_ADDRESS, cmd, dat)
            return
        except:
            byte = 0


def Read_Fingerprint():
    # self.returnfield['text'] = "User scanned: " + str(FingerprintReader())
    FingerprintReader()


def New_Fingerprint():
    # self.returnfield['text'] = "User added: " + str(FingerprintAdder())
    FingerprintAdder()


def run_DB_commit(DB, parameters):
    with sqlite3.connect(db_name) as conn:
        c = conn.cursor()
        c.execute(DB, parameters)
        conn.commit()
        c.close()


def run_DB(DB):
    conn = sqlite3.connect(db_name)
    c = conn.cursor()
    c.execute(DB)


def run_DB_Parameter(DB, parameters):
    conn = sqlite3.connect(db_name)
    c = conn.cursor()
    c.execute(DB, parameters)


def run_DB_Fetchone(DB, parameters):
    conn = sqlite3.connect(db_name)
    c = conn.cursor()
    c.execute(DB, parameters)
    return c.fetchone()


def run_DB_Fetchall(DB, parameters):
    conn = sqlite3.connect(db_name)
    c = conn.cursor()
    c.execute(DB, parameters)
    return c.fetchall()


def comb_funcs(*funcs):
    def combine_funcs(*args, **kwargs):
        for f in funcs:
            f(*args, **kwargs)
    return combine_funcs


class Home(tk.Tk):
    def __init__(self, *args, **kwargs):
        tk.Tk.__init__(self, *args, **kwargs)
        # the container is where we'll stack a bunch of frames
        # on top of each other, then the one we want visible
        # will be raised above the others
        container = tk.Frame(self)

        # Automatic refresh the frame to update the time, date and day
        self.Time = tk.Label(text="", font=LARGE_FONT, bg="gray", fg="white")
        self.Time.pack(padx=10, pady=10, fill=tk.X)
        self.update_clock()

        # Create a frame for multi-windows
        container.pack(side="top", fill="both", expand=True)

        # Within the frame or container will be set up as a grid
        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)

        self.frames = {}

        # print("Home Page")

        for F in (FingerPrintPage, ErrorPage, PatientErrorPage, AdminErrorPage,
                  PatientPage, AdminPage, DoctorPage, SettingWindow,
                  EditPatient, EditAdminPage, EditDoctor,
                  PatientSearch, DoctorSearch,
                  AddPatient, AddDoctor):
            # page_name = F.__name__
            frame = F(container, self)
            # self.frames[F] = frame
            self.frames[F] = frame
            print("For Loop: "+str(F))
            # put all of the pages in the same location
            # the one on the top of the stacking order
            # will be the one that is visible
            frame.grid(row=0, column=0, sticky="nsew")

        self.show_frame("FingerPrintPage")

    def show_frame(self, cont):
        # Show a frame for a given page name
        frame = self.frames[cont]
        WW = frame.winfo_screenwidth()
        WH = frame.winfo_screenheight()
        self.geometry("%dx%d+0+0" % (WW, WH))
        frame.tkraise()

    def update_clock(self):
        now = strftime("%I:%M:%S %p" + "  " + "%B %d,%Y" + "  " + "%A")
        self.Time.configure(text=now)
        self.after(1000, self.update_clock)


class popupWindow(object):
    def __init__(self, parent, controller):
        top = self.top = Toplevel(parent)
        WW = top.winfo_screenwidth()
        WH = top.winfo_screenheight()
        top.geometry("%dx%d+0+0" % (WW, WH))

        title = Label(top, text="Please Wait. \n Page is loading", pady=10)
        title.pack()

        FP = Read_Fingerprint()

        global query

        print("FingerprintPage: "+str(FP))
        print(isinstance(FP, int))

        if FP >= fingerprint_index or FP is None:
            c.execute("SELECT * FROM Person WHERE FingerPrintID=:FingerPrintID", {'FingerPrintID': FP})
            query = c.fetchone()
        else:
            c.execute("SELECT * FROM Person WHERE FingerPrintID=?", (1,))
            query = c.fetchone()

        print("FingerprintPage and query: "+str(query))
        # If FPID equal a Patient or Admin
        if query[1] == 'Patient':
            Text = "Welcome {}".format(query[2])
            Button = tk.Button(self, text=Text, bg="yellow",
                               command=lambda: controller.show_frame("PatientPage"))
        elif query[1] == 'Admin':
            Text = "Welcome {}".format(query[2])
            Button = tk.Button(self, text=Text, bg="red",
                               command=lambda: controller.show_frame("AdminPage"))
        else:
            # If FPID is not a patient, admin or unknown
            Button = tk.Button(self, text="Welcome Unknown User \n Access Denied", bg="yellow",
                               command=lambda: controller.show_frame("ErrorFingerPrintPage"))

        Button.pack()

    def cleanup(self):
        self.top.destroy()


class FingerPrintPage(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        # print("Before creating button")

        FirstText = "Please place your finger \n"
        SecondText = "on fingerprint scanner to start"
        Text = "{}{}".format(FirstText, SecondText)
        Text2 = "Please place your finger on fingerprint scanner to start"
        Start = tk.Button(self, text=Text2, bg="green",
                          width=tk.sys.getsizeof(Text2),
                          font=TITLE_FONT,
                          command=Read_Fingerprint)
        Start.pack(padx=10, pady=10)

#        print("After creating button")

#        path = "C:\Users\Ivan\workspace\MedespenserDisplay\MEDSPENCER.jpg"
#        path = "MEDSPENCER.jpg"
#        try:
#            MediD = Image.open(path)
#            render = PhotoImage(MediD)
#            panel = tk.Label(self, image=render)
#            panel.pack(fill="both", expand="yes")
#        except ImportError:
#            img = PhotoImage(file=path)
#            canvas = tk.Canvas(self, width=300, height=300)
#            canvas.pack()
#            canvas.create_image(20, 20, anchor=NW, image=img)

    def DefaultPage(self):
        self.w = popupWindow(self.parent)
        self.b["state"] = "disabled"
        self.wait_window(self.w.top)
        self.b["state"] = "normal"


class ErrorPage(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)

        FirstText = "Error on scanning \n"
        SecondText = "Please Re-scan Your Thumb"
        Text = "{}{}".format(FirstText, SecondText)
        label = tk.Button(self,
                          text=Text,
                          width=tk.sys.getsizeof(Text),
                          font=TITLE_FONT,
                          command=lambda: controller.show_frame(FingerPrintPage))
        label.pack(padx=10, pady=10)


class PatientErrorPage(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)

        title1 = "Sorry so this Error."
        title2 = "\n"
        title3 = "This page is under construction"
        label = tk.Label(self, text="{0} {1} {2}".format(title1, title2, title3)
                         , font=TITLE_FONT)
        label.pack(padx=10, pady=10)

        buttonQuit = tk.Button(self, width=BW_SIZE, height=BH_SIZE,
                               text="EXIT", bg="orange", fg="blue",
                               command=lambda: controller.show_frame(PatientPage))
        buttonQuit.pack(padx=10, pady=10)


class AdminErrorPage(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)

        title1 = "Sorry so this Error."
        title2 = "\n"
        title3 = "This page is under construction"
        label = tk.Label(self, text="{0}{1}{2}".format(title1, title2, title3)
                         , font=TITLE_FONT)
        label.pack(padx=10, pady=10)

        buttonQuit = tk.Button(self, width=BW_SIZE, height=BH_SIZE,
                               text="EXIT", bg="orange", fg="blue",
                               command=lambda: controller.show_frame(AdminPage))
        buttonQuit.pack(padx=10, pady=10)


class PatientPage(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        # self.title("Patient Page")
        WW = self.winfo_screenwidth()
        WH = self.winfo_screenheight()
        SW = round(WW/3)
        MSW = round(WW/3)+100

        # create the center widgets
        top_frame = Frame(self, width=SW, height=WH, padx=3)
        ctr_left = Frame(self, width=SW, padx=3, pady=3)
        ctr_mid = Frame(self, width=MSW, padx=3, pady=3)
        ctr_right = Frame(self, width=SW, padx=3)

        top_frame.grid(row=0, columnspan=3, sticky="ew")
        ctr_left.grid(row=1, column=0, sticky="ns")
        ctr_mid.grid(row=1, column=1, sticky="nsew")
        ctr_right.grid(row=1, column=2, sticky="ns")

        pTFirstNameLabel = tk.Label(ctr_left, text="First Name", font=LABEL_FONT)
        pTLastNameLabel = tk.Label(ctr_left, text="Last Name", font=LABEL_FONT)
        pTDOBLabel = tk.Label(ctr_left, text="Date of Birth", font=LABEL_FONT)
        pTDoctorLabel = tk.Label(ctr_left, text="Doctor", font=LABEL_FONT)
        pTAddressLabel = tk.Label(ctr_left, text="Address", font=LABEL_FONT)
        pTZipLabel = tk.Label(ctr_left, text="ZipCode", font=LABEL_FONT)
        pTPhoneLabel = tk.Label(ctr_left, text="Phone Number", font=LABEL_FONT)
        pTEmailLabel = tk.Label(ctr_left, text="Email", font=LABEL_FONT)

        pTFirstNameLabel.grid(row=0, padx=3, pady=3)
        pTLastNameLabel.grid(row=1, padx=3, pady=3)
        pTDOBLabel.grid(row=2, padx=3, pady=3)
        pTDoctorLabel.grid(row=3, padx=3, pady=3)
        pTAddressLabel.grid(row=4, padx=3, pady=3)
        pTZipLabel.grid(row=5, padx=3, pady=3)
        pTPhoneLabel.grid(row=6, padx=3, pady=3)
        pTEmailLabel.grid(row=7, padx=3, pady=3)

        print("Patient Page query Value: "+str(query))
        FP = query

        # print(FP)
        # c.execute("SELECT * FROM Person WHERE FingerPrintID=:FingerPrintID and PersonType=:PersonType", {'FingerPrintID': FP, 'PersonType': 'Patient'})
        c.execute("SELECT * FROM Person WHERE FingerPrintID=:FingerPrintID", {'FingerPrintID': FP})
        PersonInDB = c.fetchone()

        c.execute("SELECT * FROM Patient WHERE FingerPrintID=:FingerPrintID", {'FingerPrintID': FP})
        PatientInDB = c.fetchone()

        PTFIRSTNAME = PersonInDB[2]
        PTLASTNAME = PersonInDB[3]
        PTPHONE = PersonInDB[4]
        PTEMAIL = PersonInDB[5]

        PTDOCTOR = PatientInDB[2]
        product = PatientInDB[3]
        PTDOB = PatientInDB[4]
        PTADDRESS = PatientInDB[5]
        PTZIP = PatientInDB[6]

        c.execute("SELECT * FROM Doctor WHERE FingerPrintID=:FingerPrintID", {'FingerPrintID': PTDOCTOR})
        DoctorSp = c.fetchone()

        c.execute("SELECT * FROM Person WHERE FingerPrintID=:FingerPrintID", {'FingerPrintID': PTDOCTOR})
        DRInfo = c.fetchone()

        print(DRInfo)

        PTDOCTOR2 = "{0} {1}, \n {2}".format(DRInfo[2], DRInfo[3], DoctorSp[2])

        pTFirstName = tk.Label(ctr_mid, text=PTFIRSTNAME, font=LARGE_FONT)
        pTLastName = tk.Label(ctr_mid, text=PTLASTNAME, font=LARGE_FONT)
        pTDOB = tk.Label(ctr_mid, text=PTDOB, font=LARGE_FONT)
        pTDoctor = tk.Label(ctr_mid, text=PTDOCTOR2, font=LARGE_FONT)
        pTAddress = tk.Label(ctr_mid, text=PTADDRESS, font=LARGE_FONT)
        pTZip = tk.Label(ctr_mid, text=PTZIP, font=LARGE_FONT)
        pTPhone = tk.Label(ctr_mid, text=PTPHONE, font=LARGE_FONT)
        pTEmail = tk.Label(ctr_mid, text=PTEMAIL, font=LARGE_FONT)

        pTFirstName.grid(row=0, padx=3, pady=3)
        pTLastName.grid(row=1, padx=3, pady=3)
        pTDOB.grid(row=2, padx=3, pady=3)
        pTDoctor.grid(row=3, padx=3, pady=3)
        pTAddress.grid(row=4, padx=3, pady=3)
        pTZip.grid(row=5, padx=3, pady=3)
        pTPhone.grid(row=6, padx=3, pady=3)
        pTEmail.grid(row=7, padx=3, pady=3)

        buttonQuit = tk.Button(top_frame, text="QUIT", font=LABEL_FONT,
                               width=BW_SIZE, height=BH_SIZE,
                               bg="orange", fg="blue",
                               command=lambda: controller.show_frame("FingerPrintPage"))
        buttonQuit.pack(side=LEFT, padx=3, pady=3)

        sql_Product = "SELECT * FROM Product WHERE ProductID=:ProductID"
        par_Product = {'ProductID': product}
        # c.execute("SELECT * FROM Product WHERE ProductID=:ProductID", {'ProductID': product})
        # foundProduct = c.fetchone()
        foundProduct = run_DB_Fetchone(sql_Product, par_Product)

        scrollbar = Scrollbar(ctr_right, width=20)
        scrollbar.pack(side=RIGHT, fill=BOTH)
        listbox = Listbox(ctr_right)
        # attach listbox to scrollbar
        listbox.config(yscrollcommand=scrollbar.set)
        scrollbar.config(command=listbox.yview)

        # NCSUBSTANCE1 = "{0}\n{1}".format(foundProduct[2], foundProduct[3])
        NCSUBSTANCE1 = "Skittles \n Green"
        NCB1 = tk.Button(ctr_right, text=NCSUBSTANCE1, font=LABEL_FONT,
                         width=BW_SIZE, height=BH_SIZE, bg="green",
                         fg="white", command=Dispense1) # ServoSignal(foundProduct[1]))

        # CSUBSTANCE1 = "{0}\n{1}".format(foundProduct[2], foundProduct[3])
        CSUBSTANCE1 = "Skittles \n Orange"
        CB1 = tk.Button(ctr_right, text=CSUBSTANCE1, font=LABEL_FONT,
                        width=BW_SIZE, height=BH_SIZE, bg="orange",
                        fg="white", command=lambda: controller.show_frame(Dispense1)) #ServoSignal(foundProduct[1]))

#        if foundProduct[5] == "NC":
#            NCB1.pack(padx=10, pady=10)
#            listbox.insert(tk.END, NCB1)
#        else:
#            CB1.pack(padx=10, pady=10)
#            listbox.insert(0, CB1)

        NCB1.pack()
        CB1.pack()


class DoctorPage(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        WWidth = parent.winfo_screenwidth()
        WHeight = parent.winfo_screenheight()

        # create the center widgets
        top_frame = Frame(self, width=WWidth, height=WHeight/3, padx=3, pady=3)
        ctr_left = Frame(self, width=WWidth/3, padx=3, pady=3)
        ctr_mid = Frame(self, width=WWidth/3, padx=3, pady=3)
        ctr_right = Frame(self, width=WWidth/3, padx=3, pady=3)

        top_frame.grid(row=0, columnspan=3, sticky="ew")
        ctr_left.grid(row=1, column=0, sticky="ns")
        ctr_mid.grid(row=1, column=1, sticky="nsew")
        ctr_right.grid(row=1, column=2, sticky="ns")

        DrFirstNameLabel = tk.Label(ctr_left, text="First Name", font=LABEL_FONT)
        DrLastNameLabel = tk.Label(ctr_left, text="Last Name", font=LABEL_FONT)
        DrSpecialtyLabel = tk.Label(ctr_left, text="Specialty", font=LABEL_FONT)
        DrPhoneLabel = tk.Label(ctr_left, text="Phone Number", font=LABEL_FONT)
        DrEmailLabel = tk.Label(ctr_left, text="Email", font=LABEL_FONT)

        DrFirstNameLabel.grid(row=0, padx=3, pady=3)
        DrLastNameLabel.grid(row=1, padx=3, pady=3)
        DrSpecialtyLabel.grid(row=2, padx=3, pady=3)
        DrPhoneLabel.grid(row=3, padx=3, pady=3)
        DrEmailLabel.grid(row=4, padx=3, pady=3)

        FP = query

        c.execute("SELECT * FROM Person WHERE FingerPrintID=:FingerPrintID", {'FingerPrintID': FP})
        PersonInDB = c.fetchone()

        c.execute("SELECT * FROM Doctor WHERE FingerPrintID=:FingerPrintID", {'FingerPrintID': FP})
        DoctorInDB = c.fetchone()

        print(PersonInDB)
        print(DoctorInDB)

        DRFIRSTNAME = PersonInDB[2]
        DRLASTNAME = PersonInDB[3]
        DRPHONE = PersonInDB[4]
        DREMAIL = PersonInDB[5]

        DRSPECIALTY = DoctorInDB[2]

        DrFirstName = tk.Label(ctr_mid, text=DRFIRSTNAME, font=LABEL_FONT)
        DrLastName = tk.Label(ctr_mid, text=DRLASTNAME, font=LABEL_FONT)
        DrSpecialty = tk.Label(ctr_mid, text=DRSPECIALTY, font=LABEL_FONT)
        DrPhone = tk.Label(ctr_mid, text=DRPHONE, font=LABEL_FONT)
        DrEmail = tk.Label(ctr_mid, text=DREMAIL, font=LABEL_FONT)

        DrFirstName.grid(row=0, padx=3, pady=3)
        DrLastName.grid(row=1, padx=3, pady=3)
        DrSpecialty.grid(row=2, padx=3, pady=3)
        DrPhone.grid(row=3, padx=3, pady=3)
        DrEmail.grid(row=4, padx=3, pady=3)

        buttonEdit = tk.Button(top_frame, text="EDIT", font=LABEL_FONT,
                               width=BW_SIZE, height=BH_SIZE, bg="orange",
                               fg="blue", command=lambda: controller.show_frame(ErrorPage))
        buttonQuit = tk.Button(top_frame, text="QUIT", font=LABEL_FONT,
                               width=BW_SIZE, height=BH_SIZE, bg="orange",
                               fg="blue", command=lambda: controller.show_frame(FingerPrintPage))

        buttonEdit.pack(side=RIGHT, padx=3, pady=3)
        buttonQuit.pack(side=LEFT, padx=3, pady=3)


class AdminPage(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.controller = controller
        WWidth = parent.winfo_screenwidth()
        WHeight = parent.winfo_screenheight()

        # create the center widgets
        top_frame = Frame(self, width=WWidth, height=WHeight/3, padx=3, pady=3)
        ctr_left = Frame(self, width=WWidth/3, padx=3, pady=3)
        ctr_mid = Frame(self, width=WWidth/3, padx=3, pady=3)
        ctr_right = Frame(self, width=WWidth/3, padx=3, pady=3)

        top_frame.grid(row=0, columnspan=3, sticky="ew")
        ctr_left.grid(row=1, column=0, sticky="ns")
        ctr_mid.grid(row=1, column=1, sticky="nsew")
        ctr_right.grid(row=1, column=2, sticky="ns")

        aDFirstNameLabel = tk.Label(ctr_left, text="First Name", justify=LEFT, font=LABEL_FONT)
        aDLastNameLabel = tk.Label(ctr_left, text="Last Name", justify=LEFT, font=LABEL_FONT)
        aDPhoneLabel = tk.Label(ctr_left, text="Phone Number", justify=LEFT, font=LABEL_FONT)
        aDRelationLabel = tk.Label(ctr_left, text="Relationship", justify=LEFT, font=LABEL_FONT)
        aDEmailLabel = tk.Label(ctr_left, text="Email", justify=LEFT, font=LABEL_FONT)

        aDFirstNameLabel.pack(padx=3, pady=3)
        aDLastNameLabel.pack(padx=3, pady=3)
        aDRelationLabel.pack(padx=3, pady=3)
        aDPhoneLabel.pack(padx=3, pady=3)
        aDEmailLabel.pack(padx=3, pady=3)

        if query is None:
            FP = 1
        else:
            FP = query

        # c.execute("SELECT * FROM Person WHERE FingerPrintID=:FingerPrintID and PersonType=:PersonType", {'FingerPrintID': FP, 'PersonType': 'Admin'})
        c.execute("SELECT * FROM Person WHERE FingerPrintID=?", (FP,))
        PersonInDB = c.fetchone()

        # c.execute("SELECT * FROM Admin WHERE FingerPrintID=:FingerPrintID and PersonType=:PersonType", {'FingerPrintID': FP, 'PersonType': 'Admin'})
        c.execute("SELECT * FROM Admin WHERE FingerPrintID=?", (FP,))
        AdminInDB = c.fetchone()

        ADFIRSTNAME = PersonInDB[1]
        ADLASTNAME = PersonInDB[2]
        ADPHONE = PersonInDB[3]
        ADEMAIL = PersonInDB[4]

        ADRELATIONSHIP = AdminInDB[2]

        aDFirstName = tk.Label(ctr_mid, text=ADFIRSTNAME, font=LARGE_FONT)
        aDLastName = tk.Label(ctr_mid, text=ADLASTNAME, font=LARGE_FONT)
        aDRelation = tk.Label(ctr_mid, text=ADRELATIONSHIP, font=LARGE_FONT)
        aDPhone = tk.Label(ctr_mid, text=ADPHONE, font=LARGE_FONT)
        aDEmail = tk.Label(ctr_mid, text=ADEMAIL, font=LARGE_FONT)

        aDFirstName.pack(padx=3, pady=3)
        aDLastName.pack(padx=3, pady=3)
        aDRelation.pack(padx=3, pady=3)
        aDPhone.pack(padx=3, pady=3)
        aDEmail.pack(padx=3, pady=3)

        # self.update()

        buttonEdit = tk.Button(top_frame, text="EDIT", font=LABEL_FONT,
                               width=BW_SIZE, height=BH_SIZE, bg="orange",
                               fg="blue", command=lambda: controller.show_frame(EditAdminPage))
        buttonQuit = tk.Button(top_frame, text="EXIT", font=LABEL_FONT,
                               width=BW_SIZE, height=BH_SIZE, bg="orange",
                               fg="blue", command=lambda: controller.show_frame(FingerPrintPage))

        buttonEdit.pack(side=RIGHT, padx=3, pady=3)
        buttonQuit.pack(side=LEFT, padx=3, pady=3)

        patientWindow = tk.Button(ctr_right, text="Patient Search",
                                  font=LABEL_FONT, width=BW_SIZE, height=BH_SIZE,
                                  bg="blue", fg="white", command=lambda: controller.show_frame(PatientSearch))
        doctorWindow = tk.Button(ctr_right, text="Doctor Search",
                                 font=LABEL_FONT, width=BW_SIZE, height=BH_SIZE,
                                 bg="green", fg="white", command=lambda: controller.show_frame(DoctorSearch))
        settingWindow = tk.Button(ctr_right, text="Setting",
                                  font=LABEL_FONT, width=BW_SIZE, height=BH_SIZE,
                                  bg="red", fg="black", command=lambda: controller.show_frame(SettingWindow))

        patientWindow.pack(padx=3, pady=3)
        doctorWindow.pack(padx=3, pady=3)
        settingWindow.pack(padx=3, pady=3)


class PatientSearch(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        # WW = Window Width and WH = Window Height
        WW = parent.winfo_screenwidth()
        WH = parent.winfo_screenheight()

        # create the center widgets
        top_frame = Frame(self, width=WW, height=WH, padx=3, pady=3)
        ctr_left = Frame(self, width=WW, height=WH, padx=3, pady=3)
        ctr_right = Frame(self, width=WW, height=WH, padx=3, pady=3)

        top_frame.grid(row=0, columnspan=2, sticky="ew")
        ctr_left.grid(row=1, column=1, sticky="ns")
        ctr_right.grid(row=1, column=1, sticky="ns")

        label = tk.Label(top_frame, text="Search Patient", font=TITLE_FONT)
        label.pack(padx=10, pady=10)

        scrollbar = Scrollbar(ctr_right, width=60)
        scrollbar.grid(row=0, column=1, sticky=N+S)

        # create the listbox (note that size is in characters)
        listbox = Listbox(ctr_right, width=60, height=10)
        listbox.grid(row=0, column=0)

        # create a vertical scrollbar to the right of the listbox
        listbox.config(yscrollcommand=scrollbar.set)
        scrollbar.config(command=listbox.yview, orient=VERTICAL)

        # WRITE a code to search similar to IMS Patient Search

        #c.execute("SELECT * FROM Person WHERE PersonType = ?", {'PersonType': 'Patient'})
        #PersonInDB = c.fetchone()

        #sql_PersonSearch = "SELECT * FROM Person WHERE PersonType = ?"
        #par_Selected = ("Patient")

        # data = run_DB_Fetchall(sql_PersonSearch, par_Selected)
        c.execute("SELECT * FROM Person")
        data = c.fetchall()
        for row in data:
            if row[1] == "Patient":
                # listbox.insert(0, row)
                listbox.insert(END, row)

        FN = Label(ctr_left, text="Frist Name")
        FN.grid(row=1, column=0, padx=4, pady=4)

        first = tk.StringVar()
        entryFirst = tk.Entry(ctr_left, textvariable=first, font=LARGE_FONT)
        entryFirst.grid(row=1, column=1, padx=4, pady=4)

        LN = Label(ctr_left, text="Last Name")
        LN.grid(row=2, column=0, padx=4, pady=4)

        last = tk.StringVar()
        entryLast = tk.Entry(ctr_left, textvariable=last, font=LARGE_FONT)
        entryLast.grid(row=2, column=1, padx=4, pady=4)

        # sql_SearchPerson = "SELECT * FROM Person FirstName =? and LastName=?"
        # par_SearchPerson = (entry1.get(), entry2.get())
        c.execute("SELECT * FROM Person FirstName =:FirstName and LastName=:LastName", {'FirstName': entryFirst.get(), 'LastName': entryLast.get()})
        # data = run_DB_Fetchone(sql_SearchPerson, par_SearchPerson)
        data = c.fetchall()

        EDITFPID = data[1]

        selectPatient = tk.Button(top_frame, text="Patient Found", font=LABEL_FONT,
                                  width=BW_SIZE, height=BH_SIZE,
                                  command=lambda: controller.show_frame(EditPatient))

        if(EDITFPID != 0):
            selectPatient.pack(side=RIGHT, padx=3, pady=3)

        addPatient = tk.Button(top_frame, text="Add Patient", font=LABEL_FONT, width=BW_SIZE, height=BH_SIZE, bg="orange", fg="blue", command=lambda: controller.show_frame(AddPatient))
        addPatient.pack(side=RIGHT, padx=3, pady=3)

        buttonQuit = tk.Button(top_frame, text="EXIT", font=LABEL_FONT, width=BW_SIZE, height=BH_SIZE, bg="orange", fg="blue", command=lambda: controller.show_frame(AdminPage))
        buttonQuit.pack(side=LEFT, padx=3, pady=3)


class DoctorSearch(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        WWidth = parent.winfo_screenwidth()
        WHeight = parent.winfo_screenheight()

        # create the center widgets
        top_frame = Frame(self, width=WWidth, height=WHeight/3, padx=3, pady=3)
        ctr_left = Frame(self, width=WWidth/3, padx=3, pady=3)
        ctr_mid = Frame(self, width=WWidth/3, padx=3, pady=3)
        ctr_right = Frame(self, bg='green', width=WWidth/3, padx=3, pady=3)

        top_frame.grid(row=0, columnspan=3, sticky="ew")
        ctr_left.grid(row=1, column=0, sticky="ns")
        ctr_mid.grid(row=1, column=1, sticky="nsew")
        ctr_right.grid(row=1, column=2, sticky="ns")

        label = tk.Label(ctr_mid, text="Doctor Records", font=TITLE_FONT)
        label.pack(padx=10, pady=10)

        scrollbar = Scrollbar(ctr_right, width=60)
        scrollbar.grid(row=0, column=1, sticky=N+S)

        # create the listbox (note that size is in characters)
        listbox = Listbox(ctr_right, width=60, height=10)
        listbox.grid(row=0, column=0)

        # create a vertical scrollbar to the right of the listbox
        listbox.config(yscrollcommand=scrollbar.set)
        scrollbar.config(command=listbox.yview, orient=VERTICAL)

        # WRITE a code to search similar to IMS Patient Search
        # sql_PersonSearch = "SELECT * FROM Person WHERE PatientType = ?"
        # par_Selected = ("Patient")

        # data = run_DB_Fetchall(sql_PersonSearch, par_Selected)
        c.execute("SELECT * FROM Person")
        data = c.fetchall()
        for row in data:
            if row[1] == "Doctor":
                listbox.insert(END, row)

        FN = Label(ctr_left, Text="Frist Name")
        FN.grid(row=1, column=0, padx=4, pady=4)

        first = tk.StringVar()
        entry1 = tk.Entry(ctr_left, textvariable=first, font=LARGE_FONT)
        entry1.grid(row=1, column=1, padx=4, pady=4)

        LN = Label(ctr_left, Text="Last Name")
        LN.grid(row=2, column=0, padx=4, pady=4)

        last = tk.StringVar()
        entry2 = tk.Entry(ctr_left, textvariable=last, font=LARGE_FONT)
        entry2.grid(row=2, column=1, padx=4, pady=4)

        #sql_SearchPerson = "SELECT * FROM Person FirstName =? and LastName=?"
        #par_SearchPerson = (entry1.get(), entry2.get())
        #data = run_DB_Fetchone(sql_SearchPerson, par_SearchPerson)
        c.execute("SELECT * FROM Person FirstName =? and LastName=?", (entry1.get(), entry2.get()))
        data = c.fetchall()
        EDITFPID = data[1]

        editDoctor = tk.Button(top_frame, text="Edit Doctor", font=LABEL_FONT, width=BW_SIZE, height=BH_SIZE, bg="orange", fg="blue", command=lambda: controller.show_frame(EditDoctor))

        if(EDITFPID != 0):
            editDoctor.pack(side=RIGHT, padx=3, pady=3)

        addDoctor = tk.Button(top_frame, text="Add Doctor", font=LABEL_FONT, width=BW_SIZE, height=BH_SIZE, bg="orange", fg="blue", command=lambda: controller.show_frame(AddDoctor))
        addDoctor.pack(side=RIGHT, padx=3, pady=3)

        buttonQuit = tk.Button(top_frame, text="EXIT", font=LABEL_FONT, width=BW_SIZE, height=BH_SIZE, bg="orange", fg="blue", command=lambda: controller.show_frame(AdminPage))
        buttonQuit.pack(side=LEFT, padx=3, pady=3)


class AddPatient(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)

        # create the center widgets
        top_frame = Frame(self, padx=3, pady=3)
        ctr_left = Frame(self, bg='green')
        ctr_right = Frame(self, bg='blue')

        top_frame.grid(row=0, columnspan=2, sticky="ew")
        ctr_left.grid(row=1, column=0, sticky="ns")
        ctr_right.grid(row=1, column=1, sticky="ns")

        label = tk.Label(top_frame, text="Patient Records", font=TITLE_FONT)
        label.pack(padx=10, pady=10)

        stat = tk.Label(top_frame, text="status", font=TITLE_FONT)
        stat.pack(padx=10, pady=10)

        pTdoctoridLabel = tk.Label(ctr_left, text="Doctor ID", font=LABEL_FONT, width=W_BOX)
        pTdoctoridLabel.grid(row=0, padx=3, pady=3)

        pTservoidLabel = tk.Label(ctr_left, text="Servo ID", font=LABEL_FONT, width=W_BOX)
        pTservoidLabel.grid(row=1, padx=3, pady=3)

        pTFirstNameLabel = tk.Label(ctr_left, text="First Name", font=LABEL_FONT, width=W_BOX)
        pTFirstNameLabel.grid(row=2, padx=3, pady=3)

        pTLastNameLabel = tk.Label(ctr_left, text="Last Name", font=LABEL_FONT, width=W_BOX)
        pTLastNameLabel.grid(row=3, padx=3, pady=3)

        pTDOBLabel = tk.Label(ctr_left, text="Date of Birth", font=LABEL_FONT, width=W_BOX)
        pTDOBLabel.grid(row=4, padx=3, pady=3)

        pTAddressLabel = tk.Label(ctr_left, text="Address", font=LABEL_FONT, width=W_BOX)
        pTAddressLabel.grid(row=5, padx=3, pady=3)

        pTZipLabel = tk.Label(ctr_left, text="ZipCode", font=LABEL_FONT, width=W_BOX)
        pTZipLabel.grid(row=6, padx=3, pady=3)

        pTPhoneLabel = tk.Label(ctr_left, text="Phone Number", font=LABEL_FONT, width=W_BOX)
        pTPhoneLabel.grid(row=7, padx=3, pady=3)

        pTEmailLabel = tk.Label(ctr_left, text="Email", font=LABEL_FONT, width=W_BOX)
        pTEmailLabel.grid(row=8, padx=3, pady=3)

        doctorid = tk.StringVar()
        entry1 = tk.Entry(ctr_right, textvariable=doctorid, font=LARGE_FONT)
        entry1.grid(row=0, padx=4, pady=4)

        servoid = tk.StringVar()
        entry2 = tk.Entry(ctr_right, textvariable=servoid, font=LARGE_FONT)
        entry2.grid(row=1, padx=4, pady=4)

        first = tk.StringVar()
        entry3 = tk.Entry(ctr_right, textvariable=first, font=LARGE_FONT)
        entry3.grid(row=2, padx=4, pady=4)

        last = tk.StringVar()
        entry4 = tk.Entry(ctr_right, textvariable=last, font=LARGE_FONT)
        entry4.grid(row=3, padx=4, pady=4)

        dob = tk.StringVar()
        entry5 = tk.Entry(ctr_right, textvariable=dob, font=LARGE_FONT)
        entry5.grid(row=4, padx=4, pady=4)

        address = tk.StringVar()
        entry6 = tk.Entry(ctr_right, textvariable=address, font=LARGE_FONT)
        entry6.grid(row=5, padx=4, pady=4)

        zip = tk.StringVar()
        entry7 = tk.Entry(ctr_right, textvariable=zip, font=LARGE_FONT)
        entry7.grid(row=6, padx=4, pady=4)

        phone = tk.StringVar()
        entry8 = tk.Entry(ctr_right, textvariable=phone, font=LARGE_FONT)
        entry8.grid(row=7, padx=4, pady=4)

        email = tk.StringVar()
        entry9 = tk.Entry(ctr_right, textvariable=email, font=LARGE_FONT)
        entry9.grid(row=8, padx=4, pady=4)

        PTID = 5

        PT.fingerprint = PTID #FingerprintAdder
        PT.patientid = "Patient"
        PT.doctorid = entry1.get()
        PT.servoid = entry2.get()
        PT.first = entry3.get()
        PT.last = entry4.get()
        PT.dob = entry5.get()
        PT.address = entry6.get()
        PT.zip = entry7.get()
        PT.phone = entry8.get()
        PT.email = entry9.get()

        def Insert_to_DB():
            stat.config(text="Submited Sucessfully")
            sql_UPerson = """UPDATE Person SET value = (FingerPrintID,
                                PersonType, FirstName, LastName, Phone,
                                Email) WHERE value = (?, ?, ?, ?, ?, ?)"""
            par_UPerson = (PT.fingerprint, PT.patientid, PT.first, PT.last,
                           PT.phone, PT.email)
            run_DB_commit(sql_UPerson, par_UPerson)
            # c.execute("UPDATE Person SET value = (FingerPrintID, PersonType, FirstName, LastName, Phone, Email) WHERE value = (?, ?, ?, ?, ?, ?)", (PT.fingerprint, PT.patientid, PT.first, PT.last, PT.phone, PT.email))
            c.commit()

            sql_UPatient = """UPDATE Patient SET value = (FingerPrintID,
                                PersonType, DoctorID, ServoID, DOB, Address,
                                ZipCode) WHERE value = (?, ?, ?, ?, ?, ?, ?)"""
            par_UPatient = (PT.fingerprint, PT.patientid, PT.doctorid,
                            PT.servoid, PT.dob, PT.address, PT.zip)
            run_DB_commit(sql_UPatient, par_UPatient)
            # c.execute("UPDATE Patient SET value = (FingerPrintID,DoctorID, ServoID, DOB, Address, ZipCode) WHERE value = (?, ?, ?, ?, ?, ?, ?)", (PT.fingerprint, PT.patientid, PT.doctorid, PT.servoid, PT.dob, PT.address, PT.zip))
            c.commit()

        submitButton = tk.Button(top_frame, text="SAVE", font=LABEL_FONT,
                                 width=BW_SIZE, height=BH_SIZE, bg="orange",
                                 fg="blue", command=Insert_to_DB)
        submitButton.pack(side=RIGHT, padx=3, pady=3)

        # FPIDButton = tk.Button(ctr_right, text="Start FingerPrint Recording", font=LABEL_FONT, width=BW_SIZE, height=BH_SIZE, bg="orange", fg="blue", command=FingerprintAdder)
        # FPIDButton.grid(row=7, column=2, padx=3, pady=3)

        quitButton = tk.Button(top_frame, text="EXIT", font=LABEL_FONT,
                               width=BW_SIZE, height=BH_SIZE, bg="orange",
                               fg="blue", command=lambda: controller.show_frame(AdminPage))
        quitButton.pack(side=LEFT, padx=3, pady=3)


class AddDoctor(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)

        # create the center widgets
        top_frame = Frame(self, padx=3, pady=3)
        ctr_left = Frame(self)
        ctr_right = Frame(self)

        top_frame.grid(row=0, columnspan=2, sticky="ew")
        ctr_left.grid(row=1, column=0, sticky="ns")
        ctr_right.grid(row=1, column=1, sticky="ns")

        label = tk.Label(top_frame, text="Doctor Records", font=TITLE_FONT)
        label.pack(padx=10, pady=10)

        stat = tk.Label(top_frame, text="status", font=TITLE_FONT)
        stat.pack(padx=10, pady=10)

        DRFirstNameLabel = tk.Label(ctr_left, text="First Name", font=LABEL_FONT, width=W_BOX)
        DRFirstNameLabel.grid(row=0, padx=3, pady=3)

        DRLastNameLabel = tk.Label(ctr_left, text="Last Name", font=LABEL_FONT, width=W_BOX)
        DRLastNameLabel.grid(row=1, padx=3, pady=3)

        DRSpecialityLabel = tk.Label(ctr_left, text="Speciality", font=LABEL_FONT, width=W_BOX)
        DRSpecialityLabel.grid(row=2, padx=3, pady=3)

        DRPhoneLabel = tk.Label(ctr_left, text="Phone Number", font=LABEL_FONT, width=W_BOX)
        DRPhoneLabel.grid(row=3, padx=3, pady=3)

        pTEmailLabel = tk.Label(ctr_left, text="Email", font=LABEL_FONT, width=W_BOX)
        pTEmailLabel.grid(row=4, padx=3, pady=3)

        first = tk.StringVar()
        entry1 = tk.Entry(ctr_right, textvariable=first, font=LARGE_FONT)
        entry1.grid(row=0, padx=4, pady=4)

        last = tk.StringVar()
        entry2 = tk.Entry(ctr_right, textvariable=last, font=LARGE_FONT)
        entry2.grid(row=1, padx=4, pady=4)

        speciality = tk.StringVar()
        entry3 = tk.Entry(ctr_right, textvariable=speciality, font=LARGE_FONT)
        entry3.grid(row=2, padx=4, pady=4)

        phone = tk.StringVar()
        entry4 = tk.Entry(ctr_right, textvariable=phone, font=LARGE_FONT)
        entry4.grid(row=3, padx=4, pady=4)

        email = tk.StringVar()
        entry5 = tk.Entry(ctr_right, textvariable=email, font=LARGE_FONT)
        entry5.grid(row=4, padx=4, pady=4)

        DR.fingerprint = FingerprintAdder
        DR.id = "Doctor"
        DR.first = entry1.get()
        DR.last = entry2.get()
        DR.speciality = entry3.get()
        DR.phone = entry4.get()
        DR.email = entry5.get()

        def Insert_to_DB():
            stat.config(text="Submited Sucessfully")
            sql_UPerson = """UPDATE Person SET value = (FingerPrintID,
                            PersonType, FirstName, LastName, Phone, Email)
                            WHERE value = (?, ?, ?, ?, ?, ?)"""
            par_UPerson = (DR.fingerprint, DR.id, DR.first, DR.last,
                           DR.phone, DR.email)
            run_DB_commit(sql_UPerson, par_UPerson)
            # c.execute("UPDATE Person SET value = (FingerPrintID, PersonType, FirstName, LastName, Phone, Email) WHERE value = (?, ?, ?, ?, ?, ?)", DR.fingerprint, DR.id, DR.first, DR.last, DR.phone, DR.email)
            # c.commit()

            sql_UDoctor = """UPDATE Doctor SET value = (FingerPrintID,
                            PersonType, Speciality) WHERE value = (?, ?, ?)"""
            par_UDoctor = (DR.fingerprint, DR.doctorid, DR.speciality)
            run_DB_commit(sql_UDoctor, par_UDoctor)
            # c.execute("UPDATE Doctor SET value = (FingerPrintID, PersonType, Speciality) WHERE value = (?, ?, ?)", (DR.fingerprint, DR.patientid, DR.speciality))
            # c.commit()

        submitButton = tk.Button(top_frame, text="SAVE", font=LABEL_FONT,
                                 width=BW_SIZE, height=BH_SIZE, bg="orange",
                                 fg="blue", command=Insert_to_DB)
        submitButton.pack(side=RIGHT, padx=3, pady=3)

        quitButton = tk.Button(top_frame, text="EXIT", font=LABEL_FONT,
                               width=BW_SIZE, height=BH_SIZE, bg="orange",
                               fg="blue", command=lambda: controller.show_frame(AdminPage))
        quitButton.pack(side=LEFT, padx=3, pady=3)


class EditPatient(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)

        # create the center widgets
        top_frame = Frame(self, padx=3, pady=3)
        ctr_left = Frame(self, bg='gray')
        ctr_right = Frame(self, bg='blue')
        bottom_frame = Frame(self, padx=3, pady=3)

        top_frame.grid(row=0, columnspan=2, sticky="ew")
        ctr_left.grid(row=1, column=0, sticky="ns")
        ctr_right.grid(row=1, column=1, sticky="ns")
        bottom_frame.grid(row=2, columnspan=2, sticky="ew")

        label = tk.Label(top_frame, text="Patient Records", font=TITLE_FONT)
        label.pack(padx=10, pady=10)

        stat = tk.Label(top_frame, text="status", font=TITLE_FONT)
        stat.pack(padx=10, pady=10)

        pTdoctoridLabel = tk.Label(ctr_left, text="Doctor ID", font=LABEL_FONT)
        pTdoctoridLabel.grid(row=0, padx=3, pady=3)

        pTservoidLabel = tk.Label(ctr_left, text="Servo ID", font=LABEL_FONT)
        pTservoidLabel.grid(row=1, padx=3, pady=3)

        pTFirstNameLabel = tk.Label(ctr_left, text="First Name", font=LABEL_FONT)
        pTFirstNameLabel.grid(row=0, padx=3, pady=3)

        pTLastNameLabel = tk.Label(ctr_left, text="Last Name", font=LABEL_FONT)
        pTLastNameLabel.grid(row=1, padx=3, pady=3)

        pTDOBLabel = tk.Label(ctr_left, text="Date of Birth", font=LABEL_FONT)
        pTDOBLabel.grid(row=2, padx=3, pady=3)

        pTAddressLabel = tk.Label(ctr_left, text="Address", font=LABEL_FONT)
        pTAddressLabel.grid(row=3, padx=3, pady=3)

        pTZipLabel = tk.Label(ctr_left, text="ZipCode", font=LABEL_FONT)
        pTZipLabel.grid(row=4, padx=3, pady=3)

        pTPhoneLabel = tk.Label(ctr_left, text="Phone Number", font=LABEL_FONT)
        pTPhoneLabel.grid(row=5, padx=3, pady=3)

        pTEmailLabel = tk.Label(ctr_left, text="Email", font=LABEL_FONT)
        pTEmailLabel.grid(row=6, padx=3, pady=3)

        if query is None:
            FP = 1
        else:
            FP = query

        c.execute("SELECT * FROM Person WHERE FingerPrintID=:FingerPrintID and PersonType=:PersonType", {'FingerPrintID': FP, 'PersonTypeID': "Patient"})
        editPerson = c.fetchone()

        c.execute("SELECT * FROM Patient WHERE FingerPrintID=:FingerPrintID and PersonType=:PersonType", {'FingerPrintID': FP, 'PersonTypeID': "Patient"})
        editPatient = c.fetchone()

        PT.fingerprint = editPerson[1]
        PT.patientid = editPerson[2]
        PT.first = editPerson[3]
        PT.last = editPerson[4]
        PT.phone = editPerson[5]
        PT.email = editPerson[6]

        PT.doctorid = editPatient[2]
        PT.productid = editPatient[3]
        PT.dob = editPatient[4]
        PT.address = editPatient[5]
        PT.zip = editPatient[6]

        doctorid = tk.StringVar(ctr_right, PT.doctorid)
        productid = tk.StringVar(ctr_right, PT.productid)
        first = tk.StringVar(ctr_right, PT.first)
        last = tk.StringVar(ctr_right, PT.last)
        dob = tk.StringVar(ctr_right, PT.dob)
        address = tk.StringVar(ctr_right, PT.address)
        zip = tk.StringVar(ctr_right, PT.zip)
        phone = tk.StringVar(ctr_right, PT.phone)
        email = tk.StringVar(ctr_right, PT.email)

        try:
            entryDoctorID = tk.Text(ctr_right, text=doctorid, font=LARGE_FONT)
            entryProductID = tk.Text(ctr_right, textvariable=productid, font=LARGE_FONT)
            entryFirst = tk.Text(ctr_right, textvariable=first, font=LARGE_FONT)
            entryLast = tk.Text(ctr_right, textvariable=last, font=LARGE_FONT)
            entryDOB = tk.Text(ctr_right, textvariable=dob, font=LARGE_FONT)
            entryAddress = tk.Text(ctr_right, textvariable=address, font=LARGE_FONT)
            entryZip = tk.Text(ctr_right, textvariable=zip, font=LARGE_FONT)
            entryPhone = tk.Text(ctr_right, textvariable=phone, font=LARGE_FONT)
            entryEmail = tk.Text(ctr_right, textvariable=email, font=LARGE_FONT)
        except ImportError:
            entryDoctorID = tk.Entry(ctr_right, text=doctorid, font=LARGE_FONT)
            entryProductID = tk.Entry(ctr_right, textvariable=productid, font=LARGE_FONT)
            entryFirst = tk.Entry(ctr_right, textvariable=first, font=LARGE_FONT)
            entryLast = tk.Entry(ctr_right, textvariable=last, font=LARGE_FONT)
            entryDOB = tk.Entry(ctr_right, textvariable=dob, font=LARGE_FONT)
            entryAddress = tk.Entry(ctr_right, textvariable=address, font=LARGE_FONT)
            entryZip = tk.Entry(ctr_right, textvariable=zip, font=LARGE_FONT)
            entryPhone = tk.Entry(ctr_right, textvariable=phone, font=LARGE_FONT)
            entryEmail = tk.Entry(ctr_right, textvariable=email, font=LARGE_FONT)

        entryDoctorID.grid(row=0, padx=4, pady=4)
        entryProductID.grid(row=1, padx=4, pady=4)
        entryFirst.grid(row=2, padx=4, pady=4)
        entryLast.grid(row=3, padx=4, pady=4)
        entryDOB.grid(row=4, padx=4, pady=4)
        entryAddress.grid(row=5, padx=4, pady=4)
        entryZip.grid(row=6, padx=4, pady=4)
        entryPhone.grid(row=7, padx=4, pady=4)
        entryEmail.grid(row=8, padx=4, pady=4)

        def Update_to_DB():
            stat.config(text="Submited Sucessfully")
            c.execute("UPDATE Patient SET FingerPrintID=? WHERE DoctorID=?", {PT.fingerprint, entryDoctorID.get()})
            c.commit()

            c.execute("UPDATE Patient SET FingerPrintID=? WHERE ProductID=?", {PT.fingerprint, entryProductID.get()})
            c.commit()

            c.execute("UPDATE Person SET FingerPrintID=? WHERE FirstName=?", {PT.fingerprint, entryFirst.get()})
            c.commit()

            c.execute("UPDATE Person SET FingerPrintID=? WHERE LastName=?", {PT.fingerprint, entryLast.get()})
            c.commit()

            c.execute("UPDATE Patient SET FingerPrintID=? WHERE DOB=?", {PT.fingerprint, entryDOB.get()})
            c.commit()

            c.execute("UPDATE Patient SET FingerPrintID=? WHERE Address=?", {PT.fingerprint, entryAddress.get()})
            c.commit()

            c.execute("UPDATE Patient SET FingerPrintID=? WHERE ZipCode=?", {PT.fingerprint, entryZip.get()})
            c.commit()

            c.execute("UPDATE Person SET FingerPrintID=? WHERE Phone=?", {PT.fingerprint, entryPhone.get()})
            c.commit()

            c.execute("UPDATE Person SET FingerPrintID=? WHERE Email=?", {PT.fingerprint, entryEmail.get()})
            c.commit()


        submitButton = tk.Button(top_frame, text="SAVE", font=LABEL_FONT,
                                 width=BW_SIZE, height=BH_SIZE, bg="orange",
                                 fg="blue", command=Update_to_DB)
        submitButton.pack(side=RIGHT, padx=3, pady=3)

        quitButton = tk.Button(top_frame, text="EXIT", font=LABEL_FONT,
                               width=BW_SIZE, height=BH_SIZE, bg="orange",
                               fg="blue", command=lambda: controller.show_frame(AdminPage))
        quitButton.pack(side=LEFT, padx=3, pady=3)

        FPIDButton = tk.Button(ctr_right, text="Start FingerPrint Recording",
                               font=LABEL_FONT, width=BW_SIZE, height=BH_SIZE,
                               bg="orange", fg="blue", command=lambda: controller.show_frame(AdminErrorPage))
        FPIDButton.grid(row=7, column=2, padx=3, pady=3)


class EditAdminPage(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)

        # create the center widgets
        top_frame = Frame(self, padx=3, pady=3)
        ctr_left = Frame(self, bg='green')
        ctr_right = Frame(self, bg='blue')
        bottom_frame = Frame(self, padx=3, pady=3)

        top_frame.grid(row=0, columnspan=2, sticky="ew")
        ctr_left.grid(row=1, column=0, sticky="ns")
        ctr_right.grid(row=1, column=1, sticky="ns")
        bottom_frame.grid(row=2, columnspan=2, sticky="ew")

        label = tk.Label(top_frame, text="Admin Records", font=TITLE_FONT)
        label.pack(padx=10, pady=10)

        stat = tk.Label(top_frame, text="status", font=TITLE_FONT)
        stat.pack(padx=10, pady=10)

        ADPersonTypeLabel = tk.Label(ctr_left, text="Admin ID", font=LABEL_FONT)
        ADPersonTypeLabel.grid(row=0, padx=3, pady=3)

        ADFirstNameLabel = tk.Label(ctr_left, text="First Name", font=LABEL_FONT)
        ADFirstNameLabel.grid(row=1, padx=3, pady=3)

        ADLastNameLabel = tk.Label(ctr_left, text="Last Name", font=LABEL_FONT)
        ADLastNameLabel.grid(row=2, padx=3, pady=3)

        ADRelationshipLabel = tk.Label(ctr_left, text="Relationship", font=LABEL_FONT)
        ADRelationshipLabel.grid(row=3, padx=3, pady=3)

        ADPhoneLabel = tk.Label(ctr_left, text="Phone Number", font=LABEL_FONT)
        ADPhoneLabel.grid(row=4, padx=3, pady=3)

        ADEmailLabel = tk.Label(ctr_left, text="Email", font=LABEL_FONT)
        ADEmailLabel.grid(row=5, padx=3, pady=3)

        if query is None:
            FP = 1
        else:
            FP = query

        c.execute("SELECT * FROM Person WHERE FingerPrintID=:FingerPrintID", {'FingerPrintID': FP})
        editPerson = c.fetchone()

        c.execute("SELECT * FROM Admin WHERE FingerPrintID=:FingerPrintID", {'FingerPrintID': FP})
        editAdmin = c.fetchone()

        AD.fingerprint = editPerson[1]
        AD.adminid = editPerson[2]
        AD.first = editPerson[3]
        AD.last = editPerson[4]
        AD.phone = editPerson[5]
        AD.email = editPerson[6]

        AD.relationship = editAdmin[2]

        ADID = tk.Label(ctr_right, text=AD.adminid, font=LARGE_FONT)
        ADID.grid(row=0, padx=4, pady=4)

        first = AD.first
        entry1 = tk.Label(ctr_right, text=first, font=LARGE_FONT)
        entry1.grid(row=1, column=0, padx=4, pady=4)

        firstButton = tk.Button(ctr_right, text="Edit")
        firstButton.grid(row=1, column=1, padx=4, pady=4)

        first = tk.StringVar(ctr_right, AD.first)
        last = tk.StringVar(ctr_right, AD.last)
        relationship = tk.StringVar(ctr_right, AD.relationship)
        phone = tk.StringVar(ctr_right, AD.phone)
        email = tk.StringVar(ctr_right, AD.email)

        try:
            entryFirst = tk.Text(ctr_right, textvariable=first, font=LARGE_FONT)
            entryLast = tk.Text(ctr_right, textvariable=last, font=LARGE_FONT)
            entryRelationship = tk.Text(ctr_right, textvariable=relationship, font=LARGE_FONT)
            entryPhone = tk.Text(ctr_right, textvariable=phone, font=LARGE_FONT)
            entryEmail = tk.Text(ctr_right, textvariable=email, font=LARGE_FONT)
        except ImportError:
            entryFirst = tk.Entry(ctr_right, textvariable=first, font=LARGE_FONT)
            entryLast = tk.Entry(ctr_right, textvariable=last, font=LARGE_FONT)
            entryRelationship = tk.Entry(ctr_right, textvariable=relationship, font=LARGE_FONT)
            entryPhone = tk.Entry(ctr_right, textvariable=phone, font=LARGE_FONT)
            entryEmail = tk.Entry(ctr_right, textvariable=email, font=LARGE_FONT)

        entryFirst.grid(row=1, padx=4, pady=4)
        entryLast.grid(row=2, padx=4, pady=4)
        entryRelationship.grid(row=3, padx=4, pady=4)
        entryPhone.grid(row=4, padx=4, pady=4)
        entryEmail.grid(row=5, padx=4, pady=4)

        def Update_to_DB():
            c.execute("UPDATE Person SET FirstName=?, LastName=?, Phone=?, Email=? WHERE FingerPrintID=?", (entryFirst.get(), entryLast.get(), entryPhone.get(), entryEmail.get(), AD.fingerprint))
            c.commit()

            c.execute("UPDATE Admin SET Relationship=? WHERE FingerPrintID=?", (entryRelationship.get(), AD.fingerprint))
            c.commit()
            stat.config(text="Submited Sucessfully")

        submitButton = tk.Button(top_frame, text="SAVE", font=LABEL_FONT,
                                 width=BW_SIZE, height=BH_SIZE, bg="orange",
                                 fg="blue", command=Update_to_DB)
        submitButton.pack(side=RIGHT, padx=3, pady=3)

        quitButton = tk.Button(top_frame, text="EXIT", font=LABEL_FONT,
                               width=BW_SIZE, height=BH_SIZE, bg="orange",
                               fg="blue", command=lambda: controller.show_frame(AdminPage))
        quitButton.pack(side=LEFT, padx=3, pady=3)


class EditDoctor(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)

        # create the center widgets
        top_frame = Frame(self, padx=3, pady=3)
        ctr_left = Frame(self)
        ctr_right = Frame(self)

        top_frame.grid(row=0, columnspan=2, sticky="ew")
        ctr_left.grid(row=1, column=0, sticky="ns")
        ctr_right.grid(row=1, column=1, sticky="ns")

        label = tk.Label(top_frame, text="Doctor Records", font=TITLE_FONT)
        label.pack(padx=10, pady=10)

        stat = tk.Label(top_frame, text="status", font=TITLE_FONT)
        stat.pack(padx=10, pady=10)

        DRFirstNameLabel = tk.Label(ctr_left, text="First Name", font=LABEL_FONT)
        DRFirstNameLabel.grid(row=0, padx=3, pady=3)

        DRLastNameLabel = tk.Label(ctr_left, text="Last Name", font=LABEL_FONT)
        DRLastNameLabel.grid(row=1, padx=3, pady=3)

        DRSpecialityLabel = tk.Label(ctr_left, text="Speciality", font=LABEL_FONT)
        DRSpecialityLabel.grid(row=2, padx=3, pady=3)

        DRPhoneLabel = tk.Label(ctr_left, text="Phone Number", font=LABEL_FONT)
        DRPhoneLabel.grid(row=3, padx=3, pady=3)

        pTEmailLabel = tk.Label(ctr_left, text="Email", font=LABEL_FONT)
        pTEmailLabel.grid(row=4, padx=3, pady=3)

        if query is None:
            FP = 1
        else:
            FP = query

        c.execute("SELECT * FROM Person WHERE FingerPrintID=:FingerPrintID", {'FingerPrintID': FP})
        editPerson = c.fetchone()

        c.execute("SELECT * FROM Doctor WHERE FingerPrintID=:FingerPrintID", {'FingerPrintID': FP})
        editDoctor = c.fetchone()

        DR.fingerprint = editPerson[1]
        DR.doctorid = editPerson[2]
        DR.first = editPerson[3]
        DR.last = editPerson[4]
        DR.phone = editPerson[5]
        DR.email = editPerson[6]

        DR.speciality = editDoctor[2]

        first = tk.StringVar(ctr_right, DR.first)
        last = tk.StringVar(ctr_right, DR.last)
        speciality = tk.StringVar(ctr_right, DR.speciality)
        phone = tk.StringVar(ctr_right, DR.phone)
        email = tk.StringVar(ctr_right, DR.email)

        try:
            entryFirst = tk.Text(ctr_right, textvariable=first, font=LARGE_FONT)
            entryLast = tk.Text(ctr_right, textvariable=last, font=LARGE_FONT)
            entrySpecial = tk.Text(ctr_right, textvariable=speciality, font=LARGE_FONT)
            entryPhone = tk.Text(ctr_right, textvariable=phone, font=LARGE_FONT)
            entryEmail = tk.Text(ctr_right, textvariable=email, font=LARGE_FONT)
        except ImportError:
            entryFirst = tk.Entry(ctr_right, textvariable=first, font=LARGE_FONT)
            entryLast = tk.Entry(ctr_right, textvariable=last, font=LARGE_FONT)
            entrySpecial = tk.Entry(ctr_right, textvariable=speciality, font=LARGE_FONT)
            entryPhone = tk.Entry(ctr_right, textvariable=phone, font=LARGE_FONT)
            entryEmail = tk.Entry(ctr_right, textvariable=email, font=LARGE_FONT)

        entryFirst.grid(row=0, padx=4, pady=4)
        entryLast.grid(row=1, padx=4, pady=4)
        entrySpecial.grid(row=2, padx=4, pady=4)
        entryPhone.grid(row=3, padx=4, pady=4)
        entryEmail.grid(row=4, padx=4, pady=4)

        def Update_to_DB():
            stat.config(text="Submited Sucessfully")
            c.execute("UPDATE Person SET FingerPrintID=? WHERE FirstName=?", {DR.fingerprint, entryFirst.get()})

            c.execute("UPDATE Person SET FingerPrintID=? WHERE LastName=?", {DR.fingerprint, entryLast.get()})

            c.execute("UPDATE Doctor SET FingerPrintID=? WHERE Speciality=?", {DR.fingerprint, entrySpecial.get()})

            c.execute("UPDATE Person SET FingerPrintID=? WHERE Phone=?", {DR.fingerprint, entryPhone.get()})

            c.execute("UPDATE Person SET FingerPrintID=? WHERE Email=?", {DR.fingerprint, entryEmail.get()})
            c.commit()

        submitButton = tk.Button(top_frame, text="SAVE", font=LABEL_FONT,
                                 width=BW_SIZE, height=BH_SIZE, bg="orange",
                                 fg="blue", command=Update_to_DB)
        submitButton.pack(side=RIGHT, padx=3, pady=3)

        quitButton = tk.Button(top_frame, text="EXIT", font=LABEL_FONT,
                               width=BW_SIZE, height=BH_SIZE, bg="orange",
                               fg="blue", command=lambda: controller.show_frame(AdminPage))
        quitButton.pack(side=LEFT, padx=3, pady=3)


class SettingWindow(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        WWidth = parent.winfo_screenwidth()
        WHeight = parent.winfo_screenheight()

        # create the center widgets
        top_frame = Frame(self, width=WWidth, height=WHeight, padx=3, pady=3)
        ctr_left = Frame(self, height=WHeight, padx=3, pady=3)
        ctr_mid = Frame(self, height=WHeight, padx=3, pady=3)
        ctr_right = Frame(self, height=WHeight, padx=3, pady=3)

        top_frame.grid(row=0, columnspan=2, sticky="ew")
        ctr_left.grid(row=1, column=0, sticky="ns")
        ctr_mid.grid(row=1, column=0, sticky="ns")
        ctr_right.grid(row=1, column=2, sticky="ns")

        label = tk.Label(top_frame, text="Settings", font=TITLE_FONT)
        label.pack(padx=10, pady=10)

        buttonQuit = tk.Button(top_frame, text="EXIT", font=LABEL_FONT,
                               width=BW_SIZE, height=BH_SIZE, bg="orange",
                               fg="blue", command=lambda: controller.show_frame(AdminPage))
        buttonQuit.pack(side=LEFT, padx=3, pady=3)

        # scrollbar for the list of wi-fi

        addWiFi = tk.Label(ctr_left, text="Search for Wi-fi", font=LABEL_FONT,
                           bg="orange", fg="blue")
        addWiFi.pack(side=RIGHT, padx=3, pady=3)

        UsernameLabel = tk.Label(ctr_mid, text="Username", font=LABEL_FONT)
        UsernameLabel.pack(padx=3, pady=3)

        PasswordLabel = tk.Label(ctr_mid, text="Password", font=LABEL_FONT)
        PasswordLabel.pack(padx=3, pady=3)

        name = tk.StringVar(ctr_right, "username")
        word = tk.StringVar(ctr_right, "password")

        try:
            editUsername = tk.Text(ctr_right, text=name)
            editPassword = tk.Text(ctr_right, text=word)
        except ImportError:
            editUsername = tk.Entry(ctr_right, textvariable=name)
            editPassword = tk.Entry(ctr_right, textvariable=word)

        editUsername.pack(padx=3, pady=3)
        editPassword.pack(padx=3, pady=3)


app = Home()
app.mainloop()
