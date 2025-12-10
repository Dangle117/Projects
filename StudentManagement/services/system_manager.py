from typing import List, Optional, Dict
from pathlib import Path
from models.student import Student
from utils import file_io
from algorithms.TimSort import (sort_students, gpa_key, name_key,
                                birth_year_key, id_key, major_key)

class SystemManager:
    """
    High-level manager for Student objects.

    Responsibilities:
    - Maintain canonical list self.students (order matters for Save/SaveAs and canonical view).
    - Maintain an O(1) lookup cache self._index mapping student_id -> Student for fast operations.
    - Provide CRUD ops (add/update/delete), score updates, file load/save, and convenience sorting wrappers.

    Behavior notes / edge-cases:
    - add_student raises ValueError if ID already exists.
    - delete_student rebuilds the index after removal.
    - Sorting helpers call the algorithms.TimSort wrapper and then rebuild the index to keep lookups consistent.
    - load_from_file replaces the entire canonical list (no merge).
    """

    def __init__(self, filename: str = "students.csv"):
        """
        Initialize SystemManager.

        - filename: default data file path (relative paths resolved to cwd). Default changed to students.csv.
        - Loads students from file (if present) into self.students.
        - Builds self._index for fast id lookups.
        """
        self.filename = str(filename)
        p = Path(self.filename)
        if not p.is_absolute():
            p = Path.cwd() / p
        self.filepath = str(p)

        # Load students from disk into a Python list. Each element is a Student instance.
        self.students: List[Student] = file_io.load_students(self.filepath) or []

        # Cached index mapping student_id -> Student object for O(1) retrieval.
        self._index: Dict[str, Student] = {}
        self._build_index()

        # Flag indicating whether in-memory data differs from file on disk.
        self.unsaved_changes = False

    def _build_index(self) -> None:
        """
        Rebuild the id -> Student cache from current students list.

        This creates a new dict so that if self.students changes (replace or reorder),
        the cache is consistent. The dict stores references to the Student objects,
        not copies, so modifying a Student via either structure affects the same object.
        """
        self._index = {s.student_id: s for s in self.students}

    def _exists_id(self, student_id: str) -> bool:
        """Return True if student_id exists in cached index."""
        return student_id in self._index

    def add_student(self, student: Student):
        """
        Append a new Student to the list and update the cache.

        Raises:
            ValueError if a student with the same ID already exists.
        """
        if self._exists_id(student.student_id):
            raise ValueError(f"Student with ID '{student.student_id}' already exists")
        self.students.append(student)
        # Keep cache updated incrementally to avoid full rebuild.
        self._index[student.student_id] = student
        self.unsaved_changes = True

    def delete_student(self, student_id: str) -> bool:
        """
        Remove a student by ID.

        Returns True if a student was removed, False if not found.
        After removal we rebuild the cache to ensure consistency.
        """
        before = len(self.students)
        self.students = [s for s in self.students if s.student_id != student_id]
        changed = len(self.students) != before
        if changed:
            # Rebuild cache from updated list. Fast for typical class sizes.
            self._build_index()
            self.unsaved_changes = True
        return changed

    def find_by_id(self, student_id: str) -> Optional[Student]:
        """
        O(1) lookup for Student by ID using the cached index.

        Returns:
            Student instance or None if not found.
        """
        return self._index.get(student_id)

    def update_student(self, student_id: str, name: Optional[str] = None, birth_year: Optional[int] = None,
                       major: Optional[str] = None) -> bool:
        """
        Update basic profile fields of a Student.

        Returns True when update succeeds, False if student not found.
        """
        s = self.find_by_id(student_id)
        if not s:
            return False
        s.update_info(name, birth_year, major)
        self.unsaved_changes = True
        return True

    def add_score(self, student_id: str, subject: str, score: float) -> bool:
        """
        Set a score for a student (subject name -> numeric score).

        Returns True on success, False when student not found.
        """
        s = self.find_by_id(student_id)
        if not s:
            return False
        s.add_score(subject, score)
        self.unsaved_changes = True
        return True

    # Sorting helpers: delegate to algorithms.TimSort functions with key extractors.
    def sort_by_gpa(self):
        """Sort students in-place by GPA descending (highest first)."""
        sort_students(self.students, key=gpa_key, reverse=True)
        # Rebuild index because order changed (index maps by id to object; order change doesn't affect mapping,
        # but rebuild keeps semantics consistent if code relies on index rebuild timing).
        self._build_index()

    def sort_by_name(self):
        """Sort students in-place by name (case-insensitive)."""
        sort_students(self.students, key=name_key)
        self._build_index()

    def sort_by_birth_year(self):
        """Sort students in-place by birth year (ascending)."""
        sort_students(self.students, key=birth_year_key)
        self._build_index()
    
    def sort_by_id(self):
        """Sort students in-place by student_id (lexicographic)."""
        sort_students(self.students, key=id_key)
        self._build_index()
    
    def sort_by_major(self):
        """Sort students in-place by major (case-insensitive)."""
        sort_students(self.students, key=major_key)
        self._build_index()

    def change_student_id(self, old_id: str, new_id: str) -> bool:
        """
        Change a student's ID.
        Returns True if changed, False if old_id not found or new_id already exists.
        """
        if old_id == new_id:
            return True
        if new_id in self._index:
            return False
        s = self.find_by_id(old_id)
        if not s:
            return False
        # update id on the Student object, then rebuild index
        s.student_id = new_id
        self._build_index()
        self.unsaved_changes = True
        return True

    def save(self) -> bool:
        """
        Save students to disk via utils.file_io.save_students.
        Returns True on success; resets unsaved_changes flag.
        """
        ok = file_io.save_students(self.filepath, self.students)
        if ok:
            self.unsaved_changes = False
        return ok

    def load_from_file(self, filename: str) -> int:
        """
        Replace current student list with contents loaded from filename.

        - Loads via utils.file_io.load_students
        - Rebuilds cached index
        - Marks state as saved (unsaved_changes = False)

        Returns: number of students loaded.
        """
        loaded = file_io.load_students(filename) or []
        p = Path(filename)
        if not p.is_absolute():
            p = Path.cwd() / p
        self.filepath = str(p)
        # replace current students (do not merge)
        self.students = loaded
        # Rebuild cache for O(1) lookups
        self._build_index()
        self.unsaved_changes = False
        return len(self.students)

