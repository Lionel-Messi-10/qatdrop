import cv2
import numpy as np
from mss import mss
import os

# 1. FINAL CALIBRATED COORDINATES
BOARD_ROI = {'top': 250, 'left': 1040, 'width': 480, 'height': 940}
NEXT_ROI = {'top': 290, 'left': 1575, 'width': 200, 'height': 700}
HOLD_ROI = {'top': 310, 'left': 880, 'width': 80, 'height': 80}

# 2. UPDATED COLOR SIGNATURES (BGR)
COLOR_MAP = {
    'I': [131, 180, 50],   
    'J': [178, 51, 58],     
    'L': [40, 111 ,226],   
    'O': [75, 156, 176],   
    'S': [43, 229, 159],     
    'T': [167, 64, 157],   
    'Z': [59, 59, 172],     
}

def identify_piece_by_voting(image_crop):
    if image_crop.size == 0:
        return 'Empty'
    votes = {}
    for piece, target_bgr in COLOR_MAP.items():
        lower = np.array([max(0, c - 35) for c in target_bgr])
        upper = np.array([min(255, c + 35) for c in target_bgr])
        mask = cv2.inRange(image_crop, lower, upper)
        votes[piece] = cv2.countNonZero(mask)
    winner = max(votes, key=votes.get)
    if votes[winner] < 40:
        return 'Empty'
    return winner

def filter_floating_noise(raw_board):
    """
    Uses a Flood Fill algorithm to keep only the blocks 
    connected to the bottom of the board.
    """
    rows, cols = 20, 10
    cleaned_board = np.zeros_like(raw_board)
    visited = np.zeros((rows, cols), dtype=bool)
    
    # We start our search from every block on the bottom row (row 19)
    stack = []
    for c in range(cols):
        if raw_board[rows-1, c] == 1:
            stack.append((rows-1, c))
            visited[rows-1, c] = True

    # Standard Depth-First Search (DFS)
    while stack:
        r, c = stack.pop()
        cleaned_board[r, c] = 1

        # Check 4-way neighbors (Up, Down, Left, Right)
        for dr, dc in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
            nr, nc = r + dr, c + dc
            if 0 <= nr < rows and 0 <= nc < cols:
                if raw_board[nr, nc] == 1 and not visited[nr, nc]:
                    visited[nr, nc] = True
                    stack.append((nr, nc))
                    
    return cleaned_board


def get_board_state(sct):
    raw = sct.grab(BOARD_ROI)
    img = cv2.cvtColor(np.array(raw), cv2.COLOR_BGRA2BGR)
    board = np.zeros((20, 10), dtype=int)
    h, w = img.shape[:2]
    for r in range(20):
        for c in range(10):
            py, px = int((r + 0.5) * (h / 20)), int((c + 0.5) * (w / 10))
            sample = img[py-2:py+3, px-2:px+3]
            if np.mean(sample) > 50: 
                board[r, c] = 1
    clean_board = filter_floating_noise(board)
    return clean_board

def get_next_queue(sct):
    raw = sct.grab(NEXT_ROI)
    img = cv2.cvtColor(np.array(raw), cv2.COLOR_BGRA2BGR)
    h, w = img.shape[:2]
    queue = []
    slice_h = h / 5
    for i in range(5):
        y_start, y_end = int(i * slice_h), int((i + 1) * slice_h)
        crop = img[y_start:y_end, :]
        queue.append(identify_piece_by_voting(crop))
    return queue

def get_hold_piece(sct):
    raw = sct.grab(HOLD_ROI)
    img = cv2.cvtColor(np.array(raw), cv2.COLOR_BGRA2BGR)
    return identify_piece_by_voting(img)

if __name__ == "__main__":
    with mss() as sct:
        os.system('cls' if os.name == 'nt' else 'clear')
        
        current_piece = "Empty"
        last_next_queue = ["Empty"] * 5
        
        while True:
            try:
                board = get_board_state(sct)
                next_q = get_next_queue(sct)
                hold = get_hold_piece(sct)
                
                # Logic: If the queue has shifted, the previous first piece is now 'Current'
                # We check if the first piece of the queue has changed to determine a spawn
                if next_q[0] != last_next_queue[0] and next_q[0] != "Empty":
                    # Only update if the queue didn't just become empty (e.g. game over/pause)
                    if last_next_queue[0] != "Empty":
                        current_piece = last_next_queue[0]
                    last_next_queue = next_q.copy()

                display = []
                for row in board:
                    display.append(" ".join(['#' if val else '.' for val in row]))
                
                display.append(f"\nCurrent: {current_piece.ljust(10)}")
                display.append(f"Hold:    {hold.ljust(10)}")
                display.append(f"Next:    {' -> '.join(next_q).ljust(70)}")
                
                print("\033[H" + "\n".join(display), flush=True)
                
            except Exception:
                pass
                
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
