from win32gui import GetWindowText, GetForegroundWindow

activeWindowTitle = GetWindowText(GetForegroundWindow()) 

print(type(activeWindowTitle))