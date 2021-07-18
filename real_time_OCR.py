from google.cloud import vision
import io
import os
from enum import Enum
from PIL import Image
import cv2
import numpy as np
from google.cloud import translate_v2 as translate
import six
import win32gui, win32api, win32con, win32com.client, win32ui

# Set the Google credentials in order to use the API
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = r"C:\Users\Vamsi\Documents\!Real Time Text Translation\GoogleCredentials.json"

# Initiate the clients needed for the Google API
translate_client = translate.Client()
client = vision.ImageAnnotatorClient()


class FeatureType(Enum):
    PAGE = 1
    BLOCK = 2
    PARA = 3
    WORD = 4
    SYMBOL = 5


# Returns document bounds given an image.
def get_document_bounds(image_file, feature):

    # The list `bounds` contains the coordinates of the bounding boxes.
    bounds = []

    # Convert PIL Image to Bytes
    content = io.BytesIO()
    image_file.save(content, format='PNG')
    content = content.getvalue()

    image = vision.Image(content=content)

    response = client.document_text_detection(image=image)

    document = response.full_text_annotation

    texts = response.text_annotations

    # Add all the translated text to a list
    translated_text = []
    for text1 in texts:
        translated_text.append(translate_text('en', text1.description))

    # Collect specified feature bounds by enumerating all document features
    for page in document.pages:
        for block in page.blocks:
            for paragraph in block.paragraphs:
                for word in paragraph.words:
                    for symbol in word.symbols:
                        if (feature == FeatureType.SYMBOL):
                            bounds.append(symbol.bounding_box)

                    if (feature == FeatureType.WORD):
                        bounds.append(word.bounding_box)

                if (feature == FeatureType.PARA):
                    bounds.append(paragraph.bounding_box)

            if (feature == FeatureType.BLOCK):
                bounds.append(block.bounding_box)

    # Adds the top left coordinates of the text's bounding box to a list
    top_left = []
    for bound in bounds:
        top_left_value = bound.vertices[0].x, bound.vertices[0].y
        top_left.append(top_left_value)

    return image_file, top_left, translated_text


# Translates any text detected to english
def translate_text(target, text):

    if isinstance(text, six.binary_type):
        text = text.decode("utf-8")

    # Text can also be a sequence of strings, in which case this method will return a sequence of results for each text.
    result = translate_client.translate(text, target_language=target)

    translated_text = result["translatedText"]

    return translated_text


def background_screenshot_pil(hwnd, width, height):
    # Takes a screenshot of the selected window in bitmap and then converts it to a PIL Image

    wDC = win32gui.GetWindowDC(hwnd)
    # Returns the device context (DC) for the entire window, including title bar, menus, and scroll bars.
    dcObj=win32ui.CreateDCFromHandle(wDC)
    # Creates a DC object from an integer handle.
    cDC=dcObj.CreateCompatibleDC()
    # Creates a memory device context (DC) compatible with the specified device.

    dataBitMap = win32ui.CreateBitmap()
    # Creates a device-dependent bitmap
    dataBitMap.CreateCompatibleBitmap(dcObj, width, height)
    # Creates a bitmap compatible with the device

    cDC.SelectObject(dataBitMap)
    cDC.BitBlt((0,0),(width, height) , dcObj, (0,0), win32con.SRCCOPY)

    bmpinfo = dataBitMap.GetInfo()
    bmpstr = dataBitMap.GetBitmapBits(True)

    # Converting BitMap to a PIL Image
    im = Image.frombuffer(
        'RGB',
        (bmpinfo['bmWidth'], bmpinfo['bmHeight']),
        bmpstr, 'raw', 'BGRX', 0, 1)

    dcObj.DeleteDC()
    cDC.DeleteDC()
    win32gui.ReleaseDC(hwnd, wDC)
    # Releases the device context (DC), freeing it for use by other applications
    win32gui.DeleteObject(dataBitMap.GetHandle())
    # Deletes the bitmap handle freeing all system resources associated with the object.

    return im  # Return the PIL Image


# Shows all available window handles
def winEnumHandler(hwnd, ctx):
    if win32gui.IsWindowVisible(hwnd):
        print(hex(hwnd), win32gui.GetWindowText(hwnd))


# Set the dimensions for the monitor resolution
width = int(input('What is the width of your monitor: '))
height = int(input('What is the height of your monitor: '))

# Prints the available window handles
win32gui.EnumWindows(winEnumHandler, None)

# Set the window handle
window_name = str(input('Which window would you like to translate: '))

# Finds the window handle using the user input
active_hwnd = win32gui.FindWindow(None, window_name)

while True:

    # Take screenshots from the window handle
    pil_image = background_screenshot_pil(active_hwnd, 1920, 1080)

    # Save it to a NumPy array
    raw_img = np.array(pil_image)

    # Image colour to grayscale and binarised
    img = cv2.cvtColor(raw_img, cv2.COLOR_BGR2GRAY)
    (thresh, bw_img) = cv2.threshold(img, 128, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)

    # Convert Numpy array to PIL Image
    pil_img = Image.fromarray(bw_img)

    # Call the function
    image, top_left, translated_text = get_document_bounds(pil_img, FeatureType.WORD)

    # Make image compatible with cv2.imshow()
    image1 = np.array(image)

    # Create a blank image to put the translated text
    blank_image = np.zeros((height, width, 3), np.uint8)

    # Set the font variables
    font = cv2.FONT_HERSHEY_SIMPLEX
    font_size = 0.5
    thick = 1
    font_colour = (192, 192, 192)

    # Add an extra tuple for the total translated text which shows up in the top left corner
    top_left.insert(0, (0, 15))

    # Write translated text to OpenCV Image using the coordinates
    for index, (value1, value2) in enumerate(zip(translated_text, top_left)):
        cv2.putText(blank_image, str(value1), value2, font, font_size, font_colour, 1, cv2.LINE_AA)

    # Display the picture in fullscreen and no borders
    cv2.namedWindow('Screen Capture', flags=cv2.WINDOW_NORMAL)
    cv2.setWindowProperty('Screen Capture', cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)
    cv2.imshow('Screen Capture', blank_image)

    # Win32 API's set OpenCV to the top most window, transparent and unobtrusive
    hwnd = win32gui.FindWindow(None, 'Screen Capture')  # Get window handle
    win32gui.ShowWindow(hwnd, win32con.SW_RESTORE)
    win32gui.BringWindowToTop(hwnd)

    shell = win32com.client.Dispatch("WScript.Shell")
    shell.SendKeys('%')

    # Focus the keystrokes and mouse clicks to the window of the game
    win32gui.SetForegroundWindow(active_hwnd)

    win32gui.SetWindowPos(hwnd, win32con.HWND_NOTOPMOST, 0, 0, 0, 0, win32con.SWP_NOMOVE | win32con.SWP_NOSIZE)
    win32gui.SetWindowPos(hwnd, win32con.HWND_TOPMOST, 0, 0, 0, 0, win32con.SWP_NOMOVE | win32con.SWP_NOSIZE)
    win32gui.SetWindowPos(hwnd, win32con.HWND_NOTOPMOST, 0, 0, 0, 0, win32con.SWP_SHOWWINDOW | win32con.SWP_NOMOVE | win32con.SWP_NOSIZE)

    lExStyle = win32gui.GetWindowLong(hwnd, win32con.GWL_EXSTYLE)
    lExStyle |= win32con.WS_EX_TRANSPARENT | win32con.WS_EX_LAYERED
    win32gui.SetWindowLong(hwnd, win32con.GWL_EXSTYLE, lExStyle)
    win32gui.SetLayeredWindowAttributes(hwnd, win32api.RGB(0, 0, 0), 130, win32con.LWA_ALPHA)

    # Press "q" to quit OpenCV
    if cv2.waitKey(25) & 0xFF == ord("q"):
        cv2.destroyAllWindows()
        break
