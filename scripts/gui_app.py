import tkinter as tk
from tkinter import PhotoImage
import customtkinter
from PIL import Image
import glob
import os
import shutil
from pathvalidate import sanitize_filepath
import time
import get_display_size as gds
from globals import *

# Current file path
path = os.path.dirname(os.path.abspath(__file__))

customtkinter.set_appearance_mode("system")
customtkinter.set_default_color_theme("blue")

class App(customtkinter.CTk):
    def __init__(self):
        super().__init__()

        # The last valid folder selected by the user
        self.current_folder = ""
        # If we should cancel the copy/move operation
        self.shouldCancel = False
        # The amount of files found with the current options
        self.file_count = 0
        self.screen_size = gds.get_display_size()
        self.width = self.screen_size[0] // 5
        self.height = self.screen_size[1] // 1.5
        posx = self.screen_size[0] // 2 - self.width // 2
        posy = self.screen_size[1] // 2 - self.height // 2
        self.iconimg = os.path.abspath(os.path.join(os.path.dirname( __file__ ), 'images/icon3.ico'))
        self.folderimg = os.path.abspath(os.path.join(os.path.dirname( __file__ ), 'images/folder_img.png'))

        # Set icon. Why the hell does relative path not work??
        self.iconbitmap(self.iconimg)

        # Window title
        self.title("File Organizer")

        # Window size
        self.minsize(self.winfo_screenwidth() // 7, self.winfo_screenheight() // 2.35)
        self.geometry(f"{self.winfo_screenwidth() // 7}x{self.winfo_screenheight() // 2.35}")
        self.resizable(False, False)
        #print(self.winfo_width(), self.winfo_height())

        # Top level grid
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # Main frame spanning the entire window
        self.main = customtkinter.CTkFrame(self, corner_radius=0)
        self.main.pack(fill=tk.BOTH, expand=True)

        # Columns. Important to use weight to make the application dynamically scalable
        self.main.grid_columnconfigure(0, weight=1, minsize=10)
        self.main.grid_columnconfigure(1, weight=1, minsize=100)
        self.main.grid_columnconfigure(2, weight=1, minsize=10)

        self.main.grid_rowconfigure(0, minsize=15)


        ### Content ###

        # App info container
        self.appInfoContainer = customtkinter.CTkFrame(self.main)
        self.appInfoContainer.grid(row=1, column=1, ipadx=8, ipady=4, sticky="ew")

        # App title label
        customtkinter.CTkLabel(self.appInfoContainer, text="File Organizer", font=(None, 14, "bold")).pack(pady=5)

        # App information text label
        customtkinter.CTkLabel(self.appInfoContainer, text="A tool for organizing files, based on file extension type.").pack()



        # Folder select container
        self.folderSelectContainer = customtkinter.CTkFrame(self.main)
        self.folderSelectContainer.grid(row=2, column=1, pady=10, ipady=12, sticky="ew")

        # Instruction label
        customtkinter.CTkLabel(self.folderSelectContainer, text="Select folder:", font=(None, 14, "bold")).pack(pady=6)

        # Container for entry and button
        self.folderEntryContainer = customtkinter.CTkFrame(self.folderSelectContainer, fg_color=self.folderSelectContainer._fg_color)
        self.folderEntryContainer.pack()

        # Entry where used can paste a path, or entry will autofill according to file dialog popup
        self.folderSelect = customtkinter.CTkEntry(self.folderEntryContainer, width=250)
        self.folderSelect.pack(side=tk.LEFT)
        self.folderSelect.bind("<KeyRelease>", self.check_folder)

        # Button for opening folder select dialog
        btnimg = customtkinter.CTkImage(
            dark_image=Image.open(self.folderimg), 
            light_image=Image.open(self.folderimg),
            size=(17,17)
            )
        self.folderSelectButton = customtkinter.CTkButton(self.folderEntryContainer, image=btnimg, text="", command=self.choose_folder)
        self.folderSelectButton.configure(width=self.folderSelectButton.winfo_height())
        self.folderSelectButton.pack(side=tk.LEFT, padx=4)



        # Search method container
        self.titleFrame = customtkinter.CTkFrame(self.main)
        self.titleFrame.grid(row=3, column=1, ipady=12, sticky="ew")
        self.titleFrame.grid_columnconfigure(0, weight=1)

        # Select search method label
        self.extTypeTitle = customtkinter.CTkLabel(self.titleFrame, text="Select search method:", font=(None, 14, "bold"))
        self.extTypeTitle.grid(row=0, column=0, padx=10, pady=8)

        # Search tab view
        self.fileTypeTab = customtkinter.CTkTabview(self.titleFrame, height=145, command=self.update_folder_info)
        self.fileTypeTab.grid(row=1, column=0, padx=12, pady=0, sticky="ew")
        self.fileTypeTab.add("Simple")
        self.fileTypeTab.add("Custom")
        self.fileTypeTab.set("Simple")

        # Simple tab
        self.fileTypeLabel = customtkinter.CTkLabel(self.fileTypeTab.tab("Simple"), text="Choose a file type:")
        self.fileTypeLabel.pack(pady=6)
        self.fileTypeDropdown = customtkinter.CTkComboBox(self.fileTypeTab.tab("Simple"), values=basic_filetypes, command=self.update_folder_info)
        self.fileTypeDropdown.pack()
        self.fileTypeDropdown.bind("<ButtonRelease>", self.update_folder_info)

        # Container for amount of files found
        self.filesFoundContainer = customtkinter.CTkFrame(self.fileTypeTab.tab("Simple"), fg_color=self.fileTypeTab.tab("Simple")._fg_color)
        self.filesFoundContainer.pack(pady=16)

        # Label for showing the amount of files found
        self.filesFoundLabel = customtkinter.CTkLabel(self.filesFoundContainer, text="Files found:")
        self.filesFoundLabel.grid(row=0, column=0)

        # Label for displaying the number
        self.filesFoundNumber = customtkinter.CTkLabel(self.filesFoundContainer, text="0", fg_color="#424242", corner_radius=6)
        self.filesFoundNumber.grid(row=0, column=1, padx=8, ipadx=4)

        # Custom tab
        self.extTypeLabel = customtkinter.CTkLabel(self.fileTypeTab.tab("Custom"), text="Type the specific extensions you want:")
        self.extTypeLabel.pack(pady=6)
        self.extTypeInput = customtkinter.CTkEntry(self.fileTypeTab.tab("Custom"), placeholder_text="png, docx, exe..", )
        self.extTypeInput.pack()
        self.extTypeInput.bind("<KeyRelease>", self.update_folder_info) # Key *Release* is important! Else you don't get the newest character 



        # Container for amount of files found
        self.filesFoundContainer2 = customtkinter.CTkFrame(self.fileTypeTab.tab("Custom"), fg_color=self.fileTypeTab.tab("Custom")._fg_color)
        self.filesFoundContainer2.pack(pady=16)

        # Label for showing the amount of files found
        self.filesFoundLabel2 = customtkinter.CTkLabel(self.filesFoundContainer2, text="Files found:")
        self.filesFoundLabel2.grid(row=0, column=0)

        # Label for displaying the number
        self.filesFoundNumber2 = customtkinter.CTkLabel(self.filesFoundContainer2, text="0", fg_color="#424242", corner_radius=6)
        self.filesFoundNumber2.grid(row=0, column=1, padx=8, ipadx=4)



        # File operation mode container
        self.modeFrame = customtkinter.CTkFrame(self.main, fg_color=self.main._fg_color)
        self.modeFrame.grid(row=4, column=1, pady=15)
        self.modeFrame.grid_columnconfigure(1, minsize=20)

        # File operation mode label
        self.modeLabel = customtkinter.CTkLabel(self.modeFrame, text="File operation mode:")
        self.modeLabel.grid(row=0, column=0)
        
        # Dropdown for mode (copy/move)
        self.modeDropdown = customtkinter.CTkComboBox(self.modeFrame, values=["Copy", "Move"])
        self.modeDropdown.grid(row=0, column=3)



        # Container for folder name stuff
        self.folderNameContainer = customtkinter.CTkFrame(self.main)
        self.folderNameContainer.grid(row=5, column=1, sticky="ew", pady=10)

        # Label for displaying what the folder name will be
        self.folderNameLabel = customtkinter.CTkLabel(self.folderNameContainer, text="The files will appear in the folder: fs_images")
        self.folderNameLabel.pack(pady=4)


        # Buttons to start/stop algorithm
        self.runBtn = customtkinter.CTkButton(self.main, text="Run", command=self.run)
        self.runBtn.grid(row=6, column=1, pady=14)
        #self.runBtn.place(anchor="s", relx=0.5, rely=0.97)
        
        self.stopBtn = customtkinter.CTkButton(self.main, text="Stop", command=self.stop, fg_color="#c92222", hover_color="#911616")
        #self.stopBtn.grid(row=6, column=1, pady=14)


        # Container for progess
        self.progressContainer = customtkinter.CTkFrame(self.main)
        #self.progressContainer.grid(row=7, column=1, pady=8)

        # Progress bar title
        self.progressLabel = customtkinter.CTkLabel(self.progressContainer, text="Copying items..")
        self.progressLabel.pack(pady=2)

        # Progress bar
        self.progressbar = customtkinter.CTkProgressBar(self.progressContainer, mode="determinate", width=220)
        self.progressbar.pack()
        self.progressbar.set(0)

        #for thing in range(6,100):
        #    customtkinter.CTkButton(self.main, text=f"Button  {thing}").grid(row=thing,column=1,pady=10,padx=10)

        self.check_folder(None, False)

    def check_folder(self, event=None, updt_border=True):
        """Check if the folder the user entered is valid
        and make the entry bar red or green accordingly."""

        directory = self.folderSelect.get()
        if (os.path.exists(directory)):
            if updt_border: self.folderSelect.configure(border_color="green")
            self.current_folder = directory
            self.update_folder_info()
            self.runBtn.configure(state="normal")
        else:
            if updt_border: self.folderSelect.configure(border_color="red")
            self.runBtn.configure(state="disabled")

    def choose_folder(self):
        directory = tk.filedialog.askdirectory()
        self.folderSelect.delete(0, tk.END)
        self.folderSelect.insert(0, directory)
        self.folderSelect.xview_scroll(1000, tk.UNITS)
        self.folderSelect.focus()
        self.check_folder()

    def update_folder_info(self, event=None):
        "Update the label for showing what the folder name will be."

        if self.current_folder == "": return
        foldername = self.get_folder_name()
        if foldername != "":
            self.folderNameLabel.configure(text=f"The files will appear in the folder: {self.get_folder_name()}")

        self.filesFoundNumber.configure(text=str(self.get_num_files()))
        self.filesFoundNumber2.configure(text=str(self.get_num_files()))

    def get_ext_arr(self):
        "Get a string array of all the extensions the user has defined."

        # Get info from extension tab view
        if self.fileTypeTab.get() == "Simple":
            current_selected = self.fileTypeDropdown.get()
            for i in basic_filetypes_extensions:
                # Array structure is like this: ["images", ["png", "jpg",..]]
                if (i[0] == current_selected): return i[1]
            return []
        else:
            content = self.extTypeInput.get().lower()
            content = content.replace(" ", "")
            content = content.replace(".", "")
            ext_arr = content.split(",")
            #ext_arr = [s.strip() for s in ext_arr]
            #ext_arr = [s.strip(".") for s in ext_arr]
            for i in ext_arr:
                # Extensions can't contain these characters
                if " " in i or "." in i or i == "": ext_arr.remove(i)
            ext_arr = self.remove_duplicates(ext_arr)
            return ext_arr

    def get_folder_name(self):
        """Get the name of the folder that will contain the new files. 
        Based on the current extension selection."""

        retstr = "" # Return string
        # Get info from extension tab view
        if self.fileTypeTab.get() == "Simple":
            retstr =  folder_prefix + self.fileTypeDropdown.get()
        else:
            # Get the first three custom defined extensions
            # and make a name using those
            ext_arr = self.get_ext_arr()
            if len(ext_arr) == 0: return ""
            else:
                mystr = folder_prefix
                for i, _ in enumerate(ext_arr):
                    if i > 0:
                        mystr = mystr + "-" + ext_arr[i]
                    else:
                        mystr = mystr + ext_arr[i]
                    i = i + 1
                    if i == 3: 
                        if len(ext_arr) > i: mystr = mystr + ".."
                        break              
                retstr = sanitize_filepath(mystr)

        # If the folder exists we add "_x" to the end where "x" is
        # the numbered copy, like "New folder (1)". So we get "fo_png_1", "fo_png_2"..
        while os.path.isdir(os.path.join(self.current_folder, retstr)):
            num = 1
            if len(retstr) > 3:
                if retstr[len(retstr) - 2] == "_": # If we have already added to it
                    try:
                        num = int(retstr[len(retstr) - 1])
                    except ValueError:
                        return ""
                    num = num + 1
                    retstr = retstr[:-1]
                    retstr = retstr + str(num)
                else:
                    retstr = retstr + "_1"
            else:
                return ""
        return retstr

    def remove_duplicates(self, list):
        # List to store the unique strings
        unique_elems = []

        # Iterate through the input list
        for elem in list:
            # If the string is not already in the unique list, add it
            if elem not in unique_elems:
                unique_elems.append(elem)

        # Return the list of unique strings
        return unique_elems

    def make_folder(self, foldername):
        folderpath = os.path.join(self.current_folder, foldername)
        try:
            os.mkdir(folderpath)
            return True
        except OSError:
            print(f"ERROR: {foldername} already exists!")
            return False

    def reset_fields(self):
        "Cleans up for next operation."

        # Clear custom input field
        self.extTypeInput.delete(0, tk.END)
        # Hide progress bar
        self.progressContainer.grid_remove()
        # Reset progress bar
        self.progressbar.set(0)
        # Resize window
        self.minsize(self.winfo_screenwidth() // 7, self.winfo_screenheight() // 2.35)
        self.geometry(f"{self.winfo_screenwidth() // 7}x{self.winfo_screenheight() // 2.35}")
        # Hide stop button
        self.stopBtn.grid_forget()
        # Show run button
        self.runBtn.grid(row=6, column=1, pady=14)
        # Reset the expected folder name
        self.update_folder_info()

    def get_num_files(self):
        "Get and update the number of files found with the current options."

        ext_arr = self.get_ext_arr()
        self.file_count = 0
        # For each extension selected check how many files there are
        for extension in ext_arr:
            self.file_count = self.file_count + len(glob.glob(f"{self.current_folder}\*.{extension}"))
        return self.file_count

    def run(self):
        "Run the copy/move algorithm."

        if self.fileTypeTab.get() == "Custom" and self.extTypeInput.get().strip() == "":
            print("ERROR: No selection was made, aborting!")
            return

        # Disable run button
        self.runBtn.grid_forget()

        # Show stop button
        self.stopBtn.grid(row=6, column=1, pady=14)

        if (self.modeDropdown.get() == "Copy"):
            self.progressLabel.configure(text="Copying items: 0%")
        else:
            self.progressLabel.configure(text="Moving items: 0%")

        self.progressContainer.grid(row=7, column=1, ipadx=10, ipady=10, pady=10)

        # Expand window
        self.minsize(self.winfo_screenwidth() // 7, self.winfo_screenheight() // 2.08)
        self.geometry(f"{self.winfo_screenwidth() // 7}x{self.winfo_screenheight() // 2.08}")

        foldername = self.get_folder_name()

        if not self.make_folder(foldername):
            print("ERROR: Could not create folder, aborting!")
            return

        ext_arr = self.get_ext_arr()

        if len(ext_arr) == 0:
            print("ERROR: Extension array was empty!")
            return

        self.get_num_files()

        if self.file_count == 0:
            print("WARNING: Amount of files found was zero, aborting!")
            self.reset_fields()
            return
        
        # Used to calculate progress %
        remaining_files = self.file_count
        
        if self.modeDropdown.get() == "Copy":
            for extension in ext_arr:
                # Iterate through every file that has a matching extension
                for file in glob.glob(f"{self.current_folder}\*.{extension}"):
                    
                    if (self.shouldCancel):
                        print("Manual abort!")
                        self.reset_fields()
                        return

                    dst = os.path.join(self.current_folder, foldername)
                    print('Copying', os.path.basename(file))

                    try:
                        shutil.copy2(file, dst)
                    except Exception as e:
                        pass
                    
                    remaining_files = remaining_files - 1
                    progress_float = ((self.file_count - remaining_files) / self.file_count)
                    self.progressbar.set(progress_float)
                    self.progressLabel.configure(text=f"Copying files: {int(progress_float * 100)}%")
                    self.update() # Update UI, gets frozen once copying runs in a loop
        else:
            for extension in ext_arr:
                for file in glob.glob(f"{self.current_folder}\*.{extension}"):

                    if (self.shouldCancel):
                        print("Manual abort!")
                        self.reset_fields()
                        return

                    dst = os.path.join(self.current_folder, foldername)
                    print('Moving', os.path.basename(file))

                    try:
                        shutil.move(file, dst)
                    except Exception as e:
                        pass
                    
                    remaining_files = remaining_files - 1
                    progress_float = ((self.file_count - remaining_files) / self.file_count)
                    self.progressbar.set(progress_float)
                    self.progressLabel.configure(text=f"Moving files: {int(progress_float * 100)}%")
                    self.update()

        if (self.modeDropdown.get() == "Copy"):
            self.progressLabel.configure(text=f"Copying files: 100%")
        else:
            self.progressLabel.configure(text=f"Moving files: 100%")

        self.progressbar.set(1)
        self.update()
        time.sleep(0.5)
        self.reset_fields()

    def stop(self):
        "Stop the algorithm"
        self.shouldCancel = True