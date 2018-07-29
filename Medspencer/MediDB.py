''' Created on July 16, 2018 @author: Ivan '''

import sqlite3
from Queries import *


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

    c.execute("""CREATE TABLE IF NOT EXISTS A_Methods(
                ID TEXT,
                Subgroup TEXT,
                Method TEXT)""")

    c.execute("""CREATE TABLE IF NOT EXISTS B_Units(
                ID TEXT,
                Subgroup TEXT,
                Unit INT)""")

    c.execute("""CREATE TABLE IF NOT EXISTS C_DoseForm(
                ID TEXT,
                Subgroup TEXT,
                DoseForm TEXT)""")

    c.execute("""CREATE TABLE IF NOT EXISTS D_ModeOfDelivery(
                ID TEXT,
                Subgroup TEXT,
                ModeofDelivery TEXT)""")

    c.execute("""CREATE TABLE IF NOT EXISTS E_Timing(
                ID TEXT,
                Subgroup TEXT,
                Timing TEXT)""")

    c.execute("""CREATE TABLE IF NOT EXISTS F_Qualifier(
                ID TEXT,
                Subgroup TEXT,
                Qualifier TEXT)""")


def createData():
    sql_Person = """INSERT INTO Person (FingerPrintID, PersonType, FirstName,
                     LastName, Phone, Email) VALUES (?, ?, ?, ?, ?, ?)"""
    c.execute(sql_Person, (0, "Patient", "John", "Doe", "0000000000", "unknown@email.com"))
    c.execute(sql_Person, (1, "Patient", "Matthew", "Hoover", "8508792691", "unknown@email.com"))
    c.execute(sql_Person, (2, "Patient", "Sakeenah", "Khan", "4075751176", "Unknown"))
    c.execute(sql_Person, (3, "Patient", "Gustavo", "Morales Burbano", "4072797581", "Unknown"))
    c.execute(sql_Person, (4, "Admin", "Ivan", "Alvarez", "4072263733", "cfbh@gmail.com"))
    c.execute(sql_Person, (5, "Doctor", "Fredesvinda", "Jacobs-Alvarez", "4072263733", "cfbhealthcare@gmail.com"))
    conn.commit()

    sql_Patient = """INSERT INTO Patient (FingerPrintID, PersonType, DoctorID,
                        ProductID, DOB, Address, ZipCode) VALUES (?, ?, ?, ?, ?, ?, ?)"""
    c.execute(sql_Patient, (0, "Patient", 5, 1, "01012000", "7350 Futures Drive", "32819"))
    c.execute(sql_Patient, (1, "Patient", 5, 4, "06062006", "7350 Futures Drive", "32819"))
    c.execute(sql_Patient, (2, "Patient", 5, 3, "06062008", "Unknown", "32832"))
    c.execute(sql_Patient, (3, "Patient", 5, 2,  "06062008", "Unknown", "32822"))
    conn.commit()

    sql_Doctor = """INSERT INTO Doctor (FingerPrintID, PersonType, Speciality)
                    VALUES (?, ?, ?)"""
    c.execute(sql_Doctor, (0, "Doctor", "MD"))
    c.execute(sql_Doctor, (5, "Doctor", "Child, Adolescent and Adult Psychiatric"))
    conn.commit()

    sql_Admin = """INSERT INTO Admin (FingerPrintID, PersonType, Relationship)
                    VALUES (?, ?, ?)"""
    c.execute(sql_Admin, (0, "Admin", "Caretaker"))
    c.execute(sql_Admin, (4, "Admin", "Caretaker"))
    conn.commit()

    sql_Product = """INSERT INTO Product(ProductID, ServoID, Name, Color, Shape,
                     RxType) VALUES (?, ?, ?, ?, ?, ?)"""
    c.execute(sql_Product, (1, 1, "Skittles", "Green", "Round", "C"))
    c.execute(sql_Product, (2, 2, "Skittles", "Orange", "Round", "NC"))
    c.execute(sql_Product, (3, 3, "Skittles", "Red", "Round", "C"))
    c.execute(sql_Product, (4, 4, "Skittles", "Yellow", "Round", "NC"))
    c.execute(sql_Product, (5, 5, "Skittles", "Black", "Round", "C"))
    conn.commit()

    sql_Methods = "INSERT INTO A_Methods(ID, Subgroup, Method) VALUES (?, ?, ?)"
    c.execute(sql_Methods, ("1", "A", "Given"))
    c.execute(sql_Methods, ("2", "A", "Take"))
    c.execute(sql_Methods, ("3", "A", "Place"))
    c.execute(sql_Methods, ("4", "A", "Chew and swallow"))
    c.execute(sql_Methods, ("5", "A", "Place underneath tongue"))
    c.execute(sql_Methods, ("6", "A", "Swallow but DO NOT chew"))
    conn.commit()

    sql_Units = "INSERT INTO B_Units (ID, Subgroup, Unit) VALUES (?, ?, ?)"
    c.execute(sql_Units, ("1", "B", "1"))
    c.execute(sql_Units, ("2", "B", "2"))
    c.execute(sql_Units, ("3", "B", "3"))
    c.execute(sql_Units, ("4", "B", "4"))
    c.execute(sql_Units, ("5", "B", "5"))
    c.execute(sql_Units, ("6", "B", "6"))
    c.execute(sql_Units, ("7", "B", "7"))
    c.execute(sql_Units, ("8", "B", "8"))
    c.execute(sql_Units, ("9", "B", "9"))
    c.execute(sql_Units, ("10", "B", "10"))
    c.execute(sql_Units, ("11", "B", "12"))
    c.execute(sql_Units, ("12", "B", "14"))
    c.execute(sql_Units, ("13", "B", "15"))
    c.execute(sql_Units, ("14", "B", "24"))
    c.execute(sql_Units, ("15", "B", "28"))
    c.execute(sql_Units, ("16", "B", "30"))
    c.execute(sql_Units, ("17", "B", "36"))
    c.execute(sql_Units, ("18", "B", "45"))
    c.execute(sql_Units, ("19", "B", "48"))
    conn.commit()

    sql_DoseForm = """INSERT INTO C_DoseForm(ID, Subgroup, DoseForm) 
                        VALUES (?, ?, ?)"""
    c.execute(sql_DoseForm, ("1", "C", "gram(s)"))
    c.execute(sql_DoseForm, ("2", "C", "tablet(s)"))
    c.execute(sql_DoseForm, ("3", "C", "capsule(s)"))
    conn.commit()

    sql_ModeOfDelivery = """INSERT INTO D_ModeOfDelivery(ID, Subgroup, ModeofDelivery) 
                            VALUES (?, ?, ?)"""
    c.execute(sql_ModeOfDelivery, ("1", "D", "by mouth"))
    conn.commit()

    sql_Timing = "INSERT INTO E_Timing (ID, Subgroup, Timing) VALUES (?, ?, ?)"
    c.execute(sql_Timing, ("1", "E", "times"))
    c.execute(sql_Timing, ("2", "E", "at 4 pm"))
    c.execute(sql_Timing, ("3", "E", "at 12pm"))
    c.execute(sql_Timing, ("4", "E", "evening"))
    c.execute(sql_Timing, ("5", "E", "at dinner time"))
    c.execute(sql_Timing, ("6", "E", "daily"))
    c.execute(sql_Timing, ("7", "E", "one time"))
    c.execute(sql_Timing, ("8", "E", "twice a day"))
    c.execute(sql_Timing, ("9", "E", "three times a day"))
    c.execute(sql_Timing, ("10", "E", "four times a day"))
    c.execute(sql_Timing, ("11", "E", "at bedtime"))
    c.execute(sql_Timing, ("12", "E", "ever morning"))
    c.execute(sql_Timing, ("13", "E", "every other day"))
    c.execute(sql_Timing, ("14", "E", "every 4-6 hours"))
    c.execute(sql_Timing, ("15", "E", "every 8 hours"))
    c.execute(sql_Timing, ("16", "E", "every 6-8 hours"))
    c.execute(sql_Timing, ("17", "E", "every 72 hours"))
    c.execute(sql_Timing, ("18", "E", "before meal(s)"))
    c.execute(sql_Timing, ("19", "E", "after meal(s)"))
    conn.commit()

    sql_Qualifier = """INSERT INTO F_Qualifier (ID, Subgroup, Qualifier) 
                        VALUES (?, ?, ?)"""
    c.execute(sql_Qualifier, ("1", "F", "to"))
    c.execute(sql_Qualifier, ("2", "F", "for"))
    c.execute(sql_Qualifier, ("3", "F", "sparingly"))
    c.execute(sql_Qualifier, ("4", "F", "for one week"))
    c.execute(sql_Qualifier, ("5", "F", "to affected area"))
    c.execute(sql_Qualifier, ("6", "F", "for up to"))
    c.execute(sql_Qualifier, ("7", "F", "as needed"))
    c.execute(sql_Qualifier, ("8", "F", "as directed"))
    c.execute(sql_Qualifier, ("9", "F", "Days 1 & 2"))
    c.execute(sql_Qualifier, ("10", "F", "Days 3 & 4"))
    c.execute(sql_Qualifier, ("11", "F", "Days 5 & 6"))
    c.execute(sql_Qualifier, ("12", "F", "Days 7 & 8"))
    c.execute(sql_Qualifier, ("13", "F", "Days 9 & 10"))
    c.execute(sql_Qualifier, ("14", "F", "Days 11 & 12"))
    c.execute(sql_Qualifier, ("15", "F", "for cough"))
    c.execute(sql_Qualifier, ("16", "F", "for asthma"))
    c.execute(sql_Qualifier, ("17", "F", "for nausea"))
    conn.commit()

