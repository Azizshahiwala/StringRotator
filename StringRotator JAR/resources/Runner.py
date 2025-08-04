import sys
import PNG_creator as create
import Ascii_renderer as ascii
import pygetwindow as pw
import pyautogui as gui
import os
import time
temp_path = ""
file_name=0

'''
To run manually, 

Create a 'Temp.txt' (case sensitive) and write 9 letter word / text
Create a '.config.txt' Which has exact content as below:

halt = false
Speed = 1.0
Save = false

do not put "Save = true" It will force python script to run SaveGIF() and lag out your PC hahaha

1) run: python3 PNG_creator.py Temp.txt

PNG_creator generates Ascii_image.png 

2) run: python3 Ascii_renderer.py Ascii_image.png

This will start rendering of "Text" rotation. NOT "RGB photo" rotation.

If you want to use a rgb photo, pass it as a path.

Use:
python3 Runner.py <Text/rgb photo path> <Mode>
Where <Mode> :
1 -> runs text animation (only works if you have ascii_image.png)
2 -> runs PNG animation (No PNG_creator required.)

SaveGIF() is bugged. Which is why i will update in future versions.

This function will save your custom animation as GIF. 
''' 
def SaveGIF():
    
    file_name = 0
    Window = pw.getWindowsWithTitle(f"{temp_path}")
    if not Window:
        for i in range(14):
            print("Command prompt not found!")
        sys.exit(1)
    
    if Window:
        folder = r"GIF\ "
        folder = folder.strip()
        os.makedirs(folder, exist_ok=True)
        Coords = Window[0]
        try:
                Coords.activate()
                Coords.maximize()
        except Exception as e:
                print(f"Warning: {e} , Command Prompt not focused. Can cause issues in GIF")
                return
        
        for i in range(14):
            #i am just using file_name as a counter for naming. no need.
            file_name = 0
            file_name = i
            boundingbox = [Coords.left,Coords.top,Coords.width,Coords.height]
            screenshot = gui.screenshot(region=boundingbox)
            framePath = os.path.join(folder, f"frame_{file_name}.png")
            screenshot.save(framePath)

            if i == 13:
                break            

def main():
    if len(sys.argv) < 3:
        print("Usage: python Runner.py <TextFilePath> <mode>")
        sys.exit(1)

    temp_path = sys.argv[1].strip('"')  # strip quotes if passed through cmd
    mode = int(sys.argv[2])

    create.TempfilePath = temp_path

    #Edge cases for file opening and closing:
    if mode == 0:
        #This mode only uses TEXT!
        create.createimg()
    elif mode == 1:
        create.createimg()
        ascii.main()
    elif mode == 2:
        ascii.usePNG(temp_path)
        ascii.main()        

if __name__ == "__main__":
    main()
    