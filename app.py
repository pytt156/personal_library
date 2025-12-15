import streamlit as st
from pathlib import Path

import db
from models import create_book
from import_excel import import_excel

st.set_page_config(page_title="Personal Library", layout="wide")

db.init_db()

st.title("Personal Library")

with st.expander("Import Excel"):
    uploaded_file = st.file_uploader("Upload Excel file", type=["xlsx", "xls"])

    if uploaded_file is not None:
        temp_path = Path("data/_upload.xlsx")
        temp_path.parent.mkdir(exist_ok=True)
        temp_path.write_bytes(uploaded_file.read())

        try:
            count = import_excel(temp_path)
            st.success(f"Imported {count} books")
        except Exception as e:
            st.error(str(e))

with st.expander("Add book"):
    with st.form("add_book_form"):
        title = st.text_input("Title")
        author = st.text_input("Author")
        year = st.text_input("Year")
        isbn = st.text_input("ISBN")
        notes = st.text_input("Notes")
        genre = st.text_input("Genre")
        format = st.selectbox("Format", ["", "Inbunden", "Pocket", "E-bok"])
        last_read = st.text_input("Last read (YYYY-MM)")

        submitted = st.form_submit_button("Add")

        if submitted:
            try:
                book = create_book(
                    title=title,
                    author=author,
                    year=year,
                    isbn=isbn,
                    notes=notes
                )
                db.insert_book(book)
                st.success("Book added")
            except ValueError as e:
                st.error(str(e))

st.subheader("Library")

query = st.text_input("Search (title or author)").lower()

rows = db.get_books_with_primary_collection()

for row in rows:
    title = row["title"]
    author = row["author"] or ""
    year = row["year"] or ""
    collection = row["primary_collection"] or ""
    genre = row["genre"] or ""
    book_format = row["format"] or ""
    last_read = row["last_read"] or ""
    notes = row["notes"] or ""

    if query and query not in title.lower() and query not in author.lower():
        continue

    cols = st.columns([3, 3, 1, 2, 2, 2, 2, 2, 1])

    cols[0].write(title)
    cols[1].write(author)
    cols[2].write(year)
    cols[3].write(collection)
    cols[4].write(genre)
    cols[5].write(book_format)
    cols[6].write(last_read)
    cols[7].write(notes)

    if cols[8].button("Delete", key=f"del_{row['id']}"):
        db.delete_book(row["id"])
        st.rerun()
