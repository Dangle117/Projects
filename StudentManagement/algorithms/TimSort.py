from models.student import Student
from typing import List, Callable, Any, TypeVar, Tuple
import unicodedata

T = TypeVar('T')  # Generic type for items to sort
MIN_MERGE = 32

"""
TimSort (simplified) implementation.

Module summary:
- tim_sort: a small stable in-place sort implementation (insertion + merge) used as a wrapper.
- sort_students: convenience wrapper used by SystemManager.
- key helpers: gpa_key, name_key, birth_year_key, id_key, major_key.

Notes:
- This is a simplified TimSort-like approach (runs of min_run sorted by insertion, then merged).
- name_key implements an approximate Vietnamese-aware ordering:
  primary ordering uses a small custom VN_LETTERS list and considers breve/circumflex/horn modifiers;
  secondary ordering takes combining tone marks into account.
  The key returns tuples suitable for Python's lexicographic comparison.
"""

# Vietnamese letters in desired sort order (distinct letters include ă, â, đ, ê, ô, ơ, ư)
VN_LETTERS = [
    "a", "ă", "â", "b", "c", "d", "đ", "e", "ê", "g", "h",
    "i", "k", "l", "m", "n", "o", "ô", "ơ", "p", "q", "r",
    "s", "t", "u", "ư", "v", "x", "y"
]

# Mapping of combining tone diacritics (NFD) to tone order
# 0 = no tone (ngang), 1 = huyền (`\u0300`), 2 = hỏi (`\u0309`), 3 = ngã (`\u0303`),
# 4 = sắc (`\u0301`), 5 = nặng (`\u0323`)
TONE_MARKS_ORDER = {
    "\u0300": 1,  # huyền (grave)
    "\u0309": 2,  # hỏi (hook above)
    "\u0303": 3,  # ngã (tilde)
    "\u0301": 4,  # sắc (acute)
    "\u0323": 5,  # nặng (dot below)
}

# Unicode combining marks used to detect letter variants
COMBINING_BREVE = "\u0306"   # ă (a + breve)
COMBINING_CIRCUMFLEX = "\u0302"  # â, ê, ô (base + circumflex)
COMBINING_HORN = "\u031B"    # ơ, ư (base + horn)


def get_min_run(n: int) -> int:
    """Return a minimum run length for the given array size (heuristic)."""
    r = 0
    while n >= MIN_MERGE:
        r |= n & 1
        n >>= 1
    return n + r


def insertion_sort(arr: List[T], left: int, right: int, key: Callable[[T], Any]) -> None:
    """Sort a small subarray in-place using insertion sort and the provided key extractor."""
    for i in range(left + 1, right + 1):
        j = i
        while j > left and key(arr[j]) < key(arr[j - 1]):
            arr[j], arr[j - 1] = arr[j - 1], arr[j]
            j -= 1


def merge(arr: List[T], l: int, m: int, r: int, key: Callable[[T], Any]) -> None:
    """Merge two adjacent sorted subarrays [l..m] and [m+1..r] in-place using temporary buffers."""
    len1, len2 = m - l + 1, r - m
    left = arr[l:l + len1]
    right = arr[m + 1:m + 1 + len2]

    i, j, k = 0, 0, l

    while i < len1 and j < len2:
        if key(left[i]) <= key(right[j]):
            arr[k] = left[i]
            i += 1
        else:
            arr[k] = right[j]
            j += 1
        k += 1

    # copy remaining elements
    while i < len1:
        arr[k] = left[i]
        k += 1
        i += 1

    while j < len2:
        arr[k] = right[j]
        k += 1
        j += 1


def tim_sort(arr: List[T], key: Callable[[T], Any], reverse: bool = False) -> None:
    """
    Sort arr in-place by the provided key function.

    Args:
      arr: list to sort in-place
      key: function(item) -> comparable value
      reverse: if True, final list is reversed (descending order)
    """
    n = len(arr)
    if n < 2:
        if reverse:
            arr.reverse()
        return

    min_run = get_min_run(n)
    if min_run < 1:
        min_run = 1

    # Create and sort runs using insertion sort
    for start in range(0, n, min_run):
        end = min(start + min_run - 1, n - 1)
        insertion_sort(arr, start, end, key)

    # Iteratively merge runs
    size = min_run
    while size < n:
        for left in range(0, n, 2 * size):
            mid = min(n - 1, left + size - 1)
            right = min(n - 1, left + 2 * size - 1)
            if mid < right:
                merge(arr, left, mid, right, key)
        size *= 2

    if reverse:
        arr.reverse()


def sort_students(students: List["Student"], key: Callable[["Student"], Any], reverse: bool = False) -> None:
    """Public wrapper used by SystemManager to sort student lists using the specified key."""
    tim_sort(students, key, reverse)


# -----------------------
# Vietnamese-aware name key
# -----------------------

def _char_vietnamese_key(ch: str) -> Tuple[int, int]:
    """
    Convert a single Unicode character into a vietnamese ordering key:
    - primary: index in VN_LETTERS (accounts for breve/circumflex/horn etc.)
    - secondary: tone order integer (0..5) where 0 means no tone (ngang)
    """
    if not ch:
        # unknown/empty character -> place after usual letters
        return (len(VN_LETTERS) + ord('?'), 0)

    ch_lower = ch.lower()
    # Normalize NFD to separate base + combining marks
    nfd = unicodedata.normalize("NFD", ch_lower)
    base = nfd[0]
    comps = set(nfd[1:])  # combining chars

    # Determine tone mark if present (choose first matching combining tone)
    tone = 0
    for mark, order in TONE_MARKS_ORDER.items():
        if mark in comps:
            tone = order
            break

    # Determine primary letter considering modifiers
    # a -> a, ă, â
    if base == "a":
        if COMBINING_BREVE in comps:
            letter = "ă"
        elif COMBINING_CIRCUMFLEX in comps:
            letter = "â"
        else:
            letter = "a"
    elif base == "e":
        if COMBINING_CIRCUMFLEX in comps:
            letter = "ê"
        else:
            letter = "e"
    elif base == "o":
        if COMBINING_CIRCUMFLEX in comps:
            letter = "ô"
        elif COMBINING_HORN in comps:
            letter = "ơ"
        else:
            letter = "o"
    elif base == "u":
        if COMBINING_HORN in comps:
            letter = "ư"
        else:
            letter = "u"
    elif base == "d":
        # handle đ specially (precomposed 'đ' or 'Đ')
        if ch_lower == "đ" or "\u0111" in nfd:  # '\u0111' is latin small letter d with stroke
            letter = "đ"
        else:
            letter = "d"
    else:
        # other letters map to their base letter if present in VN_LETTERS
        if base in VN_LETTERS:
            letter = base
        else:
            # unknown characters go after defined letters but use their unicode ord for deterministic order
            return (len(VN_LETTERS) + ord(base), tone)

    # Map to index
    try:
        idx = VN_LETTERS.index(letter)
    except ValueError:
        # fallback: place unknown after known letters
        idx = len(VN_LETTERS) + ord(letter)
    return (idx, tone)


def _token_vietnamese_key(token: str) -> Tuple[Tuple[int, ...], Tuple[int, ...]]:
    """
    Return a pair of tuples describing the token:
    - tuple of primary letter indexes (per character)
    - tuple of tone orders (per character)

    These two tuples are used for lexicographic comparison:
    first compare primary letter indexes; if equal, compare tone tuples.
    """
    primaries = []
    tones = []
    for ch in token:
        idx, tone = _char_vietnamese_key(ch)
        primaries.append(idx)
        tones.append(tone)
    return (tuple(primaries), tuple(tones))


def gpa_key(student: "Student") -> float:
    """Return student's GPA for numeric comparison."""
    return student.gpa


def name_key(student: "Student"):
    """
    Vietnamese-aware name key.

    Sorting behavior:
    - Primary: given/first name (last token in the full name) using Vietnamese alphabet order.
    - Secondary: if given names have identical primary letter sequence, compare tone marks per character.
    - Tertiary: use full lower-cased name as a final tie-breaker (stable deterministic).
    - Returns a tuple suitable for Python sorting.
    """
    full = (student.name or "").strip()
    if not full:
        return ((), (), "")

    parts = [p for p in full.split() if p]
    # use last token as "given/first name" in Vietnamese order
    given = parts[-1] if parts else full
    given_prim, given_tones = _token_vietnamese_key(given)
    # include full normalized lowercase name as last tiebreaker
    return (given_prim, given_tones, full.lower())


def birth_year_key(student: "Student") -> int:
    """Return student's birth year as int."""
    return student.birth_year


def id_key(student: "Student") -> str:
    """Return student's id (string)."""
    return student.student_id


def major_key(student: "Student") -> str:
    """Return student's major lowercased for case-insensitive comparison."""
    return student.major.lower()