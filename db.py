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
        conn.executescript(
            """
            CREATE TABLE IF NOT EXISTS books (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                author TEXT,
                year INTEGER,
                isbn TEXT,
                notes TEXT,
                genre TEXT,
                format TEXT,
                last_read TEXT
            );

            CREATE TABLE IF NOT EXISTS collections (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT UNIQUE
            );

            CREATE TABLE IF NOT EXISTS book_collections (
                book_id INTEGER,
                collection_id INTEGER,
                UNIQUE(book_id, collection_id)
            );
            """
        )


def get_book_id(
    title: str, author: Optional[str], year: Optional[int]
) -> Optional[int]:
    with get_connection() as conn:
        row = conn.execute(
            """
            SELECT id
            FROM books
            WHERE title = ?
              AND (author IS ? OR author = ?)
              AND (year IS ? OR year = ?)
            LIMIT 1
            """,
            (title, author, author, year, year),
        ).fetchone()

        return row["id"] if row else None


def insert_book(book: Book) -> int:
    with get_connection() as conn:
        cur = conn.execute(
            """
            INSERT INTO books (
                title, author, year, isbn, notes, genre, format, last_read
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                book.title,
                book.author,
                book.year,
                book.isbn,
                book.notes,
                book.genre,
                book.format,
                book.last_read,
            )
        )
        return cur.lastrowid


def get_or_create_collection(name: str) -> int:
    with get_connection() as conn:
        row = conn.execute(
            "SELECT id FROM collections WHERE name = ?",
            (name,),
        ).fetchone()

        if row:
            return row["id"]

        cur = conn.execute(
            "INSERT INTO collections (name) VALUES (?)",
            (name,),
        )
        return cur.lastrowid


def link_book_to_collection(book_id: int, collection_id: int) -> None:
    with get_connection() as conn:
        conn.execute(
            """
            INSERT OR IGNORE INTO book_collections (book_id, collection_id)
            VALUES (?, ?)
            """,
            (book_id, collection_id),
        )


def row_to_book(row: sqlite3.Row) -> Book:
    return Book(
        id=row["id"],
        title=row["title"],
        author=row["author"],
        year=row["year"],
        isbn=row["isbn"],
        notes=row["notes"],
        genre=row["genre"],
        format=row["format"],
        last_read=row["last_read"]
    )

def get_all_books() -> List[Book]:
    with get_connection() as conn:
        rows = conn.execute("SELECT * FROM books").fetchall()
        return [row_to_book(row) for row in rows]


def delete_book(book_id: int) -> None:
    with get_connection() as conn:
        conn.execute("DELETE FROM books WHERE id = ?", (book_id,))

def get_books_with_primary_collection():
    with get_connection() as conn:
        rows = conn.execute(
            """
            SELECT
                b.id,
                b.title,
                b.author,
                b.year,
                b.isbn,
                b.notes,
                b.genre,
                b.format,
                b.last_read,
                COALESCE(
                    MIN(CASE WHEN c.name != 'alla' THEN c.name END),
                    MIN(c.name)
                ) AS primary_collection
            FROM books b
            LEFT JOIN book_collections bc ON bc.book_id = b.id
            LEFT JOIN collections c ON c.id = bc.collection_id
            GROUP BY b.id
            ORDER BY b.title
            """
        ).fetchall()

        return rows
