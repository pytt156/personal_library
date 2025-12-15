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

books = db.get_all_books()

if query:
    books = [
        b
        for b in books
        if query in b.title.lower()
        or (b.author and query in b.author.lower())
    ]

for book in books:
    cols = st.columns([3, 3, 1, 2, 2, 1])
    cols[0].write(book.title)
    cols[1].write(book.author or "")
    cols[2].write(book.year or "")
    cols[3].write(book.collection or "")
    cols[4].write(book.notes or "")


    if cols[5].button("Delete", key=f"del_{book.id}"):
        db.delete_book(book.id)
        st.rerun()