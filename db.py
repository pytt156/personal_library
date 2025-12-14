import sqlite3
from pathlib import Path
from typing import List, Optional

from models import Book

DB_PATH = Path("data/library.db")


def get_connection() -> sqlite3.Connection:
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db() -> None:
    with get_connection() as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS books
            (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title VARCHAR NOT NULL,
            author VARCHAR,
            year INTEGER,
            isbn VARCHAR,
            notes VARCHAR
            );
            """
        )


def insert_book(book: Book) -> int:
    with get_connection() as conn:
        cursor = conn.execute(
            """
            INSERT INTO books (title, author, year, isbn, notes)
            VALUES (?,?,?,?,?)
            """,
            (book.title, book.author, book.year, book.isbn, book.notes),
        )
        return cursor.lastrowid


def row_to_book(row: sqlite3.row) -> Book:
    return Book(
        id=row["id"],
        title=row["title"],
        author=row["author"],
        year=row["year"],
        isbn=row["isbn"],
        notes=row["notes"],
    )


def get_all_books() -> List[Book]:
    with get_connection() as conn:
        rows = conn.execute("SELECT * FROM books").fetchall()
        return [row_to_book(row) for row in rows]


def delete_book(book_id: int) -> None:
    with get_connection() as conn:
        conn.execute("DELETE FROM books WHERE id = ?", (book_id,))
