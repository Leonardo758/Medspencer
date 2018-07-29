''' Created on July 16, 2018 @author: Ivan '''


class FingerprintID:
    def __init__(self, FPID, Type):
        self.fpid = FPID
        self.type = Type

        def __repr__(self):
            return "FingerprintID('{}', '{}')".format(self.fpid, self.type)


class PT:
    def __init__(self, FingerPrintID, PersonTypeID, DoctorID, ServoID, FirstName, LastName, DOB, Address, ZipCode, Phone, Email):
        self.fingerprint = FingerPrintID
        self.patientid = PersonTypeID
        self.doctorid = DoctorID
        self.servoid = ServoID
        self.first = FirstName
        self.last = LastName
        self.dob = DOB
        self.address = Address
        self.zip = ZipCode
        self.phone = Phone
        self.email = Email

        @property
        def email(self):
            return '{}'.format(self.email)

        @property
        def fullname(self):
            return '{} {}'.format(self.first, self.last)

        @property
        def fulladdress(self):
            return '{} {}'.format(self.address, self.zip)

        def __repr__(self):
            qury_Patient = "Patient('{}', '{}', '{}', '{}', '{}', '{}', '{}', '{}', '{}', '{}', '{}')"
            return qury_Patient.format(self.fingerprint, self.pateintid, self.doctorid, self.servoid, self.first, self.last, self.dob, self.address, self.zip, self.phone, self.email)


class DR:
    def __init__(self, FingerPrintID, PersonTypeID, FirstName, LastName, Speciality, Phone, Email):
        self.doctorid = FingerPrintID
        self.id = PersonTypeID
        self.first = FirstName
        self.last = LastName
        self.speciality = Speciality
        self.phone = Phone
        self.email = Email

        @property
        def email(self):
            return '{}'.format(self.email)

        @property
        def fullname(self):
            return '{} {}, {}'.format(self.first, self.last, self.speciality)

        def __repr__(self):
            return "Doctor('{}', '{}', '{}', '{}', '{}', '{}', '{}')".format(self.id, self.ptid, self.first, self.last, self.speciality, self.phone, self.email)


class AD:
    def __init__(self, FingerPrintID, AdminID, FirstName, LastName, Phone, Relationship, Email):
        self.fingerprint = FingerPrintID
        self.adminid = AdminID
        self.first = FirstName
        self.last = LastName
        self.phone = Phone
        self.relationship = Relationship
        self.email = Email

        @property
        def email(self):
            return '{}'.format(self.email)

        @property
        def fullname(self):
            return '{} {}, {}'.format(self.first, self.last, self.relationship)

        def __repr__(self):
            return "Admin('{}', '{}', '{}', '{}', '{}', '{}', '{}')".format(self.fingerprint, self.adminid, self.first, self.last, self.phone, self.relationship, self.email)


class Wifi:
    def __init__(self, SSID, UserNameID, PasswordID):
        self.ssid = SSID
        self.username = UserNameID
        self.password = PasswordID

        def __repr__(self):
            return "Wifi('{}', '{}', '{}')".format(self.ssid, self.username, self.password)


class PatientToRx:
    def __init__(self, PatientID, ServoID):
        self.patientid = PatientID
        self.servoid = ServoID

        def __repr__(self):
            return "PatientToRx('{}', '{}')".format(self.patientid, self.servoid)


class Product:
    def __init__(self, ProductID, Servo, Name, Color, Shape):
        self.id = ProductID
        self.servo = Servo
        self.name = Name
        self.color = Color
        self.shape = Shape

        @property
        def __repr__(self):
            return "Product('{}', '{}', '{}', '{}', '{}')".format(self.id, self.servo, self.name, self.color, self.shape)


class Methods:
    def __init__(self, ID, Method):
        self.id = ID
        self.method = Method

        def __repr__(self):
            return "Methods('{}', '{}')".format(self.id, self.method)


class Units:
    def __init__(self, ID, Unit):
        self.id = ID
        self.unit = Unit

        def __repr__(self):
            return "Units('{}', '{}')".format(self.id, self.unit)


class DoseForms:
    def __init__(self, ID, DoseForm):
        self.id = ID
        self.dose = DoseForm

        def __repr__(self):
            return "DoseForms('{}', '{}')".format(self.id, self.dose)


class ModeOfDeliverys:
    def __init__(self, ID, ModeofDelivery):
        self.id = ID
        self.delivery = ModeofDelivery

        def __repr__(self):
            return "ModeOfDeliverys('{}', '{}')".format(self.id, self.delivery)


class Times:
    def __init__(self, ID, Timing):
        self.id = ID
        self.time = Timing

        def __repr__(self):
            return "Times('{}', '{}')".format(self.id, self.time)


class Qualifiers:
    def __init__(self, ID,  Qualifier):
        self.id = ID
        self.qualifier = Qualifier

        def __repr__(self):
            return "Qualifiers('{}', '{}')".format(self.id, self.qualifier)

