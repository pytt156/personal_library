from dataclasses import dataclass
from typing import Optional


@dataclass
class Book:
    id: Optional[int]
    title: str
    author: Optional[str]
    year: Optional[int]
    isbn: Optional[str]
    notes: Optional[str]
    genre: Optional[str]
    format: Optional[str]
    last_read: Optional[str]

def normalize_str(value) -> Optional[str]:
    if value is None:
        return None

    if not isinstance(value, str):
        value = str(value)

    value = value.strip()
    return value if value else None


def parse_year(value) -> Optional[int]:
    if value in (None, "", "nan"):
        return None
    try:
        return int(value)
    except ValueError:
        return None

def create_book(
    *,
    title: str,
    author: Optional[str] = None,
    year=None,
    isbn: Optional[str] = None,
    notes: Optional[str] = None,
    genre: Optional[str] = None,
    format: Optional[str] = None,
    last_read: Optional[str] = None,
    book_id: Optional[int] = None,
) -> Book:
    title = normalize_str(title)
    if not title:
        raise ValueError("Book title is required")

    return Book(
        id=book_id,
        title=title,
        author=normalize_str(author),
        year=parse_year(year),
        isbn=normalize_str(isbn),
        notes=normalize_str(notes),
        genre=normalize_str(genre),
        format=normalize_str(format),
        last_read=normalize_str(last_read),
    )
