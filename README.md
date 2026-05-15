# CITS5505 Stock Trading Simulator
CITS5505 Agile Web Development — Semester 1, 2026

---

## 1. Application Purpose, Design and Usage

### Purpose

A browser-based simulated stock trading platform where users start with **$10,000 virtual cash** and trade against a live-updating market. The goal is to grow your portfolio, climb the leaderboard, and unlock achievements — without any real financial risk.

### Design

The application is built with a **Flask** backend and a vanilla JavaScript frontend, using **SQLite** as the database managed through **Flask-Migrate**.

**Key features:**

| Feature | Description |
|---|---|
| Authentication | Register, login, logout, and password reset via email verification |
| Live Stock Market | Prices update every 2 seconds using a GBM-based simulation with momentum, mean reversion, and trade impact |
| Trading | Buy and sell stocks; portfolio tracks quantity, average cost, market value, and P&L |
| Leaderboard | Rank all users by cash, total assets, profit, or return percentage |
| Profile | Upload or generate an avatar, write a personal bio, toggle holdings visibility |
| Public Profiles | View any user's profile and portfolio (if not hidden) |
| Achievements | 14 unlockable achievements across easy / medium / hard tiers |
| Feedback | Submit feedback from the profile page; admins can view all submissions |
| Admin Panel | Manage users and stocks, view system stats and user feedback |

### Usage

After logging in, users land on the **Dashboard** where they can:
- Monitor real-time stock prices and charts
- Buy or sell stocks via the trading panel
- Track their portfolio summary (cash, stock value, total assets, P&L)
- View their transaction history

From the navigation bar, users can access the **Leaderboard**, **Users** directory, and their own **Profile**.

Administrators additionally have access to the **Admin Panel** at `/admin`, where they can add stocks, manage user roles, and read submitted feedback.

---

## 2. Group Members

| UWA ID | Name | GitHub Username |
|---|---|---|
| 24389925 | Zerun Zhang | [ElliotZhangzr](https://github.com/ElliotZhangzr) |
| 24807169 | Dilani Gunathilaka Mapitigamage | [Dilani1997](https://github.com/Dilani1997) |
| 24746589 | Weishan Li | [Weishan-Li](https://github.com/Weishan-Li) |
| 23685578 | Kushagra Patel | [kp240800](https://github.com/kp240800) |

---

## 3. Launch Instructions

### Prerequisites

- Python 3.11+
- Google Chrome (required for Selenium tests)

### Setup

**1. Clone the repository**
```bash
git clone https://github.com/ElliotZhangzr/CITS5505_project_1.git
cd CITS5505_project_1
```

**2. Create and activate a virtual environment**
```bash
python3 -m venv .venv
source .venv/bin/activate        # macOS / Linux
.venv\Scripts\activate           # Windows
```

**3. Install dependencies**
```bash
pip install -r requirements.txt
```

**4. Configure environment variables**

Create a `.env` file in the project root:
```
SECRET_KEY=your-secret-key-here
RESEND_API_KEY=your-resend-api-key
RESEND_FROM_EMAIL=noreply@yourdomain.com
```

> Password reset emails require a valid [Resend](https://resend.com) API key. The rest of the application works without it.

**5. Initialise the database**
```bash
flask db upgrade
```

**6. (Optional) Load seed data**
```bash
python seed_data.py
```

This creates three accounts:

| Username | Password | Role |
|---|---|---|
| `root` | `root` | Admin |
| `admin` | `Admin123` | Admin |
| `trader` | `Trader123` | User |

**7. Start the application**
```bash
python app.py
```

Open [http://127.0.0.1:5001](http://127.0.0.1:5001) in your browser.

---

## 4. Test Instructions



# cits5504-practice

1. Create a repository and initialized config
git init : creates a new git repository in the current folder

git clone [url] : clones an existing project from github to your local machine

git status : checks the file status, shows file that have been changed but not yet committed

git log : displays the record of commit history and their unique hashes

git remote -v : checks the details of connection between the local with remote repositories

2. update and submint
git add [filename] : adds a specific file to the staging area

git add . : adds all changed files in the folder to the staging area

git add * : adds all changed files in the folder to the staging area

git commit -m "[message]" : creates a commit with a descriptive message to record a snapshot of the current code

git commit -am "[message]" : Stages and commits all tracked, changed files in a single step.

3. branch and switch branch
git checkout -b [branch_name] : create a new branch and switch to it immediately

git checkout [branch_name/hash/tag_name] : switch to a specific branch

git branch -d [branch_name/hash/tag_name] : delete the specific branch

git tag [tag_name] : Adds a human-readable label (e.g., v0.1) to the current commit

4. github collabration
git push origin [branch_name] : Pushes local commits to the remote GitHub repository

git pull origin [branch_name] : Fetches the latest code from GitHub and merges it into the local branch.

5. project management tool
Issues:

Pull Requests(pr):

Code Review:

Branch Protection Rules:

