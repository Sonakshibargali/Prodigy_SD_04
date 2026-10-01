"""Core Sudoku Solver module implementing recursive backtracking.

This module provides a pure, self-contained Sudoku engine independent of any GUI.
It includes grid validation, constraint checking, an empty cell finder, and a genuine
depth-first recursive backtracking solver with performance statistics tracking.
"""

from dataclasses import dataclass
import random
import time
from typing import List, Optional, Tuple, Dict

Board = List[List[int]]


@dataclass
class SolverStats:
    """Holds execution metrics for the backtracking solver."""
    backtracks: int = 0
    recursion_calls: int = 0
    execution_time_ms: float = 0.0
    is_solvable: bool = False


def create_empty_board() -> Board:
    """Creates and returns a new 9x9 board filled with zeros."""
    return [[0 for _ in range(9)] for _ in range(9)]


def copy_board(board: Board) -> Board:
    """Creates a deep copy of a 9x9 Sudoku board."""
    return [row[:] for row in board]


def find_empty(board: Board) -> Optional[Tuple[int, int]]:
    """Finds the first empty cell (containing 0) in row-major order.

    Args:
        board: 9x9 2D list of integers.

    Returns:
        A tuple (row, col) of the empty cell, or None if all cells are filled.
    """
    for row in range(9):
        for col in range(9):
            if board[row][col] == 0:
                return row, col
    return None


def is_valid(board: Board, row: int, col: int, num: int) -> bool:
    """Checks whether placing `num` at `board[row][col]` satisfies Sudoku rules.

    A valid placement must not duplicate `num` within:
    1. The current row (excluding board[row][col]).
    2. The current column (excluding board[row][col]).
    3. The 3x3 subgrid box (excluding board[row][col]).

    Args:
        board: 9x9 2D list of integers.
        row: Target row index (0-8).
        col: Target column index (0-8).
        num: Digit to test (1-9).

    Returns:
        True if the placement satisfies all constraints, False otherwise.
    """
    # 1. Check current row
    for c in range(9):
        if c != col and board[row][c] == num:
            return False

    # 2. Check current column
    for r in range(9):
        if r != row and board[r][col] == num:
            return False

    # 3. Check 3x3 subgrid box
    box_row_start = (row // 3) * 3
    box_col_start = (col // 3) * 3
    for r in range(box_row_start, box_row_start + 3):
        for c in range(box_col_start, box_col_start + 3):
            if (r != row or c != col) and board[r][c] == num:
                return False

    return True


def find_mrv_empty(board: Board) -> Tuple[Optional[Tuple[int, int]], List[int]]:
    """Finds the empty cell with Minimum Remaining Values (MRV) candidate choices.

    Uses fail-fast pruning: if an unassigned cell has 0 valid candidates, returns immediately
    to trigger early pruning of invalid search branches.

    Args:
        board: 9x9 2D list of integers.

    Returns:
        Tuple of ((row, col) or None, list of valid candidate digits).
    """
    min_options = 10
    best_cell: Optional[Tuple[int, int]] = None
    best_options: List[int] = []

    for r in range(9):
        for c in range(9):
            if board[r][c] == 0:
                options = [num for num in range(1, 10) if is_valid(board, r, c, num)]
                num_options = len(options)
                if num_options == 0:
                    return (r, c), []  # Dead end reached immediately
                if num_options < min_options:
                    min_options = num_options
                    best_cell = (r, c)
                    best_options = options
                    if min_options == 1:
                        return best_cell, best_options

    return best_cell, best_options


def solve(board: Board, stats: Optional[SolverStats] = None) -> bool:
    """Solves the Sudoku puzzle in-place using recursive backtracking with MRV heuristic.

    Algorithm:
    1. Locate the unassigned cell with the Minimum Remaining Values (MRV candidate choices).
    2. If no empty cells remain, the puzzle is solved.
    3. If an empty cell has 0 candidate choices, trigger immediate fail-fast backtrack.
    4. Try candidate digits sequentially.
    5. Upon finding a valid digit, place it and recursively attempt to solve.
    6. If subsequent steps fail, undo choice (backtrack to 0) and try next digit.

    Args:
        board: 9x9 2D list of integers (modified in-place).
        stats: Optional SolverStats instance to accumulate backtrack and step counters.

    Returns:
        True if a valid solution was found, False if the puzzle is unsolvable.
    """
    cell, options = find_mrv_empty(board)
    if cell is None:
        # All cells filled legally -> Puzzle solved
        if stats:
            stats.is_solvable = True
        return True

    if not options:
        return False

    row, col = cell

    if stats:
        stats.recursion_calls += 1

    for num in options:
        board[row][col] = num

        if solve(board, stats):
            return True

        # Revert assignment (backtrack)
        board[row][col] = 0
        if stats:
            stats.backtracks += 1

    return False


def solve_with_stats(board: Board) -> Tuple[bool, Board, SolverStats]:
    """Solves a copy of the board and records performance metrics.

    Args:
        board: 9x9 2D list of integers (not modified).

    Returns:
        Tuple of (success, solved_board, stats).
    """
    working_board = copy_board(board)
    stats = SolverStats()

    start_time = time.perf_counter()
    success = solve(working_board, stats)
    end_time = time.perf_counter()

    stats.execution_time_ms = round((end_time - start_time) * 1000, 2)
    stats.is_solvable = success

    return success, working_board, stats


def validate_board(board: Board) -> Tuple[bool, str, Optional[Tuple[int, int]]]:
    """Validates an existing board for structural compliance and conflicts.

    Checks:
    1. Dimensions (must be 9x9).
    2. Value ranges (must be 0-9).
    3. Duplicate non-zero values in rows, columns, or 3x3 boxes.

    Returns:
        Tuple of (is_valid, message, conflict_coordinate).
        conflict_coordinate is (row, col) of the first offending cell, or None.
    """
    if len(board) != 9 or any(len(row) != 9 for row in board):
        return False, "Board must have 9 rows and 9 columns.", None

    for r in range(9):
        for c in range(9):
            val = board[r][c]
            if not isinstance(val, int) or val < 0 or val > 9:
                return False, f"Invalid value '{val}' at cell ({r + 1}, {c + 1}). Allowed: 0-9.", (r, c)
            if val != 0 and not is_valid(board, r, c, val):
                # Identify the specific conflict type for informative feedback
                # Check row
                row_conflict = [col_idx for col_idx in range(9) if col_idx != c and board[r][col_idx] == val]
                if row_conflict:
                    return False, f"Duplicate value {val} in Row {r + 1}.", (r, c)

                # Check column
                col_conflict = [row_idx for row_idx in range(9) if row_idx != r and board[row_idx][c] == val]
                if col_conflict:
                    return False, f"Duplicate value {val} in Column {c + 1}.", (r, c)

                # Check 3x3 block
                br, bc = (r // 3) * 3, (c // 3) * 3
                return False, f"Duplicate value {val} in 3x3 Block ({r // 3 + 1}, {c // 3 + 1}).", (r, c)

    return True, "Puzzle is valid.", None


def is_board_complete(board: Board) -> bool:
    """Verifies that the board has no empty cells and complies with all Sudoku rules."""
    if find_empty(board) is not None:
        return False

    valid, _, _ = validate_board(board)
    return valid


# =========================================================================
# Random Puzzle Generator
# =========================================================================

# Difficulty settings: number of clues to keep on the board
DIFFICULTY_CLUES = {
    "Easy": 42,
    "Medium": 34,
    "Hard": 27,
    "Expert": 22,
}


def _solve_random(board: Board) -> bool:
    """Solves using backtracking with randomized digit ordering for generation."""
    cell, options = find_mrv_empty(board)
    if cell is None:
        return True
    if not options:
        return False

    row, col = cell
    random.shuffle(options)

    for num in options:
        board[row][col] = num
        if _solve_random(board):
            return True
        board[row][col] = 0

    return False


def _count_solutions(board: Board, limit: int = 2) -> int:
    """Counts solutions up to `limit`. Used to verify uniqueness."""
    cell, options = find_mrv_empty(board)
    if cell is None:
        return 1
    if not options:
        return 0

    row, col = cell
    count = 0
    for num in options:
        board[row][col] = num
        count += _count_solutions(board, limit - count)
        board[row][col] = 0
        if count >= limit:
            break
    return count


def generate_full_solution() -> Board:
    """Generates a random fully-solved valid Sudoku board."""
    board = create_empty_board()
    _solve_random(board)
    return board


def generate_puzzle(difficulty: str = "Medium") -> Board:
    """Generates a random Sudoku puzzle with a unique solution.

    Args:
        difficulty: One of 'Easy', 'Medium', 'Hard', 'Expert'.

    Returns:
        A 9x9 board with the specified number of clue cells filled in.
    """
    target_clues = DIFFICULTY_CLUES.get(difficulty, 34)
    solution = generate_full_solution()
    puzzle = copy_board(solution)

    # Build list of all filled cell positions and shuffle
    positions = [(r, c) for r in range(9) for c in range(9)]
    random.shuffle(positions)

    cells_to_remove = 81 - target_clues
    removed = 0

    for r, c in positions:
        if removed >= cells_to_remove:
            break

        saved = puzzle[r][c]
        puzzle[r][c] = 0

        # Check that removing this cell doesn't create multiple solutions
        test = copy_board(puzzle)
        if _count_solutions(test, 2) == 1:
            removed += 1
        else:
            puzzle[r][c] = saved  # Restore — removal breaks uniqueness

    return puzzle



SAMPLE_PUZZLES: Dict[str, Dict[str, object]] = {
    "Easy": {
        "difficulty": "Easy",
        "description": "A beginner-friendly puzzle with many starting clues.",
        "grid": [
            [5, 3, 0, 0, 7, 0, 0, 0, 0],
            [6, 0, 0, 1, 9, 5, 0, 0, 0],
            [0, 9, 8, 0, 0, 0, 0, 6, 0],
            [8, 0, 0, 0, 6, 0, 0, 0, 3],
            [4, 0, 0, 8, 0, 3, 0, 0, 1],
            [7, 0, 0, 0, 2, 0, 0, 0, 6],
            [0, 6, 0, 0, 0, 0, 2, 8, 0],
            [0, 0, 0, 4, 1, 9, 0, 0, 5],
            [0, 0, 0, 0, 8, 0, 0, 7, 9],
        ]
    },
    "Medium": {
        "difficulty": "Medium",
        "description": "A balanced puzzle requiring multiple branching steps.",
        "grid": [
            [0, 0, 0, 2, 6, 0, 7, 0, 1],
            [6, 8, 0, 0, 7, 0, 0, 9, 0],
            [1, 9, 0, 0, 0, 4, 5, 0, 0],
            [8, 2, 0, 1, 0, 0, 0, 4, 0],
            [0, 0, 4, 6, 0, 2, 9, 0, 0],
            [0, 5, 0, 0, 0, 3, 0, 2, 8],
            [0, 0, 9, 3, 0, 0, 0, 7, 4],
            [0, 4, 0, 0, 5, 0, 0, 3, 6],
            [7, 0, 3, 0, 1, 8, 0, 0, 0],
        ]
    },
    "Hard": {
        "difficulty": "Hard",
        "description": "An advanced puzzle with minimal clues testing deep backtracking.",
        "grid": [
            [0, 0, 0, 6, 0, 0, 4, 0, 0],
            [7, 0, 0, 0, 0, 3, 6, 0, 0],
            [0, 0, 0, 0, 9, 1, 0, 8, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 5, 0, 1, 8, 0, 0, 0, 3],
            [0, 0, 0, 3, 0, 6, 0, 4, 5],
            [0, 4, 0, 2, 0, 0, 0, 6, 0],
            [9, 0, 3, 0, 0, 0, 0, 0, 0],
            [0, 2, 0, 0, 0, 0, 1, 0, 0],
        ]
    },
    "Expert": {
        "difficulty": "Expert",
        "description": "A minimal-clue expert puzzle demanding extensive backtracking.",
        "grid": [
            [0, 0, 0, 0, 0, 0, 0, 1, 0],
            [4, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 2, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 5, 0, 4, 0, 7],
            [0, 0, 8, 0, 0, 0, 3, 0, 0],
            [0, 0, 1, 0, 9, 0, 0, 0, 0],
            [3, 0, 0, 4, 0, 0, 2, 0, 0],
            [0, 5, 0, 1, 0, 0, 0, 0, 0],
            [0, 0, 0, 8, 0, 6, 0, 0, 0],
        ]
    }
}
