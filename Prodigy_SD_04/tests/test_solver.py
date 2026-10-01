"""Automated test suite for the Sudoku Backtracking Solver."""

import unittest
from src.solver import (
    find_empty,
    is_valid,
    solve,
    solve_with_stats,
    validate_board,
    is_board_complete,
    copy_board,
    create_empty_board,
    SAMPLE_PUZZLES,
    SolverStats,
)


class TestSudokuSolver(unittest.TestCase):
    """Test cases for the backtracking engine and Sudoku rule validators."""

    def setUp(self):
        self.easy_grid = copy_board(SAMPLE_PUZZLES["Easy"]["grid"])
        self.medium_grid = copy_board(SAMPLE_PUZZLES["Medium"]["grid"])
        self.hard_grid = copy_board(SAMPLE_PUZZLES["Hard"]["grid"])
        self.expert_grid = copy_board(SAMPLE_PUZZLES["Expert"]["grid"])

    def test_find_empty_cell(self):
        """Test finding empty cells in partially filled and completed boards."""
        # Easy grid has empty cells
        empty = find_empty(self.easy_grid)
        self.assertIsNotNone(empty)
        row, col = empty
        self.assertEqual(self.easy_grid[row][col], 0)

        # Full board has no empty cells
        full_board = [
            [5, 3, 4, 6, 7, 8, 9, 1, 2],
            [6, 7, 2, 1, 9, 5, 3, 4, 8],
            [1, 9, 8, 3, 4, 2, 5, 6, 7],
            [8, 5, 9, 7, 6, 1, 4, 2, 3],
            [4, 2, 6, 8, 5, 3, 7, 9, 1],
            [7, 1, 3, 9, 2, 4, 8, 5, 6],
            [9, 6, 1, 5, 3, 7, 2, 8, 4],
            [2, 8, 7, 4, 1, 9, 6, 3, 5],
            [3, 4, 5, 2, 8, 6, 1, 7, 9],
        ]
        self.assertIsNone(find_empty(full_board))

    def test_is_valid_rule_checks(self):
        """Verify row, column, and 3x3 box constraint checks."""
        # Row conflict
        # easy_grid[0] already has 5, 3, 7. Placing 5 at (0, 2) must be invalid.
        self.assertFalse(is_valid(self.easy_grid, 0, 2, 5))
        self.assertFalse(is_valid(self.easy_grid, 0, 2, 3))
        self.assertFalse(is_valid(self.easy_grid, 0, 2, 7))

        # Column conflict
        # Column 0 has 5, 6, 8, 4, 7. Placing 6 at (2, 0) must be invalid.
        self.assertFalse(is_valid(self.easy_grid, 2, 0, 6))

        # 3x3 Block conflict
        # Top-left box contains: 5, 3, 6, 9, 8. Placing 9 at (0, 2) must be invalid.
        self.assertFalse(is_valid(self.easy_grid, 0, 2, 9))

        # Valid candidate: 4 is not in row 0, col 2, or top-left box
        self.assertTrue(is_valid(self.easy_grid, 0, 2, 4))

    def test_solve_valid_puzzle(self):
        """Ensure the solver successfully solves known valid puzzles."""
        board = copy_board(self.easy_grid)
        stats = SolverStats()
        solved = solve(board, stats)

        self.assertTrue(solved)
        self.assertTrue(is_board_complete(board))
        self.assertIsNone(find_empty(board))
        self.assertGreater(stats.recursion_calls, 0)

    def test_solution_correctness_against_all_rules(self):
        """Verify every row, column, and 3x3 subgrid has unique numbers 1-9."""
        board = copy_board(self.easy_grid)
        solve(board)

        # Check each row has 1-9
        for r in range(9):
            self.assertEqual(sorted(board[r]), list(range(1, 10)))

        # Check each column has 1-9
        for c in range(9):
            col_vals = [board[r][c] for r in range(9)]
            self.assertEqual(sorted(col_vals), list(range(1, 10)))

        # Check each 3x3 box has 1-9
        for br in range(0, 9, 3):
            for bc in range(0, 9, 3):
                box_vals = [board[br + r][bc + c] for r in range(3) for c in range(3)]
                self.assertEqual(sorted(box_vals), list(range(1, 10)))

    def test_solve_with_stats(self):
        """Verify the solve_with_stats helper returns proper performance metrics."""
        success, solved_board, stats = solve_with_stats(self.medium_grid)

        self.assertTrue(success)
        self.assertTrue(stats.is_solvable)
        self.assertGreaterEqual(stats.execution_time_ms, 0.0)
        self.assertGreater(stats.recursion_calls, 0)
        self.assertTrue(is_board_complete(solved_board))

    def test_hard_puzzle_solves_successfully(self):
        """Test that deep backtracking handles difficult puzzles cleanly."""
        success, solved_board, stats = solve_with_stats(self.hard_grid)
        self.assertTrue(success)
        self.assertTrue(is_board_complete(solved_board))
        self.assertGreater(stats.backtracks, 0)

    def test_invalid_puzzle_detection(self):
        """Ensure validate_board flags duplicate values in rows, cols, and boxes."""
        # 1. Duplicate in row
        invalid_row = copy_board(self.easy_grid)
        invalid_row[0][2] = 5  # Row 0 already contains 5 at (0, 0)
        valid, msg, conflict = validate_board(invalid_row)
        self.assertFalse(valid)
        self.assertIn("Row 1", msg)

        # 2. Duplicate in column
        invalid_col = copy_board(self.easy_grid)
        invalid_col[2][0] = 6  # Column 0 already contains 6 at (1, 0)
        valid, msg, conflict = validate_board(invalid_col)
        self.assertFalse(valid)
        self.assertIn("Column 1", msg)

        # 3. Duplicate in 3x3 block
        invalid_box = copy_board(self.easy_grid)
        invalid_box[2][2] = 5  # Block (1,1) already contains 5 at (0, 0)
        valid, msg, conflict = validate_board(invalid_box)
        self.assertFalse(valid)
        self.assertIn("3x3 Block", msg)

    def test_expert_puzzle_solves_successfully(self):
        """Verify that the expert puzzle with minimal clues solves correctly."""
        is_struct_valid, msg, _ = validate_board(self.expert_grid)
        self.assertTrue(is_struct_valid, f"Expected structurally valid board, got: {msg}")

        success, solved_board, stats = solve_with_stats(self.expert_grid)
        self.assertTrue(success)
        self.assertTrue(stats.is_solvable)
        self.assertTrue(is_board_complete(solved_board))
        self.assertGreater(stats.backtracks, 0)

    def test_empty_board_creation(self):
        """Verify empty board initialization."""
        board = create_empty_board()
        self.assertEqual(len(board), 9)
        self.assertTrue(all(len(row) == 9 for row in board))
        self.assertTrue(all(val == 0 for row in board for val in row))
        valid, _, _ = validate_board(board)
        self.assertTrue(valid)


if __name__ == "__main__":
    unittest.main()
