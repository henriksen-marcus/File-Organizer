# Code gotten from @VoteCoffee on stackoverflow.

import ctypes
import tkinter

try: # Windows 8.1 and later
    ctypes.windll.shcore.SetProcessDpiAwareness(2)
except Exception as e:
    pass
try: # Before Windows 8.1
    ctypes.windll.user32.SetProcessDPIAware()
except: # Windows 8 or before
    pass

def get_display_size():
    root = tkinter.Tk()
    root.update_idletasks()
    root.attributes('-fullscreen', True)
    root.state('iconic')
    height = root.winfo_screenheight()
    width = root.winfo_screenwidth()
    root.destroy()
    return width, height
