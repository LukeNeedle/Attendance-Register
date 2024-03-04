# Attendance Register
 A simple system for recording attendance.

> [!CAUTION]
> The program is only written for one person to use at the same time. If multiple users try to use it at the same time side effects may occure including the database becoming corrupted or the programs crashing.

## Customisation
### Splashscreen
To add a custom splashscreen that appears as the program loads, save the image in .\Static\ with the name loadingimage.jpg.

> [!Note]
> The default aspect ratio supported for a custom splashscreen is 3:1.
> Support for different aspect ratios in setup.json is not currently implimented but may be introduced in the future.
> If you require a different aspect ration, you must edit the source code to support it.
> The lines you must edit are:
> - 809: pixel_values = image.resize((90, 30)).getdata() # Change (90,30) to (width of the image according to your aspect ratio, the number of lines the console window will display (30 is good))
> - 814: if index % 90 == 0: # Change 90 to the width of the image chosen above

> [!Important]
> The static folder must be stored in the same folder as the executable file as the spashscreen image isn't stored in the executable.

### Executable file icon
To add a custom file icon either:
- Save the icon in .\Static\ with the name icon.ico
- Adjust the compile command to point to your icon:
  
  pyinstaller.exe .\local.py --noconfirm --clean --log-level WARN --onefile --hidden-import babel.numbers --icon <\path\to\your\icon>.ico


> [!Note]
> To change the icon you must recompile the program.

## Compiling
### With custom icon
pyinstaller.exe .\local.py --noconfirm --clean --log-level WARN --onefile --hidden-import babel.numbers --icon .\Static\icon.ico

### Without custom icon
pyinstaller.exe .\local.py --noconfirm --clean --log-level WARN --onefile --hidden-import babel.numbers --icon "NONE"

## Working Directory structure
### Initial
- Static/loadingimage.jpg (Optional)
- \<Executable-File>.exe
- setup.json (Optional)
### Active (After first use)
- Static/loadingimage.jpg (Optional)
- printer/
- Temp/
- \<Executable-File>.exe
- setup.json
- storage.db
