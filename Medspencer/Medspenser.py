''' Created on Jul 16, 2018 @author: Ivan '''
#!usr/bin/python

#import modules
try:
    import Tkinter as tk
    from Tkinter import *
except  ImportError:
    import tkinter as tk
    from tkinter import *

import sys
import sqlite3
import time
from time import gmtime, strftime
from Queries import *

TITLE_FONT = ("Verdana", 12, "bold")
LARGE_FONT = ("Arial", 12)
LABEL_FONT = ("Time New Roman", 12, "bold")
ERROR_FONT = ("Verdana", 24, "bold")
BW_SIZE = "10"
BH_SIZE = "2"
W_BOX = "12"
W_BOX_LENGTH = "22"
H_BOX = "1"
SSW = 656
SSH = 512
LSW = round(SSW/3)
MSW = 300
RSW = round(SSW/3)

FP = 1
fingerprint_index = 6

I2C_ADDRESS = 0x18
NO_DATA = 0xff
ERR = 0xfe

SCAN_FINGERPRINT = 0x01
REGISTER_FINGERPRINT = 0x02
DISPENSE = 0x03
PLAY_ALARM = 0x04

import smbus
i2c = smbus.SMBus(1)


#print("TEST")

conn = sqlite3.connect('Medespenser.db')
c = conn.cursor()


def createTable():
    c.execute("""CREATE TABLE IF NOT EXISTS Person (
                FingerPrintID INT,
                PersonType TEXT,
                FirstName TEXT,
                LastName TEXT,
                Phone TEXT,
                Email TEXT)""")

    c.execute("""CREATE TABLE IF NOT EXISTS Patient (
                FingerPrintID INT,
                PersonType TEXT,
                DoctorID INT,
                ProductID INT,
                DOB TEXT,
                Address TEXT,
                ZipCode TEXT)""")

    c.execute("""CREATE TABLE IF NOT EXISTS Doctor(
                FingerPrintID INT,
                PersonType TEXT,
                Speciality TEXT)""")

    c.execute("""CREATE TABLE IF NOT EXISTS Admin(
                FingerPrintID INT,
                PersonType TEXT,
                Relationship TEXT)""")

    c.execute("""CREATE TABLE IF NOT EXISTS Product(
                ProductID INT,
                ServoID INT,
                Name TEXT,
                Color TEXT,
                Shape TEXT,
                RxType TEXT)""")

    sql_Person = """INSERT INTO Person (FingerPrintID, PersonType, FirstName,
                     LastName, Phone, Email) VALUES (?, ?, ?, ?, ?, ?)"""
    c.execute(sql_Person, (1, "Patient", "John", "Doe", "0000000000", "unknown@email.com"))
    c.execute(sql_Person, (2, "Patient", "Matthew", "Hoover", "8508792691", "unknown@email.com"))
    c.execute(sql_Person, (3, "Patient", "Sakeenah", "Khan", "4075751176", "Unknown"))
    c.execute(sql_Person, (4, "Patient", "Gustavo", "Morales Burbano", "4072797581", "Unknown"))
    c.execute(sql_Person, (5, "Admin", "Ivan", "Alvarez", "4072263733", "cfbh@gmail.com"))
    c.execute(sql_Person, (6, "Doctor", "Fredesvinda", "Jacobs-Alvarez", "4072263733", "cfbhealthcare@gmail.com"))
    c.execute(sql_Person, (ERR, "Error", "John", "Doe", "0000000000", "unknown@email.com"))
    conn.commit()

    sql_Patient = """INSERT INTO Patient (FingerPrintID, PersonType, DoctorID,
                        ProductID, DOB, Address, ZipCode) VALUES (?, ?, ?, ?, ?, ?, ?)"""
    c.execute(sql_Patient, (1, "Patient", 6, 1, "01012000", "7350 Futures Drive", "32819"))
    c.execute(sql_Patient, (2, "Patient", 6, 4, "06062006", "7350 Futures Drive", "32819"))
    c.execute(sql_Patient, (3, "Patient", 6, 3, "06062008", "Unknown", "32832"))
    c.execute(sql_Patient, (4, "Patient", 6, 2,  "06062008", "Unknown", "32822"))
    conn.commit()

    sql_Doctor = """INSERT INTO Doctor (FingerPrintID, PersonType, Speciality)
                    VALUES (?, ?, ?)"""
    c.execute(sql_Doctor, (1, "Doctor", "MD"))
    c.execute(sql_Doctor, (6, "Doctor", "Child, Adolescent and Adult Psychiatric"))
    conn.commit()

    sql_Admin = """INSERT INTO Admin (FingerPrintID, PersonType, Relationship)
                    VALUES (?, ?, ?)"""
    c.execute(sql_Admin, (1, "Admin", "Caretaker"))
    c.execute(sql_Admin, (5, "Admin", "Caretaker"))
    conn.commit()

    sql_Product = """INSERT INTO Product(ProductID, ServoID, Name, Color, Shape,
                     RxType) VALUES (?, ?, ?, ?, ?, ?)"""
    c.execute(sql_Product, (1, 1, "Skittles", "Green", "Round", "C"))
    c.execute(sql_Product, (2, 2, "Skittles", "Orange", "Round", "NC"))
    c.execute(sql_Product, (3, 3, "Skittles", "Red", "Round", "C"))
    c.execute(sql_Product, (4, 4, "Skittles", "Yellow", "Round", "NC"))
    c.execute(sql_Product, (5, 5, "Skittles", "Black", "Round", "C"))
    conn.commit()


# I2C Functions


def FingerprintReader():
    print("Reading fingerprint...")
    FPID = NO_DATA

    I2CWrite(SCAN_FINGERPRINT)

    # Loop if no data ready
    while(FPID == NO_DATA):
        #print("NO DATA")
        FPID = I2CRead()
        time.sleep(1)
    print("Fingerprint read! " + str(FPID))
    # return an int less than 128 (Registered User)
    # return ERR (Print not found, Access Denied)
    return FPID


def FingerprintAdder():
    print("Registering fingerprint...")
    FPID = NO_DATA
    global fingerprint_index

    I2CWrite(REGISTER_FINGERPRINT, fingerprint_index)
    fingerprint_index = fingerprint_index + 1

    # Loop if no data ready
    while(FPID == NO_DATA):
        #print("NO DATA")
        FPID = I2CRead()
        time.sleep(1)

    print("Fingerprint registered!")
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


def callback_FR():
    # self.returnfield['text'] = "User scanned: " + str(FingerprintReader())
    return FingerprintReader()


def callback_FNew():
    # self.returnfield['text'] = "User added: " + str(FingerprintAdder())
    FingerprintAdder()


def call_Alarm():
    # self.returnfield['text'] = "User added: " + str(FingerprintAdder())
    I2CWrite(PLAY_ALARM)


def comb_funcs(*funcs):
    def combine_funcs(*args, **kwargs):
        for f in funcs:
            f(*args, **kwargs)
    return combine_funcs


class popupWindow(object):
    def __init__(self, master):
        top = self.top = Toplevel(master)

        title = Label(top, text="Please Wait. \n Page is loading", pady=10)
        title.pack()

        global FP
        # FP = callback_FR()
        FP = 5
        # print(FP)

        if FP >= fingerprint_index or FP is None:
            PTText = "Welcome User"
            PersonFound = Button(top, text=PTText, pady=10,
                                 command=comb_funcs(EFPPage, self.cleanup))
            # print(PTText)
        else:
            c.execute("SELECT * FROM Person WHERE FingerPrintID=:FingerPrintID", {'FingerPrintID': FP})
            person = c.fetchone()
            # print(person)
            if person[1] == "Patient":
                PTText = "Welcome {}".format(person[2])
                # PersonFound = Button(top, text=PTText, pady=10,
                #                      command=comb_funcs(PatientPage, call_Alarm, self.cleanup))
                PersonFound = Button(top, text=PTText, pady=10,
                                     command=comb_funcs(PatientPage, self.cleanup))
                # print(PTText)
            elif person[1] == "Admin":
                PTText = "Welcome {}".format(person[2])
                # PersonFound = Button(top, text=PTText, pady=10,
                #                      command=comb_funcs(AdminPage, call_Alarm, self.cleanup))
                PersonFound = Button(top, text=PTText, pady=10,
                                     command=comb_funcs(AdminPage, self.cleanup))
                # print(PTText)
            else:
                PTText = "Welcome User"
                PersonFound = Button(top, text=PTText, pady=10,
                                     command=comb_funcs(EFPPage, self.cleanup))
                # print(PTText)

        PersonFound.pack()

    def cleanup(self):
        self.top.destroy()


class ThisThing(object):
    def DefaultPage(self):
        self.w = popupWindow(self.master)
        # self.b["state"] = "disabled"
        # self.wait_window(self.w.top)
        # self.b["state"] = "normal"

    def __init__(self, master):
        self. master = master
        title = Label(master, text="Please Scan your Finger", pady=10)

        # createTable()

        Text = "Please Press me to Scan your Finger"
        scanFingerprint = Button(master, text=Text, pady=10,
                                 command=self.DefaultPage)
        returnfield = Label(master, text="", pady=10)

        title.pack()
        scanFingerprint.pack()
        returnfield.pack()


class PatientPage:
    def __init__(self):
        root = Tk()
        root.title("Patient Screen")
        root.geometry("%dx%d+0+0" % (WW, WH))

        top_frame = Frame(root, width=SSW, height=2, padx=3)
        ctr_left = Frame(root, width=LSW, padx=3, pady=3)
        ctr_mid = Frame(root, width=MSW, padx=3, pady=3)
        ctr_right = Frame(root, width=RSW, padx=3)

        top_frame.grid(row=0, columnspan=3, sticky="ew")
        ctr_left.grid(row=1, column=0, sticky="ns")
        ctr_mid.grid(row=1, column=1, sticky="nsew")
        ctr_right.grid(row=1, column=2, sticky="ns")

        pTFirstNameLabel = Label(ctr_left, text="First Name", font=LABEL_FONT)
        pTLastNameLabel = Label(ctr_left, text="Last Name", font=LABEL_FONT)
        pTDOBLabel = Label(ctr_left, text="Date of Birth", font=LABEL_FONT)
        pTDoctorLabel = Label(ctr_left, text="Doctor", height=2, font=LABEL_FONT)
        pTAddressLabel = Label(ctr_left, text="Address", font=LABEL_FONT)
        pTZipLabel = Label(ctr_left, text="ZipCode", font=LABEL_FONT)
        pTPhoneLabel = Label(ctr_left, text="Phone Number", font=LABEL_FONT)
        pTEmailLabel = Label(ctr_left, text="Email", font=LABEL_FONT)

        pTFirstNameLabel.grid(row=0, padx=3, pady=3)
        pTLastNameLabel.grid(row=1, padx=3, pady=3)
        pTDOBLabel.grid(row=2, padx=3, pady=3)
        pTDoctorLabel.grid(row=3, padx=3, pady=3)
        pTAddressLabel.grid(row=4, padx=3, pady=3)
        pTZipLabel.grid(row=5, padx=3, pady=3)
        pTPhoneLabel.grid(row=6, padx=3, pady=3)
        pTEmailLabel.grid(row=7, padx=3, pady=3)

        c.execute("SELECT * FROM Person WHERE FingerPrintID=:FingerPrintID", {'FingerPrintID': FP})
        editPerson = c.fetchone()

        c.execute("SELECT * FROM Patient WHERE FingerPrintID=:FingerPrintID", {'FingerPrintID': FP})
        editPatient = c.fetchone()

        PT.fingerprint = editPerson[0]
        PT.patientid = editPerson[1]
        PT.first = editPerson[2]
        PT.last = editPerson[3]
        PT.phone = editPerson[4]
        PT.email = editPerson[5]

        PT.doctorid = editPatient[2]
        PT.productid = editPatient[3]
        PT.dob = editPatient[4]
        PT.address = editPatient[5]
        PT.zip = editPatient[6]

        c.execute("SELECT * FROM Doctor WHERE FingerPrintID=:FingerPrintID", {'FingerPrintID': PT.doctorid})
        DoctorSp = c.fetchone()

        c.execute("SELECT * FROM Person WHERE FingerPrintID=:FingerPrintID", {'FingerPrintID': PT.doctorid})
        DRInfo = c.fetchone()

        PTDOCTOR2 = "{0} {1}, \n {2}".format(DRInfo[2], DRInfo[3], DoctorSp[2])

        c.execute("SELECT * FROM Product WHERE ProductID=:ProductID", {'ProductID': PT.productid})
        foundProduct = c.fetchone()

        productid = "{0}-{1}".format(foundProduct[2], foundProduct[3])
        # print(productid)

        entryFirst = Label(ctr_mid, text=PT.first, font=LARGE_FONT)
        entryLast = Label(ctr_mid, text=PT.last, font=LARGE_FONT)
        entryDOB = Label(ctr_mid, text=PT.dob, font=LARGE_FONT)
        entryDoctorID = Label(ctr_mid, text=PTDOCTOR2, height=2, font=LARGE_FONT)
        entryAddress = Label(ctr_mid, text=PT.address, font=LARGE_FONT)
        entryZip = Label(ctr_mid, text=PT.zip, font=LARGE_FONT)
        entryPhone = Label(ctr_mid, text=PT.phone, font=LARGE_FONT)
        entryEmail = Label(ctr_mid, text=PT.email, font=LARGE_FONT)

        entryFirst.grid(row=0, padx=4, pady=4)
        entryLast.grid(row=1, padx=4, pady=4)
        entryDOB.grid(row=2, padx=4, pady=4)
        entryDoctorID.grid(row=3, padx=4, pady=4)
        entryAddress.grid(row=4, padx=4, pady=4)
        entryZip.grid(row=5, padx=4, pady=4)
        entryPhone.grid(row=6, padx=4, pady=4)
        entryEmail.grid(row=7, padx=4, pady=4)

        # NCSUBSTANCE1 = "Skittles \n Green"
        NCSUBSTANCE1 = "{0}-{1}".format(foundProduct[2], foundProduct[3])
        NCB1 = Button(ctr_right, text=NCSUBSTANCE1, font=LABEL_FONT,
                      width=BW_SIZE, height=BH_SIZE, bg=foundProduct[3],
                      fg="white", command=Dispense1)

        # CSUBSTANCE1 = "Skittles \n Orange"
        CSUBSTANCE1 = "{0}-{1}".format(foundProduct[2], foundProduct[3])
        CB1 = Button(ctr_right, text=CSUBSTANCE1, font=LABEL_FONT,
                     width=BW_SIZE, height=BH_SIZE, bg=foundProduct[3],
                     fg="white", command=Dispense1)

        scrollbar = Scrollbar(ctr_right, width=20)
        scrollbar.pack(side=RIGHT, fill=BOTH)
        listbox = Listbox(ctr_right)
        # attach listbox to scrollbar
        listbox.config(yscrollcommand=scrollbar.set)
        scrollbar.config(command=listbox.yview)

        if foundProduct[5] == "NC":
            NCB1.pack(padx=10, pady=10)
            listbox.insert(tk.END, NCB1)
        else:
            CB1.pack(padx=10, pady=10)
            listbox.insert(0, CB1)

#        NCB1.pack()
#        CB1.pack()

        buttonQuit = Button(top_frame, text="QUIT", font=LABEL_FONT,
                               width=BW_SIZE, height=BH_SIZE,
                               bg="orange", fg="blue",
                               command=self.cleanup)
        buttonQuit.pack(side=LEFT, padx=3, pady=3)

    def cleanup(self):
        self.root.destroy()


class AdminPage:
    def __init__(self):
        root = Tk()
        root.title("Admin Page Screen")
        root.geometry("%dx%d+0+0" % (WW, WH))

        # create the center widgets
        top_frame = Frame(root, width=SSW, height=2, padx=3, pady=3)
        ctr_left = Frame(root, width=LSW, padx=3, pady=3)
        ctr_mid = Frame(root, width=MSW, padx=3, pady=3)
        ctr_right = Frame(root, width=RSW, padx=3, pady=3)

        top_frame.grid(row=0, columnspan=3, sticky="ew")
        ctr_left.grid(row=1, column=0, sticky="ns")
        ctr_mid.grid(row=1, column=1, sticky="nsew")
        ctr_right.grid(row=1, column=2, sticky="ns")

        aDFirstNameLabel = Label(ctr_left, text="First Name", justify=LEFT, font=LABEL_FONT)
        aDLastNameLabel = Label(ctr_left, text="Last Name", justify=LEFT, font=LABEL_FONT)
        aDPhoneLabel = Label(ctr_left, text="Phone Number", justify=LEFT, font=LABEL_FONT)
        aDRelationLabel = Label(ctr_left, text="Relationship", justify=LEFT, font=LABEL_FONT)
        aDEmailLabel = Label(ctr_left, text="Email", justify=LEFT, font=LABEL_FONT)

        aDFirstNameLabel.pack(padx=3, pady=3)
        aDLastNameLabel.pack(padx=3, pady=3)
        aDRelationLabel.pack(padx=3, pady=3)
        aDPhoneLabel.pack(padx=3, pady=3)
        aDEmailLabel.pack(padx=3, pady=3)

        c.execute("SELECT * FROM Person WHERE FingerPrintID=?", (FP,))
        PersonInDB = c.fetchone()

        c.execute("SELECT * FROM Admin WHERE FingerPrintID=?", (FP,))
        AdminInDB = c.fetchone()

        ADFIRSTNAME = PersonInDB[1]
        ADLASTNAME = PersonInDB[2]
        ADPHONE = PersonInDB[3]
        ADEMAIL = PersonInDB[4]

        ADRELATIONSHIP = AdminInDB[2]

        aDFirstName = Label(ctr_mid, text=ADFIRSTNAME, font=LARGE_FONT)
        aDLastName = Label(ctr_mid, text=ADLASTNAME, font=LARGE_FONT)
        aDRelation = Label(ctr_mid, text=ADRELATIONSHIP, font=LARGE_FONT)
        aDPhone = Label(ctr_mid, text=ADPHONE, font=LARGE_FONT)
        aDEmail = Label(ctr_mid, text=ADEMAIL, font=LARGE_FONT)

        aDFirstName.pack(padx=3, pady=3)
        aDLastName.pack(padx=3, pady=3)
        aDRelation.pack(padx=3, pady=3)
        aDPhone.pack(padx=3, pady=3)
        aDEmail.pack(padx=3, pady=3)

        addFingerprint = Button(ctr_right, text="Add Fingerprint", font=LABEL_FONT, pady=10,
                                command=callback_FNew)
        addFingerprint.pack(padx=3, pady=3)

        editDispense1 = Button(ctr_right, text="Edit Motor 1", font=LABEL_FONT,
                               width=BW_SIZE, height=BH_SIZE,
                               command=Dispense1)
        editDispense1.pack(padx=3, pady=3)

        editDispense2 = Button(ctr_right, text="Edit Motor 2", font=LABEL_FONT,
                               width=BW_SIZE, height=BH_SIZE,
                               command=Dispense2)
        editDispense2.pack(padx=3, pady=3)

        editDispense3 = Button(ctr_right, text="Edit Motor 3", font=LABEL_FONT,
                               width=BW_SIZE, height=BH_SIZE,
                               command=Dispense3)
        editDispense3.pack(padx=3, pady=3)

        buttonQuit = Button(top_frame, text="EXIT", font=LABEL_FONT,
                            width=BW_SIZE, height=BH_SIZE, bg="orange",
                            fg="blue", command=self.cleanup)
        buttonQuit.pack(side=LEFT, padx=3, pady=3)

    def cleanup(self):
        self.root.destroy()


class EFPPage:
    def __init__(self):
        root = Tk()

        FirstText = "Error on scanning \n"
        SecondText = "Please Re-scan Your Thumb"
        Text = "{}{}".format(FirstText, SecondText)
        label = Button(root,
                       text=Text,
                       width=SSW,
                       font=TITLE_FONT,
                       command=ThisThing)
        label.pack(padx=10, pady=10)


if __name__ == "__main__":
    root = Tk()
    root.title("Fingerprint Screen")
    WW = root.winfo_screenwidth()
    WH = root.winfo_screenheight()
    root.geometry("%dx%d+0+0" % (WW, WH))
    m = ThisThing(root)
    root.mainloop()

# thisThing = ThisThing()
