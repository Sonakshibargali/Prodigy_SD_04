"""Graphical User Interface for the Sudoku Solver desktop application.

Built using Python's standard Tkinter and ttk libraries with a premium
dark theme, smooth interactions, and visual feedback.
"""

import sys
import tkinter as tk
from tkinter import ttk
from typing import Dict, List, Optional, Set, Tuple

from src.solver import (
    DIFFICULTY_CLUES,
    SAMPLE_PUZZLES,
    Board,
    SolverStats,
    copy_board,
    create_empty_board,
    find_empty,
    generate_puzzle,
    solve_with_stats,
    validate_board,
)

# =========================================================================
# Dark Theme Color Palette
# =========================================================================
BG_DEEP = "#0F0F23"
BG_SURFACE = "#161631"
BG_CARD = "#1C1C3A"
BG_CARD_HOVER = "#222248"
BG_INPUT = "#12122A"

BORDER_DIM = "#2A2A50"
BORDER_ACCENT = "#4338CA"
BORDER_FOCUS = "#6366F1"

TEXT_PRIMARY = "#F1F5F9"
TEXT_SECONDARY = "#94A3B8"
TEXT_MUTED = "#64748B"
TEXT_ACCENT = "#A5B4FC"

# Cell states
CELL_BG = "#181838"
CELL_BG_FOCUS = "#1E1E50"
CELL_CLUE_FG = "#F1F5F9"
CELL_SOLVED_FG = "#A5B4FC"
CELL_SOLVED_BG = "#1A1A48"
CELL_ERROR_FG = "#FCA5A5"
CELL_ERROR_BG = "#2D1A1A"

# Status banner
STATUS_READY_BG = "#1A1A38"
STATUS_READY_FG = "#94A3B8"
STATUS_SUCCESS_BG = "#0D2818"
STATUS_SUCCESS_FG = "#34D399"
STATUS_ERROR_BG = "#2D1A1A"
STATUS_ERROR_FG = "#FCA5A5"
STATUS_INFO_BG = "#1A1A3D"
STATUS_INFO_FG = "#A5B4FC"

# Buttons
BTN_PRIMARY_BG = "#6366F1"
BTN_PRIMARY_FG = "#FFFFFF"
BTN_PRIMARY_HOVER = "#4F46E5"
BTN_SECONDARY_BG = "#252550"
BTN_SECONDARY_FG = "#A5B4FC"
BTN_SECONDARY_HOVER = "#2E2E60"
BTN_DANGER_BG = "#3B1A1A"
BTN_DANGER_FG = "#FCA5A5"
BTN_DANGER_HOVER = "#4A2020"

# Block border for 3x3 grid separation
BLOCK_BORDER = "#4338CA"
CELL_BORDER = "#252545"


class StyledButton(tk.Button):
    """A styled flat button with hover effects for the dark theme."""

    def __init__(self, parent, text, command=None, bg=BTN_SECONDARY_BG, fg=BTN_SECONDARY_FG,
                 hover_bg=BTN_SECONDARY_HOVER, font_spec=("Segoe UI", 10, "bold"),
                 padx=16, pady=8, **kwargs):
        super().__init__(
            parent, text=text, command=command,
            bg=bg, fg=fg, activebackground=hover_bg, activeforeground=fg,
            font=font_spec, relief="flat", bd=0, cursor="hand2",
            padx=padx, pady=pady, highlightthickness=0, **kwargs
        )
        self._bg = bg
        self._hover_bg = hover_bg
        self.bind("<Enter>", lambda e: self.configure(bg=self._hover_bg))
        self.bind("<Leave>", lambda e: self.configure(bg=self._bg))



class SudokuApp:
    """Main application controller for the Sudoku Solver GUI."""

    def __init__(self, root: Optional[tk.Tk] = None):
        if root is None:
            self.root = tk.Tk()
        else:
            self.root = root

        self.root.title("Sudoku Solver")
        self.root.configure(bg=BG_DEEP)
        self.root.minsize(960, 720)
        self.root.resizable(True, True)

        # High-DPI awareness on Windows
        self._enable_dpi_awareness()

        # State tracking
        self.cells: List[List[tk.Entry]] = []
        self.initial_clues: Set[Tuple[int, int]] = set()
        self.last_loaded_preset: Optional[str] = None
        self.solved_state_active: bool = False

        self._build_ui()
        self._load_default_preset("Easy")

    def _enable_dpi_awareness(self) -> None:
        """Enables high-DPI scaling on Windows platforms."""
        if sys.platform == "win32":
            try:
                from ctypes import windll
                windll.shcore.SetProcessDpiAwareness(1)
            except Exception:
                try:
                    windll.user32.SetProcessDPIAware()
                except Exception:
                    pass

    def _build_ui(self) -> None:
        """Constructs the desktop layout."""
        # ── Header ──
        header = tk.Frame(self.root, bg=BG_DEEP, padx=32, pady=16)
        header.pack(fill="x")

        title = tk.Label(header, text="✦  Sudoku Solver", font=("Segoe UI", 22, "bold"),
                         bg=BG_DEEP, fg=TEXT_ACCENT)
        title.pack(anchor="w")

        subtitle = tk.Label(header, text="Backtracking Engine with MRV Heuristic",
                            font=("Segoe UI", 10), bg=BG_DEEP, fg=TEXT_MUTED)
        subtitle.pack(anchor="w", pady=(2, 0))

        # ── Separator ──
        sep = tk.Frame(self.root, bg=BORDER_DIM, height=1)
        sep.pack(fill="x", padx=32)

        # ── Main workspace ──
        workspace = tk.Frame(self.root, bg=BG_DEEP, padx=32, pady=20)
        workspace.pack(fill="both", expand=True)

        # Left: Board + Status
        left_col = tk.Frame(workspace, bg=BG_DEEP)
        left_col.pack(side="left", fill="both", padx=(0, 24))

        self._build_board(left_col)
        self._build_status_banner(left_col)

        # Right: Controls
        right_col = tk.Frame(workspace, bg=BG_DEEP, width=320)
        right_col.pack(side="left", fill="both", expand=True)
        right_col.pack_propagate(False)

        self._build_puzzle_loader(right_col)
        self._build_controls(right_col)
        self._build_statistics(right_col)
        self._build_algorithm_info(right_col)

    # =========================================================================
    # Board
    # =========================================================================
    def _build_board(self, parent: tk.Frame) -> None:
        """Constructs the 9x9 Sudoku board with modern dark styling."""
        board_outer = tk.Frame(parent, bg=BLOCK_BORDER, padx=3, pady=3)
        board_outer.pack(anchor="center", pady=(0, 12))

        # Cache block frames
        block_frames: List[List[tk.Frame]] = []
        for br in range(3):
            row_frames = []
            for bc in range(3):
                frame = tk.Frame(board_outer, bg=CELL_BORDER, padx=1, pady=1)
                frame.grid(row=br, column=bc, padx=1, pady=1, sticky="nsew")
                row_frames.append(frame)
            block_frames.append(row_frames)

        self.cells = []
        for r in range(9):
            row_cells: List[tk.Entry] = []
            for c in range(9):
                parent_block = block_frames[r // 3][c // 3]

                entry = tk.Entry(
                    parent_block,
                    width=2,
                    font=("Consolas", 18, "bold"),
                    justify="center",
                    relief="flat",
                    bg=CELL_BG,
                    fg=CELL_CLUE_FG,
                    insertbackground=TEXT_ACCENT,
                    highlightcolor=BORDER_FOCUS,
                    highlightthickness=1,
                    highlightbackground=CELL_BORDER,
                    selectbackground=BORDER_ACCENT,
                    selectforeground=TEXT_PRIMARY,
                    disabledbackground=CELL_BG,
                    disabledforeground=TEXT_MUTED,
                )
                entry.grid(row=r % 3, column=c % 3, padx=1, pady=1, ipadx=6, ipady=8)

                entry.bind("<Key>", lambda e, row=r, col=c: self._handle_cell_key(e, row, col))
                entry.bind("<FocusIn>", lambda e, row=r, col=c: self._on_cell_focus_in(row, col))
                entry.bind("<FocusOut>", lambda e, row=r, col=c: self._on_cell_focus_out(row, col))

                row_cells.append(entry)
            self.cells.append(row_cells)

    # =========================================================================
    # Status Banner
    # =========================================================================
    def _build_status_banner(self, parent: tk.Frame) -> None:
        """Inline status banner with themed styling."""
        self.status_frame = tk.Frame(parent, bg=STATUS_READY_BG, padx=14, pady=10)
        self.status_frame.pack(fill="x", pady=(8, 0))

        self.status_icon = tk.Label(self.status_frame, text="✦", font=("Segoe UI", 10),
                                    bg=STATUS_READY_BG, fg=STATUS_READY_FG)
        self.status_icon.pack(side="left", padx=(0, 8))

        self.status_label = tk.Label(
            self.status_frame,
            text="Ready. Enter a puzzle or load a preset.",
            font=("Segoe UI", 9, "bold"),
            bg=STATUS_READY_BG, fg=STATUS_READY_FG, anchor="w",
        )
        self.status_label.pack(side="left", fill="x", expand=True)

    # =========================================================================
    # Cards
    # =========================================================================
    def _make_card(self, parent: tk.Frame, title: str, icon: str = "") -> tk.Frame:
        """Creates a dark themed card container with optional title."""
        card = tk.Frame(parent, bg=BG_CARD, padx=18, pady=14,
                        highlightbackground=BORDER_DIM, highlightthickness=1)
        card.pack(fill="x", pady=(0, 12))

        if title:
            header = tk.Frame(card, bg=BG_CARD)
            header.pack(fill="x", pady=(0, 10))
            label_text = f"{icon}  {title}" if icon else title
            tk.Label(header, text=label_text, font=("Segoe UI", 11, "bold"),
                     bg=BG_CARD, fg=TEXT_PRIMARY).pack(anchor="w")

        return card

    def _build_puzzle_loader(self, parent: tk.Frame) -> None:
        """Preset puzzle selector card."""
        card = self._make_card(parent, "Preset Puzzles", "📚")

        row = tk.Frame(card, bg=BG_CARD)
        row.pack(fill="x")

        self.preset_var = tk.StringVar(value="Easy")
        preset_options = list(SAMPLE_PUZZLES.keys())

        combo = ttk.Combobox(row, textvariable=self.preset_var, values=preset_options,
                             state="readonly", font=("Segoe UI", 9), width=14)
        combo.pack(side="left", fill="x", expand=True, padx=(0, 8))
        combo.bind("<<ComboboxSelected>>", lambda e: self._on_load_preset_clicked())

        # Style combobox
        style = ttk.Style(self.root)
        style.theme_use("clam")
        style.configure("TCombobox",
                         fieldbackground=BG_INPUT, background=BG_INPUT,
                         foreground=TEXT_PRIMARY, bordercolor=BORDER_DIM,
                         arrowcolor=TEXT_SECONDARY, selectbackground=BORDER_ACCENT,
                         selectforeground=TEXT_PRIMARY)
        style.map("TCombobox",
                   fieldbackground=[("readonly", BG_INPUT)],
                   foreground=[("readonly", TEXT_PRIMARY)],
                   selectbackground=[("readonly", BORDER_ACCENT)],
                   selectforeground=[("readonly", TEXT_PRIMARY)])

        load_btn = StyledButton(row, "Load", command=self._on_load_preset_clicked,
                                 bg=BTN_SECONDARY_BG, fg=BTN_SECONDARY_FG,
                                 hover_bg=BTN_SECONDARY_HOVER,
                                 font_spec=("Segoe UI", 9, "bold"),
                                 padx=14, pady=6)
        load_btn.pack(side="right")

    def _build_controls(self, parent: tk.Frame) -> None:
        """Action buttons card."""
        card = self._make_card(parent, "Controls", "⚡")

        # Solve (primary)
        solve_btn = StyledButton(card, "⚡  Solve Sudoku", command=self.solve_sudoku,
                                  bg=BTN_PRIMARY_BG, fg=BTN_PRIMARY_FG,
                                  hover_bg=BTN_PRIMARY_HOVER,
                                  font_spec=("Segoe UI", 11, "bold"),
                                  padx=20, pady=10)
        solve_btn.pack(fill="x", pady=(0, 8))

        # Check
        check_btn = StyledButton(card, "Check Puzzle", command=self.check_puzzle,
                                  font_spec=("Segoe UI", 10, "bold"),
                                  padx=16, pady=8)
        check_btn.pack(fill="x", pady=(0, 8))

        # Row: Clear Solution + Reset
        btn_row = tk.Frame(card, bg=BG_CARD)
        btn_row.pack(fill="x", pady=(0, 8))

        clear_sol = StyledButton(btn_row, "Clear Solution", command=self.clear_solution,
                                  font_spec=("Segoe UI", 9, "bold"),
                                  padx=12, pady=6)
        clear_sol.pack(side="left", fill="x", expand=True, padx=(0, 4))

        reset_btn = StyledButton(btn_row, "Reset", command=self.reset_puzzle,
                                  font_spec=("Segoe UI", 9, "bold"),
                                  padx=12, pady=6)
        reset_btn.pack(side="left", fill="x", expand=True, padx=(4, 0))

        # Clear Board (danger)
        clear_board = StyledButton(card, "Clear Board", command=self.clear_board,
                                    bg=BTN_DANGER_BG, fg=BTN_DANGER_FG,
                                    hover_bg=BTN_DANGER_HOVER,
                                    font_spec=("Segoe UI", 9, "bold"),
                                    padx=16, pady=6)
        clear_board.pack(fill="x")

    def _build_statistics(self, parent: tk.Frame) -> None:
        """Solver statistics card."""
        card = self._make_card(parent, "Solver Statistics", "📊")

        self.stat_labels: Dict[str, tk.Label] = {}
        stats_data = [
            ("Status", "Idle"),
            ("Execution Time", "—"),
            ("Backtracks", "—"),
            ("Empty Cells", "—"),
        ]

        grid = tk.Frame(card, bg=BG_CARD)
        grid.pack(fill="x")

        for i, (label, default) in enumerate(stats_data):
            row_frame = tk.Frame(grid, bg=BG_CARD)
            row_frame.pack(fill="x", pady=3)

            tk.Label(row_frame, text=label, font=("Segoe UI", 9, "bold"),
                     bg=BG_CARD, fg=TEXT_MUTED, width=14, anchor="w").pack(side="left")

            val_label = tk.Label(row_frame, text=default, font=("Consolas", 10, "bold"),
                                 bg=BG_CARD, fg=TEXT_PRIMARY, anchor="e")
            val_label.pack(side="right")

            key = label.lower().replace(" ", "_")
            self.stat_labels[key] = val_label

    def _build_algorithm_info(self, parent: tk.Frame) -> None:
        """How-it-works info card."""
        card = self._make_card(parent, "How It Works", "🧠")

        steps = [
            "1. Find the cell with fewest candidates (MRV)",
            "2. Try each valid digit 1–9 sequentially",
            "3. Validate row, column & 3×3 box constraints",
            "4. Recursively solve the next empty cell",
            "5. If stuck, backtrack and try next digit",
        ]

        for step in steps:
            tk.Label(card, text=step, font=("Segoe UI", 8), bg=BG_CARD,
                     fg=TEXT_MUTED, anchor="w", justify="left").pack(fill="x", pady=1)

    # =========================================================================
    # Keyboard & Cell Events
    # =========================================================================
    def _handle_cell_key(self, event: tk.Event, row: int, col: int) -> str:
        """Processes keystrokes for digits 1-9, backspace, and navigation."""
        key = event.char
        keysym = event.keysym

        # Ignore modifier keys
        if keysym in (
            "Shift_L", "Shift_R", "Control_L", "Control_R",
            "Alt_L", "Alt_R", "Caps_Lock", "Escape", "Meta_L", "Meta_R",
            "Win_L", "Win_R", "Super_L", "Super_R",
            "F1", "F2", "F3", "F4", "F5", "F6", "F7", "F8", "F9", "F10", "F11", "F12"
        ):
            return ""

        # Numpad mapping
        numpad_map = {
            "KP_1": "1", "KP_2": "2", "KP_3": "3",
            "KP_4": "4", "KP_5": "5", "KP_6": "6",
            "KP_7": "7", "KP_8": "8", "KP_9": "9",
            "KP_0": "0", "KP_Insert": "0", "KP_Delete": "0"
        }
        if keysym in numpad_map:
            key = numpad_map[keysym]

        # Arrow navigation
        if keysym == "Up":
            self._move_focus((row - 1) % 9, col)
            return "break"
        elif keysym == "Down":
            self._move_focus((row + 1) % 9, col)
            return "break"
        elif keysym == "Left":
            self._move_focus(row, (col - 1) % 9)
            return "break"
        elif keysym == "Right":
            self._move_focus(row, (col + 1) % 9)
            return "break"

        # Clear cell
        if keysym in ("BackSpace", "Delete", "KP_Delete") or key == "0":
            self._set_cell_value(row, col, 0, is_clue=False)
            self.initial_clues.discard((row, col))
            self.solved_state_active = False
            self._reset_cell_highlight(row, col)
            self._update_board_stats()
            return "break"

        # Valid digits
        if key in "123456789":
            self._set_cell_value(row, col, int(key), is_clue=True)
            self.initial_clues.add((row, col))
            self.solved_state_active = False
            self._reset_cell_highlight(row, col)
            self._update_board_stats()
            next_col = (col + 1) % 9
            next_row = row + 1 if next_col == 0 else row
            if next_row < 9:
                self._move_focus(next_row, next_col)
            return "break"

        # Tab / Return
        if keysym in ("Tab", "Return", "ISO_Left_Tab"):
            return ""

        self.set_status("Only digits 1–9 are accepted.", "error")
        return "break"

    def _on_cell_focus_in(self, row: int, col: int) -> None:
        if (row, col) not in self.initial_clues and not self.solved_state_active:
            self.cells[row][col].configure(bg=CELL_BG_FOCUS)

    def _on_cell_focus_out(self, row: int, col: int) -> None:
        if (row, col) in self.initial_clues:
            self.cells[row][col].configure(bg=CELL_BG)
        elif self.solved_state_active:
            self.cells[row][col].configure(bg=CELL_SOLVED_BG)
        else:
            self.cells[row][col].configure(bg=CELL_BG)

    def _move_focus(self, row: int, col: int) -> None:
        self.cells[row][col].focus_set()
        self.cells[row][col].icursor(tk.END)

    def _reset_cell_highlight(self, row: int, col: int) -> None:
        is_clue = (row, col) in self.initial_clues
        bg = CELL_SOLVED_BG if (self.solved_state_active and not is_clue) else CELL_BG
        fg = CELL_CLUE_FG if is_clue else CELL_SOLVED_FG
        self.cells[row][col].configure(bg=bg, fg=fg)

    def _set_cell_value(self, row: int, col: int, val: int, is_clue: bool = False) -> None:
        entry = self.cells[row][col]
        entry.delete(0, tk.END)
        if val != 0:
            entry.insert(0, str(val))
            if is_clue:
                entry.configure(fg=CELL_CLUE_FG, font=("Consolas", 18, "bold"), bg=CELL_BG)
            else:
                entry.configure(fg=CELL_SOLVED_FG, font=("Consolas", 18, "bold"), bg=CELL_SOLVED_BG)
        else:
            entry.configure(bg=CELL_BG, fg=CELL_CLUE_FG)

    def _highlight_conflict(self, row: int, col: int) -> None:
        self.cells[row][col].configure(bg=CELL_ERROR_BG, fg=CELL_ERROR_FG)
        self.cells[row][col].focus_set()

    # =========================================================================
    # Board Data
    # =========================================================================
    def get_board(self) -> Board:
        board: Board = []
        for r in range(9):
            row_data: List[int] = []
            for c in range(9):
                text = self.cells[r][c].get().strip()
                if text.isdigit() and 1 <= int(text) <= 9:
                    row_data.append(int(text))
                else:
                    row_data.append(0)
            board.append(row_data)
        return board

    def set_board(self, board: Board, preserve_clues: bool = False) -> None:
        for r in range(9):
            for c in range(9):
                val = board[r][c]
                is_clue = (r, c) in self.initial_clues if preserve_clues else (val != 0)
                self._set_cell_value(r, c, val, is_clue=is_clue)
        self._update_board_stats()

    def set_status(self, message: str, level: str = "ready") -> None:
        theme_map = {
            "ready": (STATUS_READY_BG, STATUS_READY_FG, "✦"),
            "success": (STATUS_SUCCESS_BG, STATUS_SUCCESS_FG, "✓"),
            "error": (STATUS_ERROR_BG, STATUS_ERROR_FG, "✕"),
            "info": (STATUS_INFO_BG, STATUS_INFO_FG, "ℹ"),
        }
        bg, fg, icon = theme_map.get(level, (STATUS_READY_BG, STATUS_READY_FG, "✦"))
        self.status_frame.configure(bg=bg)
        self.status_icon.configure(text=icon, bg=bg, fg=fg)
        self.status_label.configure(text=message, bg=bg, fg=fg)

    def _update_board_stats(self) -> None:
        board = self.get_board()
        empty_count = sum(1 for row in board for val in row if val == 0)
        self.stat_labels["empty_cells"].configure(text=str(empty_count))

    # =========================================================================
    # Actions
    # =========================================================================
    def solve_sudoku(self) -> None:
        board = self.get_board()

        if find_empty(board) is None:
            valid, msg, conflict = validate_board(board)
            if valid:
                self.set_status("Sudoku is already solved and valid!", "success")
                self.stat_labels["status"].configure(text="Solved", fg=STATUS_SUCCESS_FG)
            else:
                self.set_status(msg, "error")
                if conflict:
                    self._highlight_conflict(*conflict)
            return

        if not self.solved_state_active or not self.initial_clues:
            self.initial_clues = {
                (r, c) for r in range(9) for c in range(9) if board[r][c] != 0
            }

        valid, msg, conflict = validate_board(board)
        if not valid:
            self.set_status(f"Cannot solve: {msg}", "error")
            self.stat_labels["status"].configure(text="Invalid", fg=CELL_ERROR_FG)
            if conflict:
                self._highlight_conflict(*conflict)
            return

        success, solved_board, stats = solve_with_stats(board)

        self.stat_labels["execution_time"].configure(text=f"{stats.execution_time_ms} ms")
        self.stat_labels["backtracks"].configure(text=str(stats.backtracks))

        if success:
            self.solved_state_active = True
            self.set_board(solved_board, preserve_clues=True)
            self.stat_labels["status"].configure(text="Solved", fg=STATUS_SUCCESS_FG)
            self.set_status(
                f"Solved in {stats.execution_time_ms} ms with {stats.backtracks} backtracks!",
                "success",
            )
        else:
            self.stat_labels["status"].configure(text="Unsolvable", fg=CELL_ERROR_FG)
            self.set_status(
                f"Unsolvable — evaluated {stats.backtracks} backtracks in {stats.execution_time_ms} ms.",
                "error",
            )

    def check_puzzle(self) -> None:
        board = self.get_board()
        for r in range(9):
            for c in range(9):
                self._reset_cell_highlight(r, c)

        valid, msg, conflict = validate_board(board)
        if valid:
            empty = sum(1 for row in board for val in row if val == 0)
            if empty == 0:
                self.set_status("Puzzle is completely solved and valid!", "success")
                self.stat_labels["status"].configure(text="Complete", fg=STATUS_SUCCESS_FG)
            else:
                self.set_status(f"Puzzle is valid so far ({empty} cells remaining).", "info")
                self.stat_labels["status"].configure(text="Valid", fg=TEXT_ACCENT)
        else:
            self.set_status(f"Invalid: {msg}", "error")
            self.stat_labels["status"].configure(text="Conflict", fg=CELL_ERROR_FG)
            if conflict:
                self._highlight_conflict(*conflict)

    def _on_load_preset_clicked(self) -> None:
        self._load_default_preset(self.preset_var.get())

    def _load_default_preset(self, preset_name: str) -> None:
        if preset_name not in DIFFICULTY_CLUES:
            return

        # Generate a fresh random puzzle every time
        self.set_status(f"Generating {preset_name} puzzle...", "info")
        self.root.update_idletasks()

        grid = generate_puzzle(preset_name)

        self.last_loaded_preset = preset_name
        self.solved_state_active = False
        self.initial_clues = {
            (r, c) for r in range(9) for c in range(9) if grid[r][c] != 0
        }

        for r in range(9):
            for c in range(9):
                val = grid[r][c]
                self._set_cell_value(r, c, val, is_clue=(val != 0))

        clue_count = len(self.initial_clues)
        self.stat_labels["status"].configure(text="Generated", fg=TEXT_ACCENT)
        self.stat_labels["execution_time"].configure(text="—")
        self.stat_labels["backtracks"].configure(text="—")
        self._update_board_stats()
        self.set_status(f"New {preset_name} puzzle generated ({clue_count} clues). Click 'Solve Sudoku' to solve.", "info")

    def clear_solution(self) -> None:
        if not self.initial_clues:
            self.set_status("No clues to revert to.", "info")
            return

        for r in range(9):
            for c in range(9):
                if (r, c) not in self.initial_clues:
                    self._set_cell_value(r, c, 0, is_clue=False)
                else:
                    self._reset_cell_highlight(r, c)

        self.solved_state_active = False
        self.stat_labels["status"].configure(text="Cleared", fg=TEXT_ACCENT)
        self.stat_labels["execution_time"].configure(text="—")
        self.stat_labels["backtracks"].configure(text="—")
        self._update_board_stats()
        self.set_status("Solution cleared. Original clues preserved.", "info")

    def reset_puzzle(self) -> None:
        if self.last_loaded_preset:
            self._load_default_preset(self.last_loaded_preset)
            self.set_status(f"Reset to {self.last_loaded_preset} preset.", "info")
        else:
            self.clear_board()

    def clear_board(self) -> None:
        for r in range(9):
            for c in range(9):
                self._set_cell_value(r, c, 0, is_clue=False)

        self.initial_clues.clear()
        self.solved_state_active = False
        self.last_loaded_preset = None

        self.stat_labels["status"].configure(text="Cleared", fg=TEXT_MUTED)
        self.stat_labels["execution_time"].configure(text="—")
        self.stat_labels["backtracks"].configure(text="—")
        self.stat_labels["empty_cells"].configure(text="81")
        self.set_status("Board cleared. Enter your own puzzle or load a preset.", "ready")

    def run(self) -> None:
        """Starts the Tkinter main event loop."""
        self.root.mainloop()


if __name__ == "__main__":
    app = SudokuApp()
    app.run()
