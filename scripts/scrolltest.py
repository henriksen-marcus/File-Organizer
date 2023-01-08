import tkinter as tk
import customtkinter

customtkinter.set_appearance_mode("system")
customtkinter.set_default_color_theme("blue")

class App(customtkinter.CTk):
    def __init__(self):
        super().__init__()

        self.minsize(self.winfo_screenwidth() // 7, self.winfo_screenheight() // 2.35)
        self.geometry(f"{self.winfo_screenwidth() // 7}x{self.winfo_screenheight() // 2.35}")

        # self.firstFrame = customtkinter.CTkFrame(self)
        # self.firstFrame.pack(padx=10, pady=10, expand=True, fill="x", anchor="n")
        # customtkinter.CTkLabel(self.firstFrame, text="First label").pack()

        # Create a canvas and a scrollbar
        self.canvas = customtkinter.CTkCanvas(self)
        scrollbar = customtkinter.CTkScrollbar(self, orientation="vertical", command=self.canvas.yview)

        # Set the scrollbar to the canvas
        self.canvas.configure(yscrollcommand=scrollbar.set)

        # Pack the scrollbar and canvas
        scrollbar.pack(side="right", fill="y")
        self.canvas.pack(side="left", fill="both", expand=True)

        # Add some content to the canvas
        frame = customtkinter.CTkFrame(self.canvas)
        self.canvas.create_window((0, 0), window=frame, anchor="nw")

        # Update the canvas size to fit the content, makes scrollbar fit to canvas size
        self.canvas.update_idletasks()
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        self.canvas.bind_all("<MouseWheel>", self.scroll) # Bind scrolling over the canvas to a function

        customtkinter.CTkLabel(frame, text="Canv1 Label").pack(padx=10, pady=10, anchor="n")
        customtkinter.CTkLabel(frame, text="Canv2 Label").pack(padx=10, pady=10)
        customtkinter.CTkLabel(frame, text="Canv3 Label").pack(padx=10, pady=10)
        customtkinter.CTkLabel(frame, text="Canv4 Label").pack(padx=10, pady=10)
        customtkinter.CTkLabel(frame, text="Canv5 Label").pack(padx=10, pady=10)
        customtkinter.CTkLabel(frame, text="Canv5 Label").pack(padx=10, pady=10)
        # customtkinter.CTkLabel(frame, text="Canv5 Label").pack(padx=10, pady=10)
        # customtkinter.CTkLabel(frame, text="Canv5 Label").pack(padx=10, pady=10)
        # customtkinter.CTkLabel(frame, text="Canv5 Label").pack(padx=10, pady=10)
        # customtkinter.CTkLabel(frame, text="Canv5 Label").pack(padx=10, pady=10)
        # customtkinter.CTkLabel(frame, text="Canv5 Label").pack(padx=10, pady=10)
        # customtkinter.CTkLabel(frame, text="Canv5 Label").pack(padx=10, pady=10)
        # customtkinter.CTkLabel(frame, text="Canv5 Label").pack(padx=10, pady=10)

        # We always need to do this after adding stuff to the canvas!
        self.canvas.update_idletasks()
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))


    def scroll(self, event):
        yview = self.canvas.yview() # Get the current scroll position
        if yview[0] == 0.0 and event.delta > 0: return # Return if we are trying to scroll up while already at the theoretical top
        print(f"Scroll position: ({yview[0]})")
        num = 1 if event.delta < 0 else -1 # Get -1 or 1 depending on which direction we are scrolling
        self.canvas.yview_scroll(1 * num, "units") # Manually scroll in the direction gotten above



def main():
    prog = App()
    prog.mainloop()
    
if __name__ == "__main__":
    main()