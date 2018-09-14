from os import path
import tkinter as tk
from tkinter import scrolledtext
from  tkinter import *
from tkinter import filedialog
from enum import Enum
from ntpath import basename
import re
import csv
import plotly
import plotly.graph_objs as go
import datetime
from collections import OrderedDict
import os
#Message Handle
import sys
import easygui #used for dialog box
import math

def DispalyMessage(Message,Title):
    easygui.msgbox(Message,title= Title)

def DisplayYesOrNo(Message,Title):
    msg = Message
    title = Title
    choices = ["No", "Yes"]
    choice = easygui.choicebox(msg, title, choices)
    if choice == "No":
        DispalyMessage("Application is closing...","Info")
        sys.exit(0)
    else:
        DispalyMessage("This data may not display correct results","Info")


def ErrorCheckSingle(row,FoundError):
    for I in range(1, len(row)):
        try:
            if isinstance(float(row[I]), float):
                print("")
        except:
            if FoundError != True:
                DispalyMessage("String Found In data, Changing value to Zero", "Warning")
                print(row[I])
                return True
            else:
                row[I] = 0;
                print(row)
                return FoundError

def MonthIndexSwitch(DateIndex):
    switcher = {
        1: "January",
        2: "Febuary",
        3: "March",
        4: "April",
        5: "May",
        6: "June",
        7: "July",
        8: "August",
        9: "September",
        10: "October",
        11: "November",
        12: "December"
    }
    return switcher.get(DateIndex,"nothing")

def CalculateMonth():
    for H in HouseList:
        for I in range(0, len(Date)):
            Month = Date[I].month
            H.HouseMonthValue[Month - 1] += H.HouseValues[I]
        H.TotalUsage = sum(H.HouseMonthValue)
        print(H.HouseMonthValue)
        print(len(H.HouseMonthValue))

def CalcualteMonthSingle():
    for I in range(0,len(Date)):
        Month = Date[I].month
        Shouse[0].GasValuesMonthly[Month-1] += float(Shouse[0].GasValues[I])
        Shouse[0].ElectricityValueMonthly[Month-1] += float(Shouse[0].ElectricityValue[I])
def CalculateMonthlyCost(FuelType):
    for H in HouseList:
        HS = HouseDictionary[H.PrimaryKey]
        Days = []
        if FuelType != "Gas":
            for D in Date:
                m = D.month
                Days.append((H.HouseValues[Date.index(D)] * HS.ElecUsageRate + HS.ElecStandingCharge) / 100)
                HS.HouseMonthValue[m - 1] += Days[Date.index(D)]
        else:
            for D in Date:
                m = D.month
                Days.append((H.HouseValues[Date.index(D)] * HS.GasUsageRate + HS.GasStandingCharge) / 100)
                HS.HouseMonthValue[m - 1] += Days[Date.index(D)]

def CalAvarege(HouseData):
    last = float(0)
    for I in HouseData:
        last += float(I)
    return float(last / float(len(HouseData)))

def CalStandardDeviation(HouseData,Avrg):
    StageTwo = []
    ST = float
    last = float(0)
    for v in HouseData:
        ST = float(v) - Avrg
        StageTwo.append(ST * ST)
    for v in StageTwo:
        last += v
    return math.sqrt(last / len(StageTwo))


'''
multi choice rseturns False if user selects 'NO'
//add customisation for on select 'Yes'
'''


'''
Object classes are used to sore data about the given house and all its properties
The multi House Object is used to Store Information for the data files with one house and two fuel types
The Single House Object is used for Files With One Fuel type and X number of houses
'''
Shouse = []
HouseList = [] #Array of house objects# #
Date = [] #Array Of Dates
class House(object):    # HouseMonthValue is the sum of each month
    def __init__(self,PrimaryKey=None,HouseName=None,HouseValues=None,HouseMonthValue=None,HouseMonthValues=None,TotalUsage = None):
        self.PrimaryKey = PrimaryKey
        self.HouseName = HouseName or str
        self.HouseValues = HouseValues or []
        self.HouseMonthValue = HouseMonthValue or [0,0,0,0,0,0,0,0,0,0,0,0]
        self.HouseMonthValues = HouseMonthValues or []
        self.TotalUsage = TotalUsage or float

class SingleHouse(object):
    def __init__(self,GasValues=None,ElectricityValue=None,GasValuesMonthly=None,ElectricityValueMonthly=None):
        self.GasValues = GasValues or []
        self.ElectricityValue = ElectricityValue or []
        self.GasValuesMonthly = GasValuesMonthly or [0,0,0,0,0,0,0,0,0,0,0,0]
        self.ElectricityValueMonthly = ElectricityValueMonthly or [0,0,0,0,0,0,0,0,0,0,0,0]

SupHouseList = []
HouseDictionary = {}
class SupplierHouse(object):
    def __init__(self,PrimaryKey=None, HouseName=None,supplier = None,ElecUsageRate=None,ElecStandingCharge=None,GasUsageRate=None,GasStandingCharge=None,HouseMonthValue=None):
        self.PrimaryKey = PrimaryKey
        self.HouseName = HouseName or str
        self.supplier = supplier or str
        self.ElecUsageRate = ElecUsageRate or float
        self.ElecStandingCharge = ElecStandingCharge or float
        self.GasUsageRate = GasUsageRate or float
        self.GasStandingCharge = GasStandingCharge or float
        self.HouseMonthValue = HouseMonthValue or [0,0,0,0,0,0,0,0,0,0,0,0]

'''
This file is written as a class, meaning it is defined using the 'class' keyword. Practically, 
the file is a fairly linear collection of functions, so this doesn't difr much from a linear
script. The main difrence is that variables are prefixed with 'self.' and are rerred to
as 'fields'. Functions are rerred to as 'methods', and are called using an instance of the 
class they belong to, in this case EnergyMonitor. Methods are also prefixed with 'self.' 
when called inside other methods in the class. 
'''
class EnergyMonitor():
    FuelType = str()
    HasHouseSuppliersFile = False
    HasHouseDataFile = False
    '''
    The init method is called when a class is instantiated. In this case the init method
    is creating some data structures, and creating the Tkinter widgets needed to display the
    UI correctly.
    '''
    def __init__(self, parent):
        self.parent = parent
        self.welcome_label = tk.Label(self.parent, text='Welcome to the Energy Monitor!', font=('Calibri', 32))
        self.welcome_label.configure(background='#c6e2ff')
        self.welcome_label.pack()
        self.message_label = tk.Label(self.parent, text='Please use the dialog below to load a CSV file, which will be displayed ' +
                                          'in the box below.', font=('Calibri', 14), wraplength=540)
        self.message_label.configure(background='#c6e2ff')
        self.message_label.pack(pady=20)
        self.btn_file = tk.Button(self.parent, text="Load file", command=self.load_file)
        self.btn_file.pack(pady=15)
        self.InfoLabel = tk.Label(self.parent, text='', font=('Calibri', 10))
        self.InfoLabel.configure(background='#c6e2ff')
        self.InfoLabel.pack()
        self.scrolled_text = tk.scrolledtext.ScrolledText(self.parent, width=40, height=10)
        self.scrolled_text.pack()
        #Show Single Button
        self.btn_graph_annual = tk.Button(self.parent, text='Annual Usage Single',
                                          command=self.generate_annual_graph_singlehouse)
        self.btn_graph_annual.pack_forget()
        #Show Multi button
        self.btn_graph_annual_multi = tk.Button(self.parent, text='Annual Usage Multi',
                                                command=self.generate_annual_graph_multihouse)
        self.btn_graph_annual_multi.pack_forget()
        self.btn_Next = tk.Button(self.parent, text='Show Me This Month',
                                  command=self.gen_monthly_Multi)
        #Pie
        self.btn_graph_annual_pie = tk.Button(self.parent, text='Annual Usage Multi PIE',
                                                command=self.generate_MultiHouse_Pie)
        self.btn_graph_annual_pie.pack_forget()
        #Monthly Interface///
        self.btn_graph_monthly_multi = tk.Button(self.parent, text='Monthly Usage Multi',
                                                command=self.generate_monthly_graph_multihouse)
        self.btn_graph_monthly_multi.pack_forget()
        self.MonthSelection = Spinbox(from_=1, to=12, width=5)
        #/////////////////////
        #Month By year Interface///
        self.btn_graph_annual_monthly_multi = tk.Button(self.parent, text='Annual Monthly Usage Multi',
                                                 command=self.Annual_Monthly)
        self.btn_graph_annual_monthly_multi.pack_forget()
        #Single
        self.btn_Show_Single_Metrics = tk.Button(self.parent, text="Single House Metrics",
                                                        command=self.ShowSingleMetrics)
        self.btn_Show_Single_Metrics.pack_forget()
        self.btn_graph_annual_monthly_single = tk.Button(self.parent, text="Annual Monthly Usage Single",
                                                         command=self.Genarate_MonthlyGrath_Single)
        self.btn_graph_annual_monthly_single.pack_forget()
        self.btn_Multi_Metrics = tk.Button(self.parent, text="Per House Metrics",
                                                         command=self.generate_metrics)
        self.btn_Multi_Metrics.pack_forget()
        self.btn_MultiHouse_Metrics = tk.Button(self.parent, text = "Show All Metrics",
                                                command=self.ShowMultiHouseMetrics)
        self.btn_MultiHouse_Metrics.forget()
        self.Back_Multi_btn = tk.Button(self.parent, text="Back",
                                  command=self.Back_Multi)
        self.Back_Multi_btn.forget()
        self.Back_Single_btn = tk.Button(self.parent, text="Back",
                                        command=self.Back_Single)
        self.Back_Single_btn.forget()
        self.btn_Daily_Cost_Graph = tk.Button(self.parent,text="Show Total cost graph",command=self.ShowCostGraph)
        self.btn_Daily_Cost_Graph.forget()
        self.btn_Monthly_Cost_Graph = tk.Button(self.parent, text="Show Monthly Cost Graph", command=self.ShowMonthlyCostGraph)
        self.btn_Monthly_Cost_Graph.forget()
        self.btn_Show_Cost_Metrics = tk.Button(self.parent,text="Show Cost Metrics", command=self.DisplayCostMetrix)
        self.btn_Show_Cost_Metrics.forget()
        self.btn_Show_PerHouse_CostMetrics = tk.Button(self.parent,text="Show Per House Metrics",command=self.DispalyPerHouseCostMetrics)
        self.btn_Show_PerHouse_CostMetrics.forget()
        #Menues:
        self.btn_Show_Usage_Multi_Menu = tk.Button(self.parent,text="View Usage Graphs",command=self.ShowUsageMenu)
        self.btn_Show_Usage_Multi_Menu.forget()
        self.btn_Show_Metrics_Multi_Menu = tk.Button(self.parent, text="View Usage Metrics", command=self.ShowUsageMetricsMenu)
        self.btn_Show_Metrics_Multi_Menu.forget()
        self.btn_Cost_Menu = tk.Button(self.parent, text="Show Cost Info", command=self.ShowCostMenu)
        self.btn_Cost_Menu.forget()



    def HideMenuse(self):
        self.btn_Show_Usage_Multi_Menu.forget()
        self.btn_Show_Metrics_Multi_Menu.forget()
        self.btn_Cost_Menu.forget()
    def ShowUsageMenu(self):
        self.HideMenuse()
        self.btn_graph_annual_multi.pack(pady=10)
        self.btn_graph_annual_pie.pack(pady=10)
        self.btn_graph_monthly_multi.pack(pady=10)
        self.btn_graph_annual_monthly_multi.pack(pady=10)
        self.Back_Multi_btn.pack(pady=10)
    def ShowUsageMetricsMenu(self):
        self.HideMenuse()
        self.btn_Multi_Metrics.pack(pady=10)
        self.btn_MultiHouse_Metrics.pack(pady=10)
        self.Back_Multi_btn.pack(pady=10)
    def ShowCostMenu(self):
        self.HideMenuse()
        self.btn_Daily_Cost_Graph.pack(pady=10)
        self.btn_Monthly_Cost_Graph.pack(pady=10)
        self.btn_Show_Cost_Metrics.pack(pady=10)
        self.btn_Show_PerHouse_CostMetrics.pack(pady=10)
        self.Back_Multi_btn.pack(pady=10)
    def Back_Single(self):
        self.Back_Single_btn.forget()
        self.scrolled_text.delete('1.0',END)
        self.scrolled_text.config(width= 40, height= 10)
        self.ShowSingleButtons()
    def Back_Multi(self):
        self.HideMultiButtons()
        self.btn_Show_Usage_Multi_Menu.pack(pady=10)
        self.btn_Show_Metrics_Multi_Menu.pack(pady=10)
        self.scrolled_text.delete('1.0',END)
        self.scrolled_text.config(width= 40, height= 10)
        if self.HasHouseSuppliersFile == True:
            self.btn_Cost_Menu.pack(pady=10)
    def ShowMultiButtons(self):
        self.btn_Show_Usage_Multi_Menu.pack(pady=10)
        self.btn_Show_Metrics_Multi_Menu.pack(pady=10)
        if self.HasHouseSuppliersFile == True:
            self.btn_Cost_Menu.pack(pady=10)
    def HideMultiButtons(self):
        self.btn_graph_annual_multi.forget()
        self.btn_graph_annual_pie.forget()
        self.btn_graph_monthly_multi.forget()
        self.btn_graph_annual_monthly_multi.forget()
        self.btn_Multi_Metrics.forget()
        self.btn_MultiHouse_Metrics.forget()
        self.btn_Next.forget()
        self.Back_Multi_btn.forget()
        self.MonthSelection.forget()
        self.btn_Daily_Cost_Graph.forget()
        self.btn_Cost_Menu.forget()
        self.btn_Monthly_Cost_Graph.forget()
        self.MonthSelection.forget()
        self.btn_Next.forget()
        self.Back_Multi_btn.forget()
        self.btn_Show_Cost_Metrics.forget()
        self.btn_Show_PerHouse_CostMetrics.forget()
    def ShowSingleButtons(self):
        self.HideMenuse()
        self.btn_graph_annual.pack(pady=5)
        self.btn_graph_annual_monthly_single.pack(pady=5)
        self.btn_Show_Single_Metrics.pack(pady=5)
    def HideSingleButtons(self):
        self.btn_graph_annual.forget()
        self.btn_graph_annual_monthly_single.forget()
        self.btn_Show_Single_Metrics.forget()



    def load_file(self, file=None):

        if file is None:
            #file = filedialog.askopenfilename(initialdir=path.dirname(__file__))

            #Read from scroll box
            fileName = self.scrolled_text.get(1.0,tk.END)
            fileDir = "\\Users\\l-bosier\\smart-energy-usage\\resources\\"
            fileName = str(fileName[:-1])

            print(fileDir + fileName)
            if os.path.exists(fileDir + fileName):
                file = fileDir+fileName
                print("Valid")
            else:
                DispalyMessage("File is not readable in its current format Converting to .txt", "WARNING")
                raise ValueError("This file does not exist or is not readable.")

       # elif not path.isfile(file):
            # Here we are raising an Error. Within Python this means that the application
            # cannot recover the state of the application, and it should not continue processing.
            # Since this application runs in a HUI loop, the program will not actually close,
            # but it will not be able to do further processing.

        # This is a regular expression, essentially a form of pattern-matching that will
        # allow us to check that the file name of the loaded file is in the correct format.
        # For more information about regular expressions, see https://www.learnpython.org/en/Regular_Expressions
        re_single_house = re.compile('^(.*?)_both_daily$')
        re_multiple_houses = re.compile('^multi_(gas|electricity)_daily$')
        re_suppliers_house = re.compile('^(.*?)suppliers')

        filename = basename(file).split('.')[0]
        single_match = re_single_house.search(filename)
        multiple_match = re_multiple_houses.search(filename)
        suppliers_match = re_suppliers_house.search(filename)

        '''
        Here we are checking whether or not the file is a single or multiple house file. 
        '''
        if single_match is not None:
            # Forget
            self.HideMultiButtons()
            self.process_single_file(file, single_match.group(1))
            self.ShowSingleButtons()
        elif multiple_match is not None:
            self.process_multi_file(file, multiple_match.group(1))
            # Forget
            self.HideSingleButtons()
            # Init
            self.ShowMultiButtons()
        elif suppliers_match is not None:
            self.process_supplier_file(file)
        else:
            DispalyMessage("Error Unsuported File Type\nPlease press 'OK' try another type!","ERROR")
            raise ValueError("File format is not correct, must be one of '{fuel-type}_daily.csv"
                              + " or '{house-id}_both_daily.csv is invalid")

    '''
    This method is a specific case from the above load method, which was capable of checking for difrent
    types of files. This method is specifically for dealing with one house files, which contain 
    both gas and electricity data for one house. The output of the method is to populate data_container
    with the relevant data, once it has been validated. 
    '''
    def process_single_file(self, file, house_id):
        print("This file is a single house with both fuel types. The house id is '%s'." % house_id)
        print("Deleting old data")
        self.btn_file.configure(text="Load File")
        Date.clear()
        HouseList.clear()
        SupHouseList.clear()
        Shouse.clear()
        Shouse.append(SingleHouse())
        print("Cleared All Data Structs")
        with open(file, 'r') as file_contents:
            reader = csv.reader(file_contents)
            header = next(reader, None)

            # Since this method only deals with single house files, we can check for these values
            # But - could we use the enum defined at the top of this file somehow?
            if header[1].lower() != 'electricity' or header[2].lower() != 'gas':
                DispalyMessage("Required Fields Are Incorrect","ERROR")
                raise ValueError('File is not in correct format. First column must be electricity, second must be gas.')
            # Only Check for Single House
            elif len(header) > 3:
                DisplayYesOrNo("Too many fields have been detected for a single house. This could be because of an "
                               "Incorrect File type Would you like to continue?","Warning")
            # Row Loop
            FE = False

            for row in reader:
                FE = ErrorCheckSingle(row,FE)
                Date.append(datetime.datetime.strptime(row[0], '%Y%m%d').date())
                Shouse[0].ElectricityValue.append(row[1])
                Shouse[0].GasValues.append(row[2])
            CalcualteMonthSingle()
            self.HasHouseSuppliersFile = False
            self.HasHouseDataFile = False
            self.InfoLabel.configure(text="")

    #Multi House
    def process_multi_file(self, file, house_id):
        ########
        print("Multi house loaded")
        print("Fule Type "+house_id+" detected")
        print("Removing Old data")
        ########
        self.FuelType = house_id
        Date.clear()
        HouseList.clear()
        Shouse.clear()
        #Clear Old Suppliers after loading new base file
        SupHouseList.clear()

        with open(file, 'r') as file_contents:
            reader = csv.reader(file_contents)
            ID = next(reader,None)
            del ID[0]
            for Id in ID:
                HouseList.append(House(Id))
            header = next(reader,None)
            HN = header
            del HN[0]
            for H in HouseList:
                H.HouseName = header[HouseList.index(H)]
            for row in reader:
                    Date.append(datetime.datetime.strptime(row[0], '%Y%m%d').date())
                    for I in range(0, len(HN)):
                        HouseList[I].HouseValues.append(float(row[I + 1]))
            CalculateMonth()
            self.btn_file.configure(text="Load suppliers File")
            self.InfoLabel.configure(text="Loaded:" + file + "\nOpen a suppliers file to view cost data")
            self.HasHouseDataFile = True

    def process_supplier_file(self, file):
        if self.HasHouseDataFile == True:
            HouseDictionary.clear()
            SupHouseList.clear()
            with open(file, 'r') as file_contents:
                reader = csv.reader(file_contents)
                rows = []
                for row in reader:
                    rows.append(row)
                for r in range(1,len(rows[0])):
                    SupHouseList.append(SupplierHouse(rows[0][r]))
                index = 1
                for H in SupHouseList:
                        H.HouseName = rows[1][index]
                        H.supplier = rows[2][index]
                        H.ElecUsageRate = float(rows[3][index])
                        H.ElecStandingCharge = float(rows[4][index])
                        H.GasUsageRate = float(rows[5][index])
                        H.GasStandingCharge = float(rows[6][index])
                        HouseDictionary[H.PrimaryKey] = H
                        index += 1
                self.btn_file.configure(text="Load File")
                self.btn_Cost_Menu.pack(pady=5)
                self.InfoLabel.configure(text="Loaded:" + file + "\nyou can load new suppliers files or other house data")
                self.HasHouseSuppliersFile = True
                CalculateMonthlyCost(self.FuelType)
        else:
            DispalyMessage("Please load house data befor the supplier file","Warning")

    def generate_metrics(self):
        choices = []
        for H in HouseList:
            choices.append(H.HouseName)
        choice = easygui.choicebox("Select A House", "Per House Metrics", choices)

        self.ShowHouseMetrics(choice,int(choices.index(choice)))

        Value_trace = go.Scatter(
            x=Date,
            y=HouseList[int(choices.index(choice))].HouseValues,
            name= self.FuelType + ' trace',
            fill='tozeroy',
            fillcolor='rgba(244, 66, 215, 0.5)',
            yaxis='y2'
        )
        graph_data = [Value_trace]
        layout = go.Layout(
            title=str(HouseList[int(choices.index(choice))].HouseName)+ " statistics",
            yaxis=dict(
                title=self.FuelType+' Usage'
            ),
            yaxis2=dict(
                title=str(HouseList[int(choices.index(choice))].HouseName)+' usage',
                titlefont=dict(
                    color='rgb(198, 103, 189)'
                ),
                tickfont=dict(
                    color='rgb(148, 103, 189)'
                ),
                overlaying='y',
                side='right'
            )
        )
        fig = go.Figure(data=graph_data, layout=layout)
        plotly.offline.plot(fig, auto_open=True)


    # This method uses plotly to generate graphs, which open in a browser window. Please
    # see the setup guide for more information about Plotly, as well as links to guides for
    # how to generate difrent types of graphs.

    def generate_MultiHouse_Pie(self):
        labels = []
        values = []
        Last = float(0)
        for I in range(len(HouseList)):
            labels.append(HouseList[I].HouseName)
            for V in HouseList[I].HouseValues:
                Last += V
            values.append(Last)
            Last = float(0)
        trace = [go.Pie(labels=labels, values=values)]
        plotly.offline.plot(trace, auto_open=True)

    def generate_annual_graph_singlehouse(self):

        gas_trace = go.Scatter(
            x=Date,
            y=Shouse[0].GasValues,
            name='gas trace'
        )

        Value_trace = go.Scatter(
            x=Date,
            y=Shouse[0].ElectricityValue,
            name='electricity trace',
            yaxis='y2'
        )
        graph_data = [gas_trace, Value_trace]
        layout = go.Layout(
            title='Single House Both Fuels',
            yaxis=dict(
                title='Usage (kWh)'
            ),
            yaxis2=dict(
                title='yaxis2 title',
                titlefont=dict(
                    color='rgb(148, 103, 189)'
                ),
                tickfont=dict(
                    color='rgb(148, 103, 189)'
                ),
                overlaying='y',
                side='right'
            )
        )
        fig = go.Figure(data=graph_data, layout=layout)
        plotly.offline.plot(fig, auto_open=True)


    def Genarate_MonthlyGrath_Single(self):
        print("Monthly Graph")
        LocalDate = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
        gas_trace = go.Bar(
            x=LocalDate,
            y=Shouse[0].GasValuesMonthly,
            name='gas trace'
        )
        Value_trace = go.Scatter(
            x=LocalDate,
            y=Shouse[0].ElectricityValueMonthly,
            name='electricity trace',
            yaxis='y2'
        )
        graph_data = [gas_trace, Value_trace]
        layout = go.Layout(
            title='Single House Both Fuels Monthly',
            yaxis=dict(
                title='Usage (kWh)'
            ),
            yaxis2=dict(
                title='yaxis2 title',
                titlefont=dict(
                    color='rgb(148, 103, 189)'
                ),
                tickfont=dict(
                    color='rgb(148, 103, 189)'
                ),
                overlaying='y',
                side='right'
            )
        )
        fig = go.Figure(data=graph_data, layout=layout)
        plotly.offline.plot(fig, auto_open=True)

    # Monthly Graph Multi House

    '''
    This Function is the user Interface handle for the Monthly Graph
    '''
    def generate_monthly_graph_multihouse(self):
        self.HideMultiButtons()
        self.MonthSelection.pack(pady=10)
        self.btn_Next.pack(pady=4)
        self.Back_Multi_btn.pack(pady=10)

    def gen_monthly_Multi(self):
        MonthStr = str(MonthIndexSwitch(int(self.MonthSelection.get())))
        MonthIndex = (int(self.MonthSelection.get()))
        for H in HouseList:
            H.HouseMonthValues.clear()
        MonthDates = []
        graph_data = []
        for D in Date:
            if D.month == MonthIndex:
                MonthDates.append(D)
        for H in HouseList:
            for D in Date:
                if D.month == MonthIndex:
                    H.HouseMonthValues.append(H.HouseValues[(int(Date.index(D)))])
            Trace = go.Scatter(
                x=MonthDates,
                y=H.HouseMonthValues,
                name=str(H.HouseName)
                )
            graph_data.append(Trace)
        layout = go.Layout(
            title='Multi House ' + self.FuelType + " " +str(MonthIndexSwitch(int(self.MonthSelection.get()))),
                yaxis=dict(
                    title=self.FuelType + ' Usage'
                ),
                yaxis2=dict(
                    title='',
                    titlefont=dict(
                        color='rgb(148, 103, 189)'
                    ),
                    tickfont=dict(
                        color='rgb(148, 103, 189)'
                    ),
                    overlaying='y',
                    side='right'
                )
            )
        fig = go.Figure(data=graph_data, layout=layout)
        plotly.offline.plot(fig, auto_open=True)

    ''' ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
    Monthly multi is used to get house data from a specific month of the year. 
    All House Data For the multi house is stored in THe House Object Class
        ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^'''

    def generate_annual_graph_multihouse(self):
        graph_data = []
        for I in range(len(HouseList)):
            Trace = go.Scatter(
                x=Date,
                y=HouseList[I].HouseValues,
                name=str(HouseList[I].HouseName)
            )
            graph_data.append(Trace)

        layout = go.Layout(
            title='Multi House '+self.FuelType,
            yaxis=dict(
                title=self.FuelType + ' Usage'
            ),
            yaxis2=dict(
                title='',
                titlefont=dict(
                    color='rgb(148, 103, 189)'
                ),
                tickfont=dict(
                    color='rgb(148, 103, 189)'
                ),
                overlaying='y',
                side='right'
            )
        )
        fig = go.Figure(data=graph_data, layout=layout)
        plotly.offline.plot(fig, auto_open=True)

    def Annual_Monthly(self):
        print("Annual Monthly")
        LocalDate = ["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"]
        graph_data = []
        for I in range(len(HouseList)):
            Trace = go.Bar(
                x=LocalDate,
                y=HouseList[I].HouseMonthValue,
                name=str(HouseList[I].HouseName)
            )
            graph_data.append(Trace)

        layout = go.Layout(
            title='Multi House Monthly '+ self.FuelType,
            yaxis=dict(
                title=self.FuelType+' Usage'
            ),
            yaxis2=dict(
                title='',
                titlefont=dict(
                    color='rgb(148, 103, 189)'
                ),
                tickfont=dict(
                    color='rgb(148, 103, 189)'
                ),
                overlaying='y',
                side='right'
            )
        )
        fig = go.Figure(data=graph_data, layout=layout)
        plotly.offline.plot(fig, auto_open=True)

    def ShowCostGraph(self):

        graph_data = []
        if self.FuelType == "Gas":
            for H in HouseList:
                HS = HouseDictionary[H.PrimaryKey]
                Days = []
                for D in Date:
                    Days.append((H.HouseValues[Date.index(D)] * HS.GasUsageRate + HS.GasStandingCharge) / 100)
                Trace = go.Bar(
                    x=Date,
                    y=Days,
                    name=str(H.HouseName)
                )
                graph_data.append(Trace)
        else:
            for H in HouseList:
                HS = HouseDictionary[H.PrimaryKey]
                Days = []
                for D in Date:
                    Days.append((H.HouseValues[Date.index(D)] * HS.ElecUsageRate + HS.ElecStandingCharge) / 100)
                Trace = go.Bar(
                    x=Date,
                    y=Days,
                    name=str(H.HouseName)
                )
                graph_data.append(Trace)
        layout = go.Layout(
            title='Multi House Daily Cost ' + self.FuelType,
            yaxis=dict(
                title=self.FuelType + ' cost (£)'
            ),
            yaxis2=dict(
                title='',
                titlefont=dict(
                    color='rgb(148, 103, 189)'
                ),
                tickfont=dict(
                    color='rgb(148, 103, 189)'
                ),
                overlaying='y',
                side='right'
            )
        )
        fig = go.Figure(data=graph_data, layout=layout)
        plotly.offline.plot(fig, auto_open=True)

    def ShowMonthlyCostGraph(self):
        LocalDate = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
        graph_data = []
        if self.FuelType == "Gas":
            for H in HouseList:
                HS = HouseDictionary[H.PrimaryKey]
                Days = []
                for D in Date:
                    Days.append((H.HouseValues[Date.index(D)] * HS.GasUsageRate + HS.GasStandingCharge) / 100)
                Trace = go.Bar(
                    x=LocalDate,
                    y=HS.HouseMonthValue,
                    name=str(H.HouseName)
                )
                graph_data.append(Trace)
        else:
            for H in HouseList:
                HS = HouseDictionary[H.PrimaryKey]
                Days = []
                for D in Date:
                    Days.append((H.HouseValues[Date.index(D)] * HS.ElecUsageRate + HS.ElecStandingCharge) / 100)
                Trace = go.Bar(
                    x=LocalDate,
                    y=HS.HouseMonthValue,
                    name=str(H.HouseName)
                )
                graph_data.append(Trace)
        layout = go.Layout(
            title='Multi House Monthly Cost ' + self.FuelType,
            yaxis=dict(
                title=self.FuelType + ' cost (£)'
            ),
            yaxis2=dict(
                title='',
                titlefont=dict(
                    color='rgb(148, 103, 189)'
                ),
                tickfont=dict(
                    color='rgb(148, 103, 189)'
                ),
                overlaying='y',
                side='right'
            )
        )
        fig = go.Figure(data=graph_data, layout=layout)
        plotly.offline.plot(fig, auto_open=True)


    def GraphingFunctionMultiHouse(self,GraphData,Title,YAxisName):
        print("This is where the graph function will be stored")


    def ShowHouseMetrics(self,HouseName,HouseIndex):
        HV = HouseList[HouseIndex].HouseValues
        HMV = HouseList[HouseIndex].HouseMonthValue
        AVG = float(CalAvarege(HV))
        self.scrolled_text.delete('1.0',END)
        self.scrolled_text.insert(INSERT,"Metrics for " + HouseName+" ("+self.FuelType+"):\n\n")
        self.scrolled_text.insert(INSERT,"Average Daily Consumption: "+str(AVG)+"\n")
        self.scrolled_text.insert(INSERT,"Standard Deviation: " + str(CalStandardDeviation(HV,AVG)) + "\n")
        self.scrolled_text.insert(INSERT,"Highest Consuming Day Is " + str(Date[HV.index(max(HV))].strftime('%b %d, %Y'))+": " + str(max(HV))+"\n")
        self.scrolled_text.insert(INSERT,"Lowest Consuming Day Is " + str(Date[HV.index(min(HV))].strftime('%b %d, %Y'))+": " + str(min(HV))+"\n")
        self.scrolled_text.insert(INSERT, "Highest Consuming Month Is " + str(MonthIndexSwitch(int(HMV.index(max(HMV))+1))) + ": " + str(max(HMV))+"\n")
        self.scrolled_text.insert(INSERT, "Lowest Consuming Month Is " + str(MonthIndexSwitch(int(HMV.index(min(HMV)) + 1))) + ": " + str(min(HMV)) + "\n")
        self.scrolled_text.insert(INSERT, "Average Monthly Consumption: " + str(CalAvarege(HMV)) + "\n")
        self.scrolled_text.config(width= 150, height= 20)
        self.HideMultiButtons()
        self.Back_Multi_btn.pack(pady=20)

    def ShowMultiHouseMetrics(self):
        self.scrolled_text.delete('1.0',END)
        HouseValues = []
        HVS = []
        HouseAvgs = []
        for H in HouseList:
            HouseValues.append(H.TotalUsage)
            HouseAvgs.append(CalAvarege(H.HouseValues))
            for HV in H.HouseValues:
                HVS.append(HV)
        HighestTotal = HouseList[HouseValues.index(max(HouseValues))]
        LowestTotal = HouseList[HouseValues.index(min(HouseValues))]
        HighestAvg = HouseList[HouseValues.index(max(HouseValues))]
        LowestAvg = HouseList[HouseValues.index(min(HouseValues))]
        self.scrolled_text.insert(INSERT, "Metrics for all houses ("+self.FuelType+"):\n\n")
        self.scrolled_text.insert(INSERT, "Highest Total Consumption Is " + HighestTotal.HouseName+ ": "+str(HighestTotal.TotalUsage)+"\n")
        self.scrolled_text.insert(INSERT, "Lowest Total Consumption Is " + LowestTotal.HouseName + ": " + str(LowestTotal.TotalUsage) + "\n")
        self.scrolled_text.insert(INSERT, "Highest Average Consumption Is " + HighestAvg.HouseName + ": " + str((max(HouseAvgs))) + "\n")
        self.scrolled_text.insert(INSERT, "Lowest Average Consumption Is " + LowestAvg.HouseName + ": " + str((min(HouseAvgs))) + "\n")
        self.scrolled_text.insert(INSERT, "Average Consumption For All Is: " + str(CalAvarege(HouseAvgs)) + "\n")
        self.scrolled_text.insert(INSERT, "Standard Deviation For All Is: " + str(CalStandardDeviation(HVS,CalAvarege(HouseAvgs))) + "\n")
        self.scrolled_text.config(width= 150, height= 20)
        self.HideMultiButtons()
        self.Back_Multi_btn.pack(pady=20)

    def ShowSingleMetrics(self):
        self.scrolled_text.delete('1.0', END)
        House = Shouse[0]
        HMVG = House.GasValuesMonthly
        HGV = House.GasValues
        AVGG = CalAvarege(HGV)
        HVE = House.ElectricityValue
        HMVE = House.ElectricityValueMonthly
        AVGE = CalAvarege(HVE)
        self.scrolled_text.insert(INSERT, "Metrics (Gas & Electricity)\n\n")
        self.scrolled_text.insert(INSERT, "-=GAS=-\n")
        self.scrolled_text.insert(INSERT, "Highest Daily Usage Is " + str(Date[HGV.index(max(HGV))].strftime('%b %d, %Y')) + ": " + str(max(HGV))+"\n")
        self.scrolled_text.insert(INSERT, "Lowest Daily Usage Is " + str(Date[HGV.index(min(HGV))].strftime('%b %d, %Y')) + ": " + str(min(HGV)) + "\n")
        self.scrolled_text.insert(INSERT, "Average Daily Consumption: " + str(AVGG) + "\n")
        self.scrolled_text.insert(INSERT,"Standard Deviation: " + str(CalStandardDeviation(HGV,AVGG)) + "\n")
        self.scrolled_text.insert(INSERT, "Highest Consuming Month Is " + str(MonthIndexSwitch(int(HMVG.index(max(HMVG)) + 1))) + ": " + str(max(HMVG)) + "\n")
        self.scrolled_text.insert(INSERT, "Lowest Consuming Month Is " + str(MonthIndexSwitch(int(HMVG.index(min(HMVG)) + 1))) + ": " + str(min(HMVG)) + "\n")
        self.scrolled_text.insert(INSERT, "Average Monthly Consumption: " + str(CalAvarege(HMVG)) + "\n")
        self.scrolled_text.insert(INSERT,"\n\n")
        self.scrolled_text.insert(INSERT, "-=ELECTRICITY=-\n")
        self.scrolled_text.insert(INSERT, "Highest Daily Usage Is " + str(Date[HVE.index(max(HVE))].strftime('%b %d, %Y')) + ": " + str(max(HVE)) + "\n")
        self.scrolled_text.insert(INSERT, "Lowest Daily Usage Is " + str(Date[HVE.index(min(HVE))].strftime('%b %d, %Y')) + ": " + str(min(HVE)) + "\n")
        self.scrolled_text.insert(INSERT, "Average Daily Consumption: " + str(AVGE) + "\n")
        self.scrolled_text.insert(INSERT, "Standard Deviation: " + str(CalStandardDeviation(HVE, AVGE)) + "\n")
        self.scrolled_text.insert(INSERT, "Highest Consuming Month Is " + str(MonthIndexSwitch(int(HMVE.index(max(HMVE)) + 1))) + ": " + str(max(HMVE)) + "\n")
        self.scrolled_text.insert(INSERT, "Lowest Consuming Month Is " + str(MonthIndexSwitch(int(HMVE.index(min(HMVE)) + 1))) + ": " + str(min(HMVE)) + "\n")
        self.scrolled_text.insert(INSERT, "Average Monthly Consumption: " + str(CalAvarege(HMVE)) + "\n")
        self.scrolled_text.config(width=150, height=22)
        self.HideSingleButtons()
        self.Back_Single_btn.pack(pady=5)
        #Show Back Button (Single)

    def DisplayCostMetrix(self):
        self.scrolled_text.delete('1.0', END)
        self.scrolled_text.insert(INSERT, "Cost Metrics All Houses (" + self.FuelType + ")\n\n")
        for H in HouseList:
            HS = HouseDictionary[H.PrimaryKey]
            Days = []
            if self.FuelType == "Gas":
                for D in Date:
                    Days.append((H.HouseValues[Date.index(D)] * HS.GasUsageRate + HS.GasStandingCharge) / 100)
            else:
                for D in Date:
                    Days.append((H.HouseValues[Date.index(D)] * HS.ElecUsageRate + HS.ElecStandingCharge) / 100)
            self.scrolled_text.insert(INSERT, "\nMetrics For: " + H.HouseName+"\n")
            self.scrolled_text.insert(INSERT, "Highest Costing Day For "+H.HouseName+" is "+str(Date[Days.index(max(Days))].strftime('%b %d, %Y'))+": "+str(max(Days))+"\n")
            self.scrolled_text.insert(INSERT, "Lowest Costing Day For "+H.HouseName+" is "+str(Date[Days.index(min(Days))].strftime('%b %d, %Y'))+": "+str(min(Days))+"\n")
            self.scrolled_text.insert(INSERT, "Average Daily Cost For "+H.HouseName+" is "+str(CalAvarege(Days))+"\n")
            self.scrolled_text.insert(INSERT, "Standard Deviation: " + str(CalStandardDeviation(Days, CalAvarege(Days)))+"\n")
            self.scrolled_text.insert(INSERT, "Highest Monthly Cost for " + H.HouseName + " is " + str(MonthIndexSwitch(int(HS.HouseMonthValue.index(max(HS.HouseMonthValue)) + 1))) + ": " + str(max(HS.HouseMonthValue)) + "\n")
            self.scrolled_text.insert(INSERT, "Lowest Monthly Cost for " + H.HouseName + " is " + str(MonthIndexSwitch(int(HS.HouseMonthValue.index(min(HS.HouseMonthValue)) + 1))) + ": " + str(min(HS.HouseMonthValue)) + "\n")
            self.scrolled_text.insert(INSERT, "Average Monthly Cost For " + H.HouseName + " is " + str(CalAvarege(HS.HouseMonthValue)) + "\n")
            self.scrolled_text.insert(INSERT, "Standard Deviation (Monthly) " + H.HouseName + " is " + str(CalStandardDeviation(HS.HouseMonthValue, CalAvarege(HS.HouseMonthValue))) + "\n")
            self.scrolled_text.config(width=150, height=20)
            self.HideMultiButtons()
            self.Back_Multi_btn.pack(pady=20)
    def DispalyPerHouseCostMetrics(self):
        self.scrolled_text.delete('1.0', END)
        choices = []
        for H in HouseList:
            choices.append(H.HouseName)
        choice = easygui.choicebox("Select A House", "Per House Metrics", choices)
        if choice != None:
            self.scrolled_text.config(width=150, height=20)
            H = HouseList[int(choices.index(choice))]
            HS = HouseDictionary[H.PrimaryKey]
            Days = []
            if self.FuelType == "Gas":
                for D in Date:
                    Days.append((H.HouseValues[Date.index(D)] * HS.GasUsageRate + HS.GasStandingCharge) / 100)
            else:
                for D in Date:
                    Days.append((H.HouseValues[Date.index(D)] * HS.ElecUsageRate + HS.ElecStandingCharge) / 100)
            self.scrolled_text.insert(INSERT, "\nMetrics For: " + H.HouseName + "\n")
            self.scrolled_text.insert(INSERT, "Highest Costing Day For " + H.HouseName+" is "+ str(Date[Days.index(max(Days))].strftime('%b %d, %Y'))+": " + str(max(Days))+"\n")
            self.scrolled_text.insert(INSERT, "Lowest Costing Day For " + H.HouseName+" is "+ str(Date[Days.index(min(Days))].strftime('%b %d, %Y'))+": " + str(min(Days))+"\n")
            self.scrolled_text.insert(INSERT,"Average Daily Cost For " + H.HouseName+" is "+str(CalAvarege(Days))+"\n")
            self.scrolled_text.insert(INSERT,"Standard Deviation: "+str(CalStandardDeviation(Days, CalAvarege(Days)))+"\n")
            self.scrolled_text.insert(INSERT, "Highest Monthly Cost for "+H.HouseName+" is "+str(MonthIndexSwitch(int(HS.HouseMonthValue.index(max(HS.HouseMonthValue)) + 1))) + ": "+str(max(HS.HouseMonthValue))+"\n")
            self.scrolled_text.insert(INSERT, "Lowest Monthly Cost for "+H.HouseName+" is "+str(MonthIndexSwitch(int(HS.HouseMonthValue.index(min(HS.HouseMonthValue)) + 1))) + ": "+str(min(HS.HouseMonthValue))+"\n")
            self.scrolled_text.insert(INSERT, "Average Monthly Cost For "+H.HouseName+" is " + str(CalAvarege(HS.HouseMonthValue))+"\n")
            self.scrolled_text.insert(INSERT, "Standard Deviation (Monthly) "+H.HouseName+" is "+str(CalStandardDeviation(HS.HouseMonthValue,CalAvarege(HS.HouseMonthValue)))+"\n")
            self.HideMultiButtons()
            self.Back_Multi_btn.pack(pady=20)
        else:
            DispalyMessage("Invalid Selection","Info")
            self.Back_Multi()


'''
This is the entry point of the script. The code here will run first when the script is run,
and essentially all it does is establish a w constraints of the GUI window, setup the plotly
instance, and create the EnergyMonitor class. The mainloop() method is what allows the Tkinter
widgets to respond to user input, by entering a waiting loop to detect changes in the UI. 
'''
if __name__ == "__main__":
    root = tk.Tk()
    root.title("Energy Monitor")
    root.geometry('650x750')
    root.configure(background='#c6e2ff')

    plotly.tools.set_credentials_file(username='Smokeyb05', api_key='NorktulDvAvQ0JPYFTWf')
    print(plotly.__version__)

    gui = EnergyMonitor(root)
    root.mainloop()
