import numpy as np
from numba import njit

# (Keep your PIECES dictionary at the top as it was)
PIECES = {
    'I': [np.array([[1, 1, 1, 1]]), np.array([[1],[1],[1],[1]])],
    'O': [np.array([[1, 1], [1, 1]])],
    'T': [np.array([[0, 1, 0], [1, 1, 1]]), np.array([[1, 0], [1, 1], [1, 0]]), np.array([[1, 1, 1], [0, 1, 0]]), np.array([[0, 1], [1, 1], [0, 1]])],
    'S': [np.array([[0, 1, 1], [1, 1, 0]]), np.array([[1, 0], [1, 1], [0, 1]])],
    'Z': [np.array([[1, 1, 0], [0, 1, 1]]), np.array([[0, 1], [1, 1], [1, 0]])],
    'J': [np.array([[1, 0, 0], [1, 1, 1]]), np.array([[1, 1], [1, 0], [1, 0]]), np.array([[1, 1, 1], [0, 0, 1]]), np.array([[0, 1], [0, 1], [1, 1]])],
    'L': [np.array([[0, 0, 1], [1, 1, 1]]), np.array([[1, 0], [1, 0], [1, 1]]), np.array([[1, 1, 1], [1, 0, 0]]), np.array([[1, 1], [0, 1], [0, 1]])]
}

@njit
def jit_is_valid(board, shape, r, c):
    sh, sw = shape.shape
    if r + sh > 20 or c + sw > 10 or r < 0 or c < 0:
        return False
    for i in range(sh):
        for j in range(sw):
            if shape[i, j] > 0 and board[r + i, c + j] > 0:
                return False
    return True

@njit
def jit_simulate(board, shape, column):
    landing_row = 0
    for r in range(21 - shape.shape[0]):
        if jit_is_valid(board, shape, r, column):
            landing_row = r
        else:
            break
            
    new_board = board.copy()
    sh, sw = shape.shape
    for i in range(sh):
        for j in range(sw):
            if shape[i, j] > 0:
                new_board[landing_row + i, column + j] = 1
                
    lines_cleared = 0
    final_board = np.zeros((20, 10), dtype=np.float32)
    current_row = 19
    
    for r in range(19, -1, -1):
        is_full = True
        for c in range(10):
            if new_board[r, c] == 0:
                is_full = False
                break
        if is_full:
            lines_cleared += 1
        else:
            for c in range(10):
                final_board[current_row, c] = new_board[r, c]
            current_row -= 1
            
    return final_board, lines_cleared

@njit
def jit_evaluate(board):
    """Fastmon V1.0: Aggressive Stacking Heuristics"""
    heights = np.zeros(10)
    holes = 0
    
    for c in range(10):
        h = 0
        block_found = False
        for r in range(20):
            if board[r, c] > 0:
                if not block_found:
                    h = 20 - r
                    block_found = True
            elif block_found:
                holes += 1
        heights[c] = h

    max_h = 0
    for h in heights:
        if h > max_h:
            max_h = h

    # 1. DANGER ZONE (Above 13)
    ceiling_penalty = 0.0
    if max_h > 13:
        ceiling_penalty = (max_h - 13) * 5000.0 

    # 2. THE WELL (Column 9) - Only enforced when low
    well_penalty = 0.0
    tetris_ready_rows = 0
    if max_h <= 13:
        well_penalty = heights[9] * 100.0 # Stricter well enforcement
        for r in range(20):
            row_sum = 0
            for c in range(9): row_sum += board[r, c]
            if row_sum == 9 and board[r, 9] == 0:
                tetris_ready_rows += 1

    # 3. I-DEPENDENCY (3-deep valleys)
    i_dep_penalty = 0.0
    for c in range(10):
        h_curr = heights[c]
        h_left = heights[c-1] if c > 0 else 20
        h_right = heights[c+1] if c < 9 else 20
        if (h_left - h_curr >= 3) and (h_right - h_curr >= 3):
            i_dep_penalty += 600.0 

    agg_height = np.sum(heights)
    bumpiness = 0
    for i in range(8):
        bumpiness += abs(heights[i] - heights[i+1])

    score = (
        (holes * -1500.0) +            # Holes are now even more expensive
        (well_penalty * -1.0) +
        (tetris_ready_rows * 200.0) +  # Higher reward for building the 9-0 stack
        (bumpiness * -15.0) +          # Extreme flatness requirement
        (agg_height * -2.0) +           
        (ceiling_penalty * -1.0) +
        (i_dep_penalty * -1.0)
    )
    return score

def get_best_move(board, current_piece, next_queue):
    if current_piece not in PIECES: current_piece = 'I'
    p2 = next_queue[0] if len(next_queue) > 0 and next_queue[0] in PIECES else 'I'
    p3 = next_queue[1] if len(next_queue) > 1 and next_queue[1] in PIECES else 'I'

    # Check current max height
    current_max_h = 0
    for c in range(10):
        filled = np.where(board[:, c] > 0)[0]
        h = 20 - filled[0] if len(filled) > 0 else 0
        if h > current_max_h: current_max_h = h

    best_final_score = -float('inf')
    best_overall_action = (0, 3)

    candidates = []
    for r1 in range(len(PIECES[current_piece])):
        shape1 = PIECES[current_piece][r1]
        for c1 in range(11 - shape1.shape[1]):
            b1, lines1 = jit_simulate(board, shape1, c1)
            
            # --- V1.0 AGGRESSIVE REWARD LOGIC ---
            reward1 = 0
            if lines1 == 4: 
                reward1 = 2000 # Double reward for Tetris
            elif lines1 > 0:
                if current_max_h < 10:
                    reward1 = -100 # MASSIVE penalty for singles/doubles when low
                elif current_max_h > 13:
                    reward1 = 500  # Survival mode
                else:
                    reward1 = -10  # Standard mid-game discipline
            
            score1 = jit_evaluate(b1) + reward1
            candidates.append((b1, (r1, c1), score1))

    candidates = sorted(candidates, key=lambda x: x[2], reverse=True)[:5]

    for b1, action1, score1 in candidates:
        for r2 in range(len(PIECES[p2])):
            shape2 = PIECES[p2][r2]
            for c2 in range(11 - shape2.shape[1]):
                b2, lines2 = jit_simulate(b1, shape2, c2)
                
                # Apply same logic to lookahead
                if lines2 == 4: r2_val = 2000
                elif lines2 > 0:
                    r2_val = -100 if current_max_h < 10 else (500 if current_max_h > 13 else -10)
                else: r2_val = 0
                
                for r3 in range(len(PIECES[p3])):
                    shape3 = PIECES[p3][r3]
                    for c3 in range(11 - shape3.shape[1]):
                        b3, lines3 = jit_simulate(b2, shape3, c3)
                        
                        if lines3 == 4: r3_val = 2000
                        elif lines3 > 0:
                            r3_val = -100 if current_max_h < 10 else (500 if current_max_h > 13 else -10)
                        else: r3_val = 0
                        
                        total_score = jit_evaluate(b3) + r2_val + r3_val + score1
                        
                        if total_score > best_final_score:
                            best_final_score = total_score
                            best_overall_action = action1

    return best_overall_action
