#!/usr/bin/env python3
"""
Sprint Estimator
A small desktop tool to estimate development days needed for a sprint,
based on ticket story points and assigned Senior/Junior developers.

Formula rules:
- If Junior == 0: use the "Single Member" formula (factor by story point).
- If Junior >= 1: use the "Team Estimation" formula (loss % by story point),
  regardless of how many Seniors are also assigned.
- A ticket with 0 Senior AND 0 Junior cannot be added.
"""

import tkinter as tk
from tkinter import ttk, messagebox

STORY_POINTS = [1, 2, 3, 5, 8, 13]
DEV_COUNT_OPTIONS = list(range(0, 11))  # 0 to 10

# --- Calculation logic (ported from the spreadsheet formulas) ---

def single_member_factor(sp: float) -> float:
    if sp <= 3:
        return 1.0
    if sp == 5:
        return 0.9
    if sp == 8:
        return 0.85
    return 0.8  # sp >= 13


def team_loss(sp: float) -> float:
    if sp <= 2:
        return 0.0
    if sp == 3:
        return 0.2
    if sp == 5:
        return 0.3
    if sp == 8:
        return 0.35
    return 0.4  # sp >= 13


def calculate_days(story_point: int, senior: int, junior: int):
    """Returns (estimated_days, mode_label)."""
    total_dev = senior + junior
    if total_dev == 0:
        raise ValueError("At least one developer (Senior or Junior) is required.")

    if junior == 0:
        factor = single_member_factor(story_point)
        days = story_point / (total_dev * factor)
        mode = "Solo"
    else:
        loss = team_loss(story_point)
        days = story_point / (total_dev * (1 - loss))
        mode = "Team"

    return round(days, 2), mode


class SprintEstimatorApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Sprint Estimator")
        self.geometry("720x560")
        self.minsize(680, 480)

        self.tickets = []  # in-memory list of dicts, no persistence
        self._row_counter = 0

        self._build_form()
        self._build_table()
        self._build_summary()

    # ---------------- UI construction ----------------

    def _build_form(self):
        frame = ttk.LabelFrame(self, text="Add ticket")
        frame.pack(fill="x", padx=12, pady=(12, 6))

        # Ticket name
        ttk.Label(frame, text="Ticket").grid(row=0, column=0, padx=6, pady=8, sticky="w")
        self.ticket_var = tk.StringVar()
        ttk.Entry(frame, textvariable=self.ticket_var, width=16).grid(row=1, column=0, padx=6, sticky="we")

        # Story point
        ttk.Label(frame, text="Story point").grid(row=0, column=1, padx=6, pady=8, sticky="w")
        self.sp_var = tk.IntVar(value=STORY_POINTS[0])
        ttk.Combobox(
            frame, textvariable=self.sp_var, values=STORY_POINTS,
            state="readonly", width=8
        ).grid(row=1, column=1, padx=6, sticky="we")

        # Assigned senior
        ttk.Label(frame, text="Assigned senior").grid(row=0, column=2, padx=6, pady=8, sticky="w")
        self.senior_var = tk.IntVar(value=1)
        ttk.Combobox(
            frame, textvariable=self.senior_var, values=DEV_COUNT_OPTIONS,
            state="readonly", width=8
        ).grid(row=1, column=2, padx=6, sticky="we")

        # Assigned junior
        ttk.Label(frame, text="Assigned junior").grid(row=0, column=3, padx=6, pady=8, sticky="w")
        self.junior_var = tk.IntVar(value=0)
        ttk.Combobox(
            frame, textvariable=self.junior_var, values=DEV_COUNT_OPTIONS,
            state="readonly", width=8
        ).grid(row=1, column=3, padx=6, sticky="we")

        # Add button
        ttk.Button(frame, text="Add", command=self._on_add).grid(row=1, column=4, padx=10, sticky="we")

        for i in range(5):
            frame.grid_columnconfigure(i, weight=1)

    def _build_table(self):
        frame = ttk.Frame(self)
        frame.pack(fill="both", expand=True, padx=12, pady=6)

        columns = ("ticket", "sp", "senior", "junior", "mode", "days")
        self.tree = ttk.Treeview(frame, columns=columns, show="headings", height=12)
        headings = {
            "ticket": "Ticket", "sp": "SP", "senior": "Senior",
            "junior": "Junior", "mode": "Formula", "days": "Est. days",
        }
        widths = {"ticket": 160, "sp": 60, "senior": 70, "junior": 70, "mode": 80, "days": 90}
        for col in columns:
            self.tree.heading(col, text=headings[col])
            self.tree.column(col, width=widths[col], anchor="center")
        self.tree.column("ticket", anchor="w")

        vsb = ttk.Scrollbar(frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=vsb.set)
        self.tree.pack(side="left", fill="both", expand=True)
        vsb.pack(side="right", fill="y")

        btn_frame = ttk.Frame(self)
        btn_frame.pack(fill="x", padx=12, pady=(0, 6))
        ttk.Button(btn_frame, text="Delete selected", command=self._on_delete_selected).pack(side="left")
        ttk.Button(btn_frame, text="Clear all", command=self._on_clear_all).pack(side="left", padx=8)

    def _build_summary(self):
        frame = ttk.LabelFrame(self, text="Summary")
        frame.pack(fill="x", padx=12, pady=(0, 12))

        self.total_tickets_lbl = ttk.Label(frame, text="Total tickets: 0", font=("", 11, "bold"))
        self.total_tickets_lbl.grid(row=0, column=0, padx=12, pady=10, sticky="w")

        self.total_days_lbl = ttk.Label(frame, text="Total est. days: 0.00", font=("", 11, "bold"))
        self.total_days_lbl.grid(row=0, column=1, padx=12, pady=10, sticky="w")

        ttk.Label(frame, text="Sprint capacity (days):").grid(row=0, column=2, padx=(12, 4), pady=10, sticky="e")
        self.capacity_var = tk.StringVar(value="0")
        capacity_entry = ttk.Entry(frame, textvariable=self.capacity_var, width=8)
        capacity_entry.grid(row=0, column=3, padx=(0, 12), pady=10, sticky="w")
        capacity_entry.bind("<KeyRelease>", lambda e: self._refresh_summary())

        self.capacity_status_lbl = ttk.Label(frame, text="", font=("", 10, "bold"))
        self.capacity_status_lbl.grid(row=0, column=4, padx=12, pady=10, sticky="w")

        for i in range(5):
            frame.grid_columnconfigure(i, weight=1)

    # ---------------- Event handlers ----------------

    def _on_add(self):
        try:
            sp = int(self.sp_var.get())
            senior = int(self.senior_var.get())
            junior = int(self.junior_var.get())
        except (tk.TclError, ValueError):
            messagebox.showerror("Invalid input", "Please check story point / senior / junior values.")
            return

        try:
            days, mode = calculate_days(sp, senior, junior)
        except ValueError as e:
            messagebox.showwarning("Cannot add ticket", str(e))
            return

        ticket_name = self.ticket_var.get().strip() or f"Ticket {self._row_counter + 1}"
        self._row_counter += 1

        row_id = self.tree.insert(
            "", "end",
            values=(ticket_name, sp, senior, junior, mode, f"{days:.2f}")
        )
        self.tickets.append({"id": row_id, "days": days})

        self.ticket_var.set("")
        self._refresh_summary()

    def _on_delete_selected(self):
        selected = self.tree.selection()
        if not selected:
            return
        for row_id in selected:
            self.tree.delete(row_id)
            self.tickets = [t for t in self.tickets if t["id"] != row_id]
        self._refresh_summary()

    def _on_clear_all(self):
        if not self.tickets:
            return
        if messagebox.askyesno("Clear all", "Remove all tickets from this session?"):
            for item in self.tree.get_children():
                self.tree.delete(item)
            self.tickets.clear()
            self._refresh_summary()

    def _refresh_summary(self):
        total_tickets = len(self.tickets)
        total_days = sum(t["days"] for t in self.tickets)

        self.total_tickets_lbl.config(text=f"Total tickets: {total_tickets}")
        self.total_days_lbl.config(text=f"Total est. days: {total_days:.2f}")

        try:
            capacity = float(self.capacity_var.get())
        except ValueError:
            capacity = 0.0

        if capacity <= 0:
            self.capacity_status_lbl.config(text="", foreground="black")
        elif total_days > capacity:
            over = total_days - capacity
            self.capacity_status_lbl.config(text=f"Over by {over:.2f} days", foreground="#B22222")
        else:
            remaining = capacity - total_days
            self.capacity_status_lbl.config(text=f"{remaining:.2f} days remaining", foreground="#1E7B34")


if __name__ == "__main__":
    app = SprintEstimatorApp()
    app.mainloop()
