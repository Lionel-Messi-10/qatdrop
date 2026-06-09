import cv2
import numpy as np
from mss import mss

# 1. ADJUST THESE COORDINATES 
# Open your Tetris game and try to estimate these pixel values
# 'top' is Y, 'left' is X
BOARD_ROI = {'top': 250, 'left': 1040, 'width': 480, 'height': 940}
NEXT_ROI = {'top': 290, 'left': 1575, 'width': 200, 'height': 700}
HOLD_ROI = {'top': 310, 'left': 880, 'width': 80, 'height': 80}

def calibrate():
    with mss() as sct:
        while True:
            # Capture the whole screen or specific areas
            board_img = np.array(sct.grab(BOARD_ROI))
            next_img = np.array(sct.grab(NEXT_ROI))
            hold_img = np.array(sct.grab(HOLD_ROI))

            # Convert BGRA to BGR for OpenCV
            board_img = cv2.cvtColor(board_img, cv2.COLOR_BGRA2BGR)
            next_img = cv2.cvtColor(next_img, cv2.COLOR_BGRA2BGR)
            hold_img = cv2.cvtColor(hold_img, cv2.COLOR_BGRA2BGR)

            # Show the windows
            cv2.imshow('Board Scan Area', board_img)
            cv2.imshow('Next Queue Area', next_img)
            cv2.imshow('Hold Area', hold_img)

            print("Press 'q' in the window to stop calibration.")
            if cv2.waitKey(1) & 0xFF == ord('q'):
                cv2.destroyAllWindows()
                break

if __name__ == "__main__":
    calibrate()
