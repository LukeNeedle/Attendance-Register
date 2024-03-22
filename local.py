import sqlite3
import json
import os
import colorama
from time import sleep
from tkinter import Tk, Button, Spinbox, StringVar, Label, Frame, messagebox, filedialog
from tkcalendar import Calendar
import datetime
from PIL import Image
from colr import Colr
import requests
import re
import ctypes

softwareVersion=(2,0,2)
setupVersion = 2

sqlite3.register_adapter(bool, int)
sqlite3.register_converter("BOOLEAN", lambda v: bool(int(v)))

sqlite3.register_adapter(datetime.datetime, lambda x: x.isoformat())
sqlite3.register_converter("TIMESTAMP", lambda x: datetime.datetime.fromisoformat(x.decode()))

def get_date():
    global dateReceived
    
    date = cal.get_date()
    hour = int(hour_var.get())
    minute = int(minute_var.get())
    
    date = date.split("/")
    if ((hour <= 23 or hour >= 0) and (minute >= 0 or minute <= 59) and len(date) == 3):
        if not os.path.exists("Temp/"):
            os.mkdir("Temp")
        if os.path.exists("Temp/dateReceived.txt"):
            os.remove("Temp/dateReceived.txt")
        open("Temp/dateReceived.txt", "x")
        with open("Temp/dateReceived.txt", "a") as f:
            for item in [(str(20)+date[2]), date[0], date[1], str(hour), str(minute)]:
                f.write(item + "\n")
        root.destroy()
    elif len(date) != 3:
        messagebox.showerror("Invalid Input", "Please enter a valid hour (0-23) or minute (0-59)")
    else:
        messagebox.showerror("Invalid Input", "Please enter a valid hour (0-23) or minute (0-59)")

def on_close():
    if not os.path.exists("Temp/"):
        os.mkdir("Temp")
    if os.path.exists("Temp/dateReceived.txt"):
        os.remove("Temp/dateReceived.txt")
    open("Temp/dateReceived.txt", "x")
    with open("Temp/dateReceived.txt", "a") as f:
        f.write("None")
    root.destroy()

def requestDate(label):
    global cal
    global root
    global hour_var
    global minute_var
    
    root = Tk()
    root.geometry("300x300")
    root.title("Select A Start Date")
    root.attributes('-topmost', True)
    root.protocol("WM_DELETE_WINDOW", on_close)
    
    Label(root, text=label).pack()
    
    cal = Calendar(root, selectmode='day', year=2024, month=3, day=1)
    cal.pack(pady=5)
    
    time_frame = Frame(root)
    time_frame.pack(pady=5)

    Label(time_frame, text="Hour:Minute").pack(side="top")
    
    hour_var = StringVar(root)
    minute_var = StringVar(root)
    hour_var.set("00")
    minute_var.set("00")

    hour_sb = Spinbox(time_frame, from_=0, to=23, textvariable=hour_var, width=2, format="%02.0f")
    minute_sb = Spinbox(time_frame, from_=0, to=59, textvariable=minute_var, width=2, format="%02.0f")
    
    hour_sb.pack(side="left")
    Label(time_frame, text=":").pack(side="left")
    minute_sb.pack(side="left")
    
    Button(root, text="Submit Session", command=get_date).pack(pady=5)
    root.mainloop()

def mainOption_Update(studentSelected=None, dateReceived=None, validSessionDuration=None, validSessionDurationAttended=None):
    with open("setup.json", "r") as f:
        globalVariables = json.loads(f.read())
    connection = sqlite3.connect(globalVariables['database_location'], detect_types=sqlite3.PARSE_DECLTYPES | sqlite3.PARSE_COLNAMES)
    cursor = connection.cursor()
    
    cursor.execute("SELECT StudentID, Initials FROM Students;")
    result = cursor.fetchall()
    
    if studentSelected == None:
        print("Students:")
        studentsInitials = []
        for student in result:
            studentsInitials.append(student[1])
            print(f"{colorama.Style.BRIGHT}{result.index(student)+1}{colorama.Style.RESET_ALL} | {student[1]}")
        
        studentSelectID = input("ID/initials of the student: ")
        if studentSelectID in studentsInitials:
            studentSelected = result[studentsInitials.index(studentSelectID)]
        else:
            try:
                validStudentSelectID = int(studentSelectID)
            except ValueError:
                os.system('cls' if os.name=='nt' else 'clear')
                print(f"{colorama.Fore.RED + colorama.Style.BRIGHT}Invalid input. Please enter an integer.{colorama.Fore.RESET + colorama.Style.RESET_ALL}")
                cursor.close()
                connection.close()
                return mainOption_View()
            
            if validStudentSelectID < 1 or validStudentSelectID > len(result):
                os.system('cls' if os.name=='nt' else 'clear')
                print(f"{colorama.Fore.RED + colorama.Style.BRIGHT}Invalid input. Please enter an integer between 1 and {len(result)}{colorama.Fore.RESET + colorama.Style.RESET_ALL}")
                cursor.close()
                connection.close()
                return mainOption_View()

            studentSelected = result[validStudentSelectID-1]
    
    print(f"Selected Student: {studentSelected[1]}")
    
    if dateReceived == None:
        requestDate(label="Create Session")
        with open("Temp/dateReceived.txt", "r") as f:
            lines = f.readlines()
        os.remove("Temp/dateReceived.txt")
        lines = [line.strip() for line in lines if line.strip()]
        if lines == ["None"]:
            os.system('cls' if os.name=='nt' else 'clear')
            print(f"{colorama.Fore.RED + colorama.Style.BRIGHT}Aborted Student Update{colorama.Fore.RESET + colorama.Style.RESET_ALL}")
            sleep(1)
            os.system('cls' if os.name=='nt' else 'clear')
            cursor.close()
            connection.close()
            return False
        
        dateReceived = datetime.datetime(int(lines[0]), int(lines[1]), int(lines[2]), int(lines[3]), int(lines[4]))
    
    if validSessionDuration == None:
        sessionDuration = input("Session Duration (in Hours): ")
        try:
            validSessionDuration = float(sessionDuration)
        except ValueError:
            os.system('cls' if os.name=='nt' else 'clear')
            print(f"{colorama.Fore.RED + colorama.Style.BRIGHT}Invalid input. Please enter a number between 0 and 23.{colorama.Fore.RESET + colorama.Style.RESET_ALL}")
            cursor.close()
            connection.close()
            return mainOption_Update(studentSelected=studentSelected, dateReceived=dateReceived)
        
        if validSessionDuration <= 0 or validSessionDuration > 24:
            os.system('cls' if os.name=='nt' else 'clear')
            print(f"{colorama.Fore.RED + colorama.Style.BRIGHT}Invalid input. Please enter a number between 0 and 23.{colorama.Fore.RESET + colorama.Style.RESET_ALL}")
            cursor.close()
            connection.close()
            return mainOption_Update(studentSelected=studentSelected, dateReceived=dateReceived)
    
    if validSessionDurationAttended == None:
        sessionDurationAttended = input("Session Duration Attended (in Hours): ")
        try:
            validSessionDurationAttended = float(sessionDurationAttended)
        except ValueError:
            os.system('cls' if os.name=='nt' else 'clear')
            print(f"{colorama.Fore.RED + colorama.Style.BRIGHT}Invalid input. Please enter a number between 0 and 23 and lower than the session duration ({validSessionDuration}).{colorama.Fore.RESET + colorama.Style.RESET_ALL}")
            cursor.close()
            connection.close()
            return mainOption_Update(studentSelected=studentSelected, dateReceived=dateReceived, validSessionDuration=validSessionDuration)
        
        if validSessionDurationAttended <= 0 or validSessionDurationAttended > 24:
            os.system('cls' if os.name=='nt' else 'clear')
            print(f"{colorama.Fore.RED + colorama.Style.BRIGHT}Invalid input. Please enter a number between 0 and 23 and lower than the session duration ({validSessionDuration}).{colorama.Fore.RESET + colorama.Style.RESET_ALL}")
            cursor.close()
            connection.close()
            return mainOption_Update(studentSelected=studentSelected, dateReceived=dateReceived, validSessionDuration=validSessionDuration)
        
        if validSessionDurationAttended > validSessionDuration:
            os.system('cls' if os.name=='nt' else 'clear')
            print(f"{colorama.Fore.RED + colorama.Style.BRIGHT}Invalid input. Please enter a number between 0 and 23 and lower than the session duration ({validSessionDuration}).{colorama.Fore.RESET + colorama.Style.RESET_ALL}")
            cursor.close()
            connection.close()
            return mainOption_Update(studentSelected=studentSelected, dateReceived=dateReceived, validSessionDuration=validSessionDuration)
    
    print("="*40)
    print("Session Info:")
    print(f"Initials: {studentSelected[1]}")
    print(f"Date of Session: {dateReceived}")
    print(f"Duration of Session: {validSessionDuration}")
    print(f"Duration of Session attended: {validSessionDurationAttended}")
    print("="*40)
    
    confirmation = input(f"Is this ok? ({colorama.Style.BRIGHT}Y{colorama.Style.RESET_ALL}/{colorama.Style.BRIGHT}N{colorama.Style.RESET_ALL}) ").lower()
    if confirmation == "y":
        cursor.execute("INSERT INTO Attendance(StudentID, Timestamp, Duration, AmountAttended) VALUES (?,?,?,?);", (studentSelected[0], dateReceived, validSessionDuration, validSessionDurationAttended))
        connection.commit()
        
        os.system('cls' if os.name=='nt' else 'clear')
        print(f"{colorama.Fore.GREEN + colorama.Style.BRIGHT}Successfully created new session!{colorama.Fore.RESET + colorama.Style.RESET_ALL}")
        sleep(1)
        os.system('cls' if os.name=='nt' else 'clear')
        
        cursor.close()
        connection.close()
        return False
    os.system('cls' if os.name=='nt' else 'clear')
    print(f"{colorama.Fore.RED + colorama.Style.BRIGHT}Aborted Session Creation{colorama.Fore.RESET + colorama.Style.RESET_ALL}")
    sleep(1)
    os.system('cls' if os.name=='nt' else 'clear')
    
    cursor.close()
    connection.close()

def mainOption_View(studentSelected=None):
    with open("setup.json", "r") as f:
        globalVariables = json.loads(f.read())
    connection = sqlite3.connect(globalVariables['database_location'], detect_types=sqlite3.PARSE_DECLTYPES | sqlite3.PARSE_COLNAMES)
    cursor = connection.cursor()
    
    cursor.execute("SELECT StudentID, Initials FROM Students;")
    result = cursor.fetchall()
    
    if studentSelected == None:
        print("Students:")
        studentsInitials = []
        for student in result:
            studentsInitials.append(student[1])
            print(f"{colorama.Style.BRIGHT}{result.index(student)+1}{colorama.Style.RESET_ALL} | {student[1]}")
        
        studentSelectID = input("ID/initials of the student: ")
        if studentSelectID in studentsInitials:
            studentSelected = result[studentsInitials.index(studentSelectID)]
        else:
            try:
                validStudentSelectID = int(studentSelectID)
            except ValueError:
                os.system('cls' if os.name=='nt' else 'clear')
                print(f"{colorama.Fore.RED + colorama.Style.BRIGHT}Invalid input. Please enter an integer.{colorama.Fore.RESET + colorama.Style.RESET_ALL}")
                cursor.close()
                connection.close()
                return mainOption_View()
            
            if validStudentSelectID < 1 or validStudentSelectID > len(result):
                os.system('cls' if os.name=='nt' else 'clear')
                print(f"{colorama.Fore.RED + colorama.Style.BRIGHT}Invalid input. Please enter an integer between 1 and {len(result)}{colorama.Fore.RESET + colorama.Style.RESET_ALL}")
                cursor.close()
                connection.close()
                return mainOption_View()

            studentSelected = result[validStudentSelectID-1]
    
    os.system('cls' if os.name=='nt' else 'clear')
    print_view_menu()
    print(f"Selected Student: {studentSelected[1]}")
    menuSelection = input("What would you like to do? ")
    if menuSelection not in ["1", "2", "3", "4", "5", "6"]:
        print(f"{colorama.Fore.RED + colorama.Style.BRIGHT}Invalid option{colorama.Fore.RESET + colorama.Style.RESET_ALL}")
        sleep(1)
        mainOption_View(studentSelected)
    
    menuSelection = int(menuSelection)

    cursor.close()
    connection.close()
    os.system('cls' if os.name=='nt' else 'clear')
    if menuSelection == 1:
        return mainOption_View_Session_Stats(studentSelected[0])
    elif menuSelection == 2:
        return mainOption_View_Session_Stats_Before(studentSelected[0])
    elif menuSelection == 3:
        return mainOption_View_Session_Stats_After(studentSelected[0])
    elif menuSelection == 4:
        return mainOption_View_Session_Stats_Between(studentSelected[0])
    elif menuSelection == 5:
        return mainOption_View_Print_Data(studentSelected[0])
    else:
        return False

def mainOption_View_Session_Stats(studentID):
    with open("setup.json", "r") as f:
        globalVariables = json.loads(f.read())
    connection = sqlite3.connect(globalVariables['database_location'], detect_types=sqlite3.PARSE_DECLTYPES | sqlite3.PARSE_COLNAMES)
    cursor = connection.cursor()

    cursor.execute("SELECT Initials FROM Students WHERE StudentID=?;", (studentID,))
    initials = cursor.fetchone()[0]
    
    cursor.execute("SELECT Duration, AmountAttended FROM Attendance WHERE StudentID=?;", (studentID,))
    result = cursor.fetchall()
    
    cursor.close()
    connection.close()
    
    totalDuration = 0
    totalDurationAttended = 0
    
    for timeSpent in result:
        totalDuration += timeSpent[0]
        totalDurationAttended += timeSpent[1]
    
    if totalDuration == 0:
        os.system('cls' if os.name=='nt' else 'clear')
        print(f"{colorama.Fore.RED + colorama.Style.BRIGHT}No sessions found.{colorama.Fore.RESET + colorama.Style.RESET_ALL}")
        sleep(1)
        os.system('cls' if os.name=='nt' else 'clear')
        return False
    
    percentageAttended = round((totalDurationAttended/totalDuration * 100), 1)
    
    print("="*45)
    print("Student Stats:")
    print(f"Student Initials: {initials}")
    print(f"Total Session Length: {totalDuration} hours")
    print(f"Total Session Length Attended: {totalDurationAttended} hours")
    print(f"%Attended: {percentageAttended}%")
    print("="*45)
    input(f"Press {colorama.Style.BRIGHT}enter{colorama.Style.RESET_ALL} to continue.")
    os.system('cls' if os.name=='nt' else 'clear')
    return True

def mainOption_View_Session_Stats_Before(studentID, dateReceived=None):
    with open("setup.json", "r") as f:
        globalVariables = json.loads(f.read())
    connection = sqlite3.connect(globalVariables['database_location'], detect_types=sqlite3.PARSE_DECLTYPES | sqlite3.PARSE_COLNAMES)
    cursor = connection.cursor()

    cursor.execute("SELECT Initials FROM Students WHERE StudentID=?;", (studentID,))
    initials = cursor.fetchone()[0]
    
    if dateReceived == None:
        requestDate(label="View Sessions before ...")
        with open("Temp/dateReceived.txt", "r") as f:
            lines = f.readlines()
        os.remove("Temp/dateReceived.txt")
        lines = [line.strip() for line in lines if line.strip()]
        if lines == ["None"]:
            os.system('cls' if os.name=='nt' else 'clear')
            print(f"{colorama.Fore.RED + colorama.Style.BRIGHT}Aborted Session View{colorama.Fore.RESET + colorama.Style.RESET_ALL}")
            sleep(1)
            os.system('cls' if os.name=='nt' else 'clear')
            cursor.close()
            connection.close()
            return False
        
        formattedDatetime = datetime.datetime(int(lines[0]), int(lines[1]), int(lines[2]), int(lines[3]), int(lines[4])).isoformat()
    
    cursor.execute("SELECT Duration, AmountAttended FROM Attendance WHERE StudentID=? AND Timestamp<?;", (studentID, formattedDatetime))
    result = cursor.fetchall()
    
    cursor.close()
    connection.close()
    
    totalDuration = 0
    totalDurationAttended = 0
    
    for timeSpent in result:
        totalDuration += timeSpent[0]
        totalDurationAttended += timeSpent[1]
    
    if totalDuration == 0:
        os.system('cls' if os.name=='nt' else 'clear')
        print(f"{colorama.Fore.RED + colorama.Style.BRIGHT}No sessions found.{colorama.Fore.RESET + colorama.Style.RESET_ALL}")
        sleep(1)
        os.system('cls' if os.name=='nt' else 'clear')
        return False
    
    percentageAttended = round((totalDurationAttended/totalDuration * 100), 1)
    
    print("="*45)
    print("Student Stats:")
    print(f"Student Initials: {initials}")
    print(f"Timestamp before: {formattedDatetime.replace("T", " ")}")
    print(f"Total Session Length: {totalDuration} hours")
    print(f"Total Session Length Attended: {totalDurationAttended} hours")
    print(f"%Attended: {percentageAttended}%")
    print("="*45)
    input(f"Press {colorama.Style.BRIGHT}enter{colorama.Style.RESET_ALL} to continue.")
    os.system('cls' if os.name=='nt' else 'clear')
    return True

def mainOption_View_Session_Stats_After(studentID, dateReceived=None):
    with open("setup.json", "r") as f:
        globalVariables = json.loads(f.read())
    connection = sqlite3.connect(globalVariables['database_location'], detect_types=sqlite3.PARSE_DECLTYPES | sqlite3.PARSE_COLNAMES)
    cursor = connection.cursor()

    cursor.execute("SELECT Initials FROM Students WHERE StudentID=?;", (studentID,))
    initials = cursor.fetchone()[0]
    
    if dateReceived == None:
        requestDate(label="View Sessions after ...")
        with open("Temp/dateReceived.txt", "r") as f:
            lines = f.readlines()
        os.remove("Temp/dateReceived.txt")
        lines = [line.strip() for line in lines if line.strip()]
        if lines == ["None"]:
            os.system('cls' if os.name=='nt' else 'clear')
            print(f"{colorama.Fore.RED + colorama.Style.BRIGHT}Aborted Session View{colorama.Fore.RESET + colorama.Style.RESET_ALL}")
            sleep(1)
            os.system('cls' if os.name=='nt' else 'clear')
            cursor.close()
            connection.close()
            return False
        
        formattedDatetime = datetime.datetime(int(lines[0]), int(lines[1]), int(lines[2]), int(lines[3]), int(lines[4])).isoformat()
    
    cursor.execute("SELECT Duration, AmountAttended FROM Attendance WHERE StudentID=? AND Timestamp>?;", (studentID, formattedDatetime))
    result = cursor.fetchall()
    
    cursor.close()
    connection.close()
    
    totalDuration = 0
    totalDurationAttended = 0
    
    for timeSpent in result:
        totalDuration += timeSpent[0]
        totalDurationAttended += timeSpent[1]
    
    if totalDuration == 0:
        os.system('cls' if os.name=='nt' else 'clear')
        print(f"{colorama.Fore.RED + colorama.Style.BRIGHT}No sessions found.{colorama.Fore.RESET + colorama.Style.RESET_ALL}")
        sleep(1)
        os.system('cls' if os.name=='nt' else 'clear')
        return False
    
    percentageAttended = round((totalDurationAttended/totalDuration * 100), 1)
    
    print("="*45)
    print("Student Stats:")
    print(f"Student Initials: {initials}")
    print(f"Timestamp after: {formattedDatetime.replace("T", " ")}")
    print(f"Total Session Length: {totalDuration} hours")
    print(f"Total Session Length Attended: {totalDurationAttended} hours")
    print(f"%Attended: {percentageAttended}%")
    print("="*45)
    input(f"Press {colorama.Style.BRIGHT}enter{colorama.Style.RESET_ALL} to continue.")
    os.system('cls' if os.name=='nt' else 'clear')
    return True

def mainOption_View_Session_Stats_Between(studentID, dateReceivedStart=None, dateReceivedEnd=None):
    with open("setup.json", "r") as f:
        globalVariables = json.loads(f.read())
    connection = sqlite3.connect(globalVariables['database_location'], detect_types=sqlite3.PARSE_DECLTYPES | sqlite3.PARSE_COLNAMES)
    cursor = connection.cursor()

    cursor.execute("SELECT Initials FROM Students WHERE StudentID=?;", (studentID,))
    initials = cursor.fetchone()[0]
    
    if dateReceivedStart == None:
        requestDate(label="View Sessions after ...")
        with open("Temp/dateReceived.txt", "r") as f:
            lines = f.readlines()
        os.remove("Temp/dateReceived.txt")
        lines = [line.strip() for line in lines if line.strip()]
        if lines == ["None"]:
            os.system('cls' if os.name=='nt' else 'clear')
            print(f"{colorama.Fore.RED + colorama.Style.BRIGHT}Aborted Session View{colorama.Fore.RESET + colorama.Style.RESET_ALL}")
            sleep(1)
            os.system('cls' if os.name=='nt' else 'clear')
            cursor.close()
            connection.close()
            return False
        
        formattedDatetimeStart = datetime.datetime(int(lines[0]), int(lines[1]), int(lines[2]), int(lines[3]), int(lines[4])).isoformat()
    
    if dateReceivedEnd == None:
        requestDate(label="View Sessions before ...")
        with open("Temp/dateReceived.txt", "r") as f:
            lines = f.readlines()
        lines = [line.strip() for line in lines if line.strip()]
        if lines == ["None"]:
            os.system('cls' if os.name=='nt' else 'clear')
            print(f"{colorama.Fore.RED + colorama.Style.BRIGHT}Aborted Session View{colorama.Fore.RESET + colorama.Style.RESET_ALL}")
            sleep(1)
            os.system('cls' if os.name=='nt' else 'clear')
            cursor.close()
            connection.close()
            return False
        
        formattedDatetimeEnd = datetime.datetime(int(lines[0]), int(lines[1]), int(lines[2]), int(lines[3]), int(lines[4])).isoformat()
    
    cursor.execute("SELECT Duration, AmountAttended FROM Attendance WHERE StudentID=? AND Timestamp>? AND Timestamp<?;", (studentID, formattedDatetimeStart, formattedDatetimeEnd))
    result = cursor.fetchall()
    
    cursor.close()
    connection.close()
    
    totalDuration = 0
    totalDurationAttended = 0
    
    for timeSpent in result:
        totalDuration += timeSpent[0]
        totalDurationAttended += timeSpent[1]
    
    if totalDuration == 0:
        os.system('cls' if os.name=='nt' else 'clear')
        print(f"{colorama.Fore.RED + colorama.Style.BRIGHT}No sessions found.{colorama.Fore.RESET + colorama.Style.RESET_ALL}")
        sleep(1)
        os.system('cls' if os.name=='nt' else 'clear')
        return False
    
    percentageAttended = round((totalDurationAttended/totalDuration * 100), 1)
    
    print("="*45)
    print("Student Stats:")
    print(f"Student Initials: {initials}")
    print(f"Timestamp after: {formattedDatetimeStart.replace("T", " ")}")
    print(f"Timestamp before: {formattedDatetimeEnd.replace("T", " ")}")
    print(f"Total Session Length: {totalDuration} hours")
    print(f"Total Session Length Attended: {totalDurationAttended} hours")
    print(f"%Attended: {percentageAttended}%")
    print("="*45)
    input(f"Press {colorama.Style.BRIGHT}enter{colorama.Style.RESET_ALL} to continue.")
    os.system('cls' if os.name=='nt' else 'clear')
    return True

def mainOption_View_Print_Data(studentID):
    with open("setup.json", "r") as f:
        globalVariables = json.loads(f.read())
    connection = sqlite3.connect(globalVariables['database_location'], detect_types=sqlite3.PARSE_DECLTYPES | sqlite3.PARSE_COLNAMES)
    cursor = connection.cursor()
    
    cursor.execute("SELECT TimeStamp, Duration, AmountAttended FROM Attendance WHERE StudentID=? ORDER BY TimeStamp", (studentID,))
    rows = cursor.fetchall()
    
    if len(rows) == 0:
        os.system('cls' if os.name=='nt' else 'clear')
        print(f"{colorama.Fore.RED + colorama.Style.BRIGHT}No sessions found.{colorama.Fore.RESET + colorama.Style.RESET_ALL}")
        sleep(1)
        os.system('cls' if os.name=='nt' else 'clear')
        return False
    
    timestampWidth = 25
    durationWidth = 10
    amountAttendedWidth = 15
    amountAttendedAsPercentageWidth = 10
    
    headerFormat = "{:<{}} | {:<{}} | {:<{}} | {:<{}} |".format("TimeStamp", timestampWidth, "Duration", durationWidth, "Amount Attended", amountAttendedWidth, "Running %", amountAttendedAsPercentageWidth)
    tableData = "|" + headerFormat + "\n|" + "-" * (timestampWidth+1) + "|" + "-" * (durationWidth+2) + "|" + "-" * (amountAttendedWidth+2) + "|" + "-" * (amountAttendedAsPercentageWidth+2) + "|"
    
    
    totalDuration = 0
    totalDurationAttended = 0
    
    for row in rows:
        timestamp, duration, amount_attended = row
        totalDuration += duration
        totalDurationAttended += amount_attended
        
        timestampAsString = str(datetime.datetime.strftime(timestamp, '%Y-%m-%d %H:%M').ljust(timestampWidth))
        
        durationAsString = f"{duration:.3f}".rjust(durationWidth)
        amountAttendedAsString = f"{amount_attended:.3f}".rjust(amountAttendedWidth)
        percentageAttended = f"{round((totalDurationAttended/totalDuration * 100), 1)}".rjust(amountAttendedAsPercentageWidth)
        
        row_format = "{:<{}} | {:<{}} | {:<{}} | {:<{}} |".format(timestampAsString, timestampWidth, durationAsString, durationWidth, amountAttendedAsString, amountAttendedWidth, percentageAttended, amountAttendedAsPercentageWidth)
        tableData += "\n|" + row_format
    
    cursor.execute("SELECT Initials FROM Students WHERE StudentID=?;", (studentID,))
    initials = cursor.fetchone()[0]
    
    if not os.path.exists(globalVariables['output_folder']):
        os.mkdir(globalVariables['output_folder'])
    
    suggestedFileName = f"{str(datetime.datetime.now().strftime("%Y-%m-%d %H.%M"))}-{initials}.txt"
    
    root = Tk()
    root.withdraw()
    root.attributes('-topmost', True)
    
    filePath = ""
    while filePath == "" or filePath == "/":
        filePath = filedialog.asksaveasfilename(initialdir=globalVariables['output_folder'], initialfile=suggestedFileName, filetypes=(("Student data file","*.txt"),), defaultextension=".txt", title="save")
        
        if filePath != "" and filePath != "/" and filePath != None:
            if len(filePath) < 5:
                continue
            elif filePath[-4:] != ".txt":
                continue
    
    with open(filePath, 'w') as f:
        f.write(tableData)

    print(f"Student data saved to {filePath}")
    input(f"Press {colorama.Style.BRIGHT}enter{colorama.Style.RESET_ALL} to continue.")
    os.system('cls' if os.name=='nt' else 'clear')
    cursor.close()
    connection.close() 

def mainOption_Manage_Create(students:bool):
    with open("setup.json", "r") as f:
        globalVariables = json.loads(f.read())
    connection = sqlite3.connect(globalVariables['database_location'], detect_types=sqlite3.PARSE_DECLTYPES | sqlite3.PARSE_COLNAMES)
    cursor = connection.cursor()
    
    print("If the student's initials already exist either append an identifier or, when prompted, overwrite the existing student.")
    initials = str(input(f"Students initials (Type '{colorama.Style.BRIGHT}cancel{colorama.Style.RESET_ALL}' to return to the main menu): ")).upper()
    if initials.lower() in ["cancel", "\'cancel\'"]:
        os.system('cls' if os.name=='nt' else 'clear')
        cursor.close()
        connection.close()
        return False
    
    if initials in ["", " "] or len(initials) <= 1:
        os.system('cls' if os.name=='nt' else 'clear')
        print(f"{colorama.Fore.RED + colorama.Style.BRIGHT}Please enter valid initials.{colorama.Fore.RESET + colorama.Style.RESET_ALL}")
        cursor.close()
        connection.close()
        return mainOption_Manage_Create(students)
    
    if students:
        cursor.execute("SELECT StudentID FROM Students WHERE Initials=?;", (initials, ))
        if cursor.fetchone() != None:
            print(f"{colorama.Fore.YELLOW + colorama.Style.BRIGHT}These initials are already in use.{colorama.Fore.RESET + colorama.Style.RESET_ALL}")
            deleteRequest = input(f"Would you like to {colorama.Fore.RED + colorama.Style.BRIGHT}overwrite{colorama.Fore.RESET + colorama.Style.RESET_ALL} the other student ({colorama.Style.BRIGHT}Y{colorama.Style.RESET_ALL}/{colorama.Style.BRIGHT}N{colorama.Style.RESET_ALL}): ")
            if deleteRequest.lower() == "y":
                cursor.execute("DELETE FROM Students WHERE Initials=?;", (initials, ))
                connection.commit()
            else:
                os.system('cls' if os.name=='nt' else 'clear')
                print(f"{colorama.Fore.GREEN + colorama.Style.BRIGHT}Overwrite aborted.{colorama.Fore.RESET + colorama.Style.RESET_ALL}")
                cursor.close()
                connection.close()
                return mainOption_Manage_Create(students)
    
    cursor.execute("INSERT INTO Students(Initials) VALUES (?);", (initials, ))
    connection.commit()
    
    os.system('cls' if os.name=='nt' else 'clear')
    print(f"{colorama.Fore.GREEN + colorama.Style.BRIGHT}Successfully created new student!{colorama.Fore.RESET + colorama.Style.RESET_ALL}")
    sleep(1)
    os.system('cls' if os.name=='nt' else 'clear')
    cursor.close()
    connection.close()
    return True

def mainOption_Manage_Edit(studentSelected=None):
    with open("setup.json", "r") as f:
        globalVariables = json.loads(f.read())
    connection = sqlite3.connect(globalVariables['database_location'], detect_types=sqlite3.PARSE_DECLTYPES | sqlite3.PARSE_COLNAMES)
    cursor = connection.cursor()
    
    if studentSelected == None:
        cursor.execute("SELECT StudentID, Initials FROM Students;")
        result = cursor.fetchall()
        
        print("Students:")
        for student in result:
            print(f"{colorama.Style.BRIGHT}{result.index(student)+1}{colorama.Style.RESET_ALL} | {student[1]}")
        
        studentSelectID = input("ID of the student: ")
        try:
            validStudentSelectID = int(studentSelectID)
        except ValueError:
            os.system('cls' if os.name=='nt' else 'clear')
            print(f"{colorama.Fore.RED + colorama.Style.BRIGHT}Invalid input. Please enter an integer.{colorama.Fore.RESET + colorama.Style.RESET_ALL}")
            cursor.close()
            connection.close()
            return mainOption_Manage_Edit()
        
        if validStudentSelectID < 1 or validStudentSelectID > len(result):
            os.system('cls' if os.name=='nt' else 'clear')
            print(f"{colorama.Fore.RED + colorama.Style.BRIGHT}Invalid input. Please enter an integer between 1 and {len(result)}{colorama.Fore.RESET + colorama.Style.RESET_ALL}")
            cursor.close()
            connection.close()
            return mainOption_Manage_Edit()

        studentSelected = result[validStudentSelectID-1]
    
    newInitials = input(f"Enter the new initials of the student ({studentSelected[1]}) (Type '{colorama.Style.BRIGHT}cancel{colorama.Style.RESET_ALL}' to return to the main menu): ").upper()
    if newInitials.lower() in ["cancel", "\'cancel\'"]:
        os.system('cls' if os.name=='nt' else 'clear')
        cursor.close()
        connection.close()
        return False
    
    if newInitials in ["", " "] or len(newInitials) <= 1:
        os.system('cls' if os.name=='nt' else 'clear')
        print(f"{colorama.Fore.RED + colorama.Style.BRIGHT}Please enter valid initials.{colorama.Fore.RESET + colorama.Style.RESET_ALL}")
        cursor.close()
        connection.close()
        return mainOption_Manage_Edit(studentSelected)
    
    deleteRequest = "n"
    cursor.execute("SELECT StudentID FROM Students WHERE Initials=?;", (newInitials, ))
    if cursor.fetchone() != None:
        print(f"{colorama.Fore.RED + colorama.Style.BRIGHT}These initials are already in use.{colorama.Fore.RESET + colorama.Style.RESET_ALL}")
        deleteRequest = input(f"Would you like to {colorama.Fore.RED + colorama.Style.BRIGHT}overwrite{colorama.Fore.RESET + colorama.Style.RESET_ALL} the other student ({colorama.Style.BRIGHT}Y{colorama.Style.RESET_ALL}/{colorama.Style.BRIGHT}N{colorama.Style.RESET_ALL}): ")
        if deleteRequest.lower() == "y":
            cursor.execute("DELETE FROM Students WHERE Initials=?;", (newInitials, ))
            connection.commit()
        else:
            os.system('cls' if os.name=='nt' else 'clear')
            print(f"{colorama.Fore.GREEN + colorama.Style.BRIGHT}Overwrite aborted.{colorama.Fore.RESET + colorama.Style.RESET_ALL}")
            cursor.close()
            connection.close()
            return mainOption_Manage_Edit(studentSelected)
    
    cursor.execute("UPDATE Students SET Initials=? WHERE StudentID=?;", (newInitials, studentSelected[0]))
    connection.commit()
    
    os.system('cls' if os.name=='nt' else 'clear')
    print(f"{colorama.Fore.GREEN + colorama.Style.BRIGHT}Successfully edited student!{colorama.Fore.RESET + colorama.Style.RESET_ALL}")
    sleep(1)
    os.system('cls' if os.name=='nt' else 'clear')
    
    cursor.close()
    connection.close()
    return True

def mainOption_Manage_Delete(studentSelected=None):
    with open("setup.json", "r") as f:
        globalVariables = json.loads(f.read())
    connection = sqlite3.connect(globalVariables['database_location'], detect_types=sqlite3.PARSE_DECLTYPES | sqlite3.PARSE_COLNAMES)
    cursor = connection.cursor()
    
    if studentSelected == None:
        cursor.execute("SELECT StudentID, Initials FROM Students;")
        result = cursor.fetchall()
        
        print("Students:")
        for student in result:
            print(f"{colorama.Style.BRIGHT}{result.index(student)+1}{colorama.Style.RESET_ALL} | {student[1]}")
        
        studentSelectID = input("ID of the student: ")
        try:
            validStudentSelectID = int(studentSelectID)
        except ValueError:
            os.system('cls' if os.name=='nt' else 'clear')
            print(f"{colorama.Fore.RED + colorama.Style.BRIGHT}Invalid input. Please enter an integer.{colorama.Fore.RESET + colorama.Style.RESET_ALL}")
            cursor.close()
            connection.close()
            return mainOption_Manage_Delete()
        
        if validStudentSelectID < 1 or validStudentSelectID > len(result):
            os.system('cls' if os.name=='nt' else 'clear')
            print(f"{colorama.Fore.RED + colorama.Style.BRIGHT}Invalid input. Please enter an integer between 1 and {len(result)}{colorama.Fore.RESET + colorama.Style.RESET_ALL}")
            cursor.close()
            connection.close()
            return mainOption_Manage_Delete()

        studentSelected = result[validStudentSelectID-1]
    
    deleteRequest = input(f"Would you like to {colorama.Fore.RED + colorama.Style.BRIGHT}PERMANENTLY DELETE{colorama.Fore.RESET + colorama.Style.RESET_ALL} this student ({studentSelected[1]}) ({colorama.Style.BRIGHT}Y{colorama.Style.RESET_ALL}/{colorama.Style.BRIGHT}N{colorama.Style.RESET_ALL}): ")
    if deleteRequest.lower() == "y":
        cursor.execute("DELETE FROM Students WHERE StudentID=?;", (studentSelected[0], ))
        connection.commit()
    else:
        os.system('cls' if os.name=='nt' else 'clear')
        print(f"{colorama.Fore.GREEN + colorama.Style.BRIGHT}Delete aborted.{colorama.Fore.RESET + colorama.Style.RESET_ALL}")
        sleep(1)
        os.system('cls' if os.name=='nt' else 'clear')
        cursor.close()
        connection.close()
        return False
    
    os.system('cls' if os.name=='nt' else 'clear')
    print(f"{colorama.Fore.GREEN + colorama.Style.BRIGHT}Successfully deleted student!{colorama.Fore.RESET + colorama.Style.RESET_ALL}")
    sleep(1)
    os.system('cls' if os.name=='nt' else 'clear')

    cursor.close()
    connection.close()
    return True

def update_program(softwareVersion):
    with open("setup.json", "r") as f:
        globalVariables = json.loads(f.read())
    try:
        if globalVariables['release_key'] == "":
            headers = {}
        else:
            headers = headers = {'Authorization': f"token {globalVariables['release_key']}"}
        releaseName = requests.get(globalVariables['release_URL'], headers=headers).json()['name']
    except:
        input("An error occured, press enter to exit")
        exit()
    match = re.fullmatch(r'Release v(\d+)\.(\d+)\.(\d+)', releaseName)
    if match:
        major, minor, patch = map(int, match.groups())
        validGithubRelease = True
        if (major, minor, patch) == softwareVersion:
            version_color = colorama.Fore.GREEN
            update_status = "- Up to date"
        elif (major, minor, patch) > softwareVersion:
            version_color = colorama.Fore.RED
            update_status = "- Update available"
        else:
            version_color = colorama.Fore.LIGHTYELLOW_EX
            update_status = "Beta"
    else:
        validGithubRelease = False
        version_color = colorama.Fore.RED
        update_status = "- An error occurred"
        
        # os.system('cls' if os.name=='nt' else 'clear')
        
        
    print(colorama.Style.BRIGHT + "==========================================================")
    print("||                                                      ||")
    print("||                 Software Information                 ||")
    print(f"||    Current version: {version_color}v{softwareVersion[0]}.{softwareVersion[1]}.{softwareVersion[2]} {update_status}{colorama.Style.RESET_ALL}{colorama.Style.BRIGHT}".ljust(69) + "||")
    if validGithubRelease:
        print(f"||    Latest version: {colorama.Fore.GREEN}v{major}.{minor}.{patch}{colorama.Style.RESET_ALL}{colorama.Style.BRIGHT}".ljust(69) + "||")
    if not validGithubRelease:
        print(f"||    Latest version: {colorama.Fore.RED}Error connecting to server{colorama.Style.RESET_ALL}".ljust(65) + f"{colorama.Style.BRIGHT}||")
    print("||                                                      ||")
    print("==========================================================" + colorama.Style.RESET_ALL)
        
    if not (validGithubRelease and (major, minor, patch) > softwareVersion):
        input("Press enter to continue")
        os.system('cls' if os.name=='nt' else 'clear')
        return
    if major != softwareVersion[0]:
        print("The latest update has indicated that there has been a major change to it's underlying code which may cause issues,")
        print("we will try to resolve these issues when the program next starts.")
    
    updateRequest = input(f"Would you like to {colorama.Fore.GREEN + colorama.Style.BRIGHT}update{colorama.Fore.RESET + colorama.Style.RESET_ALL} ({colorama.Style.BRIGHT}Y{colorama.Style.RESET_ALL}/{colorama.Style.BRIGHT}N{colorama.Style.RESET_ALL}): ")
    if updateRequest.lower() != "y":
        return
    os.system('cls' if os.name=='nt' else 'clear')
    print(f"{colorama.Fore.RED + colorama.Style.BRIGHT}Do not close the program. The program will close when it is completed.{colorama.Fore.RESET + colorama.Style.RESET_ALL}")
    print(f"{colorama.Fore.GREEN + colorama.Style.BRIGHT}0/4 | Downloading update...{colorama.Fore.RESET + colorama.Style.RESET_ALL}")
    try:
        if globalVariables['release_key'] == "":
            headers = {}
        else:
            headers = headers = {'Authorization': f'token {globalVariables['release_key']}'}
        assets  = requests.get(globalVariables['release_URL'], headers=headers).json()['assets']
    except:
        input("An error occured, press enter to exit")
        exit()
    for asset in assets:
        if asset['name'] == f"Attendance-Register-v{major}.{minor}.{patch}-Public.exe" or asset['name'] == f"Attendance-Register-v{major}.{minor}.{patch}-Internal.exe":
            try:
                if globalVariables['release_key'] == "":
                    headers = {}
                else:
                    headers = headers = {'Authorization': f"token {globalVariables['release_key']}", 'Accept': "application/octet-stream"}
                response = requests.get(asset['url'], headers=headers)
            except:
                input("An error occured, press enter to exit")
                exit()
            if response.status_code == 200 or response.status_code == 302:
                with open(asset['name'], 'wb') as f:
                    f.write(response.content)
                print(f"{colorama.Fore.GREEN + colorama.Style.BRIGHT}1/4 | Successfully downloaded executable file{colorama.Fore.RESET + colorama.Style.RESET_ALL}")
                if not os.path.exists("Temp/"):
                    os.mkdir("Temp/")
                with open("Temp/update.txt", "w") as f:
                    f.write("1")
                print(f"{colorama.Fore.GREEN + colorama.Style.BRIGHT}2/4 | Stored temporary files{colorama.Fore.RESET + colorama.Style.RESET_ALL}")
                
                print(f"{colorama.Fore.GREEN + colorama.Style.BRIGHT}3/4 | Updating Desktop Shortcut{colorama.Fore.RESET + colorama.Style.RESET_ALL}")
                shortcutPath = os.path.join(os.path.expanduser("~"), "Desktop", "Attendance Register.lnk")
                workingDirectory = os.getcwd()
                targetPath = workingDirectory + "\\" + asset['name']
                iconPath = workingDirectory + "\\Static\\icon.ico"
                if not os.path.exists(iconPath):
                    iconPath = ""
                
                tempDir = (os.environ.get('TMPDIR') or os.environ.get('TEMP') or os.environ.get('TMP'))
                
                if tempDir:
                    if not os.path.exists(tempDir):
                        os.mkdir(tempDir)
                    tempDir += "/Attendance_Register/"
                
                if not os.path.exists(tempDir):
                    os.mkdir(tempDir)
                
                if os.path.exists((tempDir + "shortcut_info.json")):
                    os.remove((tempDir + "shortcut_info.json"))
                
                if os.path.exists(shortcutPath):
                    with open((tempDir + "shortcut_info.json"), "w") as f:
                        json.dump({
                            "type": "modify",
                            "shortcutPath": shortcutPath,
                            "targetPath": targetPath,
                            "iconPath": workingDirectory,
                            "workingDirectory": iconPath
                            }, fp=f, indent=4)
                else:
                    with open((tempDir + "shortcut_info.json"), "w") as f:
                        json.dump({
                            "type": "create",
                            "shortcutPath": shortcutPath,
                            "targetPath": targetPath,
                            "iconPath": workingDirectory,
                            "workingDirectory": iconPath
                            }, fp=f, indent=4)
                
                print("For the desktop shortcut to update, please allow \"desktop_shortcut.exe\" app to make changes to your device")
                input("The popup will appear when you press enter (it may take a while to appear)")
                ctypes.windll.shell32.ShellExecuteW(None, "runas", "desktop_shortcut.exe", "", None, 1)
                while os.path.exists((tempDir + "shortcut_info.json")):
                    sleep(1)
                print(f"{colorama.Fore.GREEN + colorama.Style.BRIGHT}4/4 | Exiting...{colorama.Fore.RESET + colorama.Style.RESET_ALL}")
                sleep(2)
                exit()
            print(f"{colorama.Fore.RED + colorama.Style.BRIGHT}1/4 | Failed to downloaded executable file{colorama.Fore.RESET + colorama.Style.RESET_ALL}")
            print(f"{colorama.Fore.RED + colorama.Style.BRIGHT}Aborting update...{colorama.Fore.RESET + colorama.Style.RESET_ALL}")
            break

def print_view_menu():
    print(colorama.Style.BRIGHT + "=================================")
    print("||                             ||")
    print("||     View Student Record     ||")
    print("||  1) Session Stats           ||")
    print("||  2) % Before Date           ||")
    print("||  3) % After Date            ||")
    print("||  4) % Between Dates         ||")
    print("||  5) Print Data              ||")
    print("||  6) Back to main menu       ||")
    print("||                             ||")
    print("=================================" + colorama.Style.RESET_ALL)

def print_manage_menu(students=True):
    print(colorama.Style.BRIGHT + "=================================")
    print("||                             ||")
    print("||       Manage Students       ||")
    print("||  1) Create student          ||")
    if students:
        print("||  2) Edit student            ||")
        print("||  3) Delete students         ||")
    else:
        print("||" + colorama.Style.RESET_ALL + "  \033[9m2) Edit student\033[0m            " + colorama.Style.BRIGHT + "||")
        print("||" + colorama.Style.RESET_ALL + "  \033[9m3) Delete students\033[0m         " + colorama.Style.BRIGHT + "||")
    print("||  4) Back to main menu       ||")
    print("||                             ||")
    print("=================================" + colorama.Style.RESET_ALL)

def print_main_menu(students=True):
    try:
        if globalVariables['release_key'] == "":
            headers = {}
        else:
            headers = headers = {'Authorization': f"token {globalVariables['release_key']}"}
        releaseName = requests.get(globalVariables['release_URL'], headers=headers).json()['name']
    except:
        input("An error occured, press enter to exit")
        exit()
    
    match = re.fullmatch(r'Release v(\d+)\.(\d+)\.(\d+)', releaseName)
    menuColourVersion = ""
    if match:
        try:
            major, minor, patch = map(int, match.groups())
            if (major, minor, patch) == softwareVersion:
                menuColourVersion = colorama.Fore.GREEN
            elif (major, minor, patch) > softwareVersion:
                menuColourVersion = colorama.Fore.RED
        except:
            pass
    
    print(colorama.Style.BRIGHT + "=================================")
    print("||                             ||")
    print("||     Attendence Register     ||")
    if students:
        print("||  1) Update student record   ||")
        print("||  2) View student record     ||")
    else:
        print("||" + colorama.Style.RESET_ALL + "  \033[9m1) Update student record\033[0m   " + colorama.Style.BRIGHT + "||")
        print("||" + colorama.Style.RESET_ALL + "  \033[9m2) View student record\033[0m     " + colorama.Style.BRIGHT + "||")
    print("||  3) Manage students         ||")
    if menuColourVersion == "":
        print(f"||  4) Software Info{colorama.Style.RESET_ALL}{colorama.Style.BRIGHT}           ||")
    else:
        print(f"||  4) " + menuColourVersion + f"Software Info{colorama.Style.RESET_ALL}{colorama.Style.BRIGHT}           ||")
        
    print("||  5) Exit                    ||")
    print("||                             ||")
    print("=================================" + colorama.Style.RESET_ALL)


# Init
if not os.path.exists("setup.json"):
    with open("setup.json", "w") as f:
        json.dump({
            "version": setupVersion,
            "database_location": "storage.db",
            "output_folder": "printer",
            "release_URL": "https://api.github.com/repos/LukeNeedle/Attendance-Register/releases/latest",
            "release_key": ""
            }, fp=f, indent=4)
with open("setup.json", "r") as f:
    globalVariables = json.loads(f.read())

if os.path.exists("Temp/update.txt"):
    with open("Temp/update.txt", "r") as f:
        if f.readline().strip() == "1":
            updated = True
        else:
            updated = False
else:
    updated = False

if updated == True:
    # Delete Old .exe
    with os.scandir() as entries:
        for entry in entries:
            if entry.is_file() and entry.name.startswith("Attendance-Register-v") and entry.name.endswith('.exe') and f"{softwareVersion[0]}.{softwareVersion[1]}.{softwareVersion[2]}" not in entry.name:
                os.remove(entry.path)
    
    # This if statment will grow for every major update that changes setup.json or to the database schema.
    # It updates setup.json to fully support the latest update
    
    # Currently updates to setup v2
    
    if 'version' not in globalVariables: # <v2
        with open("setup.json", "w") as f:
            json.dump({
                "version": setupVersion,
                "database_location": globalVariables['database_location'],
                "output_folder": globalVariables['output_folder'],
                "release_URL": "https://api.github.com/repos/LukeNeedle/Attendance-Register/releases/latest",
                "release_key": ""
                }, fp=f, indent=4)
    
    elif globalVariables['version'] == 2: # =v2
        # Fully updated already
        pass
    
    os.remove("Temp/update.txt")

colorama.init()
os.system('cls' if os.name=='nt' else 'clear')

if os.path.exists("static/loadingimage.jpg"):
    print(colorama.Style.BRIGHT)
    os.system('cls' if os.name=='nt' else 'clear')
    image = Image.open('static/loadingimage.jpg')
    pixel_values = image.resize((90, 30)).getdata()
    for index, character in enumerate(pixel_values):
        if not isinstance(character, (tuple, list)) or len(character) != 3:
            continue # Skip this iteration if not three values
        r, g, b = character
        if index % 90 == 0:
            print("")
        print(Colr().rgb(r, g, b, "\u2584"), end="")
    sleep(3)
    print(colorama.Style.RESET_ALL)
    print("\n"*5)
    os.system('cls' if os.name=='nt' else 'clear')

mainLoop = True

while mainLoop:
    if os.path.exists(globalVariables['database_location']):
        # Open database
        connection = sqlite3.connect(globalVariables['database_location'], detect_types=sqlite3.PARSE_DECLTYPES | sqlite3.PARSE_COLNAMES)
        cursor = connection.cursor()
        cursor.execute("SELECT * FROM Students;")
        if cursor.fetchone():
            # Students are available
            students = True
        else:
            students = False
        
        cursor.close()
        connection.close()
    else:
        students = False
        # Create database
        connection = sqlite3.connect(globalVariables['database_location'], detect_types=sqlite3.PARSE_DECLTYPES | sqlite3.PARSE_COLNAMES)
        cursor = connection.cursor()
        cursor.execute("""CREATE TABLE IF NOT EXISTS "Students"(
                       "StudentID"  INTEGER NOT NULL UNIQUE,
                       "Initials" TEXT,
                       PRIMARY KEY("StudentID" AUTOINCREMENT));""")
        
        cursor.execute("""CREATE TABLE IF NOT EXISTS "Attendance"(
                       "StudentID"  INTEGER NOT NULL,
                       "Timestamp"  TIMESTAMP NOT NULL,
                       "Duration"   REAL NOT NULL,
                       "AmountAttended" REAL NOT NULL,
                       FOREIGN KEY("StudentID") REFERENCES "Students"("StudentID") ON DELETE CASCADE,
                       PRIMARY KEY("StudentID", "Timestamp"));""")
        cursor.close()
        connection.close()

    menuRepeat = True
    print_main_menu(students)
    while menuRepeat:
        menuSelection = input("What would you like to do? ")
        if menuSelection in ["1", "2", "3", "4", "5"] and students:
            menuRepeat = False
        elif menuSelection in ["3", "4", "5"] and not students:
            menuRepeat = False
        else:
            print(f"{colorama.Fore.RED + colorama.Style.BRIGHT}Invalid option{colorama.Fore.RESET + colorama.Style.RESET_ALL}")
    menuSelection = int(menuSelection)

    if menuSelection == 1:
        os.system('cls' if os.name=='nt' else 'clear')
        mainOption_Update()
    elif menuSelection == 2:
        os.system('cls' if os.name=='nt' else 'clear')
        mainOption_View()
    elif menuSelection == 3:
        os.system('cls' if os.name=='nt' else 'clear')
        manageMenuRepeat = True
        print_manage_menu(students)
        while manageMenuRepeat:
            menuSelection = input("What would you like to do? ")
            if menuSelection in ["1", "2", "3", "4"] and students:
                manageMenuRepeat = False
            elif menuSelection in ["1", "4"] and not students:
                manageMenuRepeat = False
            else:
                print(f"{colorama.Fore.RED + colorama.Style.BRIGHT}Invalid option{colorama.Fore.RESET + colorama.Style.RESET_ALL}")
                sleep(1)

        manageMenuRepeat = int(menuSelection)
        if manageMenuRepeat == 1:
            os.system('cls' if os.name=='nt' else 'clear')
            mainOption_Manage_Create(students)
        elif manageMenuRepeat == 2:
            os.system('cls' if os.name=='nt' else 'clear')
            mainOption_Manage_Edit()
        elif manageMenuRepeat == 3:
            os.system('cls' if os.name=='nt' else 'clear')
            mainOption_Manage_Delete()
        else:
            os.system('cls' if os.name=='nt' else 'clear')
    elif menuSelection == 4:
        os.system('cls' if os.name=='nt' else 'clear')
        update_program(softwareVersion)
        os.system('cls' if os.name=='nt' else 'clear')
    else:
        os.system('cls' if os.name=='nt' else 'clear')
        mainLoop = False
