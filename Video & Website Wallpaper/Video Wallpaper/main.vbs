Set WshShell = CreateObject("WScript.Shell")

' Run the Python script in a hidden command prompt
WshShell.Run "cmd /c start /min python C:\Users\97466\Documents\Lpv-main\Lpv-main\Lpv.py  C:\Users\97466\Documents\Lpv-main\Lpv-main\bk.mp4", 0, False
