import colorama
from colr import Colr
import ctypes
import datetime
import sqlite3
import json
import os
from time import sleep
from tkinter import Tk, Button, Spinbox, StringVar, Label, Frame, messagebox, filedialog
from tkcalendar import Calendar
from PIL import Image
import requests
import re

softwareVersion=(2,1,0)
setupVersion = 3
APILimit = False

sqlite3.register_adapter(bool, int)
sqlite3.register_converter("BOOLEAN", lambda v: bool(int(v)))

sqlite3.register_adapter(datetime.datetime, lambda x: x.isoformat())
sqlite3.register_converter("TIMESTAMP", lambda x: datetime.datetime.fromisoformat(x.decode()))

def check_for_updates(APILimit, APIDisabled, privateRepo, globalVariables):
    if APIDisabled:
        print("API is disabled, edit your setup.json to enable it.")
        return (0,0,0)
    
    if APILimit:
        return (0,0,0)
    
    try:
        headers = {}
        if privateRepo:
            headers = {'Authorization': f'token {globalVariables['release_key']}'}

        if not APILimit:
            releaseData = requests.get(globalVariables['release_URL'], headers=headers)
    except:
        if "API rate limit exceeded" not in releaseData['message']:
            print(f"An error occured (Code: api_update, Version: {softwareVersion})")
            return (0,0,0)
        print("API rate limit exceeded")
        APILimit = True
        return (0,0,0)
    
    releaseName = releaseData.json()['name']
    
    match = re.fullmatch(r'Release v(\d+)\.(\d+)\.(\d+)', releaseName)
    if not match:
        return (0,0,0)

    try:
        major, minor, patch = map(int, match.groups())
        return (major, minor, patch)
    except:
        return (0,0,0)

def download_desktop_shortcut(APILimit, APIDisabled, privateRepo, softwareVersion, globalVariables):
    if APIDisabled:
        print("API is disabled, edit your setup.json to enable it.")
        return False
    
    if APILimit:
        print("API limit reached, please try again later.")
        return False
    
    try:
        headers = {}
        if privateRepo:
            headers = {'Authorization': f'token {globalVariables['release_key']}'}
        assetsData = requests.get(globalVariables['release_URL'], headers=headers).json()
        assets = assetsData['assets']
    except:
        if "API rate limit exceeded" not in assetsData['message']:
            print("An error occured")
            return False
        
        print("API rate limit exceeded")
        APILimit = True
        return False
    
    updateURL = ""
    
    for asset in assets:
        if asset['name'] == "desktop_shortcut.exe":
            updateURL = asset['url']
            break
    
    try:
        if not privateRepo:
            headers = {'Accept': "application/octet-stream"}
        else:
            headers = {'Authorization': f"token {globalVariables['release_key']}", 'Accept': "application/octet-stream"}
        
        if not APILimit:
            response = requests.get(updateURL, headers=headers)
    except:
        if "API rate limit exceeded" not in response['message']:
            print("An error occured")
            return False
        print("API rate limit exceeded")
        APILimit = True
        return False
    
    if response.status_code == 200 or response.status_code == 302:
        with open("desktop_shortcut.exe", 'wb') as f:
            f.write(response.content)
        return True
    
    input(f"An error occured, press enter to exit (Code: DskSrtCtDwnld2, Version: {softwareVersion})")
    return False

def update_program(APILimit, APIDisabled, privateRepo, globalVariables):
    if APIDisabled:
        print("API is disabled, edit your setup.json to enable it.")
        return False
    
    if APILimit:
        print("API limit reached, please try again later.")
        return False
    
    major, minor, patch = latestVersion
    
    if not download_desktop_shortcut(APILimit, APIDisabled, privateRepo, softwareVersion, globalVariables):
        print("Failed to download desktop shortcut.")
        return False
    
    if APILimit:
        print("API limit reached, please try again later.")
        return False
    
    os.system('cls' if os.name=='nt' else 'clear')
    print(f"{colorama.Fore.RED + colorama.Style.BRIGHT}Do not close the program. The program will close when it is completed.{colorama.Fore.RESET + colorama.Style.RESET_ALL}")
    print(f"{colorama.Fore.GREEN + colorama.Style.BRIGHT}0/4 | Downloading update...{colorama.Fore.RESET + colorama.Style.RESET_ALL}")
    try:
        headers = {}
        if privateRepo:
            headers = headers = {'Authorization': f'token {globalVariables['release_key']}'}
        assets  = requests.get(globalVariables['release_URL'], headers=headers).json()['assets']
    except:
        input("An error occured, press enter to continue")
        return False
    
    assetURL = ""
    assetName = ""
    for asset in assets:
        if asset['name'] == f"Attendance-Register-v{major}.{minor}.{patch}-Public.exe" or asset['name'] == f"Attendance-Register-v{major}.{minor}.{patch}-Internal.exe":
            assetURL = asset['url']
            assetName = asset['name']
            break
    try:
        if not privateRepo:
            headers = {'Accept': "application/octet-stream"}
        else:
            headers = headers = {'Authorization': f"token {globalVariables['release_key']}", 'Accept': "application/octet-stream"}
        response = requests.get(assetURL, headers=headers)
    except:
        input("An error occured, press enter to continue")
        return False
    if response.status_code == 200 or response.status_code == 302:
        with open(assetName, 'wb') as f:
            f.write(response.content)
        print(f"{colorama.Fore.GREEN + colorama.Style.BRIGHT}1/4 | Successfully downloaded executable file{colorama.Fore.RESET + colorama.Style.RESET_ALL}")
        if not os.path.exists("Temp/"):
            os.mkdir("Temp/")
        with open("Temp/update.txt", "w") as f:
            f.write("1")
        print(f"{colorama.Fore.GREEN + colorama.Style.BRIGHT}2/4 | Stored temporary files{colorama.Fore.RESET + colorama.Style.RESET_ALL}")
        
        print(f"{colorama.Fore.GREEN + colorama.Style.BRIGHT}3/4 | Updating Desktop Shortcut{colorama.Fore.RESET + colorama.Style.RESET_ALL}")
        shortcutPath = os.path.join(os.path.expanduser("~"), "Desktop", "Attendance Register.lnk")
        if not os.path.exists(shortcutPath):
            print(f"{colorama.Fore.RED}An error occured: Desktop cannot be found.")
            print(f"Aborting update...{colorama.Fore.RESET}")
            os.remove("Temp/update.txt")
            sleep(1)
            return False
        
        workingDirectory = os.getcwd()
        targetPath = workingDirectory + "\\" + assetName
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
                    "iconPath": iconPath,
                    "workingDirectory": workingDirectory
                    }, fp=f, indent=4)
        else:
            with open((tempDir + "shortcut_info.json"), "w") as f:
                json.dump({
                    "type": "create",
                    "shortcutPath": shortcutPath,
                    "targetPath": targetPath,
                    "iconPath": iconPath,
                    "workingDirectory": workingDirectory
                    }, fp=f, indent=4)
        
        print("For the desktop shortcut to update, please allow \"desktop_shortcut.exe\" app to make changes to your device")
        input("The popup will appear when you press enter (it may take a while to appear)")
        ctypes.windll.shell32.ShellExecuteW(None, "runas", "desktop_shortcut.exe", "", None, 1)
        while os.path.exists((tempDir + "shortcut_info.json")):
            sleep(1)
        print(f"{colorama.Fore.GREEN + colorama.Style.BRIGHT}4/4 | Restarting...{colorama.Fore.RESET + colorama.Style.RESET_ALL}")
        sleep(2)
        return True
    print(f"{colorama.Fore.RED + colorama.Style.BRIGHT}1/4 | Failed to downloaded executable file{colorama.Fore.RESET + colorama.Style.RESET_ALL}")
    print(f"{colorama.Fore.RED + colorama.Style.BRIGHT}Aborting update...{colorama.Fore.RESET + colorama.Style.RESET_ALL}")


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
    
    cal = Calendar(root, selectmode='day', year=datetime.datetime.now().year, month=datetime.datetime.now().month, day=datetime.datetime.now().day)
    cal.pack(pady=5)
    
    time_frame = Frame(root)
    time_frame.pack(pady=5)

    Label(time_frame, text="Hour:Minute").pack(side="top")
    
    hour_var = StringVar(root)
    minute_var = StringVar(root)
    defaultHour = datetime.datetime.now().time().hour
    defaultMinute = datetime.datetime.now().time().minute

    if defaultHour < 10:
        defaultHour = f"0{str(defaultHour)}"
    else:
        defaultHour = str(defaultHour)

    if defaultMinute < 10:
        defaultMinute = f"0{str(defaultMinute)}"
    else:
        defaultMinute = str(defaultMinute)
    
    hour_var.set(defaultHour)
    minute_var.set(defaultMinute)

    hour_sb = Spinbox(time_frame, from_=0, to=23, textvariable=hour_var, width=2, format="%02.0f")
    minute_sb = Spinbox(time_frame, from_=0, to=59, textvariable=minute_var, width=2, format="%02.0f")
    
    hour_sb.pack(side="left")
    Label(time_frame, text=":").pack(side="left")
    minute_sb.pack(side="left")
    
    Button(root, text="Submit Session", command=get_date).pack(pady=5)
    root.mainloop()


def mainOption_Update(globalVariables, studentSelected=None, dateReceived=None, validSessionDuration=None, validSessionDurationAttended=None):
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
                return mainOption_Update(globalVariables)
            
            if validStudentSelectID < 1 or validStudentSelectID > len(result):
                os.system('cls' if os.name=='nt' else 'clear')
                print(f"{colorama.Fore.RED + colorama.Style.BRIGHT}Invalid input. Please enter an integer between 1 and {len(result)}{colorama.Fore.RESET + colorama.Style.RESET_ALL}")
                cursor.close()
                connection.close()
                return mainOption_Update(globalVariables)

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
            return mainOption_Update(globalVariables, studentSelected=studentSelected, dateReceived=dateReceived)
        
        if validSessionDuration <= 0 or validSessionDuration > 24:
            os.system('cls' if os.name=='nt' else 'clear')
            print(f"{colorama.Fore.RED + colorama.Style.BRIGHT}Invalid input. Please enter a number between 0 and 23.{colorama.Fore.RESET + colorama.Style.RESET_ALL}")
            cursor.close()
            connection.close()
            return mainOption_Update(globalVariables, studentSelected=studentSelected, dateReceived=dateReceived)
    
    if validSessionDurationAttended == None:
        sessionDurationAttended = input("Session Duration Attended (in Hours): ")
        try:
            validSessionDurationAttended = float(sessionDurationAttended)
        except ValueError:
            os.system('cls' if os.name=='nt' else 'clear')
            print(f"{colorama.Fore.RED + colorama.Style.BRIGHT}Invalid input. Please enter a number between 0 and 23 and lower than the session duration ({validSessionDuration}).{colorama.Fore.RESET + colorama.Style.RESET_ALL}")
            cursor.close()
            connection.close()
            return mainOption_Update(globalVariables, studentSelected=studentSelected, dateReceived=dateReceived, validSessionDuration=validSessionDuration)
        
        if validSessionDurationAttended < 0 or validSessionDurationAttended > 24:
            os.system('cls' if os.name=='nt' else 'clear')
            print(f"{colorama.Fore.RED + colorama.Style.BRIGHT}Invalid input. Please enter a number between 0 and 23 and lower than the session duration ({validSessionDuration}).{colorama.Fore.RESET + colorama.Style.RESET_ALL}")
            cursor.close()
            connection.close()
            return mainOption_Update(globalVariables, studentSelected=studentSelected, dateReceived=dateReceived, validSessionDuration=validSessionDuration)
        
        if validSessionDurationAttended > validSessionDuration:
            os.system('cls' if os.name=='nt' else 'clear')
            print(f"{colorama.Fore.RED + colorama.Style.BRIGHT}Invalid input. Please enter a number between 0 and 23 and lower than the session duration ({validSessionDuration}).{colorama.Fore.RESET + colorama.Style.RESET_ALL}")
            cursor.close()
            connection.close()
            return mainOption_Update(globalVariables, studentSelected=studentSelected, dateReceived=dateReceived, validSessionDuration=validSessionDuration)
    
    print("="*40)
    print("Session Info:")
    print(f"Initials: {studentSelected[1]}")
    print(f"Date of Session: {dateReceived}")
    print(f"Duration of Session: {validSessionDuration}")
    print(f"Duration of Session attended: {validSessionDurationAttended}")
    print("="*40)
    
    confirmation = input(f"Is this ok? ({colorama.Style.BRIGHT}y{colorama.Style.RESET_ALL}/{colorama.Style.BRIGHT}N{colorama.Style.RESET_ALL}) ").lower()
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


def mainOption_View(globalVariables, studentSelected=None):
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
                return mainOption_View(globalVariables)
            
            if validStudentSelectID < 1 or validStudentSelectID > len(result):
                os.system('cls' if os.name=='nt' else 'clear')
                print(f"{colorama.Fore.RED + colorama.Style.BRIGHT}Invalid input. Please enter an integer between 1 and {len(result)}{colorama.Fore.RESET + colorama.Style.RESET_ALL}")
                cursor.close()
                connection.close()
                return mainOption_View(globalVariables)

            studentSelected = result[validStudentSelectID-1]
    
    os.system('cls' if os.name=='nt' else 'clear')
    print_view_menu()
    print(f"Selected Student: {studentSelected[1]}")
    menuSelection = input("What would you like to do? ")
    if menuSelection not in ["1", "2", "3", "4", "5", "6"]:
        print(f"{colorama.Fore.RED + colorama.Style.BRIGHT}Invalid option{colorama.Fore.RESET + colorama.Style.RESET_ALL}")
        sleep(1)
        mainOption_View(globalVariables, studentSelected)
    
    menuSelection = int(menuSelection)

    cursor.close()
    connection.close()
    os.system('cls' if os.name=='nt' else 'clear')
    if menuSelection == 1:
        return mainOption_View_Session_Stats(studentSelected[0], globalVariables)
    elif menuSelection == 2:
        return mainOption_View_Session_Stats_Before(studentSelected[0], globalVariables)
    elif menuSelection == 3:
        return mainOption_View_Session_Stats_After(studentSelected[0], globalVariables)
    elif menuSelection == 4:
        return mainOption_View_Session_Stats_Between(studentSelected[0], globalVariables)
    elif menuSelection == 5:
        return mainOption_View_Print_Data(studentSelected[0], globalVariables)
    else:
        return False

def mainOption_View_Session_Stats(studentID, globalVariables):
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

def mainOption_View_Session_Stats_Before(studentID, globalVariables, dateReceived=None):
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

def mainOption_View_Session_Stats_After(studentID, globalVariables, dateReceived=None):
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

def mainOption_View_Session_Stats_Between(studentID, globalVariables, dateReceivedStart=None, dateReceivedEnd=None):
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

def mainOption_View_Print_Data(studentID, globalVariables):
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
    openFile = input(f"Would you like to open the file? ({colorama.Style.BRIGHT}y{colorama.Style.RESET_ALL}/{colorama.Style.BRIGHT}N{colorama.Style.RESET_ALL}): ")
    if openFile.lower() == "y":
        os.system("notepad.exe " + filePath)
    
    os.system('cls' if os.name=='nt' else 'clear')
    cursor.close()
    connection.close() 


def mainOption_Manage_Create(students:bool, globalVariables):
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
        return mainOption_Manage_Create(students, globalVariables)
    
    if students:
        cursor.execute("SELECT StudentID FROM Students WHERE Initials=?;", (initials, ))
        if cursor.fetchone() != None:
            print(f"{colorama.Fore.YELLOW + colorama.Style.BRIGHT}These initials are already in use.{colorama.Fore.RESET + colorama.Style.RESET_ALL}")
            deleteRequest = input(f"Would you like to {colorama.Fore.RED + colorama.Style.BRIGHT}overwrite{colorama.Fore.RESET + colorama.Style.RESET_ALL} the other student ({colorama.Style.BRIGHT}y{colorama.Style.RESET_ALL}/{colorama.Style.BRIGHT}N{colorama.Style.RESET_ALL}): ")
            if deleteRequest.lower() == "y":
                cursor.execute("DELETE FROM Students WHERE Initials=?;", (initials, ))
                connection.commit()
            else:
                os.system('cls' if os.name=='nt' else 'clear')
                print(f"{colorama.Fore.GREEN + colorama.Style.BRIGHT}Overwrite aborted.{colorama.Fore.RESET + colorama.Style.RESET_ALL}")
                cursor.close()
                connection.close()
                return mainOption_Manage_Create(students, globalVariables)
    
    cursor.execute("INSERT INTO Students(Initials) VALUES (?);", (initials, ))
    connection.commit()
    
    os.system('cls' if os.name=='nt' else 'clear')
    print(f"{colorama.Fore.GREEN + colorama.Style.BRIGHT}Successfully created new student!{colorama.Fore.RESET + colorama.Style.RESET_ALL}")
    sleep(1)
    os.system('cls' if os.name=='nt' else 'clear')
    cursor.close()
    connection.close()
    return True

def mainOption_Manage_Edit(globalVariables, studentSelected=None):
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
            return mainOption_Manage_Edit(globalVariables)
        
        if validStudentSelectID < 1 or validStudentSelectID > len(result):
            os.system('cls' if os.name=='nt' else 'clear')
            print(f"{colorama.Fore.RED + colorama.Style.BRIGHT}Invalid input. Please enter an integer between 1 and {len(result)}{colorama.Fore.RESET + colorama.Style.RESET_ALL}")
            cursor.close()
            connection.close()
            return mainOption_Manage_Edit(globalVariables)

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
        return mainOption_Manage_Edit(globalVariables, studentSelected)
    
    deleteRequest = "n"
    cursor.execute("SELECT StudentID FROM Students WHERE Initials=?;", (newInitials, ))
    if cursor.fetchone() != None:
        print(f"{colorama.Fore.RED + colorama.Style.BRIGHT}These initials are already in use.{colorama.Fore.RESET + colorama.Style.RESET_ALL}")
        deleteRequest = input(f"Would you like to {colorama.Fore.RED + colorama.Style.BRIGHT}overwrite{colorama.Fore.RESET + colorama.Style.RESET_ALL} the other student ({colorama.Style.BRIGHT}y{colorama.Style.RESET_ALL}/{colorama.Style.BRIGHT}N{colorama.Style.RESET_ALL}): ")
        if deleteRequest.lower() == "y":
            cursor.execute("DELETE FROM Students WHERE Initials=?;", (newInitials, ))
            connection.commit()
        else:
            os.system('cls' if os.name=='nt' else 'clear')
            print(f"{colorama.Fore.GREEN + colorama.Style.BRIGHT}Overwrite aborted.{colorama.Fore.RESET + colorama.Style.RESET_ALL}")
            cursor.close()
            connection.close()
            return mainOption_Manage_Edit(globalVariables, studentSelected)
    
    cursor.execute("UPDATE Students SET Initials=? WHERE StudentID=?;", (newInitials, studentSelected[0]))
    connection.commit()
    
    os.system('cls' if os.name=='nt' else 'clear')
    print(f"{colorama.Fore.GREEN + colorama.Style.BRIGHT}Successfully edited student!{colorama.Fore.RESET + colorama.Style.RESET_ALL}")
    sleep(1)
    os.system('cls' if os.name=='nt' else 'clear')
    
    cursor.close()
    connection.close()
    return True

def mainOption_Manage_Delete(globalVariables, studentSelected=None):
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
            return mainOption_Manage_Delete(globalVariables)
        
        if validStudentSelectID < 1 or validStudentSelectID > len(result):
            os.system('cls' if os.name=='nt' else 'clear')
            print(f"{colorama.Fore.RED + colorama.Style.BRIGHT}Invalid input. Please enter an integer between 1 and {len(result)}{colorama.Fore.RESET + colorama.Style.RESET_ALL}")
            cursor.close()
            connection.close()
            return mainOption_Manage_Delete(globalVariables)

        studentSelected = result[validStudentSelectID-1]
    
    deleteRequest = input(f"Would you like to {colorama.Fore.RED + colorama.Style.BRIGHT}PERMANENTLY DELETE{colorama.Fore.RESET + colorama.Style.RESET_ALL} this student ({studentSelected[1]}) ({colorama.Style.BRIGHT}y{colorama.Style.RESET_ALL}/{colorama.Style.BRIGHT}N{colorama.Style.RESET_ALL}): ")
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


def software_information(APILimit, APIDisabled, softwareVersion, latestVersion):
    updateAvailable = False
    
    if APIDisabled:
        print("API is disabled, edit your setup.json to enable it.")
    
    if APILimit:
        print("API limit reached, please try again later")
    
    validGithubRelease = True

    versionColour = ""
    updateStatus = ""
    if latestVersion == (0,0,0):
        validGithubRelease = False
        versionColour = colorama.Fore.RED
    elif latestVersion == softwareVersion:
        versionColour = colorama.Fore.GREEN
        updateStatus = "- Up to date"
    elif latestVersion > softwareVersion:
        versionColour = colorama.Fore.RED
        updateStatus = "- Update available"
        updateAvailable = True
    else:
        versionColour = colorama.Fore.LIGHTYELLOW_EX
        updateStatus = "Beta"
    
    if APILimit:
        versionColour = colorama.Fore.RED
        updateStatus = "- API limit reached"
        validGithubRelease = False
    
    if APIDisabled:
        versionColour = ""
        updateStatus = "- API disabled"
        validGithubRelease = False
    
    major, minor, patch = latestVersion
    
    print(colorama.Style.BRIGHT + "==========================================================")
    print("||                                                      ||")
    print("||                 Software Information                 ||")
    print(f"||    Current version: {versionColour}v{softwareVersion[0]}.{softwareVersion[1]}.{softwareVersion[2]} {updateStatus}{colorama.Style.RESET_ALL}{colorama.Style.BRIGHT}".ljust(69) + "||")
    if validGithubRelease:
        print(f"||    Latest version: {colorama.Fore.GREEN}v{major}.{minor}.{patch}{colorama.Style.RESET_ALL}{colorama.Style.BRIGHT}".ljust(69) + "||")
    if not validGithubRelease:
        print(f"||    Latest version: {colorama.Fore.RED}Error connecting to server{colorama.Style.RESET_ALL}".ljust(65) + f"{colorama.Style.BRIGHT}||")
    print("||                                                      ||")
    print("==========================================================" + colorama.Style.RESET_ALL)
    
    if not (updateAvailable and validGithubRelease):
        input("Press enter to continue")
        os.system('cls' if os.name=='nt' else 'clear')
        return False
    
    if major != softwareVersion[0]:
        print("The latest update has indicated that there has been a major change to it's underlying code which may cause issues,")
        print("we will try to resolve these issues when the program next starts.")
        print("If you have any questions, concerns or you need help updating, please contact your software distributor.")
    
    updateRequest = input(f"Would you like to {colorama.Fore.GREEN + colorama.Style.BRIGHT}update{colorama.Fore.RESET + colorama.Style.RESET_ALL} ({colorama.Style.BRIGHT}y{colorama.Style.RESET_ALL}/{colorama.Style.BRIGHT}N{colorama.Style.RESET_ALL}): ")
    if updateRequest.lower() != "y":
        return False
    
    if update_program(APILimit, APIDisabled, privateRepo, globalVariables):
        print("Updated successfully!")
        input("Press enter to restart.")
        major, minor, patch = latestVersion
        executableName = f"Attendance-Register-v{major}.{minor}.{patch}-"
        if privateRepo:
            executableName += "Internal.exe"
        else:
            executableName += "Public.exe"
        if os.path.exists(executableName):
            executablePath = os.getcwd() + "\\" + executableName
            os.system(f"start cmd.exe /C {executablePath}")
        else:
            print("An error occured, please restart manually.")
        return True
    else:
        print("Update failed. Please try again later.")
        return False


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

def print_main_menu(latestVersion, students=True):
    menuColourVersion = ""
    if latestVersion == (0,0,0):
        menuColourVersion = ""
    elif latestVersion == softwareVersion:
        menuColourVersion = colorama.Fore.GREEN
    elif latestVersion > softwareVersion:
        menuColourVersion = colorama.Fore.RED
    
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
    if menuColourVersion == "" or APILimit:
        print(f"||  4) Software Info{colorama.Style.BRIGHT}           ||")
    else:
        print(f"||  4) " + menuColourVersion + f"Software Info{colorama.Style.RESET_ALL}{colorama.Style.BRIGHT}           ||")
        
    print("||  5) Exit                    ||")
    print("||                             ||")
    print("=================================" + colorama.Style.RESET_ALL)


def loading_image():
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
    sleep(2)
    print(colorama.Style.RESET_ALL)
    print("\n"*5)
    os.system('cls' if os.name=='nt' else 'clear')


# Init
if not os.path.exists("setup.json"):
    with open("setup.json", "w") as f:
        json.dump({
            "version": setupVersion,
            "database_location": "storage.db",
            "output_folder": "printer",
            "release_URL": "https://api.github.com/repos/LukeNeedle/Attendance-Register/releases/latest",
            "release_key": "",
            "API": True
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

if updated:
    # Delete Old .exe
    with os.scandir() as entries:
        for entry in entries:
            if entry.is_file() and entry.name.startswith("Attendance-Register-v") and entry.name.endswith('.exe') and f"{softwareVersion[0]}.{softwareVersion[1]}.{softwareVersion[2]}" not in entry.name:
                os.remove(entry.path)
    
    # This if statment will grow for every major update that changes setup.json or to the database schema.
    # It updates setup.json to fully support the latest update
    
    # Currently updates to setup v3
    
    if 'version' not in globalVariables: # <v2
        with open("setup.json", "w") as f:
            json.dump({
                "version": setupVersion,
                "database_location": globalVariables['database_location'],
                "output_folder": globalVariables['output_folder'],
                "release_URL": "https://api.github.com/repos/LukeNeedle/Attendance-Register/releases/latest",
                "release_key": "",
                "API": True
                }, fp=f, indent=4)
    
    elif globalVariables['version'] == 2: # =v2
        with open("setup.json", "w") as f:
            json.dump({
                "version": setupVersion,
                "database_location": globalVariables['database_location'],
                "output_folder": globalVariables['output_folder'],
                "release_URL": globalVariables['release_URL'],
                "release_key": globalVariables['release_key'],
                "API": True
                }, fp=f, indent=4)
    
    elif globalVariables['version'] == 3: # =v3
        # Fully updated already
        pass
    
    # Reload global variables
    with open("setup.json", "r") as f:
        globalVariables = json.loads(f.read())
    
    os.remove("Temp/update.txt")


APIDisabled = False
if globalVariables['API'] == False:
    APIDisabled = True

privateRepo = False
if globalVariables['release_key'] != "":
    privateRepo = True

if updated:
    # Downloads latest version of desktop_shortcut.exe
    download_desktop_shortcut(APILimit, APIDisabled, privateRepo, softwareVersion, globalVariables)

latestVersion = check_for_updates(APILimit, APIDisabled, privateRepo, globalVariables)

colorama.init()
os.system('cls' if os.name=='nt' else 'clear')

if os.path.exists("static/loadingimage.jpg"):
    loading_image()

# Main code loop
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
    print_main_menu(latestVersion, students)
    while menuRepeat:
        menuSelection = input("What would you like to do? ")
        if menuSelection in ["1", "2", "3", "4", "5"] and students:
            menuRepeat = False
        elif menuSelection in ["3", "4", "5"] and not students:
            menuRepeat = False
        else:
            print(f"{colorama.Fore.RED + colorama.Style.BRIGHT}Invalid option{colorama.Fore.RESET + colorama.Style.RESET_ALL}")
    menuSelection = int(menuSelection)

    os.system('cls' if os.name=='nt' else 'clear')
    if menuSelection == 1:
        mainOption_Update(globalVariables)
    elif menuSelection == 2:
        mainOption_View(globalVariables)
    elif menuSelection == 3:
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
        os.system('cls' if os.name=='nt' else 'clear')
        if manageMenuRepeat == 1:
            mainOption_Manage_Create(students, globalVariables)
        elif manageMenuRepeat == 2:
            mainOption_Manage_Edit(globalVariables)
        elif manageMenuRepeat == 3:
            mainOption_Manage_Delete(globalVariables)
    elif menuSelection == 4:
        if software_information(APILimit, APIDisabled, softwareVersion, latestVersion):
            mainLoop = False
        os.system('cls' if os.name=='nt' else 'clear')
    else:
        mainLoop = False
