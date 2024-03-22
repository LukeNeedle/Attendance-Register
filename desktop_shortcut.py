try:
    import win32com.client
    import json
    import ctypes
    import sys
    import os

    def is_admin():
        try:
            return ctypes.windll.shell32.IsUserAnAdmin()
        except:
            return False

    def create_shortcut(shortcutPath, targetPath, iconPath=None, workingDirectory=None):
        shell = win32com.client.Dispatch("WScript.Shell")
        shortcut = shell.CreateShortCut(shortcutPath)
        shortcut.Targetpath = targetPath
        if iconPath:
            shortcut.IconLocation = iconPath
        if workingDirectory:
            shortcut.WorkingDirectory = workingDirectory
        
        shortcut.save()

    def modify_shortcut(shortcutPath, targetPath=None, iconPath=None, workingDirectory=None):
        shell = win32com.client.Dispatch("WScript.Shell")
        shortcut = shell.CreateShortCut(shortcutPath)
        if targetPath:
            shortcut.Targetpath = targetPath
        if workingDirectory:
            shortcut.WorkingDirectory = workingDirectory
        if iconPath:
            shortcut.IconLocation = iconPath
        shortcut.save()

    if not is_admin():
        print("For the desktop shortcut to update, please allow \"desktop_shortcut.exe\" app to make changes to your device")
        input("The popup will appear when you press enter")
        ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, " ".join(sys.argv), None, 1)
        exit()

    tempDir = (os.environ.get('TMPDIR') or os.environ.get('TEMP') or os.environ.get('TMP'))
    if tempDir:
        tempDir += "/Attendance_Register/"
        if os.path.exists(tempDir + "shortcut_info.json"):
            with open((tempDir + "shortcut_info.json"), "r") as f:
                shorcutInfo = json.loads(f.read())

            if shorcutInfo['type'] == "modify":
                modify_shortcut(shorcutInfo['shortcutPath'], shorcutInfo['targetPath'], shorcutInfo['iconPath'], shorcutInfo['workingDirectory'])
            else:
                create_shortcut(shorcutInfo['shortcutPath'], shorcutInfo['targetPath'], shorcutInfo['iconPath'], shorcutInfo['workingDirectory'])

            os.remove(tempDir + "shortcut_info.json")
        else:
            print("An error occured, please contact the distributor of this program")
    else:
        print("An error occured, please contact the distributor of this program")

    input("Press enter to exit...")
except Exception as error:
    print(f"An exception occurred: {error}")
    print("An error occured, please contact the distributor of this program")
    input("Press enter to exit...")
