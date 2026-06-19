
# 🚀 APEX ERP: Ultimate Setup Guide

A complete Student Assessment & Management Platform.

---

## 🛠 Tech Stack
| Tier | Technology |
| :--- | :--- |
| **Backend** | Python, Django, DRF |
| **Database** | SQLite (Built-in) |
| **Frontend** | React.js |

---

## 🏗 System Overview


[Image of web application architecture diagram]


---

## ⚙️ How to Run
Follow these commands in your Mac terminal:

### 1. Setup Backend
```bash
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python3 manage.py migrate
python3 manage.py runserver

```

### 2. Setup Frontend

(Open a new terminal tab)

```bash
cd frontend
npm install
npm start

```

---

## 📂 Project Structure

```text
Apex/
├── backend/    # API & Database logic
├── frontend/   # UI & React components
└── README.md   # Documentation

```


## 💡 Troubleshooting Checklist

1. **Command not found:** Install [VS Code](https://code.visualstudio.com/), [Python](https://www.python.org/), and [Node.js](https://nodejs.org/).
2. **Database:** SQLite is auto-managed; no manual SQL installation required.
3. **Ports:** Backend on `8000`, Frontend on `3000`.

