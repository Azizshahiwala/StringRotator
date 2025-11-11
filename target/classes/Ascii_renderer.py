#this file is for rendering ascii characters
from PIL import Image, ImageFilter
import time
import os
import math
import shutil
import Runner

'''
@ % # * + = - : .
'''
Speed = 1
CommandDict = {"halt" : False, "Speed": Speed, "Save" : False}

ascii_chars = "@%#*+=-:."

# Projection distance for 3D illusion
PROJECTION_DISTANCE = 4
# Lighting setup
lightx, lighty, lightz = -1, -1, PROJECTION_DISTANCE + 10  # Light coming from viewer direction

#Config
CommandStr = []
halt = []
speedList = []
PNGpath = ""
usingPNG = False
SaveSetting= []
def animate_ascii(ascii_lines = ""):
    global SCREEN_WIDTH, SCREEN_HEIGHT
    
    # Terminal size
    columns, rows = shutil.get_terminal_size()
    SCREEN_WIDTH = columns
    SCREEN_HEIGHT = rows

    angleX = 0
    angleY = 0
    while True:
        ReadWriteConfigFile()

        columns, rows = shutil.get_terminal_size()
        SCREEN_WIDTH = columns
        SCREEN_HEIGHT = rows
        max_width = int(SCREEN_WIDTH * 0.95)

        if usingPNG:
            ascii_lines = PNG_to_ascii(PNGpath, width=max_width)
        else:
            edge_img = findEdges("Ascii_image.png")
            ascii_lines = Edge_to_ascii(edge_img)

        while CommandDict["halt"]:
            ReadWriteConfigFile()

        #this method sends commands to command line
        os.system('cls' if os.name == 'nt' else 'clear')

        # Create empty screen buffer
        screen = []
        for row in range(SCREEN_HEIGHT):
            screen_row = []
            for col in range(SCREEN_WIDTH):
                screen_row.append(' ')  # fill with space
            screen.append(screen_row)

        # Create Z-buffer (for depth / z comparison) where closer char can over-ride farther ones

        zbuffer = []
        for row in range(SCREEN_HEIGHT):
            zbuffer_row = []
            for col in range(SCREEN_WIDTH):
                zbuffer_row.append(-float('inf'))  # initialize with very far distance
            zbuffer.append(zbuffer_row)
    
        # sin/cos precompute
        #cos_x = math.cos(angleX)
        #sin_x = math.sin(angleX)

        cos_x = 1
        sin_x = 0
        cos_y = math.cos(angleY)
        sin_y = math.sin(angleY)

        #for fake rotation (rotation, depth and perception)
        for x,y,lines in ascii_lines:
            z = 0  # flat image on Z=0 plane

            # Rotate around X axis (tilt up/down)
            y_rot = y * cos_x - z * sin_x
            z_rot = y * sin_x + z * cos_x
            x_rot = x

            #i want to keep it fixed on one place. hence, 
            #y_rot = y
            #z_rot = y
            #x_rot = x

            # Rotate around Y axis (left/right)
            x_final = x_rot * cos_y - z_rot * sin_y
            z_final = x_rot * sin_y + z_rot * cos_y + 5
            y_final = y_rot

            #if z_final becomes 0, convert it to 0.001
            if z_final <= 0:
                z_final = 0.001

            #at last, 3d -> 2d
            # we multiply x_final & y_final with 0.5 because terminal characters are taller than wide... It compresses chars.
            X_offset = 0
            Y_offset = 0

            scale = min(PROJECTION_DISTANCE / z_final , SCREEN_WIDTH * 0.5)
            screen_x = round(x_final + scale + SCREEN_WIDTH // 2 + X_offset)
            screen_y = round(y_final + scale + SCREEN_HEIGHT // 2 + Y_offset)

            #Normalise x, y and z | This means, if any coordinate faces us, it will add lighting effect. so normalize() will update 
            #surface facing.

            normalize_x , normalize_y, normalize_z = normalize(0,0,1) #light coming from screen. -1 is for viewer
            vector_x, vector_y, vector_z = normalize(lightx - x_final, lighty - y_final, lightz - z_final)
            New_brightness = normalize_x * vector_x + normalize_y * vector_y + normalize_z * vector_z
            New_brightness = max(0,New_brightness) #find from [0 to 1]

            light_index = int(New_brightness * (len(ascii_chars) - 1))
            lit_char = ascii_chars[light_index]

            # If inside screen boundaries
            if 0 <= screen_x < SCREEN_WIDTH and 0 <= screen_y < SCREEN_HEIGHT:
                #print(f"Placing '{lines}' at ({screen_x}, {screen_y}), depth={z_final}")
                if z_final > zbuffer[screen_y][screen_x]:
                    zbuffer[screen_y][screen_x] = z_final

                    if usePNG:
                        screen[screen_y][screen_x] = lines
                    else:
                        screen[screen_y][screen_x] = lit_char

            
        # Print frame
        for row in screen:
            print("".join(row))
    
         # Increment rotation
        #angleX += 0.03

        '''
        When the screen reaches near to flat screen (0 to 2.Pi). That means text
        is most readable and pause for 1 sec.
        '''

        if (angleY % (2 * math.pi) <= 0.04 and angleY % (2 * math.pi) > 0.03):
            angleY += 0.02
            time.sleep(2)
        else:
            time.sleep(0.001 / CommandDict["Speed"]) 

        angleY += 0.02*CommandDict["Speed"]

def usePNG(tempPNGpath):
    global PNGpath, usingPNG
    PNGpath = tempPNGpath
    usingPNG = True

def ReadWriteConfigFile():
    global CommandStr, halt, speedList, SaveSetting

    try:
        with open(".config.txt","r") as config:
            CommandStr = config.readlines()
            halt = CommandStr[0].split()
            speedList = CommandStr[1].split()
            SaveSetting = CommandStr[2].split()

        with open(".config.txt","w") as config:
            config.seek(0)
            config.writelines(CommandStr)    
            config.truncate()

        CommandDict["halt"] = halt[-1].strip().lower() == "true"
        CommandDict["Speed"] = float(speedList[-1])
        CommandDict["Save"] = SaveSetting[-1].strip().lower() == "true"

        if CommandDict["Save"]:
            Runner.SaveGIF()
            CommandDict["Save"] = False
            SaveSetting[-1] = "false"
    except IndexError:
        CommandDict["halt"] = False
        CommandDict["Speed"] = 1.0
        CommandDict["Save"] = False
        animate_ascii()


def findEdges(img_path):
    image = Image.open(img_path).convert('L') #grayscale
    edges = image.filter(ImageFilter.FIND_EDGES)

    #if the edge character is from 0 - 20, its darker shade
    #Else, its brighter
    """
    if p > 20:
        return 255
    else:
        return 0
    """
    edges = edges.point(lambda p: 255 if p > 20 else 0)
    return edges

#this method will use edges as parameter since we want to convert it to ascii also.
def Edge_to_ascii(edges):
    Width , Height = edges.size
    pixels = []

    for y in range(Height):
        for x in range(Width):
            if edges.getpixel((x, y)) == 255:
                # (x, y) is an edge pixel → center coordinates
                brightness = edges.getpixel((x, y))
                char_index = brightness * len(ascii_chars) // 256
                char = ascii_chars[char_index]
                pixels.append((x - Width // 2, y - Height // 2, char))  # replace '@' with dynamic char if needed
    return pixels

def normalize(x, y, z):
    length = math.sqrt(x * x + y * y + z * z)
    return (x / length, y / length, z / length) if length != 0 else (0, 0, 0)

def PNG_to_ascii(img_path, width=None) -> list[tuple[int, int, str]]:
    if width is None:
        columns, _ = shutil.get_terminal_size()
        width = columns // 2  # For better fit

    img = Image.open(img_path).convert("L")
    aspect_ratio = img.height / img.width
    new_height = int(width * aspect_ratio * 0.5)
    img = img.resize((width, new_height))

    pixels = []
    for y in range(img.height):
        for x in range(img.width):
            brightness = img.getpixel((x, y))
            char_index = brightness * len(ascii_chars) // 256
            char = ascii_chars[char_index]
            pixels.append((x - img.width // 2, y - img.height // 2, char))
    return pixels

def main():
    global usingPNG, PNGpath
    animate_ascii()
    usingPNG = False
    
if __name__ == "__main__":
    main()
    