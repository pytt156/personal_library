from pathlib import Path
import pandas as pd

from models import create_book
import db


COLUMN_MAP = {
    "titel": "title",
    "författare": "author",
    "år": "year",
    "isbn": "isbn",
    "anteckningar": "notes",
}

def normalize_columns(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df.columns = [c.strip().lower() for c in df.columns]

    renamed = {}
    for col in df.columns:
        if col in COLUMN_MAP:
            renamed[col] = COLUMN_MAP[col]

    return df.rename(columns=renamed)



def import_excel(file_path: Path) -> int:
    sheets = pd.read_excel(file_path, sheet_name=None)

    inserted = 0

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
                    collection=sheet_name,
                )
                db.insert_book(book)
                inserted += 1
            except ValueError:
                continue

    return inserted


if __name__ == "__main__":
    db.init_db()
    count = import_excel(Path("example.xlsx"))
    print(f"Imported {count} books")
