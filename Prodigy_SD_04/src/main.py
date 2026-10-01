"""Application entry point for the Interactive Sudoku Solver.

Prodigy Infotech Software Engineering Internship - Task 04.
"""

import os
import sys

# Ensure project root is in sys.path when executing directly or from any directory
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from src.gui import SudokuApp


def main() -> None:
    """Initializes and runs the Sudoku Solver desktop application."""
    app = SudokuApp()
    app.run()


if __name__ == "__main__":
    main()
