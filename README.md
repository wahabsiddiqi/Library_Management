# 📚 Library Management System

A web app for managing a small library: books, members, and borrowing/returning.
Originally a terminal-based Python project, now rebuilt with a **Streamlit** interface.

## Features

- **Dashboard**: total titles, copies, borrowed count, members, and recent borrowings
- **Books**: add books with multiple copies, list them, search by title or author
- **Members**: register members and see what each member has borrowed
- **Borrow / Return**: live availability tracking, only available books can be borrowed
- **Input validation**: required fields, email check, minimum copies
- **Persistent storage**: all data is saved to a local `library.json` file

## Screenshots

| Dashboard | Borrow Book |
|-----------|-------------|
| ![Dashboard](screenshots/dashboard.png) | ![Borrow](screenshots/borrow.png) |

## Tech Stack

- Python 3
- Streamlit (UI)
- Pandas (tables)
- JSON (storage)

## Run Locally

```bash
git clone https://github.com/wahabsiddiqi/Library_Management.git
cd Library_Management
pip install -r requirements.txt
streamlit run stream.py
```

On Windows, if `streamlit` is not recognized:

```powershell
py -m pip install -r requirements.txt
py -m streamlit run stream.py
```

The app opens at `http://localhost:8501`. `library.json` is created automatically on first run.

## How It Works

- Data lives in `st.session_state` and is written to `library.json` after every change.
- Streamlit reruns the script on each interaction, so state is kept in the session instead of plain variables.
- Each book and member gets a unique generated ID (e.g. `B-4F9K2`, `M-7XQ1A`).

## Roadmap

- [ ] Delete / edit books and members
- [ ] Due dates and late fines
- [ ] Switch storage from JSON to SQLite or PostgreSQL
- [ ] Login for librarian accounts

## Author

**Abdul Wahab**: [LinkedIn](https://www.linkedin.com/in/abdulwahab-dataanalyst/) · [GitHub](https://github.com/wahabsiddiqi)
