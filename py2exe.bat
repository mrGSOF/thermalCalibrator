rem Using pyinstaller (not py2exe)
rem D/L with: pip install pyinstaller
rem pyinstaller --onedir --onefile --noconfirm 3719_GUI.py
rem pyinstaller --onedir --noconfirm --icon=youricon.ico 3719_GUI.py
rem pyinstaller --onedir --onefile --noconsole --windowed --icon=Appicon.ico 3719_GUI.py
pyinstaller --onedir --onefile --icon=./Icons/Appicon.ico ThermalCalibrator_Station.py
