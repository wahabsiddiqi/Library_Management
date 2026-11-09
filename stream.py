import json
import random
import string
from datetime import datetime
from pathlib import Path

import pandas as pd
import streamlit as st

DATABASE = Path("library.json")
NOW = lambda: datetime.now().strftime("%Y-%m-%d %H:%M:%S")

st.set_page_config(page_title="Library Management System", page_icon="📚", layout="wide")


# ---------- Data layer (same library.json format as your terminal project) ----------
def load_data():
    default = {"books": [], "members": []}
    if DATABASE.exists():
        content = DATABASE.read_text().strip()
        if content:
            return json.loads(content)
    DATABASE.write_text(json.dumps(default, indent=4))
    return default


def save_data():
    DATABASE.write_text(json.dumps(st.session_state.data, indent=4, default=str))


def gen_id(prefix="B"):
    existing = {b["id"] for b in st.session_state.data["books"]} | {
        m["id"] for m in st.session_state.data["members"]
    }
    while True:
        new_id = prefix + "-" + "".join(
            random.choices(string.ascii_uppercase + string.digits, k=5)
        )
        if new_id not in existing:
            return new_id


if "data" not in st.session_state:
    st.session_state.data = load_data()

data = st.session_state.data


# ---------- Actions ----------
def add_book(title, author, copies):
    data["books"].append(
        {
            "id": gen_id("B"),
            "title": title.strip(),
            "author": author.strip(),
            "total_copies": int(copies),
            "available_copies": int(copies),
            "added_on": NOW(),
        }
    )
    save_data()


def add_member(name, email):
    data["members"].append(
        {"id": gen_id("M"), "name": name.strip(), "email": email.strip(), "borrowed": []}
    )
    save_data()


def borrow_book(member, book):
    if book["available_copies"] <= 0:
        return False
    member["borrowed"].append(
        {"book_id": book["id"], "title": book["title"], "borrow_on": NOW()}
    )
    book["available_copies"] -= 1
    save_data()
    return True


def return_book(member, index):
    selected = member["borrowed"].pop(index)
    for b in data["books"]:
        if b["id"] == selected["book_id"]:
            b["available_copies"] += 1
            break
    save_data()
    return selected


# ---------- Sidebar navigation ----------
st.sidebar.title("📚 Library")
page = st.sidebar.radio(
    "Menu",
    ["Dashboard", "Books", "Members", "Borrow Book", "Return Book"],
)
st.sidebar.divider()
st.sidebar.caption(f"{len(data['books'])} books · {len(data['members'])} members")

# helper labels for selectboxes
book_label = lambda b: f"{b['title']} — {b['author']} ({b['available_copies']} available) [{b['id']}]"
member_label = lambda m: f"{m['name']} [{m['id']}]"


# ---------- Pages ----------
if page == "Dashboard":
    st.title("Library Management System")
    total_copies = sum(b["total_copies"] for b in data["books"])
    available = sum(b["available_copies"] for b in data["books"])
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Book titles", len(data["books"]))
    c2.metric("Total copies", total_copies)
    c3.metric("Currently borrowed", total_copies - available)
    c4.metric("Members", len(data["members"]))

    st.subheader("Recently borrowed")
    rows = [
        {"Member": m["name"], "Book": b["title"], "Borrowed on": b["borrow_on"]}
        for m in data["members"]
        for b in m["borrowed"]
    ]
    if rows:
        df = pd.DataFrame(rows).sort_values("Borrowed on", ascending=False)
        st.dataframe(df, use_container_width=True, hide_index=True)
    else:
        st.info("No books are borrowed right now.")

elif page == "Books":
    st.title("Books")
    tab_list, tab_add = st.tabs(["All books", "Add book"])

    with tab_list:
        if not data["books"]:
            st.info("No books available in the library. Add one from the 'Add book' tab.")
        else:
            search = st.text_input("Search by title or author")
            df = pd.DataFrame(data["books"])
            if search:
                mask = df["title"].str.contains(search, case=False) | df["author"].str.contains(
                    search, case=False
                )
                df = df[mask]
            df = df.rename(
                columns={
                    "id": "ID",
                    "title": "Title",
                    "author": "Author",
                    "total_copies": "Total",
                    "available_copies": "Available",
                    "added_on": "Added on",
                }
            )
            st.dataframe(df, use_container_width=True, hide_index=True)

    with tab_add:
        with st.form("add_book_form", clear_on_submit=True):
            title = st.text_input("Book title")
            author = st.text_input("Author")
            copies = st.number_input("Copies", min_value=1, value=1, step=1)
            if st.form_submit_button("Add book"):
                if not title.strip() or not author.strip():
                    st.error("Title and author are required.")
                else:
                    add_book(title, author, copies)
                    st.success(f"Added '{title}'.")

elif page == "Members":
    st.title("Members")
    tab_list, tab_add = st.tabs(["All members", "Add member"])

    with tab_list:
        if not data["members"]:
            st.info("No members available in the library. Add one from the 'Add member' tab.")
        else:
            for m in data["members"]:
                with st.expander(f"{m['name']} · {m['email']} · {len(m['borrowed'])} borrowed [{m['id']}]"):
                    if m["borrowed"]:
                        st.dataframe(
                            pd.DataFrame(m["borrowed"]).rename(
                                columns={
                                    "book_id": "Book ID",
                                    "title": "Title",
                                    "borrow_on": "Borrowed on",
                                }
                            ),
                            use_container_width=True,
                            hide_index=True,
                        )
                    else:
                        st.write("No borrowed books.")

    with tab_add:
        with st.form("add_member_form", clear_on_submit=True):
            name = st.text_input("Member name")
            email = st.text_input("Member email")
            if st.form_submit_button("Add member"):
                if not name.strip() or "@" not in email:
                    st.error("Enter a name and a valid email.")
                else:
                    add_member(name, email)
                    st.success(f"Added member '{name}'.")

elif page == "Borrow Book":
    st.title("Borrow a book")
    if not data["members"] or not data["books"]:
        st.warning("You need at least one member and one book first.")
    else:
        member = st.selectbox("Member", data["members"], format_func=member_label)
        available_books = [b for b in data["books"] if b["available_copies"] > 0]
        if not available_books:
            st.warning("Sorry, no books are currently available.")
        else:
            book = st.selectbox("Book", available_books, format_func=book_label)
            if st.button("Borrow", type="primary"):
                if borrow_book(member, book):
                    st.success(f"{member['name']} borrowed '{book['title']}'.")
                else:
                    st.error("Sorry, this book is currently not available.")

elif page == "Return Book":
    st.title("Return a book")
    members_with_books = [m for m in data["members"] if m["borrowed"]]
    if not members_with_books:
        st.info("No member has borrowed any book right now.")
    else:
        member = st.selectbox("Member", members_with_books, format_func=member_label)
        idx = st.selectbox(
            "Borrowed book",
            range(len(member["borrowed"])),
            format_func=lambda i: f"{member['borrowed'][i]['title']} "
            f"(ID: {member['borrowed'][i]['book_id']}, since {member['borrowed'][i]['borrow_on']})",
        )
        if st.button("Return", type="primary"):
            selected = return_book(member, idx)
            st.success(f"'{selected['title']}' returned by {member['name']}.")
            st.rerun()