qatdrop is a tetrio bot that uses cv2 to view your screen and pyautogui to input keystrokes. it currently attempts to build tetrises and downstacks when above line 13.

**instructions:**
1. open tetrio, and set graphics to minimal
2. set the following controls: (left arrow = left, right arrow = right, down arrow = ccw spin, up arrow = cw spin, capslock = 180 spin, space = hard drop)
3. make sure you have cv2, njit, and pyautogui installed
4. clone the repo
5. run calibrate.py, and adjust the coordinates until the 20x10 grid is captured in the main game box, and the next queue is capture in the queue box
6. add the coordinates you found in calibrate.py, and enter them into vision.py. then, run vision.py, and confirm that your boxes are working properly
7. run qatdrop.py
8. run run.py and quickly switch to your game window

contact me at @erlinghaalandcat on discord for any inquiries

**coming soon:**
1. easier instructions
2. better placement algo
3. learning tspins
4. customizable speed, algos, etc.

**notes:**
1. this is essentially undetectable, as it scans the screen and inputs keystrokes, instead of any web-based cheat
2. use this at your own risk; if you don't modify the code, you will likely be fine, but if you increase the speed, anticheat might catch you
