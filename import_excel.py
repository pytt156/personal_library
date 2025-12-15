from pathlib import Path
import pandas as pd

from models import create_book
import db


COLUMN_ALIASES = {
    "title": [
        "titel",
        "boktitel",
        "namn",
    ],
    "author": [
        "författare",
        "forfattare",
        "author",
        "upphov",
    ],
    "year": [
        "år",
        "ar",
        "utgivningsår",
        "year",
    ],
    "genre": [
        "genre",
        "typ",
        "kategori",
    ],
    "format": [
        "format",
        "form",
        "band",
        "inbunden/pocket",
    ],
    "last_read": [
        "senast läst",
        "senastlast",
        "last read",
    ],
    "isbn": [
        "isbn",
    ],
    "notes": [
        "anteckningar",
        "notering",
        "notes",
    ],
}

def normalize_header(value: str) -> str:
    return (
        value.strip()
        .lower()
        .replace("å", "a")
        .replace("ä", "a")
        .replace("ö", "o")
    )

def normalize_columns(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()

    normalized = {col: normalize_header(col) for col in df.columns}

    reverse_map = {}
    for internal, aliases in COLUMN_ALIASES.items():
        for alias in aliases:
            reverse_map[normalize_header(alias)] = internal

    renamed = {}
    for original, norm in normalized.items():
        if norm in reverse_map:
            renamed[original] = reverse_map[norm]

    return df.rename(columns=renamed)


def import_excel(file_path: Path) -> int:
    sheets = pd.read_excel(file_path, sheet_name=None)
    linked = 0

    for sheet_name, df in sheets.items():
        df = normalize_columns(df)

        if "title" not in df.columns:
            continue

        for _, row in df.iterrows():
            try:
                book = create_book(
                    title=row.get("title"),
                    author=row.get("author"),
                    year=row.get("year"),
                    isbn=row.get("isbn"),
                    notes=row.get("notes"),
                )

                book_id = db.get_book_id(
                    book.title,
                    book.author,
                    book.year,
                )

                if book_id is None:
                    book_id = db.insert_book(book)

                collection_id = db.get_or_create_collection(sheet_name)

                db.link_book_to_collection(book_id, collection_id)
                linked += 1

            except ValueError:
                continue

    return linked


if __name__ == "__main__":
    db.init_db()
    count = import_excel(Path("example.xlsx"))
    print(f"Imported {count} books")
