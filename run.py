import time
import numpy as np
from mss import mss
from vision import get_board_state, get_next_queue
from qatdrop import get_best_move
import pyautogui
import random

PIECE_MAP = ['I', 'J', 'L', 'O', 'S', 'T', 'Z']
last_block_count = 0
last_next_q = []
current_piece = "I"

PIECES = {
    'I': [np.array([[1, 1, 1, 1]]), np.array([[1],[1],[1],[1]])],
    'O': [np.array([[1, 1], [1, 1]])],
    'T': [np.array([[0, 1, 0], [1, 1, 1]]), np.array([[1, 0], [1, 1], [1, 0]]), np.array([[1, 1, 1], [0, 1, 0]]), np.array([[0, 1], [1, 1], [0, 1]])],
    'S': [np.array([[0, 1, 1], [1, 1, 0]]), np.array([[1, 0], [1, 1], [0, 1]])],
    'Z': [np.array([[1, 1, 0], [0, 1, 1]]), np.array([[0, 1], [1, 1], [1, 0]])],
    'J': [np.array([[1, 0, 0], [1, 1, 1]]), np.array([[1, 1], [1, 0], [1, 0]]), np.array([[1, 1, 1], [0, 0, 1]]), np.array([[0, 1], [0, 1], [1, 1]])],
    'L': [np.array([[0, 0, 1], [1, 1, 1]]), np.array([[1, 0], [1, 0], [1, 1]]), np.array([[1, 1, 1], [1, 0, 0]]), np.array([[1, 1], [0, 1], [0, 1]])]
}

SPAWN_COL = {
    'I': 3, 'O': 4, 'T': 3, 'J': 3, 'L': 3, 'S': 3, 'Z': 3
}


FINESSE_DATA = {
    'I': [3, 5, 3, 4],
    'Z': [3, 4, 3, 3],
    'L': [3, 4, 3, 3],
    'J': [3, 4, 3, 3],
    'T': [3, 4, 3, 3],
    'O': [4, 4, 4, 4],
    'S': [3, 4, 3, 3]
}

def execute_move_finesse(rotation_idx, target_col, piece_type):
    """
    Executes movement with perfect finesse using Arkar's custom controls
    and verified rotation offsets.
    """
    pyautogui.PAUSE = 0.06+random.random()  /10
    if rotation_idx == 1:
        pyautogui.press('up')    
    elif rotation_idx == 2:
        pyautogui.press('capslock')     
    elif rotation_idx == 3:
        pyautogui.press('down')  

    if piece_type in FINESSE_DATA:
        current_left_col = FINESSE_DATA[piece_type][rotation_idx]
    else:
        current_left_col = 3 

    diff = target_col - current_left_col
    
    if diff < 0:
        for _ in range(abs(diff)):
            pyautogui.press('left')
    elif diff > 0:
        for _ in range(diff):
            pyautogui.press('right')

    pyautogui.press('space')

def run_monte():
    last_block_count = 0
    last_next_q = []
    
    with mss() as sct:
        print("Monte v0.4.5 (Finesse Mode) Active.")
        
        while True:
            board = get_board_state(sct)
            next_q = get_next_queue(sct)
            
            current_block_count = np.sum(board)
            
            if current_block_count != last_block_count or (next_q and next_q != last_next_q):
                
                time.sleep(0)
                board = get_board_state(sct)
                
                current_p = last_next_q[0] if last_next_q else "T"
                
                if current_p in ["Empty", "Unknown"]:
                    last_next_q = next_q.copy()
                    continue

                rot_idx, target_col = get_best_move(board, current_p, next_q)
                
                print(f"Finesse Move: {current_p} to Col {target_col} (Rot {rot_idx})")
                execute_move_finesse(rot_idx, target_col, current_p)
                
                last_block_count = np.sum(get_board_state(sct))
                last_next_q = next_q.copy()
                
            time.sleep(0)

if __name__ == "__main__":
    run_monte()
