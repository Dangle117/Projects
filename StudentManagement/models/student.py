from typing import Dict, Optional, List

class Student:
    """
    Student data model.

    Responsibilities:
    - store immutable id and editable fields: name, birth_year, major
    - maintain subject scores in a private dict (subject -> float)
    - compute GPA as arithmetic mean of DEFAULT_SUBJECTS scores
    - provide lightweight CSV-compatible serialization helpers (to_row / from_row)

    Notes / invariants:
    - DEFAULT_SUBJECTS defines the 4 expected subject columns in file I/O.
    - Scores and GPA are floats; scores are clamped at minimum 0.0 by set_score.
    - from_row attempts to be permissive for malformed input but will raise if student_id is missing.
    """

    DEFAULT_SUBJECTS: List[str] = ["CSI106", "PFP191", "MAD101", "MAE101"]

    def __init__(self, student_id: str, name: str, birth_year: int, major: str, gpa: float = 0.0):
        # Validate required id and normalize inputs
        if not student_id:
            raise ValueError("student_id is required")
        self.__student_id = str(student_id).strip()
        self.__name = str(name).strip() if name is not None else ""
        try:
            self.__birth_year = int(birth_year)
        except (TypeError, ValueError):
            self.__birth_year = 0
        self.__major = str(major).strip() if major is not None else ""
        try:
            self.__gpa = float(gpa)
        except (TypeError, ValueError):
            self.__gpa = 0.0

        # Private scores dict: subject -> float
        # Initialized with DEFAULT_SUBJECTS set to 0.0 so UI can show consistent columns.
        self.__scores: Dict[str, float] = {subj: 0.0 for subj in self.DEFAULT_SUBJECTS}

    # --- properties ---
    @property
    def student_id(self) -> str:
        """Return the unique student identifier (string)."""
        return self.__student_id

    @property
    def name(self) -> str:
        """Return student's name."""
        return self.__name

    @property
    def birth_year(self) -> int:
        """Return birth year as int (0 if unknown/invalid)."""
        return self.__birth_year

    @property
    def major(self) -> str:
        """Return major field (string)."""
        return self.__major

    @property
    def gpa(self) -> float:
        """Return the computed GPA (float)."""
        return float(self.__gpa)

    @property
    def scores(self) -> Dict[str, float]:
        """Return a shallow copy of the scores dict to prevent external mutation of internals."""
        return dict(self.__scores)

    # convenience getter
    def get_score(self, subject: str) -> float:
        """Return numeric score for subject, default 0.0 when missing."""
        return float(self.__scores.get(subject, 0.0))

    # convenience setter (keeps GPA recalculated)
    def set_score(self, subject: str, score: float):
        """
        Set a numeric score for a subject and recalculate GPA.

        Raises ValueError for invalid subject or non-numeric score input.
        """
        if not subject:
            raise ValueError("Subject required")
        try:
            val = float(score)
        except (TypeError, ValueError):
            raise ValueError("Score must be a number")
        if val < 0:
            val = 0.0
        self.__scores[str(subject).strip()] = val
        self.__calculate_gpa()

    # --- operations ---
    def add_score(self, subject: str, score: float):
        """Alias to set_score for backward compatibility."""
        self.set_score(subject, score)

    def update_info(self, name: Optional[str] = None, birth_year: Optional[int] = None, major: Optional[str] = None):
        """Update profile fields (no validation beyond type conversion)."""
        if name is not None:
            self.__name = str(name).strip()
        if birth_year is not None:
            try:
                self.__birth_year = int(birth_year)
            except (TypeError, ValueError):
                pass
        if major is not None:
            self.__major = str(major).strip()

    def __calculate_gpa(self):
        """Compute GPA as mean of present scores; keep previous GPA if no scores exist."""
        if self.__scores:
            self.__gpa = sum(self.__scores.values()) / len(self.__scores)
        else:
            try:
                self.__gpa = float(self.__gpa)
            except (TypeError, ValueError):
                self.__gpa = 0.0

    # --- serialization helpers (CSV-friendly) ---
    def to_row(self) -> List[str]:
        """
        Return a CSV row (list of values) with 9 columns:
        [student_id, name, birth_year, major, subj1, subj2, subj3, subj4, gpa]
        Values are strings or numbers (csv.writer will convert/quote as needed).
        """
        subj_vals = [f"{self.get_score(s):.2f}" for s in self.DEFAULT_SUBJECTS]
        return [
            self.student_id,
            self.name,
            str(self.birth_year),
            self.major,
            *subj_vals,
            f"{self.gpa:.2f}"
        ]

    @classmethod
    def from_row(cls, row: List[str]):
        """
        Create Student from a CSV row (list-like).
        Accepts rows with >=9 elements; missing values are treated as empty/zero.
        Subject columns are mapped to DEFAULT_SUBJECTS in order.

        GPA handling:
        - If GPA column exists and all subject scores are zero: keep provided GPA
        - If GPA column exists but doesn't match calculated GPA: recalculate from scores
        - If GPA column missing: calculate from available subject scores
        - Missing subject scores default to 0.0
        """
        # ensure at least 9 elements
        cells = list(row) + [""] * max(0, 9 - len(row))
        sid = str(cells[0]).strip() if cells[0] is not None else ""
        name = str(cells[1]).strip() if cells[1] is not None else ""
        try:
            birth_i = int(cells[2]) if cells[2] not in (None, "") else 0
        except Exception:
            birth_i = 0
        major = str(cells[3]).strip() if cells[3] is not None else ""

        # subject columns are at positions 4..7
        subj_vals = []
        for i in range(4, 8):
            v = cells[i]
            try:
                subj_vals.append(float(v) if v not in (None, "") else 0.0)
            except Exception:
                subj_vals.append(0.0)

        # Get GPA from column 8 if present
        file_gpa = None
        try:
            if cells[8] not in (None, ""):
                file_gpa = float(cells[8])
        except Exception:
            file_gpa = None

        if not sid:
            raise ValueError("Missing student_id in row")

        # Create student with temporary 0 GPA
        student = cls(sid, name, birth_i, major, 0.0)
        
        # Set available subject scores (this will calculate initial GPA)
        for subj_name, val in zip(cls.DEFAULT_SUBJECTS, subj_vals):
            try:
                student.set_score(subj_name, val)
            except Exception:
                pass

        # GPA decision logic:
        if file_gpa is not None:
            # Calculate expected GPA from scores
            calculated_gpa = sum(student.get_score(s) for s in cls.DEFAULT_SUBJECTS) / len(cls.DEFAULT_SUBJECTS)
            
            # If all scores are 0 but file has GPA, use file's GPA
            if all(student.get_score(s) == 0.0 for s in cls.DEFAULT_SUBJECTS):
                student._Student__gpa = file_gpa
            # If calculated GPA doesn't match file (within rounding), use calculated
            elif abs(calculated_gpa - file_gpa) > 0.01:
                student._Student__gpa = calculated_gpa
            # Otherwise keep file GPA (they match within rounding)
            else:
                student._Student__gpa = file_gpa
        # If no GPA in file, the calculated one from set_score remains

        return student

    # legacy compatibility helpers (optional)
    def to_line(self, sep: str = ",") -> str:
        """Return a single CSV line (deprecated: prefer to_row + csv.writer)."""
        return ",".join(self.to_row()) + "\n"

    @classmethod
    def from_line(cls, line: str, sep: str = ","):
        """Parse a CSV line (deprecated: prefer from_row called with csv.reader row)."""
        parts = [p.strip() for p in line.strip().split(sep)]
        return cls.from_row(parts)

    def __str__(self):
        return f"{self.student_id},{self.name},{self.birth_year},{self.major},{self.gpa:.2f}"

    def __repr__(self):
        return f"<Student {self.student_id} {self.name!r}>"

