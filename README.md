qatdrop is a tetrio bot that uses cv2 to view your screen and pyautogui to input keystrokes. it currently attempts to build tetrises and downstacks when above line 13.

instructions:
1. open tetrio, and set graphics to minimal
2. set the following controls: (left arrow = left, right arrow = right, down arrow = ccw spin, up arrow = cw spin, capslock = 180 spin, space = hard drop)
3. clone the repo
4. run calibrate.py, and adjust the coordinates until the 20x10 grid is captured in the main game box, and the next queue is capture in the queue box
5. run vision.py, and confirm that your boxes are working properly
6. run qatdrop.py
7. run run.py and quickly switch to your game window

contact me at @erlinghaalandcat on discord for any inquiries

coming soon:
1. easier instructions
2. better placement algo
3. learning tspins
4. customizable speed, algos, etc.
