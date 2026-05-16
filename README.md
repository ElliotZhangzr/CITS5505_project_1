# CITS5505 Stock Trading Simulator
CITS5505 Agile Web Development — Semester 1, 2026

## 1. Application Purpose, Design and Usage

### Purpose

This platform is a browser-based simulated stock trading system that provides a complete long and short trading mechanism with no position limits or risk control rules, presenting the gains and risks of stock trading in a way that most closely resembles the real market. The platform is designed for two scenarios: financial education and competitive gaming. On the educational side, it helps learners build an intuitive understanding of market volatility, position management, and profit/loss logic in a zero-financial-risk environment. On the gaming side, it drives user competition through leaderboards and achievement systems to enhance engagement and enjoyment.

### Design

**Tech Stack**

The backend uses **Flask** (Python web framework) to handle routing and business logic, the database uses **SQLite**, data reads and writes are performed through **SQLAlchemy ORM**, and **Flask-Migrate** manages database schema versioning. The frontend uses native HTML, CSS, and JavaScript without relying on frontend frameworks such as React or Vue.

**Page Rendering**

Pages are generated as complete HTML by the server-side Jinja2 template engine and returned to the browser, with all content assembled on the server. On top of this, some pages use JavaScript for dynamic updates: the dashboard requests the latest stock prices from the server every 2 seconds and refreshes the charts and holdings data without reloading the entire page.

**Backend Structure**

Business logic is split into independent modules by function. The routing layer is only responsible for receiving requests and returning responses, with specific logic handled by each service module:
- `trading_service.py` — buying and selling stocks, updating holdings, calculating profit/loss
- `stock_simulator.py` — generating simulated stock prices
- `achievement_service.py` — determining whether achievements are unlocked
- `leaderboard.py` — calculating user rankings
- `password_reset_service.py` — verification code generation, validation, and expiry management

**In-Process State Store**

Stock simulation state (buy/sell pressure accumulated from user trades) and password reset verification codes are held in `memory_store.py`, an in-process key-value store rather than the database. This avoids database writes on every price tick and keeps reset codes entirely out of persistent storage. The trade-off is that simulation pressure state resets to zero when the server restarts.

**Stock Price Simulation**

A new price is generated every 2 seconds, with price changes determined by three overlapping components:
- Random fluctuation (random numbers based on the stock's volatility parameter)
- Mean reversion (the further the price deviates from the base price, the stronger the pull-back force)
- Trade impact (user buys push the price up, sells push it down, with the effect decaying over time)

**Database Structure**

There are 6 tables in total, recording user information, stock parameters, price history, holdings, transaction records, and feedback. All monetary fields use the Decimal precision type to avoid floating-point errors. When historical prices exceed 6,000 records, a database trigger automatically deletes the oldest records to control storage size.

**Security**

All forms have CSRF Token enabled to prevent cross-site request forgery. Passwords are stored after being salted and hashed using the `pbkdf2:sha256` algorithm, with no plaintext stored in the database. Admin functionality is intercepted via route decorators, and non-admin accounts cannot access it. Password reset verification codes are stored only as their SHA256 digest, valid for 10 minutes, and automatically invalidated after 5 consecutive incorrect attempts.


### Usage

**Registration and Login**

New users visit the `/register` page, fill in their username, email, and password to complete registration. The system automatically allocates $10,000 in virtual starting funds and redirects to the dashboard. Existing users can log in with their username or email. If a password is forgotten, a 6-character alphanumeric verification code (uppercase letters and digits) can be received via email to complete the reset. The code is valid for 10 minutes, and a minimum of 60 seconds must pass before a new code can be requested.

**Dashboard**

After logging in, users are taken to the dashboard by default. The page is divided into four areas:
- **Stock Chart**: Switch between different stocks via tabs; the chart displays price trends in real time, refreshing every 2 seconds
- **Trading Panel**: Select a stock and quantity, then click the buy or sell button to execute a trade
- **Holdings List**: Displays the quantity, average price, current price, market value, and profit/loss of all current holdings, with total assets, realised profit/loss, and unrealised profit/loss summarised at the bottom
- **Market Overview**: A real-time list of current prices for all stocks

**Profile**

Users can perform the following actions on their profile page:
- Upload a local avatar (any image format is automatically converted to PNG on save) or generate one randomly via the DiceBear API (requires an internet connection)
- Edit their bio (up to 200 characters)
- View a holdings and assets overview; the profile also displays the account creation date ("Member since Month Year")
- The registered email address is masked by default; click **Show** to reveal it
- Toggle the "Hide Holdings" switch; when enabled, other users cannot view their holdings
- View unlocked achievements (14 in total, divided into Easy / Medium / Hard tiers)
- Submit usage feedback (up to 1,000 characters)
- Permanently delete their account after password confirmation

**Leaderboard**

Four ranking dimensions are available to switch between: Total Assets, Cash, Total Profit, and Return Rate (%). The currently logged-in user is highlighted in the list.

**User Directory**

Displays a list of all registered users with support for searching by username or ID. Clicking a username opens their public profile, including their avatar, bio, achievements, and holdings information (if the user has not hidden them).

**Admin Panel** (visible to admins only)

Admins access `/admin` via the top navigation bar and can access four management modules:
- **Overview**: View the total number of users, stocks, trades, and feedback entries in the system
- **User Management**: View all user information, grant or revoke admin privileges (cannot act on oneself)
- **Stock Management**: Add new stocks by filling in the symbol, name, and base price
- **Feedback Management**: View all feedback submitted by users, sorted in reverse chronological order


---

## 2. Group Members

| UWA ID | Name | GitHub Username |
|---|---|---|
| 24389925 | Zerun Zhang | https://github.com/ElliotZhangzr |
| 24807169 | Dilani Gunathilaka Mapitigamage | https://github.com/Dilani1997 |
| 24746589 | Weishan Li | https://github.com/Weishan-Li |
| 23685578 | Kushagra Patel | https://github.com/kp240800 |


---

## 3. Launch Instructions

### Prerequisites

- Python 3.9+
- Google Chrome (required for running Selenium tests)

### Setup

**1. Clone the repository**
```bash
git clone https://github.com/ElliotZhangzr/CITS5505_project_1.git
cd CITS5505_project_1
```

**2. Create and activate a virtual environment**

macOS / Linux:
```bash
python3 -m venv .venv
source .venv/bin/activate
```

Windows:
```bat
python -m venv .venv
.venv\Scripts\activate
```

**3. Install dependencies**
```bash
pip install -r requirements.txt
```

**4. Configure environment variables**

Create a `.env` file in the project root directory:
```
RESEND_API_KEY=re_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
RESEND_FROM_EMAIL=noreply@yourdomain.com
```

> Both values can be obtained after registering at [Resend](https://resend.com). They are only required for the password reset email feature and do not affect any other functionality.

**5. Initialise the database**

Must run:
```bash
flask db upgrade
```
Please confirm the above step has been completed.

The database file will be generated at `instance/app.db`. To view migration history or roll back:
```bash
flask db history    # view migration history
flask db downgrade  # roll back one version
```

**6. Load seed data**
Must run:
```bash
python seed_data.py
```
Please confirm the above step has been completed.

The following test accounts are created after execution:

| Username | Password | Role |
|---|---|---|
| `root` | `root` | Admin |
| `admin` | `Admin123` | Admin |
| `trader` | `Trader123` | Regular User |

**7. Start the application**
```bash
python app.py
```

Visit `http://127.0.0.1:5001` in a browser. Devices on the same local network (e.g. a mobile phone) can access it via the host machine's local IP address, for example `http://10.x.x.x:5001`.

> This information is displayed in the running terminal.

---

## 4. Test Instructions

### 1. How to Run Tests

#### Unit Tests

Run all unit tests (from the project root directory):

```bash
python -m pytest tests/unit/
```

Example of running a single test file:

```bash
python -m pytest tests/unit/test_auth_forms.py
python -m pytest tests/unit/test_trading_service.py
```

#### Selenium Tests

Selenium tests require the Flask server to be started first, then run in a separate terminal (Chrome browser must be installed; ChromeDriver is installed automatically via `webdriver-manager`):

macOS / Linux:

```bash
# Terminal 1 (if using a virtual environment, first run: source .venv/bin/activate)
flask run

# Terminal 2 (new window requires re-activation; first run: source .venv/bin/activate)
python -m pytest tests/selenium/
```

Windows:

```bat
:: Terminal 1 (if using a virtual environment, first run: .venv\Scripts\activate)
flask run

:: Terminal 2 (new window requires re-activation; first run: .venv\Scripts\activate)
python -m pytest tests/selenium/
```

Example of running a single Selenium test file:

```bash
python -m pytest tests/selenium/test_login.py
python -m pytest tests/selenium/test_admin.py
```

> Selenium tests depend on the following accounts already existing in the database (run seed or register manually):
>
> ```bash
> python seed_data.py
> ```
>
> - Regular user: `testuser1` / `Testuser1`
> - Admin: `root` / `root`


---

### Unit Tests

- `test_auth_forms.py` — Tests password validation on the registration form (length, uppercase letters, numbers), required field validation on the login form, password match validation on the reset password form, and whether passwords are stored in hashed form after registration and whether initial funds are correctly written to the database.

- `test_user_service.py` — Tests paginated user queries (number of users per page, has_next/has_prev flags, last page content), searching by username or ID, and verifies that returned data does not contain emails or password hashes.

- `test_trading_service.py` — Tests the complete buy and sell transaction flow: cash deduction, holding creation/update/deletion, transaction record writing, average cost recalculation; and various failure scenarios (insufficient balance, stock not found, no price data, quantity of zero, selling beyond holdings).

- `test_portfolio.py` — Tests portfolio construction: total assets equal cash when there are no holdings, market value and floating profit/loss calculated from current prices when holdings exist, accumulated realised profit/loss after selling, no crash when a stock has no price, and returned data does not expose emails or password hashes.

- `test_leaderboard.py` — Tests ranking by four methods: cash, total assets, profit, and return rate. Verifies ranking order, rank starting at 1, return rate formula correctness, no error with an empty user table, and output data does not contain password hashes.

- `test_admin_logic.py` — Tests the `admin_required` decorator's different handling of admins, regular users, and unauthenticated users; tests role labels and "current user" marking in the user list; tests the logic for toggling admin privileges, and that admins cannot modify their own privileges.

- `test_delete_account.py` — Tests account deletion: with the correct password, the user, holdings, and transaction records are all deleted and the user is logged out; with the wrong password, data remains unchanged; after account deletion, login is no longer possible.

- `test_password_reset_service.py` — Tests the password reset flow: a verification code is generated and sent when the email exists, a generic message is returned when it does not, repeated requests within a short time are rejected; the password is updated and the cache cleared when the code is correct, the failure count is incremented when it is wrong, the code is cleared after the maximum number of attempts is reached, and mismatched or too-short passwords are rejected.

- `test_profile_logic.py` — Tests profile updates: saving a bio of up to 200 characters, returning 400 if the length is exceeded; toggling the "Hide Holdings" switch; uploading a PNG avatar and saving it to disk and the database; rejecting empty data, non-PNG formats, and invalid base64-encoded avatars.

- `test_seed_data.py` — Tests the database initialisation script: correctly creates the root/admin/trader users and their permissions, root password is stored as a hash, creates AAPL/TSLA/NVDA stocks and their price history, trader's holdings and buy transactions are correct, and running twice does not produce duplicate data.

- `test_stock_data_and_simulator.py` — Tests stock data queries (returns a list of stocks and price history, supports limit to fetch the latest N records); tests the price simulator (minimum floor of 1.00 for negative values, single-step increase capped at 15%, not below min_price, buy and sell operations correctly apply market pressure).

### Selenium Tests

- `test_login.py` — Verifies the login page loads correctly; login with either username or email redirects to the dashboard; incorrect or non-existent username/password shows an error message; submitting an empty form stays on the login page; unauthenticated access to the dashboard redirects to login; after logging out, returning to the dashboard is still blocked.

- `test_register.py` — Verifies the registration page loads correctly; successful registration with a unique username and email redirects to the dashboard; registering an already-existing username or email shows an error message; submitting an empty form stays on the registration page; the registration page contains a login link.

- `test_dashboard.py` — Verifies the dashboard is accessible after login; the stock chart area, buy/sell interaction area, holdings list area, and portfolio summary data all display correctly; the Canvas chart renders actual content; logged-in users can access `/api/stocks` and `/api/portfolio`; unauthenticated users accessing the dashboard are redirected to the login page.

- `test_leaderboard.py` — Verifies the leaderboard page loads correctly; the Total Assets, Cash, Profit, and Return Rate ranking tabs can all be switched between without errors; the page displays usernames and ranking information; the current user's cash data is visible; passing an invalid ranking type does not crash the page.

- `test_admin.py` — Verifies that admins can access `/admin` and `/admin/users`, and that regular users are redirected to the dashboard when attempting to access them; the user management page displays role information; admins cannot revoke their own admin privileges; the stock management page loads without errors, and regular users cannot access it.