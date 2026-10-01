# 🧩 Sudoku Solver

> **Prodigy InfoTech — Software Development Internship | Task 04**

A desktop Sudoku Solver built with **Python and Tkinter** that solves 9×9 Sudoku puzzles using a **recursive backtracking algorithm**.

## 🚀 Features

- Interactive 9×9 Sudoku grid
- Enter custom Sudoku puzzles
- Easy, Medium, Hard, and Unsolvable presets
- Recursive backtracking solver
- Row, column, and 3×3 box validation
- Highlights invalid/conflicting cells
- Tracks solving time, backtracking steps, and recursion depth
- Clear Solution, Reset, and Clear Board options
- Keyboard-friendly grid navigation
- Automated unit tests
- Uses only Python standard libraries

## 🛠️ Tech Stack

- **Language:** Python 3.10+
- **GUI:** Tkinter / ttk
- **Algorithm:** Recursive Backtracking
- **Testing:** Python `unittest`

## 📁 Project Structure

```text
sudoku-solver/
├── src/
│   ├── __init__.py
│   ├── solver.py
│   ├── gui.py
│   └── main.py
├── tests/
│   ├── __init__.py
│   └── test_solver.py
├── screenshots/
├── .gitignore
├── LICENSE
└── README.md
```

## ⚙️ Setup & Run

### 1. Clone the repository

```bash
git clone <your-repository-url>
cd sudoku-solver
```

### 2. Check Python and Tkinter

```bash
python --version
python -c "import tkinter; print('Tkinter is ready')"
```

Python **3.10 or higher** is recommended.

### 3. Run the application

```bash
python src/main.py
```

## 🎮 How to Use

1. Load an **Easy, Medium, Hard, or Unsolvable** puzzle, or enter your own puzzle.
2. Enter digits from **1–9** in the grid.
3. Use arrow keys to navigate between cells.
4. Click **Check Puzzle** to validate the board.
5. Click **Solve Sudoku** to solve the puzzle using recursive backtracking.
6. Use **Clear Solution**, **Reset**, or **Clear Board** when needed.

## 🧠 Algorithm

The application uses **recursive backtracking**:

1. Find an empty cell.
2. Try digits from 1–9.
3. Check whether the digit is valid in its row, column, and 3×3 box.
4. Place the valid digit and recursively solve the remaining cells.
5. If no valid digit works, backtrack and try another value.
6. Continue until the puzzle is solved or determined to be unsolvable.

## 🧪 Run Tests

Run the automated test suite using:

```bash
python -m unittest discover -s tests -v
```

The tests cover:

- Empty-cell detection
- Row, column, and 3×3 box validation
- Valid puzzle solving
- Invalid puzzle detection
- Unsolvable puzzle handling
- Solution correctness

## 👤 Author

**Sonakshi Bargali**

**Prodigy InfoTech — Software Development Internship**  
**Task 04: Sudoku Solver**


