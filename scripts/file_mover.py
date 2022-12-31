from gui_app import *

def main():
    prog = App()
    prog.mainloop()
    
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