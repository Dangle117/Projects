import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from services.system_manager import SystemManager
from models.student import Student
from utils import file_io
import os
import math
from algorithms.TimSort import (sort_students, gpa_key, name_key,
                                birth_year_key, id_key, major_key)

class StudentApp(ttk.Frame):
    def __init__(self, root)    :
        super().__init__(root, padding=10)
        self.root = root
        self.root.title("Student Manager")
        self.root.geometry("1350x800")
        self.root.minsize(1250, 750)

        self.style = ttk.Style()
        self.style.theme_use("clam")

        # make nicer fonts and colors
        self.style.configure("Accent.TButton", foreground="#2563eb", background="white", font=("Segoe UI", 11, "bold"))
        self.style.configure("TLabel", font=("Segoe UI", 11))

        # system manager (load data)
        self.sm = SystemManager()

        # current view list (supports filtering). Defaults to all students.
        self.view_students = list(self.sm.students)
        # whether view is currently filtered (True => view_students is a filtered subset)
        self.is_filtered = False

        # initialize search state early so refresh_table and other methods can access them
        self.search_matches = []   # list of tree iids that match current search
        self.search_index = -1     # current index into search_matches

        # Sorting state per-column:
        # None -> original order, "asc" -> ascending, "desc" -> descending
        self._sort_state = {c: None for c in ("no", "id", "name", "birth", "major", "gpa")}
        # snapshot of canonical students before a sort so we can restore "original" order
        self._canon_snapshot = None
        # snapshots for filtered views per-column
        self._view_snapshots = {}

        self.pack(fill="both", expand=True)

        # Top toolbar (search + actions)
        toolbar = ttk.Frame(self)
        toolbar.pack(fill="x", pady=(0, 6))

        ttk.Label(toolbar, text="Search:").pack(side="left", padx=(6, 4))
        self.search_var = tk.StringVar()
        search_entry = ttk.Entry(toolbar, textvariable=self.search_var, width=30)
        search_entry.pack(side="left", padx=(0, 6))
        search_entry.bind("<Return>", lambda e: self.search_student())

        ttk.Button(toolbar, text="🔍", command=self.search_student).pack(side="left", padx=4)

        # navigation buttons for search results
        self.prev_btn = ttk.Button(toolbar, text="▲", command=self.prev_match, state="disabled")
        self.prev_btn.pack(side="left", padx=(6, 2))
        self.next_btn = ttk.Button(toolbar, text="▼", command=self.next_match, state="disabled")
        self.next_btn.pack(side="left", padx=(2, 8))

        self.add_btn = ttk.Button(toolbar, text="➕ Add", style="Accent.TButton", command=self.add_student_popup)
        self.add_btn.pack(side="left", padx=8)
        ttk.Button(toolbar, text="✏️ Edit", command=self.edit_selected).pack(side="left", padx=4)
        ttk.Button(toolbar, text="🗑️ Delete", command=self.delete_selected).pack(side="left", padx=4)
        ttk.Button(toolbar, text="📂 Load", command=self.load_file).pack(side="left", padx=4)
        ttk.Button(toolbar, text="💾 Save", command=self.save).pack(side="left", padx=4)
        ttk.Button(toolbar, text="💾 Save As...", command=self.save_as).pack(side="left", padx=4)
        # Filter controls
        ttk.Button(toolbar, text="🔎 Filter", command=self.open_filter_popup).pack(side="left", padx=8)
        ttk.Button(toolbar, text="❌ Clear Filter", command=self.clear_filter).pack(side="left", padx=4)

        # Treeview
        self.subjects = ["CSI106", "PFP191", "MAD101", "MAE101"]

        # Create and configure the main Treeview table.
        self._create_table()

        # Custom table heading
        self.style.configure("Treeview.Heading",
                        background="white",
                        font=("Segoe UI", 14, "bold"))

        # Custom table rows
        self.style.configure("Treeview",
                        font=("Segoe UI", 13),
                        rowheight=25)
        self.style.map("Treeview",
                  background=[("selected", "#4a6984")],
                  foreground=[("selected", "white")])

        # Bindings
        self._setup_bindings()

        # status bar
        self._create_status_bar()
        self._update_status()

        self._build_context_menu()
        self.refresh_table()

    # ---------- UI helpers ----------
    def _create_table(self):
        """
        Create and configure the main Treeview table.

        Features:
        - Sortable columns with click handlers
        - Row striping for better readability
        - Custom fonts and colors
        - Double-click and right-click bindings
        """
        # Define columns (no subject columns - they're only shown in edit dialog)
        columns = ("no", "id", "name", "birth", "major", "gpa")
        self.tree = ttk.Treeview(self, columns=columns, show="headings", selectmode="browse")

        # Configure column headings with sort callbacks
        for col in columns:
            self.tree.heading(col, text=col.upper(),
                              command=lambda c=col: self._on_heading_click(c))
            self.tree.column(col, anchor="center")

        # Special width for row number column
        self.tree.column("no", width=50)

        # Row appearance
        self.tree.tag_configure("oddrow", background="#edebeb")
        self.tree.tag_configure("evenrow", background="#ffffff")

        self.tree.pack(fill="both", expand=True, padx=6, pady=6)

    def _create_status_bar(self):
        """Create bottom status bar showing student count and save state."""
        status = ttk.Frame(self)
        status.pack(fill="x", side="bottom")
        self.status_var = tk.StringVar()
        self.status_label = ttk.Label(status, textvariable=self.status_var, anchor="w")
        self.status_label.pack(fill="x", padx=6)

    def _setup_bindings(self):
        """Setup keyboard shortcuts and window event handlers."""
        # Table row interactions
        self.tree.bind("<Double-1>", self._on_double_click)
        self.tree.bind("<Button-3>", self._on_right_click)

        # Window-level bindings
        self.root.protocol("WM_DELETE_WINDOW", self._on_close)  # handle window close
        self.root.bind_all("<Control-s>", self.save)           # Ctrl+S to save

    def _build_context_menu(self):
        """Create right-click context menu for table rows."""
        self.ctx = tk.Menu(self.root, tearoff=0)
        self.ctx.add_command(label="Edit", command=self.edit_selected)
        self.ctx.add_command(label="Delete", command=self.delete_selected)

    def _on_double_click(self, event):
        """Handle double-click on table row - open edit dialog."""
        self.edit_selected()

    def _on_right_click(self, event):
        """
        Show context menu on right-click.
        Only shows menu if clicking on a valid row.
        """
        iid = self.tree.identify_row(event.y)
        if iid:
            self.tree.selection_set(iid)
            self.ctx.tk_popup(event.x_root, event.y_root)

    def _on_heading_click(self, col):
        """
        Handle column header clicks for sorting.
        Sorts the current filtered view instead of the main list.
        """
        # Cycle states: None -> asc -> desc -> None (original)
        state = self._sort_state.get(col)

        # map column to key function
        key_map = {
            "gpa": gpa_key,
            "name": name_key,
            "id": id_key,
            "major": major_key,
            "birth": birth_year_key
        }
        key = key_map.get(col)

        # If unsupported column (e.g., "no") just ignore
        if key is None:
            return

        # Determine next state and act accordingly
        if state is None:
            # store snapshot to allow "original" restore
            if self.is_filtered:
                self._view_snapshots[col] = list(self.view_students)
            else:
                self._canon_snapshot = list(self.sm.students)
            reverse = False  # ascending first
            self._sort_state[col] = "asc"
        elif state == "asc":
            reverse = True   # descending
            self._sort_state[col] = "desc"
        else:
            # restore original order
            if self.is_filtered:
                orig = self._view_snapshots.pop(col, None)
                if orig is not None:
                    self.view_students = orig
            else:
                if self._canon_snapshot is not None:
                    self.sm.students = self._canon_snapshot
                    # rebuild index after replacing canonical list
                    try:
                        self.sm._build_index()
                    except Exception:
                        pass
                    self.view_students = list(self.sm.students)
                self._canon_snapshot = None
            # clear this column state and leave others cleared too
            for k in self._sort_state:
                self._sort_state[k] = None
            self.refresh_table()
            return

        # perform sorting according to current filter state
        if self.is_filtered:
            sort_students(self.view_students, key=key, reverse=reverse)
        else:
            # sort canonical list directly and rebuild index
            sort_students(self.sm.students, key=key, reverse=reverse)
            try:
                self.sm._build_index()
            except Exception:
                pass
            self.view_students = list(self.sm.students)

        # clear other column sort states (only one active at a time)
        for k in self._sort_state:
            if k != col:
                self._sort_state[k] = None

        self.refresh_table()

    def _update_status(self):
        """Update status bar with current student count and save state."""
        total = len(self.sm.students)
        unsaved = " (unsaved)" if self.sm.unsaved_changes else ""
        self.status_var.set(f"Students: {total}{unsaved}")

    def refresh_table(self):
        """
        Rebuild entire table contents from current view (self.view_students).

        - Clears and repopulates all rows
        - Applies row striping
        - Resets search state (since row IDs change)
        - Updates status bar
        """
        # Clear existing rows
        for r in self.tree.get_children():
            self.tree.delete(r)

        # Use view_students (may be filtered) instead of self.sm.students
        for i, s in enumerate(self.view_students, start=1):
            tag = "evenrow" if i % 2 == 0 else "oddrow"
            row = (i, s.student_id, s.name, s.birth_year, s.major, f"{s.gpa:.2f}")
            self.tree.insert("", "end", values=row, tags=(tag,))

        # Reset search state since row IDs changed
        self.search_matches = []
        self.search_index = -1
        self.prev_btn.configure(state="disabled")
        self.next_btn.configure(state="disabled")

        self._update_status()

    def _get_selected_id(self):
        """
        Get student_id from currently selected table row.
        Returns None if no row selected.
        Note: student_id is at index 1 because index 0 is row number.
        """
        sel = self.tree.selection()
        if not sel:
            return None
        vals = self.tree.item(sel[0])["values"]
        return str(vals[1])  # student_id is second column

    # ---------- CRUD UI ----------
    def add_student_popup(self):
        self._edit_popup(mode="add")

    def edit_selected(self):
        sid = self._get_selected_id()
        if not sid:
            messagebox.showinfo("Edit", "Select a student first.")
            return
        self._edit_popup(mode="edit", student_id=sid)

    def _edit_popup(self, mode: str = "add", student_id: str = None):
        """
        Unified Add / Edit popup with cleaner layout and validation.

        - mode: "add" or "edit"
        - student_id: when editing, the student's id to load
        """
        is_edit = (mode == "edit")

        popup = tk.Toplevel(self.root)
        popup.transient(self.root)
        popup.grab_set()
        popup.title("Edit Student" if is_edit else "Add Student")
        popup.resizable(False, False)
        popup.geometry("480x420")

        frm = ttk.Frame(popup, padding=12)
        frm.pack(fill="both", expand=True)

        lbl_font = ("Segoe UI", 10)
        entry_w = 32

        # --- Basic info grid ---
        basic = ttk.LabelFrame(frm, text="Basic Information", padding=10)
        basic.pack(fill="x", pady=(0, 8))

        ttk.Label(basic, text="ID:", font=lbl_font).grid(row=0, column=0, sticky="e", padx=6, pady=6)
        id_var = tk.StringVar()
        id_entry = ttk.Entry(basic, textvariable=id_var, width=entry_w)
        id_entry.grid(row=0, column=1, sticky="w", padx=6, pady=6)

        ttk.Label(basic, text="Full name:", font=lbl_font).grid(row=1, column=0, sticky="e", padx=6, pady=6)
        name_var = tk.StringVar()
        name_entry = ttk.Entry(basic, textvariable=name_var, width=entry_w)
        name_entry.grid(row=1, column=1, sticky="w", padx=6, pady=6)

        ttk.Label(basic, text="Birth year:", font=lbl_font).grid(row=2, column=0, sticky="e", padx=6, pady=6)
        birth_var = tk.StringVar()
        birth_entry = ttk.Entry(basic, textvariable=birth_var, width=entry_w)
        birth_entry.grid(row=2, column=1, sticky="w", padx=6, pady=6)

        ttk.Label(basic, text="Major:", font=lbl_font).grid(row=3, column=0, sticky="e", padx=6, pady=6)
        major_var = tk.StringVar()
        major_entry = ttk.Entry(basic, textvariable=major_var, width=entry_w)
        major_entry.grid(row=3, column=1, sticky="w", padx=6, pady=6)

        # --- Scores section ---
        scores_frame = ttk.LabelFrame(frm, text="Subject Scores (0-10)", padding=10)
        scores_frame.pack(fill="both", expand=True, pady=(0, 8))

        subj_vars = {}
        for i, subj in enumerate(self.subjects):
            ttk.Label(scores_frame, text=f"{subj}:", font=lbl_font).grid(row=i, column=0, sticky="e", padx=6, pady=4)
            v = tk.StringVar()
            ent = ttk.Entry(scores_frame, textvariable=v, width=12)
            ent.grid(row=i, column=1, sticky="w", padx=6, pady=4)
            subj_vars[subj] = v

        # Fill values when editing
        if is_edit and student_id:
            s = self.sm.find_by_id(student_id)
            if s:
                id_var.set(s.student_id)
                id_entry.configure(state="readonly")
                name_var.set(s.name or "")
                birth_var.set(str(s.birth_year or ""))
                major_var.set(s.major or "")
                for subj, var in subj_vars.items():
                    var.set(f"{s.get_score(subj):.2f}")

        # validation helpers
        def _validate_basic() -> bool:
            sid = id_var.get().strip()
            name = name_var.get().strip()
            birth = birth_var.get().strip()
            mj = major_var.get().strip()
            if not (sid and name and birth and mj):
                messagebox.showwarning("Validation", "Please fill all basic fields.", parent=popup)
                return False
            try:
                int(birth)
            except Exception:
                messagebox.showwarning("Validation", "Birth year must be an integer.", parent=popup)
                return False
            return True

        def _parse_scores():
            parsed = {}
            for subj, var in subj_vars.items():
                txt = var.get().strip()
                if txt == "":
                    val = 0.0
                else:
                    try:
                        val = float(txt)
                    except Exception:
                        messagebox.showwarning("Validation", f"Invalid score for {subj}.", parent=popup)
                        return None
                if not (0.0 <= val <= 10.0):
                    messagebox.showwarning("Validation", f"Score for {subj} must be 0-10.", parent=popup)
                    return None
                parsed[subj] = val
            return parsed

        # Save action
        def _on_save(event=None):
            if not _validate_basic():
                return
            scores = _parse_scores()
            if scores is None:
                return

            sid = id_var.get().strip()
            name = name_var.get().strip()
            birth_i = int(birth_var.get().strip())
            mj = major_var.get().strip()

            try:
                if is_edit:
                    ok = self.sm.update_student(sid, name, birth_i, mj)
                    if not ok:
                        messagebox.showerror("Error", "Student not found.", parent=popup)
                        return
                    # update scores
                    for subj, val in scores.items():
                        self.sm.add_score(sid, subj, val)
                else:
                    new = Student(sid, name, birth_i, mj)
                    self.sm.add_student(new)
                    for subj, val in scores.items():
                        self.sm.add_score(sid, subj, val)
                # If we're showing a filtered view, ensure view is consistent:
                if not self.is_filtered:
                    self.view_students = list(self.sm.students)
                else:
                    # For edit: update item in current filtered view; for add: append if it matches filter is left to user
                    if is_edit:
                        for idx, s in enumerate(self.view_students):
                            if s.student_id == sid:
                                self.view_students[idx] = self.sm.find_by_id(sid)
                                break
                self.refresh_table()

                # select and focus the saved student
                for iid in self.tree.get_children():
                    vals = self.tree.item(iid)["values"]
                    if len(vals) > 1 and str(vals[1]) == sid:
                        self.tree.selection_set(iid)
                        self.tree.see(iid)
                        break

                popup.destroy()
            except ValueError as e:
                messagebox.showerror("Error", str(e), parent=popup)

        # Buttons
        btn_frame = ttk.Frame(frm)
        btn_frame.pack(fill="x", pady=(6, 0))
        save_btn = ttk.Button(btn_frame, text="Save", command=_on_save, style="Accent.TButton")
        save_btn.pack(side="right", padx=6)
        ttk.Button(btn_frame, text="Cancel", command=popup.destroy).pack(side="right", padx=6)

        popup.bind("<Return>", _on_save)
        popup.bind("<Escape>", lambda e: popup.destroy())

        # focus
        if is_edit:
            name_entry.focus_set()
        else:
            id_entry.focus_set()

    def delete_selected(self):
        sid = self._get_selected_id()
        if not sid:
            messagebox.showinfo("Delete", "Select a student first.")
            return
        if not messagebox.askyesno("Delete", f"Delete student {sid}?"):
            return
        deleted = self.sm.delete_student(sid)
        if deleted:
            # remove from current view as well if present (handles filtered view)
            self.view_students = [s for s in self.view_students if s.student_id != sid]
            # if not filtered, ensure view shows canonical list
            if not self.is_filtered:
                self.view_students = list(self.sm.students)
            self.refresh_table()
        else:
            messagebox.showinfo("Delete", "Student not found.")

    # ---------- Search / Load / Save ----------
    def search_student(self):
        """
        Search for students by ID or complete name tokens (case-insensitive).

        Examples:
        - "An" matches "An Nguyen" but not "Trang" or "Khanh"
        - "nguyen" matches "Nguyen Van A" but not "Nguyen_Van_A"
        - "van" matches "Nguyen Van An" but not "Vandal"
        """
        key = self.search_var.get().strip()
        if not key:
            self.tree.selection_remove(*self.tree.selection())
            self.search_matches = []
            self.search_index = -1
            self.prev_btn.configure(state="disabled")
            self.next_btn.configure(state="disabled")
            return

        # Find all matching rows
        key_l = key.lower()
        matches = []
        for iid in self.tree.get_children():
            vals = self.tree.item(iid)["values"]

            # Always match exact student ID
            if str(vals[1]).lower() == key_l:
                matches.append(iid)
                continue

            # For names, split into tokens and match complete words only
            name = str(vals[2])
            name_tokens = [token.lower() for token in name.split()]

            # Check if search key matches any complete name token
            if key_l in name_tokens:
                matches.append(iid)

        if not matches:
            self.tree.selection_remove(*self.tree.selection())
            self.search_matches = []
            self.search_index = -1
            self.prev_btn.configure(state="disabled")
            self.next_btn.configure(state="disabled")
            messagebox.showinfo("Search", "Student not found.")
            return

        # Select first match and enable navigation if multiple matches
        self.search_matches = matches
        self.search_index = 0
        iid = self.search_matches[self.search_index]
        self.tree.selection_set(iid)
        self.tree.see(iid)

        if len(self.search_matches) > 1:
            self.prev_btn.configure(state="normal")
            self.next_btn.configure(state="normal")
        else:
            self.prev_btn.configure(state="disabled")
            self.next_btn.configure(state="disabled")

    def next_match(self):
        if not self.search_matches:
            return
        self.search_index = (self.search_index + 1) % len(self.search_matches)
        iid = self.search_matches[self.search_index]
        self.tree.selection_set(iid)
        self.tree.see(iid)

    def prev_match(self):
        if not self.search_matches:
            return
        self.search_index = (self.search_index - 1) % len(self.search_matches)
        iid = self.search_matches[self.search_index]
        self.tree.selection_set(iid)
        self.tree.see(iid)

    def load_file(self):
        p = filedialog.askopenfilename(
            title="Select Student File",
            initialdir=os.getcwd(),
            filetypes=[
                ("CSV files", "*.csv"),
                ("Excel files", "*.xlsx *.xlsm"),
                ("All files", "*.*")
            ]
        )
        if not p:
            return
        try:
            loaded_count = self.sm.load_from_file(p)
            # refresh view to new data and reset filters
            self.view_students = list(self.sm.students)
            self.is_filtered = False
            # reset any stored sort snapshots / states when loading new data
            self._sort_state = {c: None for c in ("no", "id", "name", "birth", "major", "gpa")}
            self._canon_snapshot = None
            self._view_snapshots.clear()
            # re-enable add button when not filtered
            try:
                self.add_btn.configure(state="normal")
            except Exception:
                pass
            self.refresh_table()
            if loaded_count:
                messagebox.showinfo("Load", f"Loaded {loaded_count} students from file.")
            else:
                messagebox.showinfo("Load", "Loaded file but no students were found.")
        except Exception as e:
            messagebox.showerror("Load Error", f"Failed to load file:\n{e}")

    def save(self, event=None):
        """Save to current manager filepath (students.csv by default)."""
        ok = self.sm.save()
        if ok:
            messagebox.showinfo("Save", "Saved successfully.")
        else:
            messagebox.showerror("Save", "Save failed. Check console for details.")
        self._update_status()

    def save_as(self):
        """
        Save As dialog — export to .csv or .xlsx.
        - For .csv uses utils.file_io.save_students (CSV 9-column).
        - For .xlsx uses openpyxl if available.
        On success updates SystemManager.filepath so future Save goes to this file.
        """
        f = filedialog.asksaveasfilename(
            title="Save As",
            initialdir=os.getcwd(),
            defaultextension=".csv",
            filetypes=[
                ("CSV file", "*.csv"),
                ("Excel workbook", "*.xlsx"),
                ("All files", "*.*"),
            ],
        )
        if not f:
            return

        try:
            if f.lower().endswith(".xlsx"):
                # export to xlsx
                try:
                    file_io.export_xlsx(f, self.sm.students)
                except ImportError:
                    messagebox.showerror("Save As", "openpyxl is required to export .xlsx.\nInstall with: pip install openpyxl")
                    return
            else:
                # default CSV
                ok = file_io.save_students(f, self.sm.students)
                if not ok:
                    messagebox.showerror("Save As", "Failed to save CSV. See console for details.")
                    return

            # update manager filepath so Save uses this file by default
            self.sm.filepath = f
            self.sm.filename = os.path.basename(f)
            self.sm.unsaved_changes = False
            self._update_status()
            messagebox.showinfo("Save As", "Export completed.")
        except Exception as e:
            messagebox.showerror("Save As Error", f"Failed to export file:\n{e}")

    # ---------- exit handling ----------
    def _on_close(self):
        """
        Handle window close event.
        Prompts to save if there are unsaved changes.
        """
        if self.sm.unsaved_changes:
            res = messagebox.askyesnocancel("Exit", "Save changes before exit?")
            if res is None:  # Cancel
                return
            if res:  # Yes
                if not self.sm.save():
                    messagebox.showerror("Save", "Save failed — cancel exit.")
                    return
        self.root.destroy()

    # ---------- Filter UI / logic ----------
    def open_filter_popup(self):
        """
        Open a popup that allows the user to enter multiple filter criteria.
        Supported filters:
         - First name (given name = last token of full name)
         - Birth year (single year or range '1990-1995')
         - Major (case-insensitive token match)
         - Subject scores (each subject: single number -> floor..floor+0.99, or range 'min-max')
         - GPA (same numeric behavior as subject scores)
        Multiple fields combine with logical AND.
        """
        popup = tk.Toplevel(self.root)
        popup.transient(self.root)
        popup.grab_set()
        popup.title("Filter Students")
        popup.geometry("650x500")
        popup.resizable(False, False)

        main_frame = ttk.Frame(popup, padding=16)
        main_frame.pack(fill="both", expand=True)

        # Styles
        section_font = ("Segoe UI", 12, "bold")
        label_font = ("Segoe UI", 10)
        entry_width = 25

        # Basic Info Section
        basic_frame = ttk.LabelFrame(main_frame, text="Basic Information", padding=10)
        basic_frame.pack(fill="x", padx=5, pady=(0, 10))

        # Grid for basic info
        ttk.Label(basic_frame, text="First name:", font=label_font).grid(row=0, column=0, sticky="e", padx=8, pady=6)
        first_var = tk.StringVar()
        ttk.Entry(basic_frame, textvariable=first_var, width=entry_width).grid(row=0, column=1, sticky="w", padx=8, pady=6)
        ttk.Label(basic_frame, text="(matches given name exactly)", font=("Segoe UI", 9)).grid(row=0, column=2, sticky="w", padx=4)

        ttk.Label(basic_frame, text="Birth year:", font=label_font).grid(row=1, column=0, sticky="e", padx=8, pady=6)
        birth_var = tk.StringVar()
        ttk.Entry(basic_frame, textvariable=birth_var, width=entry_width).grid(row=1, column=1, sticky="w", padx=8, pady=6)
        ttk.Label(basic_frame, text="(e.g., 1998 or 1990-1995)", font=("Segoe UI", 9)).grid(row=1, column=2, sticky="w", padx=4)

        ttk.Label(basic_frame, text="Major:", font=label_font).grid(row=2, column=0, sticky="e", padx=8, pady=6)
        major_var = tk.StringVar()
        ttk.Entry(basic_frame, textvariable=major_var, width=entry_width).grid(row=2, column=1, sticky="w", padx=8, pady=6)
        ttk.Label(basic_frame, text="(case-insensitive search)", font=("Segoe UI", 9)).grid(row=2, column=2, sticky="w", padx=4)

        # Scores Section
        scores_frame = ttk.LabelFrame(main_frame, text="Subject Scores", padding=10)
        scores_frame.pack(fill="x", padx=5, pady=(0, 10))

        ttk.Label(scores_frame, text="Enter single value (e.g., 8.5) or range (e.g., 7-9)", 
                  font=("Segoe UI", 9, "italic")).pack(anchor="w", padx=8, pady=(0, 8))

        subj_vars = {}
        for i, subj in enumerate(self.subjects):
            subj_frame = ttk.Frame(scores_frame)
            subj_frame.pack(fill="x", padx=4, pady=2)
            
            ttk.Label(subj_frame, text=f"{subj}:", font=label_font, width=10).pack(side="left", padx=(8, 4))
            v = tk.StringVar()
            ttk.Entry(subj_frame, textvariable=v, width=15).pack(side="left", padx=4)
            subj_vars[subj] = v

        # GPA Section
        gpa_frame = ttk.LabelFrame(main_frame, text="GPA Filter", padding=10)
        gpa_frame.pack(fill="x", padx=5, pady=(0, 16))

        ttk.Label(gpa_frame, text="GPA:", font=label_font).pack(side="left", padx=8)
        gpa_var = tk.StringVar()
        ttk.Entry(gpa_frame, textvariable=gpa_var, width=15).pack(side="left", padx=4)
        ttk.Label(gpa_frame, text="(single value or range, e.g., 3.0 or 2.5-3.5)", 
                  font=("Segoe UI", 9)).pack(side="left", padx=8)

        # Buttons
        btn_frame = ttk.Frame(main_frame)
        btn_frame.pack(fill="x", pady=(0, 8))


        def do_apply(event=None):
            # Build criteria dict
            criteria = {}
            fn = first_var.get().strip()
            if fn:
                criteria["first_name"] = fn.lower()
            by = self.parse_year_range(birth_var.get())
            if by:
                criteria["birth_year"] = by
            mj = major_var.get().strip()
            if mj:
                criteria["major"] = mj.lower()

            subj_criteria = {}
            for subj, var in subj_vars.items():
                r = self.parse_numeric_range(var.get())
                if r:
                    subj_criteria[subj] = r
            if subj_criteria:
                criteria["subjects"] = subj_criteria

            gpa_r = self.parse_numeric_range(gpa_var.get())
            if gpa_r:
                criteria["gpa"] = gpa_r

            # Apply filter
            self.apply_filter(criteria)
            popup.destroy()

        ttk.Button(btn_frame, text="Apply Filter", command=do_apply, 
                   style="Accent.TButton", width=15).pack(side="left", padx=(8, 4))
        ttk.Button(btn_frame, text="Cancel", command=popup.destroy, 
                   width=15).pack(side="left", padx=4)

        # Key bindings
        popup.bind("<Return>", do_apply)
        popup.bind("<Escape>", lambda e: popup.destroy())

        # Center popup on main window
        popup.update_idletasks()
        x = self.root.winfo_x() + (self.root.winfo_width() - popup.winfo_width()) // 2
        y = self.root.winfo_y() + (self.root.winfo_height() - popup.winfo_height()) // 2
        popup.geometry(f"+{x}+{y}")

    def apply_filter(self, criteria: dict):
        """
        Filter self.sm.students according to criteria and set self.view_students.

        criteria keys:
         - first_name: lowercase string that must match given name (last token)
         - birth_year: (min_year, max_year) inclusive
         - major: lowercase substring or token to match in major
         - subjects: dict {subject: (lo, hi)}
         - gpa: (lo, hi)
        All criteria combine with AND.
        """
        def matches(s: Student) -> bool:
            # first name (exact token match of last token)
            fn = criteria.get("first_name")
            if fn:
                parts = [p for p in (s.name or "").split() if p]
                given = parts[-1].lower() if parts else ""
                if given != fn:
                    return False

            # birth year
            by = criteria.get("birth_year")
            if by:
                if not (by[0] <= (s.birth_year or 0) <= by[1]):
                    return False

            # major
            mj = criteria.get("major")
            if mj:
                if mj not in (s.major or "").lower():
                    return False

            # subjects
            subs = criteria.get("subjects", {})
            for subj, (lo, hi) in subs.items():
                val = float(s.get_score(subj))
                if not (lo <= val <= hi):
                    return False

            # gpa
            gpa_r = criteria.get("gpa")
            if gpa_r:
                g = float(s.gpa)
                if not (gpa_r[0] <= g <= gpa_r[1]):
                    return False

            return True

        # If no criteria provided, clear filter.
        if not criteria:
            self.clear_filter()
            return

        filtered = [s for s in self.sm.students if matches(s)]
        self.view_students = filtered
        self.is_filtered = True
        # disable adding while filtered (user requested)
        try:
            self.add_btn.configure(state="disabled")
        except Exception:
            pass
        self.refresh_table()

    def clear_filter(self):
        """Reset view to all students and refresh table."""
        self.view_students = list(self.sm.students)
        self.is_filtered = False
        try:
            self.add_btn.configure(state="normal")
        except Exception:
            pass
        self.refresh_table()

    def parse_year_range(self, text: str):
        """Parse birth year input -> (min_year, max_year) or None."""
        t = text.strip()
        if not t:
            return None
        if "-" in t:
            parts = t.split("-", 1)
            try:
                lo = int(parts[0].strip())
                hi = int(parts[1].strip())
                return (min(lo, hi), max(lo, hi))
            except Exception:
                return None
        else:
            try:
                y = int(t)
                return (y, y)
            except Exception:
                return None

    def parse_numeric_range(self, text: str):
        """Parse single numeric or range 'min-max'."""
        t = text.strip()
        if not t:
            return None
        if "-" in t:
            parts = t.split("-", 1)
            try:
                a = float(parts[0].strip())
                b = float(parts[1].strip())
                lo = min(a, b)
                hi = max(a, b) + 0.99
                return (lo, hi)
            except Exception:
                return None
        else:
            try:
                v = float(t)
                lo = math.floor(v)
                hi = lo + 0.99
                return (float(lo), float(hi))
            except Exception:
                return None

def main():
    root = tk.Tk()
    app = StudentApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()