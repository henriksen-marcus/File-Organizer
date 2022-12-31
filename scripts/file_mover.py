import glob
import os
import shutil
#import cv2
from pathvalidate import sanitize_filepath
import time
# UI
from tkinter import *
import tkinter.messagebox
import customtkinter

customtkinter.set_appearance_mode("system")
customtkinter.set_default_color_theme("blue")

# Used in the simple file types dropdown
basic_filetypes = ["images", "videos", "documents", "executables", "code"]

# Used to dertermine which file extensions the basic file types apply to
basic_filetypes_extensions = [
    ["images", ["bmp", "gif", "jpg", "jpeg", "png", "tif", "tiff"]],
    ["videos", ["3g2", "3gp", "avi", "flv", "h264", "m4v", "mkv", "mov", "mp4", "mpg", "mpeg", "rm", "swf", "vob", "wmv"]],
    ["documents", ["txt", "doc", "docx", "xls", "xlsx", "ppt", "pptx", "pdf"]],
    ["executables", ["exe", "com", "bat", "msi"]],
    ["code", ["py", "c", "cpp", "java", "html", "css", "js", "php", "cpp", "h", "hpp", "pyw", "json", "pch", "cs"]]
    ]

# Current file path
path = os.path.dirname(os.path.abspath(__file__))


# Code block gotten from @VoteCoffee on stackoverflow.
import ctypes
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
# End code block.


class App(customtkinter.CTk):
    def __init__(self):
        super().__init__()

        #self.after(100, self.tickfunc)

        self.title("File Cleanup")
        
        screen_size = get_display_size()
        width = screen_size[0] // 5
        height = screen_size[1] // 2.5
        posx = screen_size[0] // 2 - width // 2 - 50
        posy = screen_size[1] // 2 - height // 2 - 50

        self.minsize(400, 400)
        self.maxsize(screen_size[0]//5, screen_size[1]//3)
        self.geometry(f"{400}x{500}+{posx}+{posy}")
        #print(f"width:{screen_size[0]} height:{screen_size[1]}")


        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self.main = customtkinter.CTkFrame(self, corner_radius=0)
        self.main.grid(row=0, column=0, padx=0, pady=0, sticky="nsew")

        #self.main.grid_columnconfigure(tuple(range(2)), weight=1, minsize = 25)
        #self.main.grid_rowconfigure(tuple(range(5)), weight=1, minsize = 20)
        
        # Title padding
        #self.main.grid_rowconfigure((0, 3, 5, 7, 9), minsize=20)
        #self.main.grid_rowconfigure(tuple(range(10)), weight=1)
        # Main column
        self.main.grid_columnconfigure(0, weight=1, minsize=10)
        self.main.grid_columnconfigure(1, weight=1, minsize=400)
        self.main.grid_columnconfigure(2, weight=1, minsize=10)

        ### Content ###

        # Select search method label
        self.titleFrame = customtkinter.CTkFrame(self.main, width=200)
        self.titleFrame.grid(row=0, column=1, pady=10, sticky="ew")

        self.extTypeTitle = customtkinter.CTkLabel(self.titleFrame, text="Select search method:", font=(None, 14, "bold"))
        self.extTypeTitle.pack(padx=10, pady=10)


        # Simple/Custom tab
        self.fileTypeTab = customtkinter.CTkTabview(self.main, height=145, command=self.update_folder_info_manual)
        self.fileTypeTab.grid(row=1, column=1, sticky="ew")
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



        # Container for mode (copy/move)
        self.modeFrame = customtkinter.CTkFrame(self.main, fg_color=self.main._fg_color)
        self.modeFrame.grid(row=2, column=1, pady=15)
        self.modeFrame.grid_columnconfigure(1, minsize=20)

        self.modeLabel = customtkinter.CTkLabel(self.modeFrame, text="File operation mode:")
        self.modeLabel.grid(row=0, column=0)
        
        # Dropdown for mode (copy/move)
        self.modeDropdown = customtkinter.CTkComboBox(self.modeFrame, values=["Copy", "Move"])
        self.modeDropdown.grid(row=0, column=3)

        # Container for folder name stuff
        self.folderNameContainer = customtkinter.CTkFrame(self.main)
        self.folderNameContainer.grid(row=2, column=1, sticky="ew", pady=10)

        # Label for displaying what the folder name will be
        self.folderNameLabel = customtkinter.CTkLabel(self.folderNameContainer, text="The folder name will be: fs_images")
        self.folderNameLabel.pack(pady=4)

        # Button to start algorithm
        self.runBtn = customtkinter.CTkButton(self.main, text="Run", command=self.run)
        self.runBtn.grid(row=3, column=1, pady=14)


        # Container for progess
        self.progressContainer = customtkinter.CTkFrame(self.main)
        #self.progressContainer.grid(row=10, column=1)

        # Progress bar title
        self.progressLabel = customtkinter.CTkLabel(self.progressContainer, text="Copying items..")
        self.progressLabel.pack()


        # Progress bar
        self.progressbar = customtkinter.CTkProgressBar(self.progressContainer, mode="determinate", width=200)
        self.progressbar.pack()
        self.progressbar.set(0)

        self.update_folder_info_manual()

    def update_folder_info_manual(self):
        "Update the label for showing what the folder name will be."

        foldername = self.get_folder_name()
        if foldername != "":
            self.folderNameLabel.configure(text=f"The folder name will be: {self.get_folder_name()}")

        self.filesFoundNumber.configure(text=str(self.get_num_files()))
        self.filesFoundNumber2.configure(text=str(self.get_num_files()))

    def update_folder_info(self, event):
        self.update_folder_info_manual()

    def get_ext_arr(self):
        "Get a string array off all the extensions the user has defined."

        # Get info from extension tab view
        if self.fileTypeTab.get() == "Simple":
            current_selected = self.fileTypeDropdown.get()
            for i in basic_filetypes_extensions:
                # Array structure is like this: ["images", ["png", "jpg",..]]
                if (i[0] == current_selected): return i[1]
            return []
        else:
            #print(f"Original string: {self.extTypeInput.get()}")
            ext_arr = self.extTypeInput.get().split(",")
            #print(f"After split: {ext_arr}")
            ext_arr = [s.strip() for s in ext_arr]
            ext_arr = [s.strip(".") for s in ext_arr]
            #print(f"After strip: {ext_arr}")
            for i in ext_arr:
                if " " in i or "." in i or i == "": ext_arr.remove(i)
            #print(f"After remove: {ext_arr}")
            ext_arr = self.remove_duplicates(ext_arr)
            return ext_arr

    def get_folder_name(self):
        """Get the name of the folder that will contain the new files. 
        Based on the current extension selection."""

        retstr = "" # Return string
        # Get info from extension tab view
        if self.fileTypeTab.get() == "Simple":
            retstr =  "fc_" + self.fileTypeDropdown.get()
        else:
            # Get the first three custom defined extensions
            # and make a name using those
            ext_arr = self.get_ext_arr()
            if len(ext_arr) == 0: return ""
            #print(f"ext_arr: {ext_arr}")
            if len(ext_arr) == 0:
                return "fc_none"
            else:
                mystr = "fc_"
                for i, _ in enumerate(ext_arr):
                    if i > 0:
                        mystr = mystr + "-" + ext_arr[i]
                    else:
                        mystr = mystr + ext_arr[i]
                    #print(f"str = {str}, i = {i}")
                    i = i + 1
                    if i == 3: 
                        if len(ext_arr) > i: mystr = mystr + ".."
                        break              
                retstr = sanitize_filepath(mystr)

        # If the folder exists we add "_x" to the end where "x" is
        # the numbered copy, like "New folder (1)". So we get "fc_png_1", "fc_png_2"..
        while os.path.isdir(os.path.join(path, retstr)):
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
        # Create a new list to store the unique strings
        unique_elems = []

        # Iterate through the input list
        for elem in list:
            # If the string is not already in the unique list, add it
            if elem not in unique_elems:
                unique_elems.append(elem)

        # Return the list of unique strings
        return unique_elems
                
    def make_folder(self, foldername):
        folderpath = os.path.join(path, foldername)

        try:
            os.mkdir(folderpath)
            return True
        except OSError:
            print(foldername + " already exists!")
            return False

    def reset_fields(self):
        self.fileTypeDropdown.set(basic_filetypes[0])
        self.extTypeInput.delete(0, END)
        self.progressContainer.grid_remove()
        self.progressbar.set(0)
        self.runBtn.configure(state="normal")
        self.update_folder_info_manual()

    def get_num_files(self):
        ext_arr = self.get_ext_arr()
        file_count = 0
        for extension in ext_arr:
            file_count = file_count + len(glob.glob(f"{path}\*.{extension}"))
        return file_count

    def run(self):
        "Run the copy/move algorithm."

        if self.fileTypeTab.get() == "Custom" and self.extTypeInput.get().strip() == "":
            print("No selection was made, aborting.")
            return

        # Disable run button
        self.runBtn.configure(state="disabled")

        if (self.modeDropdown.get() == "Copy"):
            self.progressLabel.configure(text="Copying files: 0%")
        else:
            self.progressLabel.configure(text="Moving files: 0%")

        self.progressContainer.grid(row=6, column=1, ipadx=10, ipady=10, pady=10)

        foldername = self.get_folder_name()

        if not self.make_folder(foldername):
            return
        ext_arr = self.get_ext_arr()

        if len(ext_arr) == 0:
            print("ext_arr 0!")
            return

        print(ext_arr)
        original_file_count = 0
        for extension in ext_arr:
            original_file_count = original_file_count + len(glob.glob(f"{path}\*.{extension}"))

        if original_file_count == 0:
            print("Amount of files found was zero. Returning.")
            self.reset_fields()
            return
        
        remaining_files = original_file_count
        
        if self.modeDropdown.get() == "Copy":
            for extension in ext_arr:
                # Iterate through every file that has a matching extension
                for file in glob.glob(f"{path}\*.{extension}"):

                    dst = os.path.join(path, foldername)
                    progress_float = ((original_file_count - remaining_files) / original_file_count)

                    try:
                        print('Copying', os.path.basename(file))
                        shutil.copy2(file, dst)
                        remaining_files = remaining_files - 1

                        self.progressbar.set(progress_float)
                        self.progressLabel.configure(text=f"Copying files: {int(progress_float * 100)}%")
                        self.update()

                        print(f"Progress: {progress_float}")

                    except shutil.SameFileError:
                        remaining_files  = remaining_files  - 1
                        self.progressbar.set(progress_float)
                        self.update()
        else:
            for extension in ext_arr:
                # Iterate through every file that has a matching extension
                for file in glob.glob(f"{path}\*.{extension}"):

                    dst = os.path.join(path, foldername)
                    progress_float = ((original_file_count - remaining_files) / original_file_count)

                    try:
                        print('Moving', os.path.basename(file))
                        shutil.move(file, dst)
                        remaining_files  = remaining_files  - 1
                        self.progressbar.set(progress_float)
                        self.progressLabel.configure(text=f"Moving files: {int(progress_float * 100)}%")
                        self.update()

                    except shutil.SameFileError:
                        remaining_files  = remaining_files - 1
                        self.progressbar.set(progress_float)
                        self.update()

        self.progressbar.set(1)
        self.progressLabel.configure(text=f"Moving files: 100%")
        self.update()
        time.sleep(0.8)
        self.reset_fields()
        # Finished

    def tickfunc(self):
        print(f"{self.winfo_geometry()}")
        self.after(100, self.tickfunc)



def main():
    app = App()
    app.mainloop()
    
    
if __name__ == "__main__":
    main()


 # if ext == "webm":
                    #     video = cv2.VideoCapture(src)
                    #     frames = int(video.get(cv2.CAP_PROP_FRAME_COUNT))
                    #     fps = video.get(cv2.CAP_PROP_FPS)
                    #     length = frames / fps
                    #     # Skip move if the length is shorter than 30 sec
                    #     if length > 30:
                    #         print ("Video too long, skipping. Length: ", length)
                    #         continue
                    #     video.release()

                    # Recursive search
                    #Path(path).rglob("*." + extension):