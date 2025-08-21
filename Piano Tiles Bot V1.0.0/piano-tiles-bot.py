import numpy as np
import cv2
import time
import ctypes
import keyboard
import win32gui
from mss import mss

CLICK_DELAY = 0.0001
BLACK_THRESHOLD = 15
MIN_TILE_AREA = 90
WINDOW_TITLE = "SM-X200" # Put your scrcpy windows name here for auto detection
SAFE_MARGIN_TOP = 335  

class PrecisionClicker:
    def __init__(self):
        self.user32 = ctypes.windll.user32
    
    def safe_click(self, x, y):
        if y < SAFE_MARGIN_TOP:
            return False
            
        self.user32.SetCursorPos(x, y)
        time.sleep(0.005)
        self.user32.mouse_event(0x0002, 0, 0, 0, 0)
        time.sleep(0.005)
        self.user32.mouse_event(0x0004, 0, 0, 0, 0)
        return True

def get_adjusted_window_rect():
    try:
        hwnd = win32gui.FindWindow(None, WINDOW_TITLE)
        if hwnd:
            rect = list(win32gui.GetWindowRect(hwnd))
            
            rect[0] += 8    
            rect[1] += 31   
            rect[2] -= 8    
            rect[3] -= 8    
            
            rect[1] += SAFE_MARGIN_TOP
            rect[3] -= 5    
            
            return rect
    except Exception as e:
        print(f"Error {e}")
    return None

def main():
    print("=== Piano Tiles Bot V1.0.0 - By Hypervisor (d3buug on discord) ===")
    print(f"Target Windows Locked: {WINDOW_TITLE}")
    
    window_rect = get_adjusted_window_rect()
    if not window_rect:
        print("ERROR: Cannot found windows, make sur you entered the right windows name in the code")
        return
    
    region = {
        'left': window_rect[0],
        'top': window_rect[1],
        'width': window_rect[2] - window_rect[0],
        'height': window_rect[3] - window_rect[1]
    }
    
    print(f"Game Zone: {region}")
    
    clicker = PrecisionClicker()
    sct = mss()
    active = False
    
    while True:
        if keyboard.is_pressed('F3'):
            active = not active
            print(f"{'ACTIVE' if active else 'INACTIVE'}")
            time.sleep(0.5)
        
        if keyboard.is_pressed('esc'):
            print("Stopped")
            break
            
        if not active:
            time.sleep(0.08)
            continue
            
        try:
            img = np.array(sct.grab(region))
            
            gray = cv2.cvtColor(img, cv2.COLOR_BGRA2GRAY)
            _, mask = cv2.threshold(gray, BLACK_THRESHOLD, 255, cv2.THRESH_BINARY_INV)
            
            kernel = np.ones((3,3), np.uint8)
            cleaned = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)
            
            contours, _ = cv2.findContours(cleaned, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            
            for cnt in contours:
                if cv2.contourArea(cnt) < MIN_TILE_AREA:
                    continue
                    
                x, y, w, h = cv2.boundingRect(cnt)
                center_x = x + w//2 + region['left']
                center_y = y + h//2 + region['top']
                
                if clicker.safe_click(center_x, center_y):
                    time.sleep(CLICK_DELAY)
                    
        except Exception as e:
            print(f"Error: {e}")
            time.sleep(1)

if __name__ == "__main__":
    main()