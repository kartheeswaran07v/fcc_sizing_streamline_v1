import datetime
from flask_sqlalchemy import SQLAlchemy
from flask import Flask, render_template, redirect, url_for, flash, request, jsonify
from sqlalchemy import Column, Integer, ForeignKey, String, Boolean, DateTime, Float, or_
from sqlalchemy.orm import relationship
from sqlalchemy.orm.exc import DetachedInstanceError
import math
import csv
from flask_login import UserMixin, login_user, LoginManager, login_required, current_user, logout_user
import pandas
from formulae import *

# -----------^^^^^^^^^^^^^^----------------- IMPORT STATEMENTS -----------------^^^^^^^^^^^^^------------ #


## Constants
# todo = Constants
N5_mm = 0.00241  # in mm
N5_in = 1000
N6_kghr_kPa_kgm3 = 2.73
N6_kghr_bar_kgm3 = 27.3
N6_lbhr_psi_lbft3 = 63.3
N7_O_m3hr_kPa_C = 3.94  # input in Kelvin
N7_0_m3hr_bar_C = 394
N7_155_m3hr_kPa_C = 4.17
N7_155_m3hr_bar_C = 417
N7_60_scfh_psi_F = 1360  # input in R
N8_kghr_kPa_K = 0.498
N8_kghr_bar_K = 94.8
N8_lbhr_psi_K = 19.3
N9_O_m3hr_kPa_C = 21.2  # input in Kelvin
N9_0_m3hr_bar_C = 2120
N9_155_m3hr_kPa_C = 22.4
N9_155_m3hr_bar_C = 2240
N9_60_scfh_psi_F = 7320  # input in R

N1 = {('m3/hr', 'kpa'): 0.0865, ('m3/hr', 'bar'): 0.865, ('gpm', 'psia'): 1}
N2 = {'mm': 0.00214, 'inch': 890}
N4 = {('m3/hr', 'mm'): 76000, ('gpm', 'inch'): 173000}

ACCURACY = 0.001

# app configuration
app = Flask(__name__)

app.config['SECRET_KEY'] = "kkkkk"

# CONNECT TO DB
# app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get("DATABASE_URL", "sqlite:///dfx_db_seis.db")
app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///fcc_filled_db_v2.db"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)


# db = SQLAlchemy(app, session_options{
#     'expire_on_commit': False
# })


# TODO ------------------------------------------ DB TABLE CREATION --------------------------------------- #

# CREATE TABLE IN DB
# class User(UserMixin, db.Model):
#     __tablename__ = "Users"
#     id = Column(Integer, primary_key=True)
#     email = Column(String(100), unique=True)
#     password = Column(String(100))
#     name = Column(String(1000))
#
#     # relationships
#     # TODO 1 - Employee Master
#     employee = relationship("employeeMaster", back_populates="user")
#     # TODO 2 - roster Master
#     roster = relationship("rosterMaster", back_populates="user")
#     # TODO 3 - Time sheet master
#     timesheet = relationship("timesheetMaster", back_populates="user")
#     # TODO 4 - Leave Appln Master
#     leave = relationship("leaveApplicationMaster", back_populates="user")
#     # TODO 5 - Passport Appln Master
#     passport = relationship("passportApplicationMaster", back_populates="user")
#


# 1
class projectMaster(db.Model):
    __tablename__ = "projectMaster"
    id = Column(Integer, primary_key=True)
    quote = Column(Integer)
    received_date = Column(DateTime)
    work_order = Column(Integer)
    due_date = Column(DateTime)
    # relationship as parent
    item = relationship("itemMaster", back_populates="project")
    # relationship as child
    # TODO - Industry
    IndustryId = Column(Integer, ForeignKey("industryMaster.id"))
    industry = relationship("industryMaster", back_populates="project")
    # TODO - Region
    regionID = Column(Integer, ForeignKey("regionMaster.id"))
    region = relationship("regionMaster", back_populates="project")
    # TODO - Status
    statusID = Column(Integer, ForeignKey("statusMaster.id"))
    status = relationship("statusMaster", back_populates="project")
    # TODO - Customer
    customerID = Column(Integer, ForeignKey("customerMaster.id"))
    customer = relationship("customerMaster", back_populates="project")
    # TODO - Engineer
    engineerID = Column(Integer, ForeignKey("engineerMaster.id"))
    engineer = relationship("engineerMaster", back_populates="project")


# 2
class industryMaster(db.Model):  # TODO - Paandi ----- Done
    __tablename__ = "industryMaster"
    id = Column(Integer, primary_key=True)
    name = Column(String(300))

    # relationship as parent
    project = relationship("projectMaster", back_populates="industry")


# 3
class regionMaster(db.Model):  # TODO - Paandi  ------ Done
    __tablename__ = "regionMaster"
    id = Column(Integer, primary_key=True)
    name = Column(String(300))

    # relationship as parent
    project = relationship("projectMaster", back_populates="region")


# 4
class statusMaster(db.Model):  # TODO - Paandi     --------Done
    __tablename__ = "statusMaster"
    id = Column(Integer, primary_key=True)
    name = Column(String(300))

    # relationship as parent
    project = relationship("projectMaster", back_populates="status")


# 5
class customerMaster(db.Model):  # TODO - Paandi
    __tablename__ = "customerMaster"
    id = Column(Integer, primary_key=True)
    name = Column(String(300))

    # relationship as parent
    project = relationship("projectMaster", back_populates="customer")


# 6
class engineerMaster(db.Model):  # TODO - Paandi
    __tablename__ = "engineerMaster"
    id = Column(Integer, primary_key=True)
    name = Column(String(300))

    # relationship as parent
    project = relationship("projectMaster", back_populates="engineer")


# 7
class itemMaster(db.Model):
    __tablename__ = "itemMaster"
    id = Column(Integer, primary_key=True)
    alt = Column(String(300))
    tag_no = Column(String(300))
    unit_price = Column(String(300))
    qty = Column(String(300))
    # relationship as parent
    cases = relationship("itemCases", back_populates="item")
    valveDetails = relationship("valveDetails", back_populates="item")
    # relationship as child
    # TODO - Project
    projectID = Column(Integer, ForeignKey("projectMaster.id"))
    project = relationship("projectMaster", back_populates="item")
    # TODO - Serial
    serialID = Column(Integer, ForeignKey("valveSeries.id"))
    serial = relationship("valveSeries", back_populates="item")
    # TODO - Size
    sizeID = Column(Integer, ForeignKey("valveSize.id"))
    size = relationship("valveSize", back_populates="item")
    # TODO - Model
    modelID = Column(Integer, ForeignKey("modelMaster.id"))
    model = relationship("modelMaster", back_populates="item")
    # TODO - Type
    typeID = Column(Integer, ForeignKey("valveStyle.id"))
    type = relationship("valveStyle", back_populates="item")
    # TODO - Rating
    ratingID = Column(Integer, ForeignKey("rating.id"))
    rating = relationship("rating", back_populates="item")
    # TODO - Material
    materialID = Column(Integer, ForeignKey("materialMaster.id"))
    material = relationship("materialMaster", back_populates="item")


# 8
class modelMaster(db.Model):  # TODO - Paandi
    __tablename__ = "modelMaster"
    id = Column(Integer, primary_key=True)
    name = Column(String(300))

    # relationship as master
    item = relationship("itemMaster", back_populates="model")


# 9
class valveSeries(db.Model):  # TODO - Paandi        -------Done
    __tablename__ = "valveSeries"
    id = Column(Integer, primary_key=True)
    name = Column(String(300))

    # relationship as master
    item = relationship("itemMaster", back_populates="serial")


# 10
class valveStyle(db.Model):  # TODO - Paandi
    __tablename__ = "valveStyle"
    id = Column(Integer, primary_key=True)
    name = Column(String(300))

    # relationship as master
    item = relationship("itemMaster", back_populates="type")


# 11
class valveSize(db.Model):  # TODO - Paandi
    __tablename__ = "valveSize"
    id = Column(Integer, primary_key=True)
    size = Column(Integer)  # in inches

    # relationship as master
    item = relationship("itemMaster", back_populates="size")


# 12
class rating(db.Model):  # TODO - Paandi
    __tablename__ = "rating"
    id = Column(Integer, primary_key=True)
    size = Column(Integer)  # in inches

    # relationship as master
    item = relationship("itemMaster", back_populates="rating")


# 13
class materialMaster(db.Model):
    __tablename__ = "materialMaster"
    id = Column(Integer, primary_key=True)
    name = Column(String(300))
    max_temp = Column(Integer)
    min_temp = Column(Integer)

    # relationship as master
    item = relationship("itemMaster", back_populates="material")


# 13A
class itemCases(db.Model):
    __tablename__ = "itemCases"
    id = Column(Integer, primary_key=True)
    flowrate = Column(Integer)
    iPressure = Column(Integer)
    oPressure = Column(Integer)
    iTemp = Column(Integer)
    sGravity = Column(Integer)
    vPressure = Column(Integer)
    viscosity = Column(Integer)
    vaporMW = Column(Integer)
    vaporInlet = Column(Integer)
    vaporOutlet = Column(Integer)
    CV = Column(Integer)
    openPercent = Column(Integer)
    valveSPL = Column(Integer)
    iVelocity = Column(Integer)
    oVelocity = Column(Integer)
    pVelocity = Column(Integer)
    chokedDrop = Column(Integer)
    Xt = Column(Integer)
    warning = Column(Integer)
    trimExVelocity = Column(Integer)
    sigmaMR = Column(Integer)
    reqStage = Column(Integer)
    fluidName = Column(Integer)
    fluidState = Column(Integer)
    criticalPressure = Column(Integer)
    iPipeSize = Column(Integer)
    iPipeSizeSch = Column(Integer)
    oPipeSize = Column(Integer)
    oPipeSizeSch = Column(Integer)

    # relationship as child
    itemID = Column(Integer, ForeignKey("itemMaster.id"))
    item = relationship("itemMaster", back_populates="cases")


# 13B
class valveDetails(db.Model):
    __tablename__ = "valveDetails"
    id = Column(Integer, primary_key=True)
    # Valve Identification
    tag = Column(String(300))
    quantity = Column(Integer)
    application = Column(String(300))
    serial_no = Column(Integer)

    # Pressure Temp rating
    rating = Column(String(300))
    body_material = Column(String(300))
    shutOffDelP = Column(Integer)
    maxPressure = Column(Integer)
    maxTemp = Column(Integer)
    minTemp = Column(Integer)

    # Valve Selection
    valve_series = Column(String(300))
    valve_size = Column(Integer)
    rating_v = Column(String(300))
    ratedCV = Column(Integer)
    endConnection_v = Column(String(300))
    endFinish_v = Column(String(300))
    bonnetType_v = Column(String(300))
    bonnetExtDimension = Column(String(300))
    packingType_v = Column(String(300))
    trimType_v = Column(String(300))
    flowCharacter_v = Column(String(300))
    flowDirection_v = Column(String(300))
    seatLeakageClass_v = Column(String(300))

    # Material Selection
    body_v = Column(String(300))
    bonnet_v = Column(String(300))
    nde1 = Column(String(300))
    nde2 = Column(String(300))
    plug = Column(String(300))
    stem = Column(String(300))
    seat = Column(String(300))
    cage_clamp = Column(String(300))
    balanceScale = Column(String(300))
    packing = Column(String(300))
    stud_nut = Column(String(300))
    gasket = Column(String(300))

    # relationship as child
    itemID = Column(Integer, ForeignKey("itemMaster.id"))
    item = relationship("itemMaster", back_populates="valveDetails")


# 14
class standardMaster(db.Model):  # TODO - Paandi    ----------Done
    __tablename__ = "standardMaster"
    id = Column(Integer, primary_key=True)
    name = Column(String(300))


# 15
class fluidType(db.Model):  # TODO - Paandi     -------Done
    __tablename__ = "fluidType"
    id = Column(Integer, primary_key=True)
    name = Column(String(300))


# 16
class applicationMaster(db.Model):  # TODO - Paandi    -----------Done
    __tablename__ = "applicationMaster"
    id = Column(Integer, primary_key=True)
    name = Column(String(300))


# 17 - rated cv - to be integrated

# 18
class endConnection(db.Model):  # TODO - Paandi    ----------Done
    __tablename__ = "endConnection"
    id = Column(Integer, primary_key=True)
    name = Column(String(300))


# 19
class endFinish(db.Model):  # TODO - Paandi      -------------Done
    __tablename__ = "endFinish"
    id = Column(Integer, primary_key=True)
    name = Column(String(300))


# 20
class bonnetType(db.Model):  # TODO - Paandi  -----------------Done
    __tablename__ = "bonnetType"
    id = Column(Integer, primary_key=True)
    name = Column(String(300))


# 21
class packingType(db.Model):  # TODO - Paandi
    __tablename__ = "packingType"
    id = Column(Integer, primary_key=True)
    name = Column(String(300))


# 21A
class packingMaterial(db.Model):  # TODO - Paandi     -----------Done
    __tablename__ = "packingMaterial"
    id = Column(Integer, primary_key=True)
    name = Column(String(300))


# 22
class trimType(db.Model):  # TODO - Paandi  -----------Done
    __tablename__ = "trimType"
    id = Column(Integer, primary_key=True)
    name = Column(String(300))


# 23
class flowDirection(db.Model):  # TODO - Paandi  ............Done
    __tablename__ = "flowDirections"
    id = Column(Integer, primary_key=True)
    name = Column(String(300))


# 24
class seatLeakageClass(db.Model):  # TODO - Paandi    ..........Done
    __tablename__ = "seatLeakageClass"
    id = Column(Integer, primary_key=True)
    name = Column(String(300))


# 25
class bodyBonnet(db.Model):  # NDE  # TODO - Paandi
    __tablename__ = "bodyBonnet"
    id = Column(Integer, primary_key=True)
    name = Column(String(300))


# 26
class softPartsMaterial(db.Model):  # TODO - Paandi            ................Done
    __tablename__ = "softPartsMaterial"
    id = Column(Integer, primary_key=True)
    name = Column(String(300))


# 27
class fluidName(db.Model):  # TODO - Paandi          ----------------Done
    __tablename__ = "fluidName"
    id = Column(Integer, primary_key=True)
    name = Column(String(300))


# 28
class valveBalancing(db.Model):  # TODO - Paandi      --------------Done
    __tablename__ = "valveBalancing"
    id = Column(Integer, primary_key=True)
    name = Column(String(300))


# 29
class actuatorSeries(db.Model):  # TODO - Paandi          __________Done
    __tablename__ = "actuatorSeries"
    id = Column(Integer, primary_key=True)
    name = Column(String(300))


# 30
class actuatorSize(db.Model):  # TODO - Paandi
    __tablename__ = "actuatorSize"
    id = Column(Integer, primary_key=True)
    name = Column(String(300))


# 31
class handweel(db.Model):  # TODO - Paandi        ..........Done
    __tablename__ = "handweel"
    id = Column(Integer, primary_key=True)
    name = Column(String(300))


# 32
class travelStops(db.Model):  # TODO - Paandi       .............Done
    __tablename__ = "travelStops"
    id = Column(Integer, primary_key=True)
    name = Column(String(300))


# 33
class butterflyTable(db.Model):
    __tablename__ = "butterflyTable"
    id = Column(Integer, primary_key=True)
    typeID = Column(Integer)  # double or triple offset
    ratingID = Column(Integer)  # 150, 300, 600
    coeffID = Column(Integer)  # Cv, FL, Xt, FD
    size = Column(Integer)  # 3-30
    one = Column(Integer)  # All below are opening percentage
    two = Column(Integer)
    three = Column(Integer)
    four = Column(Integer)
    five = Column(Integer)
    six = Column(Integer)
    seven = Column(Integer)
    eight = Column(Integer)
    nine = Column(Integer)


# 34
class globeTable(db.Model):  # series 1000
    __tablename__ = "globeTable"
    id = Column(Integer, primary_key=True)
    trimTypeID = Column(Integer)  # Microspline, contoured, ported, mhc-1
    flow = Column(Integer)  # over, under, both
    coeffID = Column(Integer)  # Cv, FL, Xt, FD
    size = Column(Integer)  # 1-24
    charac = Column(Integer)  # linear, equal%
    one = Column(Integer)  # All below are opening percentage
    two = Column(Integer)
    three = Column(Integer)
    four = Column(Integer)
    five = Column(Integer)
    six = Column(Integer)
    seven = Column(Integer)
    eight = Column(Integer)
    nine = Column(Integer)
    ten = Column(Integer)


# 35
class schedule(db.Model):  # TODO - Paandi      ----------Done
    __tablename__ = "schedule"
    id = Column(Integer, primary_key=True)
    name = Column(String(300))


# 36
class failAction(db.Model):  # TODO - Paandi  ----------Done
    __tablename__ = "failAction"
    id = Column(Integer, primary_key=True)
    name = Column(String(300))


# 37
class positionerMakeModel(db.Model):  # TODO - Paandi  ................Done
    __tablename__ = "positionerMakeModel"
    id = Column(Integer, primary_key=True)
    name = Column(String(300))


# 38
class airset(db.Model):  # TODO - Paandi           ................Done
    __tablename__ = "airset"
    id = Column(Integer, primary_key=True)
    name = Column(String(300))


# 39
class solenoidValve(db.Model):  # TODO - Paandi     ............Done
    __tablename__ = "solenoidValve"
    id = Column(Integer, primary_key=True)
    name = Column(String(300))


# 40
class lockValve(db.Model):  # TODO - Paandi          ............done
    __tablename__ = "lockValve"
    id = Column(Integer, primary_key=True)
    name = Column(String(300))


# 41
class qevBoosters(db.Model):  # TODO - Paandi        ...........Done
    __tablename__ = "qevBoosters"
    id = Column(Integer, primary_key=True)
    name = Column(String(300))


# 42
class pilotValve(db.Model):  # TODO - Paandi       ...........Done
    __tablename__ = "pilotValve"
    id = Column(Integer, primary_key=True)
    name = Column(String(300))


# 43
class switchPosition(db.Model):  # TODO - Paandi        ........DOne
    __tablename__ = "switchPosition"
    id = Column(Integer, primary_key=True)
    name = Column(String(300))


# 44
class IPConverter(db.Model):  # TODO - Paandi        -----------Done
    __tablename__ = "IPConverter"
    id = Column(Integer, primary_key=True)
    name = Column(String(300))


# 45
class airReceiver(db.Model):  # TODO - Paandi       ------------Done
    __tablename__ = "sirReceiver"
    id = Column(Integer, primary_key=True)
    name = Column(String(300))


# 46
class tubing(db.Model):  # TODO - Paandi            ----------------Done
    __tablename__ = "tubing"
    id = Column(Integer, primary_key=True)
    name = Column(String(300))


# 47
class fittings(db.Model):  # TODO - Paandi     ---------------Done
    __tablename__ = "fittings"
    id = Column(Integer, primary_key=True)
    name = Column(String(300))


# 48
class cleaning(db.Model):  # TODO - Paandi     .....................Done
    __tablename__ = "cleaning"
    id = Column(Integer, primary_key=True)
    name = Column(String(300))


# 49
class certification(db.Model):  # TODO - Paandi          --------------Done
    __tablename__ = "certification"
    id = Column(Integer, primary_key=True)
    name = Column(String(300))


# 50
class paintFinish(db.Model):  # TODO - Paandi       -------------------Done

    __tablename__ = "paintFinish"
    id = Column(Integer, primary_key=True)
    name = Column(String(300))


# 51
class paintCerts(db.Model):  # TODO - Paandi        .................Done

    __tablename__ = "paintCerts"
    id = Column(Integer, primary_key=True)
    name = Column(String(300))


# #
# with app.app_context():
#     db.create_all()

# TODO ------------------------------------------ DATA INPUT TO THE DATABASE --------------------------------------- #
with app.app_context():
    # projects
    industry_element_1 = industryMaster.query.get(16)
    region_element_1 = regionMaster.query.get(2)
    status_element_1 = statusMaster.query.get(6)
    customer_element_1 = customerMaster.query.get(1)
    engineer_element_1 = engineerMaster.query.get(2)
    industry_element_2 = industryMaster.query.get(1)
    region_element_2 = regionMaster.query.get(1)
    status_element_2 = statusMaster.query.get(1)
    customer_element_2 = customerMaster.query.get(2)
    engineer_element_2 = engineerMaster.query.get(3)

    # items
    # 1
    project_element_1 = projectMaster.query.get(1)
    valve_series_element_1 = valveSeries.query.get(1)
    valve_size_element_1 = valveSize.query.get(1)
    model_element_1 = modelMaster.query.get(1)
    type_element_1 = valveStyle.query.get(1)
    rating_element_1 = rating.query.get(1)
    material_element_1 = materialMaster.query.get(2)
    # 2
    project_element_2 = projectMaster.query.get(2)
    valve_series_element_2 = valveSeries.query.get(2)
    valve_size_element_2 = valveSize.query.get(5)
    model_element_2 = modelMaster.query.get(3)
    type_element_2 = valveStyle.query.get(2)
    rating_element_2 = rating.query.get(3)
    material_element_2 = materialMaster.query.get(6)
    # 3
    valve_size_element_3 = valveSize.query.get(4)
    rating_element_3 = rating.query.get(2)

project2 = {"Industry": industry_element_1, "Region": region_element_1, "Qoute": 502, "Status": status_element_1,
            "Customer": customer_element_1, "Enquiry": 000,
            "received": datetime.datetime.today().date(), "Engineer": engineer_element_1,
            "Due Date": datetime.datetime.today().date(),
            "WorkOrder": 000}
project1 = {"Industry": industry_element_2, "Region": region_element_2, "Qoute": 501, "Status": status_element_2,
            "Customer": customer_element_2, "Enquiry": 000,
            "received": datetime.datetime.today().date(), "Engineer": engineer_element_2,
            "Due Date": datetime.datetime.today().date(),
            "WorkOrder": 000}
projectsList = [project1, project2]

# # add projects to db
# for i in projectsList:
#     new_project = projectMaster(industry=i['Industry'], region=i['Region'], quote=i['Qoute'], status=i['Status'],
#                                 customer=i['Customer'],
#                                 received_date=i['received'],
#                                 engineer=i['Engineer'],
#                                 work_order=i['WorkOrder'],
#                                 due_date=i['Due Date'])
#     with app.app_context():
#         db.session.add(new_project)
#         db.session.commit()


# add items in projects

item1 = {"alt": 'A', "tagNo": 101, "serial": valve_series_element_1, "size": valve_size_element_1,
         "model": model_element_1, "type": type_element_1, "rating": rating_element_1,
         "material": material_element_1, "unitPrice": 1, "Quantity": 2, "Project": project_element_1}
item2 = {"alt": 'A', "tagNo": 102, "serial": valve_series_element_2, "size": valve_size_element_2,
         "model": model_element_2, "type": type_element_2, "rating": rating_element_2,
         "material": material_element_2, "unitPrice": 3, "Quantity": 4, "Project": project_element_2}
item3 = {"alt": 'A', "tagNo": 102, "serial": valve_series_element_2, "size": valve_size_element_3,
         "model": model_element_2, "type": type_element_1, "rating": rating_element_3,
         "material": material_element_2, "unitPrice": 3, "Quantity": 4, "Project": project_element_2}

itemsList = [item3]
#
# for i in itemsList:
#     new_item = itemMaster(alt=i['alt'], tag_no=i['tagNo'], serial=i['serial'], size=i['size'], model=i['model'],
#                           type=i['type'], rating=i['rating'], material=i['material'], unit_price=i['unitPrice'],
#                           qty=i['Quantity'], project=i['Project'])
#     with app.app_context():
#         db.session.add(new_item)
#         db.session.commit()

# add csv globe data to db
filename = "globe1000s.csv"
fields = []
rows = []

# reading csv file
with open(filename, 'r') as csvfile:
    # creating a csv reader object
    csvreader = csv.reader(csvfile)

    # extracting field names through first row
    fields = next(csvreader)

    # extracting each data row one by one
    for row in csvreader:
        rows.append(row)

# for row in rows:
#     new_entry_globe = globeTable(trimTypeID=row[0], flow=row[1], charac=row[2], size=row[3], coeffID=row[4],
#                                  one=row[5],
#                                  two=row[6],
#                                  three=row[7],
#                                  four=row[8],
#                                  five=row[9],
#                                  six=row[10],
#                                  seven=row[11],
#                                  eight=row[12],
#                                  nine=row[13],
#                                  ten=row[14])
#     with app.app_context():
#         db.session.add(new_entry_globe)
#         db.session.commit()


# add csv globe data to db
filename_c = "materials_meta.csv"
fields_c = []
rows_c = []

# materials csv
with open(filename_c, 'r') as csvfile:
    # creating a csv reader object
    csvreader = csv.reader(csvfile)

    # extracting field names through first row
    fields_c = next(csvreader)

    # extracting each data row one by one
    for row in csvreader:
        rows_c.append(row)

# for row in rows_c:
#     new_material = materialMaster(name=row[0], max_temp=row[1], min_temp=row[2])
#
#     with app.app_context():
#         db.session.add(new_material)
#         db.session.commit()


seat_list = ['Water', 'Gas', 'Vapor']

# for seat in seat_list:
#     new_seat_data = seatLeakageClass(name='seat')
#     with app.app_context():
#         db.session.add(new_seat_data)
#         db.session.commit()

# add csv butterfly data to db
filename_b = "butterfly.csv"
fields_b = []
rows_b = []

# reading csv file
with open(filename_b, 'r') as csvfile:
    # creating a csv reader object
    csvreader = csv.reader(csvfile)

    # extracting field names through first row
    fields_b = next(csvreader)

    # extracting each data row one by one
    for row in csvreader:
        rows_b.append(row)


#
# for row in rows_b:
#     new_entry_butterfly = butterflyTable(typeID=row[0], ratingID=row[1], coeffID=row[2], size=row[3],
#                                          one=row[4],
#                                          two=row[5],
#                                          three=row[6],
#                                          four=row[7],
#                                          five=row[8],
#                                          six=row[9],
#                                          seven=row[10],
#                                          eight=row[11],
#                                          nine=row[12])
#     with app.app_context():
#         db.session.add(new_entry_butterfly)
#         db.session.commit()

# TODO - For Paandi - Write the python codes here

# Todo - 1 - Example code for you!
#
# seat_list = ['Water', 'Gas', 'Vapor']
#
# for seat in seat_list:
#     new_seat_data = seatLeakageClass(name=seat)
#     with app.app_context():
#         db.session.add(new_seat_data)
#         db.session.commit()
#
# # use the list here with the correct name convention: list_*the table name*
# list_industry = ['Agriculture', 'Chemical', 'Drink', 'Food', 'Gas Transport / Distribution', 'Heating and Ventilation',
#                  'Industrial Gas Production', 'Iron & Steel Production', 'Marine', 'Minig', 'Miscellaneous',
#                  'Oil & Gas Production Offshore', 'Oil & Gas Production Onshore', 'OEM', 'Paper & Board',
#                  'Petrochemical']
# # use the for loop given, the table name should match, other wise it is a waste. Comment after running the code.
# for i in list_industry:
#     new_industry = industryMaster(name=i)
#     with app.app_context():
#         db.session.add(new_industry)
#         db.session.commit()
#
# list_region = ['Europe', 'Asia', 'Middle East', 'Western Countries']
#
# for i in list_region:
#     new_region = regionMaster(name=i)
#     with app.app_context():
#         db.session.add(new_region)
#         db.session.commit()
#
# list_Status = ['Live', 'Own ', 'Lost', 'Dead', 'Declined', 'New', 'Quoted', 'Pending']
#
# for i in list_Status:
#     new_status = statusMaster(name=i)
#     with app.app_context():
#         db.session.add(new_status)
#         db.session.commit()
#
# list_Series = ['10000', '10000', '30000', '30000', '40000']
#
# for i in list_Series:
#     new_series = valveSeries(name=i)
#     with app.app_context():
#         db.session.add(new_series)
#         db.session.commit()
#
# list_Standard_Name = ['ASME', 'API']
#
# for i in list_Standard_Name:
#     new_standard = standardMaster(name=i)
#     with app.app_context():
#         db.session.add(new_standard)
#         db.session.commit()
#
# list_Fluid_Type = ['Water', 'Gas', 'Vapor']
#
# for i in list_Fluid_Type:
#     new_fluidtype = fluidType(name=i)
#     with app.app_context():
#         db.session.add(new_fluidtype)
#         db.session.commit()
#
# list_Application = ['Temperature Control ', 'Pressure Control', 'Flow Control', 'Level Control', 'Compressor Re-cycle',
#                     'Compressor Anti-Surge', 'Cold Box Service', 'Condenste Service', 'Cryogenic Service',
#                     'Desuperheater Service', 'Feedwater Service', 'Heater Drain', 'High P & T Steam',
#                     'Hydrogen / He. Service', 'Joule Thompson Valve', 'L.N.G Service', 'Soot Blower Valve',
#                     'Spraywater Valve', 'Switching Valve']
# for i in list_Application:
#     new_application = applicationMaster(name=i)
#     with app.app_context():
#         db.session.add(new_application)
#         db.session.commit()
#
# list_End_Connection_Option = ['None', 'Integral Flange', 'Loose Flange', 'Flange (Drilled ASME 150)', 'Screwed NPT',
#                               'Screwed BSPT', 'Screwed BSP', 'Socket Weld', 'Butt Weld', 'Grayloc Hub',
#                               'Vector / Techlok Hub', 'Destec Hub', 'Galperti Hub', 'BW Stubs', 'Plain Stubs',
#                               'Drilled Lug', 'Tapped Lug', 'BW Stubs Sch 10', 'BW Stubs Sch 40', 'BW Stubs Sch 80']
# for i in list_End_Connection_Option:
#     new_Connection = endConnection(name=i)
#     with app.app_context():
#         db.session.add(new_Connection)
#         db.session.commit()
#
# list_End_Finish = ['N/A', 'RF Serrated', 'RF (125 -250AARH) 3.2-6.3um', 'RF(63-125AARH)1.6-3.2um', 'FF Serrated',
#                    'FF (125 -250AARH) 3.2-6.3um', 'FF(63-125AARH)1.6-3.2um', 'RTJ', 'ASME B16.25 Fig.2a']
# #
# for i in list_End_Finish:
#     new_Finish = endFinish(name=i)
#     with app.app_context():
#         db.session.add(new_Finish)
#         db.session.commit()
#
# list_Bonnet_Type = ['Standard', 'Standard Extension', 'Normalized / Finned', 'Bellow Seal', 'Cyrogenic',
#                     'Cyrogenic +Drip Plate', 'Cyrogenic + Seal Boot', 'Cyrogenic + Cold Box Flange']
# for i in list_Bonnet_Type:
#     new_bonnetType = bonnetType(name=i)
#     with app.app_context():
#         db.session.add(new_bonnetType)
#         db.session.commit()
#
# list_Packing_Material = ['Graphite / Ceramic', 'Graphite / Ni-Resist', 'Graphite / DU Glacier',
#                          'Graphite / DUB Glacier', 'Graphite / MP2', 'Graphite / MP3', 'Graphite / 316-Armaloy',
#                          'Graphite / Stellite', 'Graphite / N.60-Armaloy', 'High Integrity Gland', 'HIG Supagraf',
#                          'PTFE Chevron', 'PTFE Braid', 'High Intensity Gland', 'Graphite']
# for i in list_Packing_Material:
#     new_packingMaterial = packingMaterial(name=i)
#     with app.app_context():
#         db.session.add(new_packingMaterial)
#         db.session.commit()
#
# list_Trim_Type = ['Modified', 'Microspline', 'Contoured', 'Ported', 'MHC-1']
# for i in list_Trim_Type:
#     new_trimTyp = trimType(name=i)
#     with app.app_context():
#         db.session.add(new_trimTyp)
#         db.session.commit()
#
# list_Flow_Direction = ['Seat Downstream''Seat Upstream']
#
# for i in list_Flow_Direction:
#     new_flowDirection = flowDirection(name=i)
#     with app.app_context():
#         db.session.add(new_flowDirection)
#         db.session.commit()
#
# List_Seat_Leakage_Class = ['ANSI Class III', 'ANSI Class IV', 'ANSI Class V', 'ANSI Class VI']
#
# for i in List_Seat_Leakage_Class:
#     new_seatLeakageClass = seatLeakageClass(name=i)
#     with app.app_context():
#         db.session.add(new_seatLeakageClass)
#         db.session.commit()
#
# list_Soft_Parts_Material = ['Standard for Service', 'PTFE', 'PCTFE (KEL-F)', 'Spiral Wound 316L/Graph',
#                             'Spiral Wound 316L/PTFE', 'Spiral Wound 31803/Graph', 'Spiral Wound 31803/PTFE',
#                             'Spiral Wound 32760/Graph', 'Spiral Wound 32760/PTFE', 'Spiral Wound 625/Graph',
#                             'Spiral Wound 625/PTFE', 'Graphite', 'Metal Seal', 'Double ABS (cryo)']
#
# for i in list_Soft_Parts_Material:
#     new_softPartsMaterial = softPartsMaterial(name=i)
#     with app.app_context():
#         db.session.add(new_softPartsMaterial)
#         db.session.commit()
#
# list_Fluid_Name = ['Acetic Acid', 'Acetic Anhydride', 'Acetone', 'Acetylene', 'Acrylic Acid', 'Air', 'Ammonia', 'Argon',
#                    'Benzene', 'Bromine', 'Butadiene 1,3', 'Butane', 'Butyl Alcohol', 'Carbon Dixide ',
#                    'Carbon monoxide', 'Carbon Tetrachloride', 'Chlorine Dry', 'chlorine Wet', 'Demin.Water',
#                    'Dowtherm A', 'Ethane', 'Ethyl Alcohol', 'Ethylene', 'Helium', 'Heptane', 'Hexane',
#                    'hydrocarbon Gas', 'Hydrocarbon Liquid', 'Hydrogen', 'hydrogen Chloride', 'Hydrogen Fluoride',
#                    'Hydrogen Sulphide', 'Isopropyl Alcohol', 'Methane', 'Methyle Alcohol', 'Methyle Chloride',
#                    'Natural Gas', 'Nitrogen', 'Octane', 'Oxygen', 'Pentance', 'Phenol', 'Propene', 'Propyl Alchohol',
#                    'Propyl Chloride', 'Propylene', 'Pyridine', 'Refrigerant 12', 'Refrigerant 22', 'Sea Water', 'Steam',
#                    'Sulphur Dioxide', 'Toluene', 'Water']
# for i in list_Fluid_Name:
#     new_fluidName = fluidName(name=i)
#     with app.app_context():
#         db.session.add(new_fluidName)
#         db.session.commit()
#
# list_Valve_Balancing = ['Unbalanced', 'PTFE Seal', 'Graphite']
# for i in list_Valve_Balancing:
#     new_valveBalancing = valveBalancing(name=i)
#     with app.app_context():
#         db.session.add(new_valveBalancing)
#         db.session.commit()
#
# list_Act_Series = ['N/A', 'Manual Gear Box', 'SD', 'PA', 'Scotch Yoke ', 'Electrical Actuator', 'Hydraulic Actuator',
#                    'Electro- Hydraulic Actuator']
# for i in list_Act_Series:
#     new_actuatorSeries = actuatorSeries(name=i)
#     with app.app_context():
#         db.session.add(new_actuatorSeries)
#         db.session.commit()
#
# list_Handwheel = ['None', 'Side Mounted Handwheel', 'Top Mounted Handwheel', 'Top Mtd. Jacking Screw',
#                   'Hydraulic Override']
# for i in list_Handwheel:
#     new_handweel = handweel(name=i)
#     with app.app_context():
#         db.session.add(new_handweel)
#         db.session.commit()
#
# list_Travel_Stops = ['None', 'Limit Opening', 'Limit Closing', 'Factory Standard']
#
# for i in list_Travel_Stops:
#     new_travelStops = travelStops(name=i)
#     with app.app_context():
#         db.session.add(new_travelStops)
#         db.session.commit()
#
# list_Schedule = ['5S', '10S', '40S', '80S', '10', '20', '30', '40', 'STD', '60', '80', 'XS', '100', '120', '140', '160',
#                  'XXS']
#
# for i in list_Schedule:
#     new_schedule = schedule(name=i)
#     with app.app_context():
#         db.session.add(new_schedule)
#         db.session.commit()
#
# list_Fail_Action = ['Modulating AFO', 'Modulating AFC', 'Modulating AFS', 'On/Off AFO', 'On/Off AFC', 'On/Off AFS']
#
# for i in list_Fail_Action:
#     new_failAction = failAction(name=i)
#     with app.app_context():
#         db.session.add(new_failAction)
#         db.session.commit()
#
# list_Positioner_make_model = ['None', 'Tissin ', 'Siemens Moore 760p', 'siemens PS2 HART', 'siemens PS2 F',
#                               'Metso ND9000 HART', 'Metso ND9000 F', 'Fisher DVC6200AC', 'Fisher DVC6200HC HART',
#                               'Fisher DVC6200AD HART', 'Fisher DVC6200PD HART', 'Fisher DVC 6200F-SCFD',
#                               'Fisher DVC 6200F-SCAD', 'Fisher DVC 6200F-SCPD', 'See Note']
#
# for i in list_Positioner_make_model:
#     new_positionerMakeModel = positionerMakeModel(name=i)
#     with app.app_context():
#         db.session.add(new_positionerMakeModel)
#         db.session.commit()
#
# # airset
# list_Airset = ['None', '1/4" NPT ControlAir 300', '1/4" NPT ControlAir 350 SS', '1/2" NPT ControlAir 350 SS',
#                '1/4"NPT AL.+SS Gauge', '1/2"NPT AL.+SS Gauge', '1/4"NPT 316SS + SS Gauge', '1/2"NPT 316SS + SS Gauge',
#                'See Note']
#
# for i in list_Airset:
#     new_airset = airset(name=i)
#     with app.app_context():
#         db.session.add(new_airset)
#         db.session.commit()
#
# list_Solenoid_Valve = ['None', '1/4" Asco 3/2 Br. IP66 Exd', '1/4" Asco 5/4 Br. IP66 Exd', '1/4" Asco 3/2 S/S IP66 Exd',
#                        '1/4" Asco 5/4 S/S IP66 Exd', '1/4" ICO4 3/2 S/S IP66 Exd', '1/4" ICO4  5/4 S/S IP66 Exd',
#                        '1/4" ICO3  3/2 S/S IP66 Exd', '1/4" ICO2  3/2 S/S IP66 Exi', '1/4" ICO2  5/4 S/S IP66 Exi']
#
# for i in list_Solenoid_Valve:
#     new_solenoidValve = solenoidValve(name=i)
#     with app.app_context():
#         db.session.add(new_solenoidValve)
#         db.session.commit()
#
# list_Lock_Valve = ['None', '164A AI.Alloy / Epoxy']
#
# for i in list_Lock_Valve:
#     new_lockValve = lockValve(name=i)
#     with app.app_context():
#         db.session.add(new_lockValve)
#         db.session.commit()
#
# list_Qev_Boosters = ['None', '1/4" NPT IB10 Al./Epoxy', '1/4"NPT IB10 S/S', '1/2" NPT IB10 Al./Epoxy',
#                      '1/2"NPT IB10 S/S', '3/4" NPT IB10 Al./Epoxy', '3/4"NPT IB10 S/S', '1/4"NPT.Q.E.AL/Epoxy',
#                      '1/4"NPT.Q.E. S/s', '1/2"NPT.Q.E.AL/Epoxy', '1/2"NPT.Q.E. S/s', '3/4"NPT.Q.E.AL/Epoxy',
#                      '3/4"NPT.Q.E. S/s']
#
# for i in list_Qev_Boosters:
#     new_qevBoosters = qevBoosters(name=i)
#     with app.app_context():
#         db.session.add(new_qevBoosters)
#         db.session.commit()
#
# list_Pilot_Valve = ['None', 'Versa 1/4" Brass', 'Versa 1/4" StSt', 'Versa 1/2" Brass', 'Versa 1/2" StSt',
#                     'Versa 3/4" brass', 'Mid.Pneu. 1/4" St.St.', 'Mid.Pneu. 1/2" St.St.', 'Mid.Pneu. 3/4" St.St.']
#
# for i in list_Pilot_Valve:
#     new_pilotValve = pilotValve(name=i)
#     with app.app_context():
#         db.session.add(new_pilotValve)
#         db.session.commit()
#
# list_Switch_Position = ['None', '4am=Closed, 20ma=Open', '4am=Open, 20ma=Close', 'Limit Switch Open&Closed',
#                         '4am=Closed. 20ma=Open', '4am=Open,.20ma=Close']
#
# for i in list_Switch_Position:
#     new_switchPosition = switchPosition(name=i)
#     with app.app_context():
#         db.session.add(new_switchPosition)
#         db.session.commit()
#
# list_IP_Converter = ['None', 'ABB AI.3-15psi IP65 Exia', 'ABB AI.0.2-1bar IP65 Exia', 'ABB AI.3-15psi IP65 Exd',
#                      'ABB AI.0.2-1bar IP65 Exd', 'ABB SS 3-15psi IP65 Exia', 'ABB SS 0.2-1psi IP65 Exia',
#                      'ABB SS 3-15psi IP65 Exd', 'ABB SS 0.2-1bar Ip65Exd']
#
# for i in list_IP_Converter:
#     new_IPConverter = IPConverter(name=i)
#     with app.app_context():
#         db.session.add(new_IPConverter)
#         db.session.commit()
#
# list_Air_Receiver = ['None', '113L ASME VIII St St Kit', '303L ASME VIII St St Kit', '50L BS EN286 Brass Kit',
#                      '113L BS EN286 Brass Kit', '50L BS EN286 St St Kit', '113L BS EN286 St St Kit', 'See note N7']
#
# for i in list_Air_Receiver:
#     new_airReceiver = airReceiver(name=i)
#     with app.app_context():
#         db.session.add(new_airReceiver)
#         db.session.commit()
#
# list_Tubing = ['None', 'Metric Copper', 'Metric PVC / Copper', 'metric 316L SS', 'Imperial Copper',
#                'Imperial PVC / Copper', 'Imperial 316L SS', 'Imperial 6Mo', 'Metric 6Mo', 'Imperial Super Duplex',
#                'Metric Super Duplex']
#
# for i in list_Tubing:
#     new_tubing = tubing(name=i)
#     with app.app_context():
#         db.session.add(new_tubing)
#         db.session.commit()
#
# list_Fittings = ['None', 'Wadelok Brass', 'Swagelok Brass', 'A-Lok SS', 'Swagelok SS', 'Gyrolok SS', 'Swagelok 6Mo',
#                  'Swagelok Super Dulex', 'Parker 6mo', 'Parker Super Duplex']
#
# for i in list_Fittings:
#     new_fittings = fittings(name=i)
#     with app.app_context():
#         db.session.add(new_fittings)
#         db.session.commit()
#
# list_Cleaning = ['Standard Workshop', 'Clean for Oxygen Service', 'Clean for Cryogenic', 'UHP(DS-153)']
#
# for i in list_Cleaning:
#     new_cleaning = cleaning(name=i)
#     with app.app_context():
#         db.session.add(new_cleaning)
#         db.session.commit()
#
# list_Certification = ['N/A', 'PED Mod H + ATEX', 'PED SEP H + ATEX', 'PED N/A + ATEX', 'PED Mod H + ATEX N?A',
#                       'PED SEP + ATEX N?A', 'See note ']
#
# for i in list_Certification:
#     new_certification = certification(name=i)
#     with app.app_context():
#         db.session.add(new_certification)
#         db.session.commit()
#
# list_Paint_Finish = ['None', 'Offshore', 'High Temp', 'Specification Standard', 'Colour Specification',
#                      'Customer Paint Spec.', 'See Note ']
#
# for i in list_Paint_Finish:
#     new_paintFinish = paintFinish(name=i)
#     with app.app_context():
#         db.session.add(new_paintFinish)
#         db.session.commit()
#
# list_Paint_Certs = ['None', 'Standard Mati Certs BFV', '3.1+NACE MR017/ISO15156', '3.1 Body,Disc,Shaft,Cover',
#                     'SHELL MESC SPE 77/302', 'NACE MR-01-75-2022, 3.1', 'NACE ISO 15156, 3.1',
#                     'MR-01-75+ISO 10204, 3.2', 'ISO 15156+ISO 10204 3.2', 'See note ']
#
# for i in list_Paint_Certs:
#     new_paintCerts = paintCerts(name=i)
#     with app.app_context():
#         db.session.add(new_paintCerts)
#         db.session.commit()
#
# eng_list = ['Divya', 'Nisha', 'Suraj', 'Veerapandi', 'Nishanth']
# for i in eng_list:
#     new_eng = engineerMaster(name=i)
#     with app.app_context():
#         db.session.add(new_eng)
#         db.session.commit()
#
# customer_list = ['Customer_1', 'Customer_2', 'Customer_3', 'Customer_4', 'Customer_5']
# for i in customer_list:
#     new_customer = customerMaster(name=i)
#     with app.app_context():
#         db.session.add(new_customer)
#         db.session.commit()
#
# valve_size_list = [1, 1.5, 2, 3, 4, 6, 8, 10, 12, 14, 16, 18, 20, 24, 30]
# model_list = ['Model_1', 'Model_2', 'Model_3']
#
# for i in valve_size_list:
#     new_size = valveSize(size=i)
#     with app.app_context():
#         db.session.add(new_size)
#         db.session.commit()
#
#
# for i in model_list:
#     new_model = modelMaster(name=i)
#     with app.app_context():
#         db.session.add(new_model)
#         db.session.commit()
#
# rating_list = [150, 300, 600, 900, 1500, 2500, 5000, 10000, 15000]
# for i in rating_list:
#     new_rating = rating(size=i)
#     with app.app_context():
#         db.session.add(new_rating)
#         db.session.commit()

def nothing():
    pass


# TODO ------------------------------------------ SIZING PYTHON CODE --------------------------------------- #


# Cv1 = Cv_butterfly_6
# FL1 = Fl_butterfly_6


# TODO - Liquid Sizing - fisher

def etaB(valveDia, pipeDia):
    return 1 - ((valveDia / pipeDia) ** 4)


def eta1(valveDia, pipeDia):
    return 0.5 * ((1 - ((valveDia / pipeDia) ** 2)) ** 2)


def eta2(valveDia, pipeDia):
    return 1 * ((1 - ((valveDia / pipeDia) ** 2)) ** 2)


def sigmaEta(valveDia, inletDia, outletDia):
    a_ = eta1(valveDia, inletDia) + eta2(valveDia, outletDia) + etaB(valveDia, inletDia) - etaB(valveDia, outletDia)
    return round(a_, 2)


def fP(C, valveDia, inletDia, outletDia, N2_value):
    a = (sigmaEta(valveDia, inletDia, outletDia) / N2_value) * ((C / valveDia ** 2) ** 2)
    b_ = 1 / math.sqrt(1 + a)
    return round(b_, 2)


def delPMax(Fl, Ff, inletPressure, vaporPressure):
    a_ = Fl * Fl * (inletPressure - (Ff * vaporPressure))
    return round(a_, 1)


def selectDelP(Fl, Ff, inletPressure, vaporPressure, outletPressure):
    a_ = delPMax(Fl, Ff, inletPressure, vaporPressure)
    b_ = inletPressure - outletPressure
    return min(a_, b_)


def Cvt(flowrate, N1_value, inletPressure, outletPressure, sGravity):
    a_ = N1_value * math.sqrt((inletPressure - outletPressure) / sGravity)
    b_ = flowrate / a_
    return round(b_)


def reynoldsNumber(N4_value, Fd, flowrate, viscosity, Fl, N2_value, pipeDia, N1_value, inletPressure, outletPressure,
                   sGravity):
    Cv_1 = Cvt(flowrate, N1_value, inletPressure, outletPressure, sGravity)
    print(Cv_1)
    a_ = (N4_value * Fd * flowrate) / (viscosity * math.sqrt(Fl * Cv_1))
    # print(a_)
    b_ = ((Fl * Cv_1) ** 2) / (N2_value * (pipeDia ** 4))
    c_ = (1 + b_) ** (1 / 4)
    d_ = a_ * c_
    return round(d_, 2)


# print(7600, 1, 300, 8000, 0.68, 0.00214, 80, 0.865, 8.01, 6.01, 0.908)


def CV(flowrate, C, valveDia, inletDia, outletDia, N2_value, inletPressure, outletPressure, sGravity, N1_value, FR,
       vaporPressure, Fl, Ff):
    delP = selectDelP(Fl, Ff, inletPressure, vaporPressure, outletPressure)
    print(delP)
    print(inletPressure, outletPressure)
    fp_val = fP(C, valveDia, inletDia, outletDia, N2_value)
    print(sGravity)
    a_ = N1_value * fp_val * FR * math.sqrt(delP / sGravity)
    b_ = flowrate / a_
    return round(b_, 1)


# TODO - GAS SIZING


def x_gas(inletPressure, outletPressure):
    result = (inletPressure - outletPressure) / inletPressure
    print(f"x value is: {round(result, 2)}")
    return round(result, 2)


def etaB_gas(valveDia, pipeDia):
    result = 1 - ((valveDia / pipeDia) ** 4)
    return round(result, 2)


def eta1_gas(valveDia, pipeDia):
    result = 0.5 * ((1 - ((valveDia / pipeDia) ** 2)) ** 2)
    return round(result, 2)


def eta2_gas(valveDia, pipeDia):
    result = 1 * ((1 - ((valveDia / pipeDia) ** 2)) ** 2)
    return round(result, 2)


def sigmaEta_gas(valveDia, inletDia, outletDia):
    result = eta1_gas(valveDia, inletDia) + eta2_gas(valveDia, outletDia) + etaB_gas(valveDia, inletDia) - etaB_gas(
        valveDia, outletDia)
    return round(result, 2)


def fP_gas(C, valveDia, inletDia, outletDia):
    a = (sigmaEta_gas(valveDia, inletDia, outletDia) / 890) * ((C / valveDia ** 2) ** 2)
    result = 1 / math.sqrt(1 + a)
    print(f"FP value is: {round(result, 2)}")
    return round(result, 2)


# specific heat ratio - gamma
def F_Gamma_gas(gamma):
    result = gamma / 1.4
    print(f"F-Gamma: {round(result, 2)}")
    return round(result, 2)


def xChoked_gas(gamma, C, valveDia, inletDia, outletDia, xT):
    f_gamma = F_Gamma_gas(gamma)
    if valveDia != inletDia:
        fp = fP_gas(C, valveDia, inletDia, outletDia)
        etaI = eta1_gas(valveDia, inletDia) + etaB_gas(valveDia, inletDia)
        print(f"etaI: {round(etaI, 2)}")
        a_ = xT / fp ** 2
        b_ = (xT * etaI * C * C) / (N5_in * (valveDia ** 4))
        xTP = a_ / (1 + b_)
        result = f_gamma * xTP
        print(f"xChoked1: {round(result, 2)}")
    else:
        result = f_gamma * xT
        print(f"xChoked2: {round(result, 3)}")
    return round(result, 3)


def xSizing_gas(inletPressure, outletPressure, gamma, C, valveDia, inletDia, outletDia, xT):
    result = min(xChoked_gas(gamma, C, valveDia, inletDia, outletDia, xT), x_gas(inletPressure, outletPressure))
    print(f"xSizing: {round(result, 3)}")
    return round(result, 3)


def xTP_gas(xT, C, valveDia, inletDia, outletDia):
    etaI = eta1_gas(valveDia, inletDia) + etaB_gas(valveDia, inletDia)
    fp = fP_gas(C, valveDia, inletDia, outletDia)
    a_ = xT / fp ** 2
    b_ = xT * etaI * C * C / (N5_in * (valveDia ** 4))
    result = a_ / (1 + b_)
    pass


# Expansion factor
def Y_gas(inletPressure, outletPressure, gamma, C, valveDia, inletDia, outletDia, xT):
    a = 1 - (xSizing_gas(inletPressure, outletPressure, gamma, C, valveDia, inletDia, outletDia, xT) / (
            3 * xChoked_gas(gamma, C, valveDia, inletDia, outletDia, xT)))
    print(
        f"rhs for y: {(xSizing_gas(inletPressure, outletPressure, gamma, C, valveDia, inletDia, outletDia, xT) / (3 * xChoked_gas(gamma, C, valveDia, inletDia, outletDia, xT)))}")
    # if a > 0.667:
    #     result = 0.667
    # else:
    #     result = a

    result = a

    print(f"Y value is: {round(result, 3)}")

    return round(result, 3)


def Cv_gas(inletPressure, outletPressure, gamma, C, valveDia, inletDia, outletDia, xT, temp, compressibilityFactor,
           flowRate, sg, sg_):
    # sg_ = int(input("Which value do you want to give? \nVolumetric Flow - Specific Gravity (1) \nVolumetric Flow - "
    #                 "Molecular Weight (2)\nMass Flow - Specific Weight (3)\nMass Flow - Molecular Weight (4)\nSelect "
    #                 "1 0r 2 0r 3 or 4: "))

    sg_ = sg_

    # if sg_ == 1:
    #     Gg = int(input("Give value of Gg: "))
    #     sg = 0.6
    # elif sg_ == 2:
    #     M = int(input("Give value of M: "))
    #     sg = M
    # elif sg_ == 3:
    #     gamma_1 = int(input("Give value of Gamma1: "))
    #     sg = gamma_1
    # else:
    #     M = int(input("Give value of M: "))
    #     sg = M

    # sg = 1.0434
    sg = sg

    a_ = inletPressure * fP_gas(C, valveDia, inletDia, outletDia) * Y_gas(inletPressure, outletPressure, gamma, C,
                                                                          valveDia,
                                                                          inletDia, outletDia, xT)
    b_ = temp * compressibilityFactor
    x_ = x_gas(inletPressure, outletPressure)
    x__ = xSizing_gas(inletPressure, outletPressure, gamma, C, valveDia, inletDia, outletDia, xT)
    if sg_ == 1:
        A = flowRate / (
                N7_60_scfh_psi_F * inletPressure * fP_gas(C, valveDia, inletDia, outletDia) * Y_gas(inletPressure,
                                                                                                    outletPressure,
                                                                                                    gamma, C,
                                                                                                    valveDia,
                                                                                                    inletDia,
                                                                                                    outletDia,
                                                                                                    xT) * math.sqrt(
            x__ / (sg * temp * compressibilityFactor)))
        return round(A, 3)

    elif sg_ == 2:
        A = flowRate / (N9_O_m3hr_kPa_C * a_ * math.sqrt(x_ / (sg * b_)))
        return A

    elif sg_ == 3:
        A = flowRate / (
                N6_lbhr_psi_lbft3 * fP_gas(C, valveDia, inletDia, outletDia) * Y_gas(inletPressure, outletPressure,
                                                                                     gamma, C, valveDia,
                                                                                     inletDia, outletDia,
                                                                                     xT) * math.sqrt(
            x__ * sg * inletPressure))
        return A

    else:
        A = flowRate / (N8_kghr_bar_K * a_ * math.sqrt((x_ * sg) / b_))
        return A


# TODO - Trim exit velocities and other velocities

def trimExitVelocity(inletPressure, outletPressure, specificGravity, trimType, numberOfTurns):
    a_ = math.sqrt(((inletPressure - outletPressure) * 201) / specificGravity)
    K1, K2 = getMultipliers(trimType, numberOfTurns)
    return a_ * K1 * K2


def getMultipliers(trimType, numberOfTurns):
    trimDict = {"Baffle Plate": 0.7, "Trickle": 0.92, "Contoured": 0.92, "Cage": 0.57, "MLT": 0.53}
    turnsDict = {2: 0.88, 4: 0.9, 6: 0.91, 8: 0.92, 10: 0.93, 12: 0.96, "other": 1}

    K1 = trimDict[trimType]
    K2 = turnsDict[numberOfTurns]

    return K1, K2


def getVelocity(Flowrate, inletDia, outletDia, valveDia):
    # give values of Dias in, flow rate in m3/hr
    inletDia = inletDia * 0.0254
    outletDia = outletDia * 0.0254
    valveDia = valveDia * 0.0254
    print(inletDia, outletDia, valveDia)
    inletVelocity = (Flowrate / (0.785 * (inletDia ** 2))) / 3600
    outletVelocity = (Flowrate / (0.785 * (outletDia ** 2))) / 3600
    valveVelocity = (Flowrate / (0.785 * (valveDia ** 2))) / 3600

    return inletVelocity, outletVelocity, valveVelocity


# TODO - Liquid noise calculations

N0 = 1
N14 = 0.0046
N34 = 1.17

Cv1 = [0, 1688, 2531.3, 2742.188, 2847.656, 2953.125, 3375, 6750]
FL1 = [0.85, 0.713, 0.645, 0.627, 0.619, 0.61, 0.576, 0.54]


# Cv1 = [0, 17.2, 50.2, 87.8, 146, 206, 285, 365, 465, 521, 1000]
# FL1 = [0.85, 0.85, 0.84, 0.79, 0.75, 0.71, 0.63, 0.58, 0.56, 0.54, 0.54]

# 1
def getFL_v(C):
    a = 0
    while True:
        if Cv1[a] == C:
            return FL1[a]
        elif Cv1[a] > C:
            break
        else:
            a += 1

    Fllll = FL1[a - 1] - (((Cv1[a - 1] - C) / (Cv1[a - 1] - Cv1[a])) * (FL1[a - 1] - FL1[a]))

    # return round(Fllll, 3)
    return 0.9


# rW
# 2
def getAcousticPower():
    return 5


# Pressure recovery ratio
# 3
def xF(inletPressure, outletPressure, vaporPressure):
    print(f'XF: {(inletPressure - outletPressure) / (inletPressure - vaporPressure)}')
    return (inletPressure - outletPressure) / (inletPressure - vaporPressure)


# 4
def deltaPC(C, inletPressure, outletPressure, vaporPressure):
    a = inletPressure - outletPressure
    b = (getFL_v(C) ** 2) * (inletPressure - vaporPressure)
    print(f"deltaPC: {min(a, b)}")
    return min(a, b)


# 5
def xFZ(holeDia, C, Fd):
    if holeDia == 0:
        a = 0.90 / math.sqrt(1 + (3 * Fd * math.sqrt(C / (N34 * getFL_v(C)))))
        # For hole trim
    else:
        a = 1 / math.sqrt(4.5 + (1.650 * N0 * holeDia * holeDia / getFL_v(C)))

    print(f"xFZ: {a}")
    return a


# 6
# Differential Pressure ratio corrected at inlet
def XFZP1(holeDia, C, Fd, inletPressure):
    a = xFZ(holeDia, C, Fd) * ((600000 / inletPressure) ** 0.125)
    print(f"xFZP1: {a}")
    return a


# 7
# Dj
def jetDia(Fd, C):
    print(f"jetDia: {N14 * Fd * math.sqrt(C * getFL_v(C))}")
    return N14 * Fd * math.sqrt(C * getFL_v(C))


# 8
# Uvc
def jetVelocity(C, inletPressure, outletPressure, vaporPressure, density):
    a = (1 / getFL_v(C)) * (math.sqrt(2 * deltaPC(C, inletPressure, outletPressure, vaporPressure) / density))
    print(f"jetVelocity: {a}")
    return a


# 9
# Wm
def mechanicalPower(massFlowRate, C, inletPressure, outletPressure, vaporPressure, density):
    Wm = massFlowRate * (jetVelocity(C, inletPressure, outletPressure, vaporPressure, density) ** 2) * getFL_v(
        C) * getFL_v(
        C) * 0.5
    print(f"Mechanical Power: {Wm}")
    return Wm


# 10
# TODO 5 - Cav vs Turbulent
def etaTurb(C, inletPressure, outletPressure, vaporPressure, density, speedS):
    print(
        f"etaTurb value is: {(10 ** (-4)) * (jetVelocity(C, inletPressure, outletPressure, vaporPressure, density) / speedS)}")
    return (10 ** (-4)) * (jetVelocity(C, inletPressure, outletPressure, vaporPressure, density) / speedS)


# 11
def etaCav(C, inletPressure, outletPressure, vaporPressure, density, speedS, holeDia, Fd):
    etaTurbulent = etaTurb(C, inletPressure, outletPressure, vaporPressure, density, speedS)
    delta_PC = deltaPC(C, inletPressure, outletPressure, vaporPressure)
    xfzp_1 = XFZP1(holeDia, C, Fd, inletPressure)
    xf = xF(inletPressure, outletPressure, vaporPressure)
    deltaP = inletPressure - outletPressure
    ePower5 = 2.718281828459045 ** (5 * xfzp_1)
    a1 = 0.32 * etaTurbulent * math.sqrt(deltaP / (delta_PC * xfzp_1)) * ePower5
    a2 = ((1 - xfzp_1) / (1 - xf)) ** 0.5
    a3 = (xf / xfzp_1) ** 5
    a4 = (xf - xfzp_1) ** 1.5
    print(f"etaCav: {a1 * a2 * a3 * a4}")
    return a1 * a2 * a3 * a4


# 12
# Wa
def soundPower(C, inletPressure, outletPressure, vaporPressure, density, speedS, massFlowRate, rW, holeDia, Fd):
    etaCavitation = etaCav(C, inletPressure, outletPressure, vaporPressure, density, speedS, holeDia, Fd)
    etaTurbulent = etaTurb(C, inletPressure, outletPressure, vaporPressure, density, speedS)
    wm = mechanicalPower(massFlowRate, C, inletPressure, outletPressure, vaporPressure, density)
    a = 1
    if a == 1:
        print(f"Sound Power: {etaTurbulent * wm * rW}")
        return etaTurbulent * wm * rW
    else:
        return (etaTurbulent + etaCavitation) * wm * rW


# 13
# Lpi
def overallInternalSound(Fd, C, inletPressure, outletPressure, vaporPressure, density, speedS, massFlowRate, rW,
                         holeDia, internalPipeDia):
    sound_power = soundPower(C, inletPressure, outletPressure, vaporPressure, density, speedS, massFlowRate, rW,
                             holeDia, Fd)
    a_ = ((3.2 * (10 ** 9)) * sound_power * density * speedS) / (internalPipeDia * internalPipeDia)
    print(f"Overall Internal Sound: {10 * math.log10(a_)}")
    return 10 * math.log10(a_)


# 14
# N_STR
def strouhalNumber(Fd, C, inletPressure, vaporPressure, holeDia, seatDia, valveDia):
    pressure_coeff = (1 / (inletPressure - vaporPressure)) ** 0.57
    xfzp_1 = XFZP1(holeDia, C, Fd, inletPressure)
    denom = N34 * (xfzp_1 ** 1.5) * valveDia * seatDia
    fl = getFL_v(C)
    numer = 0.02 * fl * fl * C
    numer2 = 0.036 * fl * fl * C * (Fd ** 0.75)
    print(f"Strouhal Number: {numer2 * pressure_coeff / denom}")
    return numer2 * pressure_coeff / denom


# 15
# TODO 4 - Cav vs Turbulent
# Fp_turb
def internalPeakSound(Fd, C, inletPressure, outletPressure, density, vaporPressure, holeDia, seatDia, valveDia):
    N_STR = strouhalNumber(Fd, C, inletPressure, vaporPressure, holeDia, seatDia, valveDia)
    jet_velocity = jetVelocity(C, inletPressure, outletPressure, vaporPressure, density)
    jet_dia = jetDia(Fd, C)
    print(f"Internal Peak Sound: {N_STR * jet_velocity / jet_dia}")
    return N_STR * jet_velocity / jet_dia


# 16
def fpCav(Fd, C, inletPressure, outletPressure, density, vaporPressure, holeDia, seatDia, valveDia):
    fp_turb = internalPeakSound(Fd, C, inletPressure, outletPressure, density, vaporPressure, holeDia, seatDia,
                                valveDia)
    xfzp_1 = XFZP1(holeDia, C, Fd, inletPressure)
    xf = xF(inletPressure, outletPressure, vaporPressure)
    a_ = ((1 - xf) / (1 - xfzp_1)) ** 2
    b_ = (xfzp_1 / xf) ** 2.5
    print(f"FP_Cav: {6 * fp_turb * a_ * b_}")
    return 6 * fp_turb * a_ * b_


# 17
# fr
def ringFrequency(internalPipeDia):
    Cp = 5000  # Speed of sound in pipe
    print(f"ring frequency: {Cp / (math.pi * internalPipeDia)}")
    return Cp / (math.pi * internalPipeDia)


# 18
# TL_Fr
def minTransmissionLoss(densityPipe, wallThicknessPipe, speedSinPipe, densityAir, internalPipeDia):
    Co = 343  # speed of sound in air(m/s)
    a_ = (speedSinPipe * densityPipe * wallThicknessPipe) / (Co * densityAir * internalPipeDia)
    print(f"Min Transmission Loss: {-10 - (10 * math.log10(a_))}")
    return -10 - (10 * math.log10(a_))


# 19
# delta_TL_(fp,turb)
def deltaTransmissionLoss(Fd, C, inletPressure, outletPressure, density, vaporPressure, holeDia, seatDia, valveDia,
                          internalPipeDia):
    fp_turb = internalPeakSound(Fd, C, inletPressure, outletPressure, density, vaporPressure, holeDia, seatDia,
                                valveDia)
    fr = ringFrequency(internalPipeDia)
    a_ = fr / fp_turb
    print(f"Delta Transmission Loss: {-20 * math.log10(a_ + (a_ ** (-1.5)))}")
    return -20 * math.log10(a_ + (a_ ** (-1.5)))


# 20
# TODO 3 - Cav vs Turbulent
# TL_turb
def overallTransmissionLoss(Fd, C, inletPressure, outletPressure, density, vaporPressure, holeDia, seatDia, valveDia,
                            internalPipeDia, densityPipe, wallThicknessPipe, speedSinPipe, densityAir):
    delta_TL_fp_turb = deltaTransmissionLoss(Fd, C, inletPressure, outletPressure, density, vaporPressure, holeDia,
                                             seatDia, valveDia, internalPipeDia)
    TL_fr = minTransmissionLoss(densityPipe, wallThicknessPipe, speedSinPipe, densityAir, internalPipeDia)
    print(f"Overall Transmission Loss: {delta_TL_fp_turb + TL_fr}")
    return delta_TL_fp_turb + TL_fr


# 21
# TL_cav
def overTransmissionLossCav(Fd, C, inletPressure, outletPressure, density, speedS, vaporPressure, holeDia, seatDia,
                            valveDia, internalPipeDia, densityPipe, wallThicknessPipe, speedSinPipe, densityAir):
    TL_turb = overallTransmissionLoss(Fd, C, inletPressure, outletPressure, density, vaporPressure, holeDia, seatDia,
                                      valveDia, internalPipeDia, densityPipe, wallThicknessPipe, speedSinPipe,
                                      densityAir)
    fp_cav = fpCav(Fd, C, inletPressure, outletPressure, density, vaporPressure, holeDia, seatDia, valveDia)
    fp_turb = internalPeakSound(Fd, C, inletPressure, outletPressure, density, vaporPressure, holeDia, seatDia,
                                valveDia)
    eta_cav = etaCav(C, inletPressure, outletPressure, vaporPressure, density, speedS, holeDia, Fd)
    eta_turb = etaTurb(C, inletPressure, outletPressure, vaporPressure, density, speedS)
    a_ = 250 * ((fp_cav ** 1.5) / (fp_turb ** 2)) * (eta_cav / (eta_turb + eta_cav))
    print(f" Overall transmission Loss Cav: {TL_turb + 10 * math.log10(a_)}")
    return TL_turb + 10 * math.log10(a_)


#  Table 3 – Indexed third octave center frequencies and “A” weighting factors
# f_i indexed frequency bands
frequencies = [12.5, 16, 20, 25, 31.5, 40, 50, 63, 80, 100, 125, 160, 200, 250, 315, 400, 500, 630, 800, 1000, 1250,
               1600, 2000, 2500, 3150, 4000, 5000, 6300, 8000, 10000, 12500, 16000, 20000]
# delta_LA(fi)
a_factor = [-63.4, -56.7, -50.5, -44.7, -39.4, -34.6, -30.2, -26.2, 22.5, -19.1, -16.1, -13.4, -10.9, -8.6, -6.6, -4.8,
            -3.2, -1.9, -0.8, 0, 0.6, 1, 1.2, 1.3, 1.2, 1, 0.5, -0.1, -1.1, -2.5, -4.3, -6.6, -9.3]


# 22
# TODO 2 - Cav vs Turbulent
# F_turb(f_i)
def f_turbulence(fi, Fd, C, inletPressure, outletPressure, density, vaporPressure, holeDia, seatDia, valveDia):
    fp_turb = internalPeakSound(Fd, C, inletPressure, outletPressure, density, vaporPressure, holeDia, seatDia,
                                valveDia)
    a_ = fi / fp_turb
    b_ = fp_turb / fi
    return -10 * math.log10((0.25 * (a_ ** 3)) + b_) - 3.1


# 23
# F-cav(fi)
def f_cav(fi, Fd, C, inletPressure, outletPressure, density, vaporPressure, holeDia, seatDia, valveDia):
    fp_cav = fpCav(Fd, C, inletPressure, outletPressure, density, vaporPressure, holeDia, seatDia, valveDia)
    a_ = fi / fp_cav
    b_ = fp_cav / fi
    return -10 * math.log10((0.25 * (a_ ** 1.5)) + (b_ ** 1.5)) - 3.5


# 24
# TODO 1 - Cav vs Turbulent
# Lpi(fi) - turbulent
def LpiTurbulent(fi, Fd, C, inletPressure, outletPressure, vaporPressure, density, speedS, massFlowRate, rW, holeDia,
                 seatDia, valveDia, internalPipeDia):
    Lpi = overallInternalSound(Fd, C, inletPressure, outletPressure, vaporPressure, density, speedS, massFlowRate, rW,
                               holeDia, internalPipeDia)
    f_turb = f_turbulence(fi, Fd, C, inletPressure, outletPressure, density, vaporPressure, holeDia, seatDia, valveDia)
    return Lpi + f_turb


# 25
# Lpi(fi) - cavitating
def LpiCavitation(fi, Fd, C, inletPressure, outletPressure, vaporPressure, density, speedS, massFlowRate, rW, holeDia,
                  seatDia, valveDia, internalPipeDia):
    Lpi = overallInternalSound(Fd, C, inletPressure, outletPressure, vaporPressure, density, speedS, massFlowRate, rW,
                               holeDia, internalPipeDia)
    eta_cav = etaCav(C, inletPressure, outletPressure, vaporPressure, density, speedS, holeDia, Fd)
    eta_turb = etaTurb(C, inletPressure, outletPressure, vaporPressure, density, speedS)
    f_turb = f_turbulence(fi, Fd, C, inletPressure, outletPressure, density, vaporPressure, holeDia, seatDia, valveDia)
    a_ = 10 ** (0.1 * f_turb)
    b_ = (eta_turb * a_) / (eta_cav + eta_turb)
    c_ = (eta_cav * a_) / (eta_cav + eta_turb)
    return Lpi + 10 * math.log10(b_ + c_)


# 26
# delta_TL(fi)
def delta_TL_fi(fi, internalPipeDia):
    f_r = ringFrequency(internalPipeDia)
    a_ = f_r / fi
    return -20 * math.log10(a_ + (a_ ** (-1.5)))


# 27
# TL(fi) - transmission loss at fi
def TL(fi, densityPipe, wallThicknessPipe, speedSinPipe, densityAir, internalPipeDia):
    tl_fr = minTransmissionLoss(densityPipe, wallThicknessPipe, speedSinPipe, densityAir, internalPipeDia)
    del_tl = delta_TL_fi(fi, internalPipeDia)
    return tl_fr + del_tl


# 28
# Lpe,1m(fi)
def Lpe1m(fi, Fd, C, inletPressure, outletPressure, vaporPressure, density, speedS, massFlowRate, rW, holeDia, seatDia,
          valveDia, densityPipe, wallThicknessPipe, speedSinPipe, densityAir, internalPipeDia):
    # lpi_cav = LpiCavitation(fi, Fd, C, inletPressure, outletPressure, vaporPressure, density, speedS, massFlowRate,
    # rW, holeDia, seatDia, valveDia)
    lpi_turb = LpiTurbulent(fi, Fd, C, inletPressure, outletPressure, vaporPressure, density, speedS, massFlowRate, rW,
                            holeDia, seatDia, valveDia, internalPipeDia)
    a = 5
    lpi_cav = lpi_turb

    if a == 5:
        lpi = lpi_turb
    else:
        lpi = lpi_cav

    tl_fi = TL(fi, densityPipe, wallThicknessPipe, speedSinPipe, densityAir, internalPipeDia)
    a_ = (internalPipeDia + 2 * wallThicknessPipe + 2) / (internalPipeDia + 2 * wallThicknessPipe)
    return lpi + tl_fi - 10 * math.log10(a_)


# 29
# final
def summation(Fd, C, inletPressure, outletPressure, vaporPressure, density, speedS, massFlowRate, rW, holeDia, seatDia,
              valveDia, densityPipe, wallThicknessPipe, speedSinPipe, densityAir, internalPipeDia):
    sum_ = 0
    for f_i in frequencies:
        a_ = 0.1 * Lpe1m(f_i, Fd, C, inletPressure, outletPressure, vaporPressure, density, speedS, massFlowRate, rW,
                         holeDia, seatDia, valveDia, densityPipe, wallThicknessPipe, speedSinPipe, densityAir,
                         internalPipeDia)
        b_ = 10 ** a_
        print(f"One of Sum value {frequencies.index(f_i)}: {b_}")
        sum_ = sum_ + b_

    return 10 * math.log10(sum_)


# TODO - Power Level - Gas and Liquid
# pressure in psi, plevel in kw
def power_level_liquid(inletPressure, outletPressure, sGravity, Cv):
    a_ = ((inletPressure - outletPressure) ** 1.5) * Cv
    b_ = sGravity * 2300
    c_ = a_ / b_
    return round(c_, 3)


# flowrate in lb/s, pressure in psi
def power_level_gas(specificHeatRatio, inletPressure, outletPressure, flowrate):
    pressureRatio = outletPressure / inletPressure
    specificVolume = 1 / pressureRatio
    heatRatio = specificHeatRatio / (specificHeatRatio - 1)
    a_ = heatRatio * inletPressure * specificVolume
    b_ = (1 - pressureRatio ** (1 / heatRatio)) * flowrate / 5.12
    c_ = a_ * b_
    return round(c_, 3)


# TODO ------------------------------------------ FLASK ROUTING --------------------------------------- #
with app.app_context():
    selected_item = db.session.query(itemMaster).filter_by(id=1).first()


def convert_project_data(project_list):
    data_update_list2 = []

    with app.app_context():
        for i in project_list:
            industry_updated = db.session.query(industryMaster).filter_by(id=i.IndustryId).first()
            region_updated = db.session.query(regionMaster).filter_by(id=i.regionID).first()
            status_updated = db.session.query(statusMaster).filter_by(id=i.statusID).first()
            customer_updated = db.session.query(customerMaster).filter_by(id=i.customerID).first()
            engineer_updated = db.session.query(engineerMaster).filter_by(id=i.engineerID).first()

            if region_updated:
                region_updated = region_updated
            else:
                region_updated = db.session.query(regionMaster).filter_by(id=1).first()

            if industry_updated:
                industry_updated = industry_updated
            else:
                industry_updated = db.session.query(industryMaster).filter_by(id=1).first()

            if status_updated:
                status_updated = status_updated
            else:
                status_updated = db.session.query(statusMaster).filter_by(id=1).first()

            if customer_updated:
                customer_updated = customer_updated
            else:
                customer_updated = db.session.query(customerMaster).filter_by(id=1).first()

            if engineer_updated:
                engineer_updated = engineer_updated
            else:
                engineer_updated = db.session.query(engineerMaster).filter_by(id=1).first()



            project_updated = {"id": i.id, "quote": i.quote, "received_date": i.received_date,
                               "work_order": i.work_order,
                               "due_date": i.due_date, "IndustryID": industry_updated.name,
                               "regionID": region_updated.name,
                               "statusID": status_updated.name, "customerID": customer_updated.name,
                               "engineerID": engineer_updated.name}

            data_update_list2.append(project_updated)
    return data_update_list2


def convert_item_data(list_item):
    data_list = []
    with app.app_context():
        for i in list_item:
            serial_updated = db.session.query(valveSeries).filter_by(id=i.serialID).first()
            size_updated = db.session.query(valveSize).filter_by(id=i.sizeID).first()
            model_updated = db.session.query(modelMaster).filter_by(id=i.modelID).first()
            type_updated = db.session.query(valveStyle).filter_by(id=i.typeID).first()
            rating_updated = db.session.query(rating).filter_by(id=i.ratingID).first()
            material_updated = db.session.query(materialMaster).filter_by(id=i.materialID).first()

            if serial_updated:
                serial_updated = serial_updated
            else:
                serial_updated = db.session.query(valveSeries).filter_by(id=1).first()

            if size_updated:
                size_updated = size_updated
            else:
                size_updated = db.session.query(valveSize).filter_by(id=5).first()

            if model_updated:
                model_updated = model_updated
            else:
                model_updated = db.session.query(modelMaster).filter_by(id=1).first()

            if type_updated:
                type_updated = type_updated
            else:
                type_updated = db.session.query(valveStyle).filter_by(id=1).first()

            if rating_updated:
                rating_updated = rating_updated
            else:
                rating_updated = db.session.query(rating).filter_by(id=1).first()

            if material_updated:
                material_updated = material_updated
            else:
                material_updated = db.session.query(materialMaster).filter_by(id=1).first()

            item_updated = {"id": i.id, "alt": i.alt, "tag_no": i.tag_no, "unit_price": i.unit_price,
                            "qty": i.qty, "projectID": i.projectID, "serialID": serial_updated.name,
                            "sizeID": size_updated.size, "modelID": model_updated.name, "typeID": type_updated.name,
                            "ratingID": rating_updated.size, "materialID": material_updated.name}
            data_list.append(item_updated)
    return data_list


# Website routes
@app.route('/', methods=["GET", "POST"])
def home():
    with app.app_context():
        item_details = db.session.query(itemMaster).filter_by(id=selected_item.id).first()

        data = projectMaster.query.all()
        data2 = itemMaster.query.all()

        data_update_list2 = convert_project_data(data)
        item_list = convert_item_data(data2)

        if request.method == 'POST':
            projectId = int(request.form['projects'])
            print(projectId)
            data = projectMaster.query.all()
            data3 = db.session.query(itemMaster).filter_by(projectID=projectId).all()
            data_updated_list = convert_project_data(data)
            item_list = convert_item_data(data3)

            return render_template("dashboard_with_db.html", title='Dashboard', data=data_updated_list, data2=item_list,
                                   item_d=item_details)

        return render_template("dashboard_with_db.html", title='Dashboard', data=data_update_list2, data2=item_list,
                               item_d=item_details)


@app.route('/filter', methods=["GET", "POST"])
def filter_dashboard():
    with app.app_context():
        if request.method == "POST":
            filer_criter = request.form.get('filter_criteria')
            search_c = request.form.get('search')
            filter_list = {'IndustryId': industryMaster, 'regionID': regionMaster, 'engineerID': engineerMaster,
                           'statusID': statusMaster, 'quote': 0, 'work_order': 0, 'customerID': customerMaster}
            if filer_criter == 'IndustryId':
                industry_e = db.session.query(industryMaster).filter_by(name=search_c).first()
                if industry_e:
                    project_data = db.session.query(projectMaster).filter_by(IndustryId=industry_e.id).all()
                else:
                    project_data = projectMaster.query.all()

                data_update_list2 = convert_project_data(project_data)

            elif filer_criter == 'regionID':
                region_e = db.session.query(regionMaster).filter_by(name=search_c).first()
                if region_e:
                    project_data = db.session.query(projectMaster).filter_by(regionID=region_e.id).all()
                else:
                    project_data = projectMaster.query.all()
                data_update_list2 = convert_project_data(project_data)

            elif filer_criter == 'engineerID':
                engineer_e = db.session.query(engineerMaster).filter_by(name=search_c).first()
                if engineer_e:
                    project_data = db.session.query(projectMaster).filter_by(engineerID=engineer_e.id).all()
                else:
                    project_data = projectMaster.query.all()
                data_update_list2 = convert_project_data(project_data)

            elif filer_criter == 'statusID':
                status_e = db.session.query(statusMaster).filter_by(name=search_c).first()
                if status_e:
                    project_data = db.session.query(projectMaster).filter_by(statusID=status_e.id).all()
                else:
                    project_data = projectMaster.query.all()
                data_update_list2 = convert_project_data(project_data)

            elif filer_criter == 'quote':
                project_data = db.session.query(projectMaster).filter_by(quote=search_c).all()
                if project_data:
                    data_update_list2 = convert_project_data(project_data)
                else:
                    project_data = projectMaster.query.all()
                    data_update_list2 = convert_project_data(project_data)

            elif filer_criter == 'work_order':
                project_data = db.session.query(projectMaster).filter_by(work_order=search_c).all()
                if project_data:
                    data_update_list2 = convert_project_data(project_data)
                else:
                    project_data = projectMaster.query.all()
                    data_update_list2 = convert_project_data(project_data)

            elif filer_criter == 'customerID':
                customer_e = db.session.query(customerMaster).filter_by(name=search_c).first()
                if customer_e:
                    project_data = db.session.query(projectMaster).filter_by(customerID=customer_e.id).all()
                else:
                    project_data = projectMaster.query.all()
                data_update_list2 = convert_project_data(project_data)

            data2 = itemMaster.query.all()
            item_list = convert_item_data(data2)

            return render_template("dashboard_with_db.html", title='Dashboard', data=data_update_list2, data2=item_list,
                                   item_d=selected_item)


@app.route('/items', methods=["GET", "POST"])
def getItems():
    global selected_item
    if request.method == "POST":
        item_ = int(request.form.get('item'))

        with app.app_context():
            item_1 = db.session.query(itemMaster).filter_by(id=item_).first()
            selected_item = item_1

        return redirect(url_for('home'))


#
# @app.route('/select-item', methods=["GET", "POST"])
# def selectItem():
#     if request.method == "POST":
#         item_ = request.form.get('item')
#         print(item_)
#     with app.app_context():
#         data = projectMaster.query.all()
#         data2 = itemMaster.query.all()
#
#     return redirect(url_for('home'))
# #
# with app.app_context():
#     items_all = itemCases.query.all()
#     for i in items_all:
#         if i.valveSPL:
#             i.valveSPL = round(i.valveSPL, 2)
#         if i.iVelocity:
#             i.iVelocity = round(i.iVelocity, 2)
#         if i.oVelocity:
#             i.oVelocity = round(i.oVelocity, 2)
#         if i.pVelocity:
#             i.pVelocity = round(i.pVelocity, 2)
#         i.chokedDrop = round(i.chokedDrop, 2)
#         db.session.commit()


@app.route('/project-details', methods=["GET", "POST"])
def projectDetails():
    if request.method == 'POST':
        customer = request.form.get('customer')
        engRef = request.form.get('eRef')
        enqDate = request.form.get('eDate')
        recDate_1 = request.form.get('rDate')
        recDate = datetime.datetime.strptime(recDate_1, '%Y-%m-%d')
        aEng = request.form.get('aEng')
        bDate_1 = request.form.get('bDate')
        bDate = datetime.datetime.strptime(bDate_1, '%Y-%m-%d')
        purpose = request.form.get('purpose')
        industry = request.form.get('industry')
        region = request.form.get('region')
        projectRev = request.form.get('projectRev')
        cEng = request.form.get('cEng')
        cNo = request.form.get('cNo')
        wNo = request.form.get('wNo')
        with app.app_context():
            customer_element = db.session.query(customerMaster).filter_by(name=customer).first()
            engineer_element = db.session.query(engineerMaster).filter_by(name=aEng).first()
            industry_element = db.session.query(industryMaster).filter_by(name=industry).first()
            region_element = db.session.query(regionMaster).filter_by(name=region).first()

            print(wNo)

            new_project = projectMaster(industry=industry_element, region=region_element, quote=purpose,
                                        customer=customer_element,
                                        received_date=recDate,
                                        engineer=engineer_element,
                                        work_order=wNo,
                                        due_date=bDate,
                                        status=status_element_1)

            db.session.add(new_project)
            db.session.commit()

            return render_template("Project Details.html", title='Project Details', item_d=selected_item)

    return render_template("Project Details.html", title='Project Details', item_d=selected_item)


# @app.route('/valve-selection', methods=["GET", "POST"])
# def valveSelection():
#     # get data from db to give in template
#     with app.app_context():
#         rating_list = rating.query.all()
#         material_list = materialMaster.query.all()
#         series_list = valveSeries.query.all()
#         size_list = valveSize.query.all()  # size
#         end_connection = endConnection.query.all()  # name
#         end_finish = endFinish.query.all()  # name
#         bonnet_type = bonnetType.query.all()  # name
#         packing_type = packingType.query.all()
#         trim_type = trimType.query.all()
#         flow_charac = [{"id": 1, "name": "Equal %"}, {"id": 2, "name": "Linear"}]
#         flow_direction = flowDirection.query.all()
#         seat_leakage = seatLeakageClass.query.all()
#
#     template_list = [rating_list, material_list, series_list, size_list, end_finish, end_connection, bonnet_type,
#                      packing_type, trim_type, flow_charac, flow_direction, seat_leakage]
#
#     if request.method == 'POST':
#         if request.form.get('update'):
#             with app.app_context():
#                 itemdetails = db.session.query(itemMaster).filter_by(id=selected_item.id).first()
#                 valvesDetails = db.session.query(valveDetails).filter_by(itemID=itemdetails.id).all()
#                 if len(valvesDetails) > 0:
#                     return f"Valve Details already exists"
#                 else:
#                     new_valve_details = valveDetails(tag=request.form.get('tag'), quantity=request.form.get('qty'),
#                                                      application=request.form.get('application'),
#                                                      serial_no=request.form.get('sNo'),
#                                                      rating=request.form.get('ratingP'),
#                                                      body_material=request.form.get('bMaterial'),
#                                                      shutOffDelP=request.form.get('shutOffP'),
#                                                      maxPressure=request.form.get('maxP'),
#                                                      maxTemp=request.form.get('maxT'),
#                                                      minTemp=request.form.get('minT'),
#                                                      valve_series=request.form.get('vSeries'),
#                                                      valve_size=request.form.get('vSize'),
#                                                      rating_v=request.form.get('ratingV'),
#                                                      ratedCV=request.form.get('cv'),
#                                                      endConnection_v=request.form.get('endConnection'),
#                                                      endFinish_v=request.form.get('endFinish'),
#                                                      bonnetType_v=request.form.get('bonnetType'),
#                                                      bonnetExtDimension=request.form.get('bed'),
#                                                      packingType_v=request.form.get('packingType'),
#                                                      trimType_v=request.form.get('trimType'),
#                                                      flowCharacter_v=request.form.get('flowCharacter'),
#                                                      flowDirection_v=request.form.get('flowDirection'),
#                                                      seatLeakageClass_v=request.form.get('SLClass'), body_v=None,
#                                                      bonnet_v=None,
#                                                      nde1=None, nde2=None, plug=None, stem=None, seat=None,
#                                                      cage_clamp=None,
#                                                      balanceScale=None, packing=None, stud_nut=None, gasket=None,
#                                                      item=itemdetails)
#
#                     db.session.add(new_valve_details)
#                     db.session.commit()
#
#             return f"Suceess"
#         elif request.form.get('new'):
#             pass
#
#     return render_template("Valve Selection.html", title='Valve Selection', data=template_list, item_d=selected_item)


@app.route('/valve-selection', methods=["GET", "POST"])
def valveSelection():
    # get data from db to give in template
    with app.app_context():
        rating_list = rating.query.all()
        material_list = materialMaster.query.all()
        series_list = valveSeries.query.all()
        size_list = valveSize.query.all()  # size
        end_connection = endConnection.query.all()  # name
        end_finish = endFinish.query.all()  # name
        bonnet_type = bonnetType.query.all()  # name
        packing_type = packingType.query.all()
        trim_type = trimType.query.all()
        flow_charac = [{"id": 1, "name": "Equal %"}, {"id": 2, "name": "Linear"}]
        flow_direction = flowDirection.query.all()
        seat_leakage = seatLeakageClass.query.all()
        # series = valveSeries.query.all()

        template_list = [rating_list, material_list, series_list, size_list, end_finish, end_connection, bonnet_type,
                         packing_type, trim_type, flow_charac, flow_direction, seat_leakage]

        if request.method == 'POST':
            if request.form.get('update'):
                itemdetails = db.session.query(itemMaster).filter_by(id=selected_item.id).first()
                valvesDetails = db.session.query(valveDetails).filter_by(itemID=itemdetails.id).all()
                valve_element = db.session.query(valveDetails).filter_by(itemID=itemdetails.id).first()
                if len(valvesDetails) > 0:
                    valve_element.tag = request.form.get('tag')
                    valve_element.quantity = request.form.get('qty')
                    valve_element.application = request.form.get('application')
                    valve_element.serial_no = request.form.get('sNo')
                    valve_element.rating = request.form.get('ratingP')
                    valve_element.body_material = request.form.get('bMaterial')
                    valve_element.shutOffDelP = request.form.get('shutOffP')
                    valve_element.maxPressure = request.form.get('maxP')
                    valve_element.maxTemp = request.form.get('maxT')
                    valve_element.minTemp = request.form.get('minT')
                    valve_element.valve_series = request.form.get('vSeries')
                    valve_element.valve_size = request.form.get('vSize')
                    valve_element.rating_v = request.form.get('ratingV')
                    valve_element.ratedCV = request.form.get('cv')
                    valve_element.endConnection_v = request.form.get('endConnection')
                    valve_element.endFinish_v = request.form.get('endFinish')
                    valve_element.bonnetType_v = request.form.get('bonnetType')
                    valve_element.bonnetExtDimension = request.form.get('bed')
                    valve_element.packingType_v = request.form.get('packingType')
                    valve_element.trimType_v = request.form.get('trimType')
                    valve_element.flowCharacter_v = request.form.get('flowCharacter')
                    valve_element.flowDirection_v = request.form.get('flowDirection')
                    valve_element.seatLeakageClass_v = request.form.get('SLClass')
                    valve_element.body_v = None
                    valve_element.bonnet_v = None
                    valve_element.nde1 = None
                    valve_element.nde2 = None
                    valve_element.plug = None
                    valve_element.stem = None
                    valve_element.seat = None
                    valve_element.cage_clamp = None
                    valve_element.balanceScale = None
                    valve_element.packing = None
                    valve_element.stud_nut = None
                    valve_element.gasket = None
                    valve_element.item = itemdetails
                    db.session.commit()
                    # do update operation
                    pass
                else:
                    new_valve_details = valveDetails(tag=request.form.get('tag'), quantity=request.form.get('qty'),
                                                     application=request.form.get('application'),
                                                     serial_no=request.form.get('sNo'),
                                                     rating=request.form.get('ratingP'),
                                                     body_material=request.form.get('bMaterial'),
                                                     shutOffDelP=request.form.get('shutOffP'),
                                                     maxPressure=request.form.get('maxP'),
                                                     maxTemp=request.form.get('maxT'),
                                                     minTemp=request.form.get('minT'),
                                                     valve_series=request.form.get('vSeries'),
                                                     valve_size=request.form.get('vSize'),
                                                     rating_v=request.form.get('ratingV'),
                                                     ratedCV=request.form.get('cv'),
                                                     endConnection_v=request.form.get('endConnection'),
                                                     endFinish_v=request.form.get('endFinish'),
                                                     bonnetType_v=request.form.get('bonnetType'),
                                                     bonnetExtDimension=request.form.get('bed'),
                                                     packingType_v=request.form.get('packingType'),
                                                     trimType_v=request.form.get('trimType'),
                                                     flowCharacter_v=request.form.get('flowCharacter'),
                                                     flowDirection_v=request.form.get('flowDirection'),
                                                     seatLeakageClass_v=request.form.get('SLClass'), body_v=None,
                                                     bonnet_v=None,
                                                     nde1=None, nde2=None, plug=None, stem=None, seat=None,
                                                     cage_clamp=None,
                                                     balanceScale=None, packing=None, stud_nut=None, gasket=None,
                                                     item=itemdetails)

                    db.session.add(new_valve_details)
                    db.session.commit()

                pass

            elif request.form.get('new'):
                valveType = request.form.get('vStyle')
                if valveType == 'Globe':
                    vtypeid = 1
                else:
                    vtypeid = 2

                # Add New Item first
                model_element = db.session.query(modelMaster).filter_by(name='Model_1').first()
                project_element = db.session.query(projectMaster).filter_by(id=1).first()
                serial_element = db.session.query(valveSeries).filter_by(id=int(request.form.get('vSeries'))).first()
                size_element = db.session.query(valveSize).filter_by(id=int(request.form.get('vSize'))).first()
                rating_element = db.session.query(rating).filter_by(id=int(request.form.get('ratingP'))).first()
                material_element = db.session.query(materialMaster).filter_by(
                    id=int(request.form.get('bMaterial'))).first()
                type_element = db.session.query(valveStyle).filter_by(id=vtypeid).first()

                item4 = {"alt": 'A', "tagNo": request.form.get('tag'), "serial": serial_element, "size": size_element,
                         "model": model_element, "type": type_element, "rating": rating_element,
                         "material": material_element, "unitPrice": 1, "Quantity": 1, "Project": project_element}

                itemsList = [item4]

                for i in itemsList:
                    new_item = itemMaster(alt=i['alt'], tag_no=i['tagNo'], serial=i['serial'], size=i['size'],
                                          model=i['model'],
                                          type=i['type'], rating=i['rating'], material=i['material'],
                                          unit_price=i['unitPrice'],
                                          qty=i['Quantity'], project=i['Project'])

                    db.session.add(new_item)
                    db.session.commit()

                # Add Valve Details Then
                new_valve_details = valveDetails(tag=request.form.get('tag'), quantity=request.form.get('qty'),
                                                 application=request.form.get('application'),
                                                 serial_no=request.form.get('sNo'),
                                                 rating=request.form.get('ratingP'),
                                                 body_material=request.form.get('bMaterial'),
                                                 shutOffDelP=request.form.get('shutOffP'),
                                                 maxPressure=request.form.get('maxP'),
                                                 maxTemp=request.form.get('maxT'),
                                                 minTemp=request.form.get('minT'),
                                                 valve_series=request.form.get('vSeries'),
                                                 valve_size=request.form.get('vSize'),
                                                 rating_v=request.form.get('ratingV'),
                                                 ratedCV=request.form.get('cv'),
                                                 endConnection_v=request.form.get('endConnection'),
                                                 endFinish_v=request.form.get('endFinish'),
                                                 bonnetType_v=request.form.get('bonnetType'),
                                                 bonnetExtDimension=request.form.get('bed'),
                                                 packingType_v=request.form.get('packingType'),
                                                 trimType_v=request.form.get('trimType'),
                                                 flowCharacter_v=request.form.get('flowCharacter'),
                                                 flowDirection_v=request.form.get('flowDirection'),
                                                 seatLeakageClass_v=request.form.get('SLClass'), body_v=None,
                                                 bonnet_v=None,
                                                 nde1=None, nde2=None, plug=None, stem=None, seat=None,
                                                 cage_clamp=None,
                                                 balanceScale=None, packing=None, stud_nut=None, gasket=None,
                                                 item=new_item)
                pass

        return render_template("Valve Selection.html", title='Valve Selection', data=template_list,
                               item_d=selected_item)


def sort_list_latest(list_1, selected):
    for i in list_1:
        if i['id'] == selected:
            removing_element = i
            list_1.remove(removing_element)
            print(list_1)
            list_1 = [removing_element] + list_1
    return list_1


@app.route('/valve-sizing', methods=["GET", "POST"])
def valveSizing():
    with app.app_context():
        item_selected = db.session.query(itemMaster).filter_by(id=selected_item.id).first()
        itemCases_1 = db.session.query(itemCases).filter_by(itemID=item_selected.id).all()
        fluid_data = fluidName.query.all()

        case_len = len(itemCases_1)
        length_unit_list = [{'id': 'inch', 'name': 'inch'}, {'id': 'm', 'name': 'm'}, {'id': 'mm', 'name': 'mm'},
                            {'id': 'cm', 'name': 'cm'}]

        if request.method == 'POST':
            serial = selected_item.serialID
            size_ = db.session.query(valveSize).filter_by(id=item_selected.sizeID).first()
            size = size_.size
            valve_type_ = db.session.query(valveStyle).filter_by(id=item_selected.typeID).first()
            valve_type = valve_type_.name
            print(valve_type)

            # from valveDetails
            valveD = db.session.query(valveDetails).filter_by(itemID=item_selected.id).first()
            rating_new = valveD.rating
            flow_direction = valveD.flowDirection_v
            # print(rating_new, flow_direction)
            # db.session.expunge_all()

            # inputs for CV and FL and % Opening
            # trim_type_gl = int(
            #     valveD.trimType_v) - 2  # subtracting 2 from trim type for globe, to match with globe CV table
            # valve_type_db = valve_type.lower()  # lower casing Globe==>globe and Butterfly==>butterfly
            # trim_type_butterfly = 0  # double offset as static, cz test data is that, should be made dynamic

            # if valve_type_db == 'globe':
            #     trim_type_globe = int(trim_type_gl)
            # else:
            #     trim_type_globe = int(trim_type_butterfly)
            characteristic_globe = 1
            rating_db = 1  # 300 as static, cz test data is 300 rating, should be made dynamic

            valve_size_mm = float(size) * 25.4

            # get data from html
            flowrate_form = float(request.form.get('flowrate'))
            inletPressure_form = float(request.form.get('iPressure'))
            outletPressure_form = float(request.form.get('oPressure'))
            inletTemp_form = float(request.form.get('iTemp'))
            specificGravity = float(request.form.get('sGravity'))
            vaporPressure = float(request.form.get('vPressure'))
            viscosity = request.form.get('viscosity')
            state = request.form.get('fState')
            criticalPressure_form = float(request.form.get('cPressure'))
            inletPipeDia_form = float(request.form.get('iPipeSize'))
            outletPipeDia_form = float(request.form.get('oPipeSize'))

            iP_mm = float(inletPipeDia_form) * 25.4
            oP_mm = float(outletPipeDia_form) * 25.4

            print(flowrate_form)
            print(state)

            if state == 'Liquid':
                print(state)

                # check whether flowrate, pres and l are in correct units
                # 1. flowrate
                if request.form.get('flowrate_unit') not in ['m3/hr', 'gpm']:
                    flowrate_liq = meta_convert_P_T_FR_L('FR', flowrate_form, request.form.get('flowrate_unit'),
                                                         'm3/hr',
                                                         specificGravity * 1000)
                    fr_unit = 'm3/hr'
                else:
                    fr_unit = request.form.get('flowrate_unit')
                    flowrate_liq = flowrate_form

                # 2. Pressure
                # A. inletPressure
                if request.form.get('iPresUnit') not in ['kpa', 'bar', 'psia']:
                    inletPressure_liq = meta_convert_P_T_FR_L('P', inletPressure_form, request.form.get('iPresUnit'),
                                                              'bar', specificGravity * 1000)
                    iPres_unit = 'bar'
                else:
                    iPres_unit = request.form.get('iPresUnit')
                    inletPressure_liq = inletPressure_form

                # B. outletPressure
                if request.form.get('oPresUnit') not in ['kpa', 'bar', 'psia']:
                    outletPressure_liq = meta_convert_P_T_FR_L('P', outletPressure_form, request.form.get('oPresUnit'),
                                                               'bar', specificGravity * 1000)
                    oPres_unit = 'bar'
                else:
                    oPres_unit = request.form.get('oPresUnit')
                    outletPressure_liq = outletPressure_form

                # C. vaporPressure
                if request.form.get('vPresUnit') not in ['kpa', 'bar', 'psia']:
                    vaporPressure = meta_convert_P_T_FR_L('P', vaporPressure, request.form.get('vPresUnit'), 'bar',
                                                          specificGravity * 1000)
                    vPres_unit = 'bar'
                else:
                    vPres_unit = request.form.get('vPresUnit')

                # 3. Length
                if request.form.get('iPipeUnit') not in ['mm', 'inch']:
                    inletPipeDia_liq = meta_convert_P_T_FR_L('L', inletPipeDia_form, request.form.get('iPipeUnit'),
                                                             'inch',
                                                             specificGravity * 1000)
                    iPipe_unit = 'inch'
                else:
                    iPipe_unit = request.form.get('iPipeUnit')
                    inletPipeDia_liq = inletPipeDia_form

                if request.form.get('oPipeUnit') not in ['mm', 'inch']:
                    outletPipeDia_liq = meta_convert_P_T_FR_L('L', outletPipeDia_form, request.form.get('oPipeUnit'),
                                                              'inch', specificGravity * 1000)
                    oPipe_unit = 'inch'
                else:
                    oPipe_unit = request.form.get('oPipeUnit')
                    outletPipeDia_liq = outletPipeDia_form

                service_conditions_sf = {'flowrate': flowrate_liq, 'flowrate_unit': fr_unit,
                                         'iPres': inletPressure_liq, 'oPres': outletPressure_liq,
                                         'iPresUnit': iPres_unit,
                                         'oPresUnit': oPres_unit, 'temp': inletTemp_form,
                                         'temp_unit': request.form.get('iTempUnit'), 'sGravity': specificGravity,
                                         'iPipeDia': inletPipeDia_liq,
                                         'oPipeDia': outletPipeDia_liq,
                                         'valveDia': size, 'iPipeDiaUnit': iPipe_unit,
                                         'oPipeDiaUnit': oPipe_unit, 'valveDiaUnit': 'inch',
                                         'C': 121, 'FR': 1, 'vPres': vaporPressure, 'Fl': 0.84, 'Ff': 0.90}

                service_conditions_1 = service_conditions_sf
                N1_val = N1[(service_conditions_1['flowrate_unit'], service_conditions_1['iPresUnit'])]
                N2_val = N2[service_conditions_1['valveDiaUnit']]

                result = CV(service_conditions_1['flowrate'], service_conditions_1['C'],
                            service_conditions_1['valveDia'],
                            service_conditions_1['iPipeDia'],
                            service_conditions_1['oPipeDia'], N2_val, service_conditions_1['iPres'],
                            service_conditions_1['oPres'],
                            service_conditions_1['sGravity'], N1_val, service_conditions_1['FR'],
                            service_conditions_1['vPres'],
                            service_conditions_1['Fl'], service_conditions_1['Ff'])

                chokedP = selectDelP(service_conditions_1['Fl'], service_conditions_1['Ff'],
                                     service_conditions_1['iPres'],
                                     service_conditions_1['vPres'], service_conditions_1['oPres'])

                # noise and velocities
                summation1 = summation(C=113.863, inletPressure=1000000, outletPressure=900000, density=974.1,
                                       vaporPressure=10000,
                                       speedS=4000, massFlowRate=27.06, Fd=0.23, densityPipe=7800, speedSinPipe=5000,
                                       wallThicknessPipe=0.0002, internalPipeDia=0.1000, seatDia=0.1, valveDia=0.1,
                                       densityAir=1.293,
                                       holeDia=0, rW=0.25)

                # Power Level
                outletPressure_p = meta_convert_P_T_FR_L('P', outletPressure_form, request.form.get('oPresUnit'),
                                                         'psia', specificGravity * 1000)
                inletPressure_p = meta_convert_P_T_FR_L('P', inletPressure_form, request.form.get('iPresUnit'),
                                                        'psia', specificGravity * 1000)
                pLevel = power_level_liquid(inletPressure_p, outletPressure_p, specificGravity, result)

                # convert flowrate and dias for velocities
                flowrate_v = meta_convert_P_T_FR_L('FR', flowrate_form, request.form.get('flowrate_unit'), 'm3/hr',
                                                   1000)
                inletPipeDia_v = meta_convert_P_T_FR_L('L', inletPipeDia_form, request.form.get('iPipeUnit'), 'inch',
                                                       1000)
                outletPipeDia_v = meta_convert_P_T_FR_L('L', outletPipeDia_form, request.form.get('oPipeUnit'), 'inch',
                                                        1000)

                # convert pressure for tex, p in bar, l in in
                inletPressure_v = meta_convert_P_T_FR_L('P', inletPressure_form, request.form.get('iPresUnit'), 'bar',
                                                        1000)
                outletPressure_v = meta_convert_P_T_FR_L('P', outletPressure_form, request.form.get('oPresUnit'), 'bar',
                                                         1000)

                tEX = trimExitVelocity(inletPressure_v, outletPressure_v, specificGravity, "Contoured", 'other')
                iVelocity, oVelocity, pVelocity = getVelocity(flowrate_v, inletPipeDia_v, outletPipeDia_v,
                                                              valve_size_mm)

                data = {'cv': round(result, 3),
                        'percent': 80,
                        'spl': round(summation1, 3),
                        'iVelocity': iVelocity,
                        'oVelocity': round(oVelocity, 3), 'pVelocity': round(pVelocity, 3), 'choked': round(chokedP, 3),
                        'texVelocity': round(tEX, 3)}

                # load case data with item ID
                new_case = itemCases(flowrate=flowrate_form, iPressure=inletPressure_form,
                                     oPressure=outletPressure_form,
                                     iTemp=inletTemp_form, sGravity=specificGravity,
                                     vPressure=vaporPressure, viscosity=viscosity, vaporMW=None, vaporInlet=None,
                                     CV=round(result, 3), openPercent=data['percent'],
                                     valveSPL=round(summation1, 2), iVelocity=round(iVelocity, 2),
                                     oVelocity=round(oVelocity, 2), pVelocity=round(pVelocity, 2),
                                     chokedDrop=round(chokedP, 3),
                                     Xt=None, warning=1, trimExVelocity=data['texVelocity'],
                                     sigmaMR=pLevel, reqStage=None, fluidName=None, fluidState=state,
                                     criticalPressure=criticalPressure_form, iPipeSize=inletPipeDia_form,
                                     oPipeSize=outletPipeDia_form,
                                     iPipeSizeSch=inletPipeDia_form, oPipeSizeSch=outletPipeDia_form,
                                     item=item_selected)

                db.session.add(new_case)
                db.session.commit()

                print(data)
                # print(f"The calculated Cv is: {result}")
                return redirect(url_for('valveSizing'))

            elif state == 'Gas':
                print(state)

                # Unit Conversion
                # 1. Flowrate

                # 2. Pressure

                # logic to choose which formula to use - using units of flowrate and sg
                fl_unit = request.form.get('flowrate_unit')
                if fl_unit in ['m3/hr', 'scfh', 'gpm']:
                    fl_bin = 1
                else:
                    fl_bin = 2

                sg_unit = request.form.get('sg')
                if sg_unit == 'sg':
                    sg_bin = 1
                else:
                    sg_bin = 2

                def chooses_gas_fun(flunit, sgunit):
                    eq_dict = {(1, 1): 1, (1, 2): 2, (2, 1): 3, (2, 2): 4}
                    return eq_dict[(flunit, sgunit)]

                sg__ = chooses_gas_fun(fl_bin, sg_bin)

                if sg__ == 1:
                    # to be converted to scfh, psi, R, in
                    # 3. Pressure
                    inletPressure = meta_convert_P_T_FR_L('P', inletPressure_form, request.form.get('iPresUnit'),
                                                          'psia',
                                                          1000)
                    outletPressure = meta_convert_P_T_FR_L('P', outletPressure_form, request.form.get('oPresUnit'),
                                                           'psia',
                                                           1000)
                    # 4. Length
                    inletPipeDia = meta_convert_P_T_FR_L('L', inletPipeDia_form, request.form.get('iPipeUnit'), 'inch',
                                                         1000)
                    outletPipeDia = meta_convert_P_T_FR_L('L', outletPipeDia_form, request.form.get('oPipeUnit'),
                                                          'inch',
                                                          1000)
                    # 1. Flowrate
                    flowrate = meta_convert_P_T_FR_L('FR', flowrate_form, request.form.get('flowrate_unit'), 'scfh',
                                                     1000)
                    # 2. Temperature
                    inletTemp = meta_convert_P_T_FR_L('T', inletTemp_form, request.form.get('iTempUnit'), 'R',
                                                      1000)
                elif sg__ == 2:
                    # to be converted to m3/hr, kPa, C, in
                    # 3. Pressure
                    inletPressure = meta_convert_P_T_FR_L('P', inletPressure_form, request.form.get('iPresUnit'), 'kpa',
                                                          1000)
                    outletPressure = meta_convert_P_T_FR_L('P', outletPressure_form, request.form.get('oPresUnit'),
                                                           'kpa',
                                                           1000)
                    # 4. Length
                    inletPipeDia = meta_convert_P_T_FR_L('L', inletPipeDia_form, request.form.get('iPipeUnit'), 'inch',
                                                         1000)
                    outletPipeDia = meta_convert_P_T_FR_L('L', outletPipeDia_form, request.form.get('oPipeUnit'),
                                                          'inch',
                                                          1000)
                    # 1. Flowrate
                    flowrate = meta_convert_P_T_FR_L('FR', flowrate_form, request.form.get('flowrate_unit'), 'm3/hr',
                                                     1000)
                    # 2. Temperature
                    inletTemp = meta_convert_P_T_FR_L('T', inletTemp_form, request.form.get('iTempUnit'), 'C',
                                                      1000)
                elif sg__ == 3:
                    # to be converted to lbhr, psi, F, in
                    # 3. Pressure
                    inletPressure = meta_convert_P_T_FR_L('P', inletPressure_form, request.form.get('iPresUnit'),
                                                          'psia',
                                                          1000)
                    outletPressure = meta_convert_P_T_FR_L('P', outletPressure_form, request.form.get('oPresUnit'),
                                                           'psia',
                                                           1000)
                    # 4. Length
                    inletPipeDia = meta_convert_P_T_FR_L('L', inletPipeDia_form, request.form.get('iPipeUnit'), 'inch',
                                                         1000)
                    # print(request.form.get('iPipeUnit'))
                    outletPipeDia = meta_convert_P_T_FR_L('L', outletPipeDia_form, request.form.get('oPipeUnit'),
                                                          'inch',
                                                          1000)
                    # 1. Flowrate
                    flowrate = meta_convert_P_T_FR_L('FR', flowrate_form, request.form.get('flowrate_unit'), 'lb/hr',
                                                     1000)
                    # 2. Temperature
                    inletTemp = meta_convert_P_T_FR_L('T', inletTemp_form, request.form.get('iTempUnit'), 'F',
                                                      1000)
                else:
                    # to be converted to kg/hr, bar, K, in
                    # 3. Pressure
                    inletPressure = meta_convert_P_T_FR_L('P', inletPressure_form, request.form.get('iPresUnit'), 'bar',
                                                          1000)
                    outletPressure = meta_convert_P_T_FR_L('P', outletPressure_form, request.form.get('oPresUnit'),
                                                           'bar',
                                                           1000)
                    # 4. Length
                    inletPipeDia = meta_convert_P_T_FR_L('L', inletPipeDia_form, request.form.get('iPipeUnit'), 'inch',
                                                         1000)
                    outletPipeDia = meta_convert_P_T_FR_L('L', outletPipeDia_form, request.form.get('oPipeUnit'),
                                                          'inch',
                                                          1000)
                    # 1. Flowrate
                    flowrate = meta_convert_P_T_FR_L('FR', flowrate_form, request.form.get('flowrate_unit'), 'kg/hr',
                                                     1000)
                    # 2. Temperature
                    inletTemp = meta_convert_P_T_FR_L('T', inletTemp_form, request.form.get('iTempUnit'), 'K',
                                                      1000)

                # python sizing function - gas

                inputDict_4 = {"inletPressure": inletPressure, "outletPressure": outletPressure,
                               "gamma": specificGravity,
                               "C": 236,
                               "valveDia": size,
                               "inletDia": inletPipeDia,
                               "outletDia": outletPipeDia, "xT": float(request.form.get('xt')),
                               "compressibilityFactor": 1,
                               "flowRate": flowrate,
                               "temp": inletTemp, "sg": float(request.form.get('sg_value')), "sg_": sg__}

                inputDict = inputDict_4

                Cv1 = Cv_gas(inletPressure=inputDict['inletPressure'], outletPressure=inputDict['outletPressure'],
                             gamma=inputDict['gamma'],
                             C=inputDict['C'], valveDia=inputDict['valveDia'], inletDia=inputDict['inletDia'],
                             outletDia=inputDict['outletDia'], xT=inputDict['xT'],
                             compressibilityFactor=inputDict['compressibilityFactor'],
                             flowRate=inputDict['flowRate'], temp=inputDict['temp'], sg=inputDict['sg'],
                             sg_=inputDict['sg_'])

                xChoked = xChoked_gas(gamma=inputDict['gamma'], C=inputDict['C'], valveDia=inputDict['valveDia'],
                                      inletDia=inputDict['inletDia'], outletDia=inputDict['outletDia'],
                                      xT=inputDict['xT'])

                # noise and velocities
                # convert values to noise units - Pressure in Pa, density in kg/m3, speed in m/s, flowrate in m3/hr, L in m
                inletPressure_noise = meta_convert_P_T_FR_L('P', inletPressure_form, request.form.get('iPresUnit'),
                                                            'pa',
                                                            1000)
                outletPressure_noise = meta_convert_P_T_FR_L('P', outletPressure_form, request.form.get('oPresUnit'),
                                                             'pa',
                                                             1000)
                vaporPressure_noise = meta_convert_P_T_FR_L('P', vaporPressure, request.form.get('vPresUnit'), 'pa',
                                                            1000)
                flowrate_noise = meta_convert_P_T_FR_L('FR', flowrate_form, request.form.get('flowrate_unit'), 'm3/hr',
                                                       1000)
                inletPipeDia_noise = meta_convert_P_T_FR_L('L', inletPipeDia_form, request.form.get('iPipeUnit'), 'm',
                                                           1000)
                size_noise = meta_convert_P_T_FR_L('L', size, 'inch', 'm', 1000)

                # summation1 = summation(C=113.863, inletPressure=inletPressure_noise, outletPressure=outletPressure_noise, density=specificGravity*1000,
                #                        vaporPressure=vaporPressure_noise,
                #                        speedS=4000, massFlowRate=flowrate_noise, Fd=0.23, densityPipe=7800, speedSinPipe=5000,
                #                        wallThicknessPipe=0.0002, internalPipeDia=inletPipeDia_noise, seatDia=0.1, valveDia=size_noise,
                #                        densityAir=1.293,
                #                        holeDia=0, rW=0.25)

                summation1 = summation(C=113.863, inletPressure=1000000, outletPressure=900000, density=974.1,
                                       vaporPressure=10000,
                                       speedS=4000, massFlowRate=27.06, Fd=0.23, densityPipe=7800, speedSinPipe=5000,
                                       wallThicknessPipe=0.0002, internalPipeDia=0.1000, seatDia=0.1, valveDia=0.1,
                                       densityAir=1.293,
                                       holeDia=0, rW=0.25)

                # Power Level
                # getting fr in lb/s
                flowrate_p = meta_convert_P_T_FR_L('FR', flowrate_form, request.form.get('flowrate_unit'), 'lb/hr',
                                                   specificGravity * 1000) / 3600
                inletPressure_p = meta_convert_P_T_FR_L('P', inletPressure_form, request.form.get('iPresUnit'), 'psia',
                                                        1000)
                outletPressure_p = meta_convert_P_T_FR_L('P', outletPressure_form, request.form.get('oPresUnit'),
                                                         'psia',
                                                         1000)
                pLevel = power_level_gas(specificGravity, inletPressure_p, outletPressure_p, flowrate_p)

                # convert flowrate and dias for velocities
                flowrate_v = meta_convert_P_T_FR_L('FR', flowrate_form, request.form.get('flowrate_unit'), 'm3/hr',
                                                   1000)
                inletPipeDia_v = meta_convert_P_T_FR_L('L', inletPipeDia_form, request.form.get('iPipeUnit'), 'inch',
                                                       1000)
                outletPipeDia_v = meta_convert_P_T_FR_L('L', outletPipeDia_form, request.form.get('oPipeUnit'), 'inch',
                                                        1000)

                iVelocity, oVelocity, pVelocity = getVelocity(flowrate_v / (2200 * specificGravity), inletPipeDia_v,
                                                              outletPipeDia_v,
                                                              size)

                # convert pressure for tex, p in bar, l in in
                inletPressure_v = meta_convert_P_T_FR_L('P', inletPressure_form, request.form.get('iPresUnit'), 'bar',
                                                        1000)
                outletPressure_v = meta_convert_P_T_FR_L('P', outletPressure_form, request.form.get('oPresUnit'), 'bar',
                                                         1000)
                print(f"Outlet Pressure V{outletPressure_v}")

                tEX = trimExitVelocity(inletPressure_v, outletPressure_v, 1000, "Contoured",
                                       'other')
                print(summation1)

                data = {'cv': round(Cv1, 3),
                        'percent': 83,
                        'spl': round(summation1, 3),
                        'iVelocity': round(iVelocity, 3),
                        'oVelocity': round(oVelocity, 3), 'pVelocity': round(pVelocity, 3), 'choked': round(xChoked, 3),
                        'texVelocity': round(tEX, 3)}

                # load case data with item ID
                new_case = itemCases(flowrate=flowrate_form, iPressure=inletPressure_form,
                                     oPressure=outletPressure_form,
                                     iTemp=inletTemp_form, sGravity=specificGravity,
                                     vPressure=vaporPressure, viscosity=viscosity,
                                     vaporMW=float(request.form.get('sg_value')), vaporInlet=None,
                                     CV=round(Cv1, 3), openPercent=data['percent'],
                                     valveSPL=data['spl'], iVelocity=data['iVelocity'], oVelocity=data['oVelocity'],
                                     pVelocity=data['pVelocity'],
                                     chokedDrop=data['choked'],
                                     Xt=float(request.form.get('xt')), warning=1, trimExVelocity=data['texVelocity'],
                                     sigmaMR=pLevel, reqStage=None, fluidName=None, fluidState=state,
                                     criticalPressure=round(criticalPressure_form, 3), iPipeSize=inletPipeDia_form,
                                     oPipeSize=outletPipeDia_form,
                                     iPipeSizeSch=inletPipeDia_form, oPipeSizeSch=outletPipeDia_form,
                                     item=item_selected)
                db.session.add(new_case)
                db.session.commit()

                return redirect(url_for('valveSizing'))

        return render_template("Valve Sizing 2.html", title='Valve Sizing', cases=itemCases_1, item_d=item_selected,
                               fluid=fluid_data, len_c=range(case_len), length_unit=length_unit_list)


@app.route('/actuator-sizing', methods=["GET", "POST"])
def actuatorSizing():
    return render_template("Actuator Sizing.html", title='Actuator Sizing', item_d=selected_item)


@app.route('/accessories', methods=["GET", "POST"])
def accessories():
    return render_template("Accessories & Fittings.html", title='Accessories', item_d=selected_item)


@app.route('/item-notes', methods=["GET", "POST"])
def itemNotes():
    if request.method == 'POST':
        data = request.form.get('abc')
        return f"{data}"
    return render_template("Item Notes.html", title='Item Notes', item_d=selected_item)


@app.route('/project-notes', methods=["GET", "POST"])
def projectNotes():
    # with app.app_context():
    #     Cv_value = db.session.query(globeTable).filter_by(trimTypeID=2, flow=0, charac=0,
    #                                                       size=6, coeffID=0)
    #     Fl_value = db.session.query(globeTable).filter_by(trimTypeID=2, flow=0, charac=0,
    #                                                       size=6, coeffID=1)

    return render_template("Project Notes.html", title='Project Notes', item_d=selected_item)


@app.route('/delete-cases/<case_id>', methods=["GET", "POST"])
def deleteCase(case_id):
    with app.app_context():
        entry_to_delete = itemCases.query.get(case_id)
        db.session.delete(entry_to_delete)
        db.session.commit()
    return redirect(url_for("valveSizing"))


@app.route('/add-item', methods=['GET', 'POST'])
def addItem():
    with app.app_context():
        series = valveSeries.query.all()
        size = valveSize.query.all()
        type = valveStyle.query.all()
        rating_1 = rating.query.all()
        material = materialMaster.query.all()

        if request.method == "POST":
            alt = request.form.get('alt')
            tag_no = request.form.get('tag_no')
            serial = int(request.form.get('series'))
            size__ = int(request.form.get('size'))
            model = request.form.get('model')
            type__ = int(request.form.get('type'))
            rating__ = int(request.form.get('rating'))
            material__ = int(request.form.get('material'))
            uPrice = request.form.get('unitPrice')
            qty = request.form.get('quantity')
            projectID = int(request.form.get('projectID'))

            model_element = db.session.query(modelMaster).filter_by(name=model).first()
            project_element = db.session.query(projectMaster).filter_by(id=projectID).first()
            serial_element = db.session.query(valveSeries).filter_by(id=serial).first()
            size_element = db.session.query(valveSize).filter_by(id=size__).first()
            rating_element = db.session.query(rating).filter_by(id=rating__).first()
            material_element = db.session.query(materialMaster).filter_by(id=material__).first()
            type_element = db.session.query(valveStyle).filter_by(id=type__).first()

            item4 = {"alt": alt, "tagNo": tag_no, "serial": serial_element, "size": size_element,
                     "model": model_element, "type": type_element, "rating": rating_element,
                     "material": material_element, "unitPrice": uPrice, "Quantity": qty, "Project": project_element}

            itemsList = [item4]

            for i in itemsList:
                new_item = itemMaster(alt=i['alt'], tag_no=i['tagNo'], serial=i['serial'], size=i['size'], model=i['model'],
                                      type=i['type'], rating=i['rating'], material=i['material'], unit_price=i['unitPrice'],
                                      qty=i['Quantity'], project=i['Project'])

                db.session.add(new_item)
                db.session.commit()

            return redirect(url_for('home'))

        return render_template('addItem.html', item_d=selected_item, series=series, size=size, type=type, rating=rating_1,
                               material=material)


@app.route('/generate-csv', methods=['GET', 'POST'])
def generate_csv():
    with app.app_context():
        item_selected = db.session.query(itemMaster).filter_by(id=selected_item.id).first()
        itemCases_1 = db.session.query(itemCases).filter_by(itemID=item_selected.id).all()
        date = datetime.date.today().strftime("%d-%m-%Y -- %H-%M-%S")
        size__ = db.session.query(valveSize).filter_by(id=item_selected.sizeID).first().size
        rating__ = db.session.query(rating).filter_by(id=item_selected.ratingID).first().size
        project__ = db.session.query(projectMaster).filter_by(id=item_selected.projectID).first()
        customer__ = db.session.query(customerMaster).filter_by(id=project__.customerID).first().name

        fields___ = ['Flow Rate', 'Inlet Pressure', 'Outlet Pressure', 'Inlet Temperature', 'Specific Gravity',
                     'Viscosity', 'Vapor Pressure', 'Xt', 'Calculated Cv', 'Open %', 'Valve SPL', 'Inlet Velocity',
                     'Outlet Velocity', 'Trim Exit Velocity', 'Tag Number', 'Item Number', 'Fluid State',
                     'Critical Pressure',
                     'Inlet Pipe Size', 'Outlet Pipe Size', 'Valve Size', 'Rating', 'Quote No.', 'Work Order No.',
                     'Customer']

        # other_fields_row = [item_selected.tag_no, item_selected.id, itemCases_1[0].fState,
        #                     itemCases_1[0].criticalPressure,
        #                     itemCases_1.iPipeSize, itemCases_1.oPipeSize, size__, rating__, project__.quote,
        #                     project__.work_order,
        #                     customer__]

        # data rows of csv file
        rows___ = []
        for i in itemCases_1[:3]:
            case_list = [i.flowrate, i.iPressure, i.oPressure, i.iTemp, i.sGravity, i.viscosity, i.vPressure, i.Xt,
                         i.CV, i.openPercent, i.valveSPL,
                         i.iVelocity, i.oVelocity, i.trimExVelocity, item_selected.tag_no, item_selected.id,
                         itemCases_1[0].fluidState, itemCases_1[0].criticalPressure,
                         itemCases_1[0].iPipeSize, itemCases_1[0].oPipeSize, size__, rating__, project__.quote,
                         project__.work_order,
                         customer__]
            rows___.append(case_list)

        pd = pandas.DataFrame(rows___, columns=fields___)
        pd.to_csv(f"C:/Users/FCC/Desktop/case_data_{item_selected.id}-{len(itemCases_1)}-{date}.csv")

    return redirect(url_for('valveSizing'))


if __name__ == "__main__":
    app.run(debug=True)




# Hi da Paandi - github testdddaaakkkkkkkkkkkkkkkk