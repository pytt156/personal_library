from pathlib import Path
import pandas as pd

from models import create_book
import db


def normalize_columns(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df.columns = [c.strip().lower() for c in df.columns]
    return df


def import_excel(file_path: Path) -> int:
    df = pd.read_excel(file_path)
    df = normalize_columns(df)

    required = {"title"}
    if not required.issubset(df.columns):
        raise ValueError("Excelfiles must contain a 'title' column")

    inserted = 0

    for _, row in df.iterrows():
        try:
            book = create_book(
                title=row.get("title"),
                author=row.get("author"),
                year=row.get("year"),
                isbn=row.get("isbn"),
                notes=row.get("notes"),
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
