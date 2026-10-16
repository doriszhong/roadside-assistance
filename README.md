<div align="center">

<img src="https://capsule-render.vercel.app/api?type=waving&color=ff5c2b&height=200&section=header&text=MechanicGo&fontSize=80&fontColor=ffffff&fontAlignY=35&desc=Roadside%20Assistance%2C%20Redefined&descAlignY=60&descSize=22" width="100%"/>

<br/>

[![Python](https://img.shields.io/badge/Python-3.8+-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://python.org)
[![Flask](https://img.shields.io/badge/Flask-3.x-000000?style=for-the-badge&logo=flask&logoColor=white)](https://flask.palletsprojects.com)
[![MySQL](https://img.shields.io/badge/MySQL-8.0-4479A1?style=for-the-badge&logo=mysql&logoColor=white)](https://mysql.com)
[![Render](https://img.shields.io/badge/Deployed_on-Render-46E3B7?style=for-the-badge&logo=render&logoColor=black)](https://render.com)
[![Railway](https://img.shields.io/badge/Database-Railway-0B0D0E?style=for-the-badge&logo=railway&logoColor=white)](https://railway.app)
[![License](https://img.shields.io/badge/License-MIT-green?style=for-the-badge)](LICENSE)
[![Status](https://img.shields.io/badge/Status-Live-brightgreen?style=for-the-badge&logo=statuspage)](https://mechanicgo.onrender.com)

<br/>

> **🔧 A full-stack, production-ready roadside assistance platform that connects stranded drivers with the nearest certified mechanics in real-time — powered by GPS, Flask, and MySQL.**

<br/>

### 🌐 [Live Demo 1 — Render](https://mechanicgo.onrender.com/) &nbsp;&nbsp;|&nbsp;&nbsp; 🤗 [Live Demo 2 — HuggingFace](https://ministerchief-mechanicgo.hf.space)

<br/>

---

</div>

## 📸 Screenshots & UI Preview

<br/>

<table>
<tr>
<td width="50%">

### 🏠 Landing Page
> Sleek hero section with animated phone mockup, feature highlights, and one-click sign-up/login flow

<img width="1752" height="941" alt="image" src="https://github.com/user-attachments/assets/4f215a0c-4f8e-4c53-a5ef-0aeb429d1242" />


</td>
<td width="50%">

### 🚨 User Dashboard — SOS Panel
> Issue selector, live GPS coordinates, and one-tap emergency dispatch

<img width="1752" height="941" alt="image" src="https://github.com/user-attachments/assets/b3ac70e3-c5b7-43a6-a70a-58250802a101" />


</td>
</tr>
<tr>
<td width="50%">

### 🔧 Mechanic Portal
> Availability toggle, real-time job assignments, location sharing, and earnings tracker

<img width="1752" height="941" alt="image" src="https://github.com/user-attachments/assets/c4a4401f-7171-473c-8b4e-1ed765bc9a70" />


</td>
<td width="50%">

### 👑 Admin Console
> Analytics charts, full request oversight, user & mechanic management

<img width="1752" height="941" alt="image" src="https://github.com/user-attachments/assets/b957f003-74f2-401a-b818-fe147168c066" />


</td>
</tr>
</table>

<br/>


---

## ✨ Feature Highlights

<br/>

### 🚗 Car Owner (User) Features

| Feature | Description |
|---|---|
| 🚨 **One-Tap SOS** | Instantly triggers automatic dispatch to the nearest available mechanic |
| 📍 **Live GPS Matching** | Haversine formula finds the closest mechanic with sub-second precision |
| 🗺️ **OpenStreetMap Integration** | Embedded live map shows your location and mechanic's route |
| ⭐ **Rate & Review** | 5-star rating system with written review after every completed job |
| 🔔 **Real-Time Notifications** | Live status updates from dispatch → en-route → completed |
| 📋 **Request History** | Full history of all past SOS requests with status and mechanic details |
| 🔧 **Issue Type Selection** | Choose from: Flat Tyre, Dead Battery, Engine Problem, No Fuel, Towing, Other |
| ❌ **Cancel Requests** | Cancel active requests before a mechanic arrives |

<br/>

### 🔧 Mechanic Features

| Feature | Description |
|---|---|
| 🟢 **Availability Toggle** | One-click go online/offline control |
| 📍 **Auto Location Sharing** | Seamless background GPS coordinate update to server |
| 📥 **Live Job Dashboard** | View assigned requests, customer phone, map coordinates |
| ▶ **Job Workflow** | Step-by-step status: Dispatched → Start → In Progress → Complete |
| 💰 **Earnings Tracker** | Per-job earnings summary with cumulative total |
| 🔄 **Auto Job Polling** | Dashboard auto-refreshes every 15 seconds for new assignments |

<br/>

### 👑 Admin Console Features

| Feature | Description |
|---|---|
| 📊 **Analytics Dashboard** | Chart.js bar and doughnut charts for request trends and issue breakdown |
| 📈 **7-Day Request Graph** | Visual daily request volume for the past week |
| 🍩 **Issue Breakdown Chart** | Doughnut chart showing distribution of issue types |
| 👥 **User Management** | View, search, and delete any user account |
| 🔧 **Mechanic Overview** | Monitor all mechanics with availability, rating, and specialty |
| 📋 **Global Request Control** | Override status of any active/completed/cancelled request |
| 🔍 **Search & Filter** | Real-time search and status filter on all request tables |

---

## 🏗️ Tech Stack

<br/>

```
┌─────────────────────────────────────────────────────────────┐
│                        FRONTEND                             │
│   HTML5 · CSS3 · Vanilla JS · Chart.js 4.4 · OpenStreetMap  │
│   Google Fonts (Syne + DM Sans) · CSS Variables & Animations│
├─────────────────────────────────────────────────────────────┤
│                         BACKEND                             │
│            Python 3.8+ · Flask 3.x · Flask-CORS             │
│         Token Auth (SHA-256) · Connection Pooling            │
├─────────────────────────────────────────────────────────────┤
│                        DATABASE                             │
│     MySQL 8.0 · mysql-connector-python · 7-table schema     │
│           Auto-init on first run · Railway hosted            │
├─────────────────────────────────────────────────────────────┤
│                       DEPLOYMENT                            │
│        Web App → Render · Database → Railway MySQL           │
│                  Gunicorn WSGI server                        │
└─────────────────────────────────────────────────────────────┘
```

---

## 🗄️ Database Schema

```sql
┌──────────────────────────────────────────────────────────────────────┐
│                        DATABASE SCHEMA                               │
│                                                                      │
│  ┌─────────┐   ┌────────────┐   ┌───────────────┐                   │
│  │  users  │──▶│  sessions  │   │   mechanics   │                   │
│  │─────────│   │────────────│   │───────────────│                   │
│  │ id (PK) │   │ id (PK)    │   │ id (PK)       │                   │
│  │ name    │   │ user_id(FK)│   │ user_id (FK)  │                   │
│  │ email   │   │ token      │   │ specialty     │                   │
│  │ pw_hash │   │ role       │   │ latitude      │                   │
│  │ role    │   │ expires_at │   │ longitude     │                   │
│  │ phone   │   └────────────┘   │ is_available  │                   │
│  └────┬────┘                    │ rating        │                   │
│       │                         │ total_jobs    │                   │
│       │    ┌────────────────┐   └───────┬───────┘                   │
│       └───▶│  sos_requests  │◀──────────┘                           │
│            │────────────────│                                       │
│            │ id (PK)        │   ┌──────────────┐                    │
│            │ user_id (FK)   │──▶│   ratings    │                    │
│            │ mechanic_id(FK)│   │──────────────│                    │
│            │ latitude       │   │ request_id   │                    │
│            │ longitude      │   │ mechanic_id  │                    │
│            │ issue_type     │   │ user_id      │                    │
│            │ status         │   │ rating (1-5) │                    │
│            │ estimated_eta  │   │ review       │                    │
│            └───────┬────────┘   └──────────────┘                    │
│                    │                                                 │
│       ┌────────────┴───────┐   ┌──────────────┐                     │
│       │   notifications    │   │   payments   │                     │
│       │────────────────────│   │──────────────│                     │
│       │ id, user_id, title │   │ request_id   │                     │
│       │ message, type      │   │ amount       │                     │
│       │ is_read            │   │ method       │                     │
│       └────────────────────┘   │ status       │                     │
│                                └──────────────┘                     │
└──────────────────────────────────────────────────────────────────────┘
```

**Tables:** `users` · `sessions` · `mechanics` · `sos_requests` · `ratings` · `notifications` · `payments`

All tables are **auto-created on first run** — zero manual setup required.

---

## 🚀 Local Setup

### Prerequisites

- Python 3.8+
- MySQL 8.0+ (local or remote)
- pip

### 1. Clone the Repository

```bash
git clone https://github.com/username/mechanicgo.git
cd mechanicgo
```

### 2. Create Virtual Environment & Install Dependencies

```bash
python -m venv venv

# Linux / macOS
source venv/bin/activate

# Windows
venv\Scripts\activate

pip install -r requirements.txt
```

### 3. Configure Environment Variables

```bash
cp .env_example .env
```

Edit `.env` with your MySQL credentials:

```env
SECRET_KEY=generate_a_random_secure_string_here
DB_HOST=localhost
DB_USER=root
DB_PASSWORD=your_password
DB_NAME=mechanicgo
DB_PORT=3306
FLASK_ENV=development
```

### 4. Run

```bash
python app.py
```

> ✅ Database tables initialize automatically on first run.
> App runs at **http://localhost:5000**

---

## ☁️ Cloud Deployment Guide

### Step 1 — Deploy MySQL on Railway

1. Go to [railway.app](https://railway.app) → **New Project** → **MySQL**
2. Wait for provisioning, then open the **Connect** tab
3. Note: `Host`, `Port`, `User`, `Password`, `Database`

```
Example credentials (replace with yours):
  DB_HOST     = abc123.proxy.rlwy.net
  DB_PORT     = 23921
  DB_USER     = root
  DB_PASSWORD = xxxxxxxxxxxxxxxx
  DB_NAME     = railway
```

### Step 2 — Deploy Flask App on Render

1. Go to [render.com](https://render.com) → **New** → **Web Service**
2. Connect your GitHub repo
3. Fill in settings:

| Setting | Value |
|---|---|
| **Environment** | Python 3 |
| **Build Command** | `pip install -r requirements.txt` |
| **Start Command** | `gunicorn app:app` |

4. Add **Environment Variables** from your Railway MySQL setup + a secure `SECRET_KEY`
5. Click **Deploy** — Render handles the rest 🚀

---

## 🔌 API Reference

### Authentication

| Method | Endpoint | Description | Auth |
|---|---|---|---|
| `POST` | `/api/auth/register` | Register user or mechanic | ❌ |
| `POST` | `/api/auth/login` | Login → returns session token | ❌ |
| `POST` | `/api/auth/logout` | Invalidate session token | ✅ |
| `GET` | `/api/auth/me` | Get current user profile | ✅ |

### SOS & Requests

| Method | Endpoint | Description | Auth |
|---|---|---|---|
| `POST` | `/api/sos` | Trigger SOS dispatch | ✅ User |
| `GET` | `/api/requests` | List requests (role-filtered) | ✅ Any |
| `PATCH` | `/api/requests/:id/status` | Update request status | ✅ Any |

### Mechanics

| Method | Endpoint | Description | Auth |
|---|---|---|---|
| `GET` | `/api/mechanics` | List all mechanics | ✅ Any |
| `POST` | `/api/mechanics/location` | Update live GPS coordinates | ✅ Mechanic |
| `PATCH` | `/api/mechanics/availability` | Toggle online/offline | ✅ Mechanic |

### Ratings & Notifications

| Method | Endpoint | Description | Auth |
|---|---|---|---|
| `POST` | `/api/ratings` | Submit job rating (1–5 stars) | ✅ User |
| `GET` | `/api/notifications` | Get user notifications | ✅ Any |
| `GET` | `/api/notifications/unread-count` | Get unread count | ✅ Any |

### Admin

| Method | Endpoint | Description | Auth |
|---|---|---|---|
| `GET` | `/api/admin/stats` | System-wide analytics | ✅ Admin |
| `GET` | `/api/admin/users` | List all users | ✅ Admin |
| `DELETE` | `/api/admin/users/:id` | Delete a user | ✅ Admin |

<details>
<summary>📋 Example API Request/Response</summary>

**POST /api/sos**
```json
// Request
{
  "lat": 30.9010,
  "lon": 76.5762,
  "issue_type": "Flat Tyre",
  "description": "Front left tyre puncture on NH-21"
}

// Response (200 OK)
{
  "status": "success",
  "request_id": 42,
  "mechanic_assigned": "Raj Kumar",
  "estimated_arrival_minutes": 8,
  "message": "Mechanic Raj Kumar is on the way!"
}
```

**POST /api/auth/login**
```json
// Request
{ "email": "user@example.com", "password": "mypassword" }

// Response (200 OK)
{
  "token": "a3f1c2d8e9...",
  "user": {
    "id": 7,
    "name": "Arjun Singh",
    "role": "user",
    "email": "user@example.com"
  }
}
```
</details>

---

## 🔑 Default Credentials

| Role | Email | Password |
|---|---|---|
| Admin | `admin@mechanicgo.com` | `admin123` |

> ⚠️ **Change this password immediately after your first deployment!**

---

## 📁 Project Structure

```
mechanicgo/
│
├── app.py                  # Flask application, all API routes
├── database.py             # DB connection pool + schema init
├── requirements.txt        # Python dependencies
├── .env_example            # Environment variable template
│
├── templates/
│   ├── index.html          # Landing page (auth modals, hero, features)
│   ├── dashboard.html      # User dashboard (SOS, requests, map, ratings)
│   ├── mechanic.html       # Mechanic portal (jobs, location, earnings)
│   └── admin.html          # Admin console (analytics, user mgmt)
│
└── static/                 # (optional) CSS/JS/image assets
```

---

## 🛠️ How It Works — Under the Hood

```
User triggers SOS
        │
        ▼
Server receives (lat, lon, issue_type)
        │
        ▼
Haversine formula runs across all
available mechanics with GPS coords
        │
        ▼
Nearest mechanic selected & assigned
        │
        ├── mechanic.is_available → 0 (marked busy)
        ├── sos_request row created with mechanic_id
        └── estimated_arrival = distance × 3 min/km
                │
                ▼
        Mechanic updates job status:
        searching → dispatched → in_progress → completed
                │
                ▼
        Mechanic freed (is_available → 1)
        User prompted to rate (1–5 ⭐)
        Mechanic average rating recalculated
```

---

## 🔒 Security Features

- **SHA-256 password hashing** — plain-text passwords never stored
- **Token-based authentication** — 64-character hex tokens with 7-day expiry
- **Role-based access control** — `user`, `mechanic`, `admin` role gates on every protected route
- **CORS configured** — `flask-cors` with credentials support
- **MySQL connection pooling** — pool of 10 connections, auto-retry on failure
- **Session invalidation** — tokens deleted from DB on logout

---

## 🤝 Contributing

Contributions, issues, and feature requests are welcome!

```bash
# Fork the repo, then:
git checkout -b feature/your-feature-name
git commit -m "feat: add your feature"
git push origin feature/your-feature-name
# Open a Pull Request
```

**Ideas for contribution:**
- 🔔 WebSocket-based real-time updates (replace polling)
- 💳 Payment gateway integration (Razorpay / Stripe)
- 📱 Progressive Web App (PWA) support
- 🌐 Multi-language / i18n support
- 🧪 Unit & integration test suite

---

## 📄 License

Distributed under the **MIT License**. See [`LICENSE`](LICENSE) for full terms.

```
MIT License — © 2026 NIELIT ROPAR
Free to use, modify, and distribute with attribution.
```

---

## 🙏 Acknowledgements & Credits

<div align="center">

### 💡 Special Thanks

---

<table align="center">
<tr>
<td align="center" width="300">

### 👨‍💻 Lovnish Verma
**Mentor & Project Engineer at NIELIT Ropar**

*NIELIT Ropar*

A heartfelt thanks to **Lovnish Verma Sir** for his invaluable mentorship, technical guidance, and continuous support throughout the development of this project. His expertise in full-stack development, encouragement during challenging phases, and vision for building real-world impactful applications made MechanicGo possible.

🔗 [GitHub](https://github.com/lovnishverma) &nbsp;·&nbsp; [LinkedIn](https://linkedin.com/in/lovnishverma)

</td>
</tr>
</table>

---

### 🛠️ Built With

[![Flask](https://img.shields.io/badge/Flask-000000?style=flat-square&logo=flask)](https://flask.palletsprojects.com)
[![MySQL](https://img.shields.io/badge/MySQL-4479A1?style=flat-square&logo=mysql&logoColor=white)](https://mysql.com)
[![Chart.js](https://img.shields.io/badge/Chart.js-FF6384?style=flat-square&logo=chart.js&logoColor=white)](https://chartjs.org)
[![OpenStreetMap](https://img.shields.io/badge/OpenStreetMap-7EBC6F?style=flat-square&logo=openstreetmap&logoColor=white)](https://openstreetmap.org)
[![Railway](https://img.shields.io/badge/Railway-0B0D0E?style=flat-square&logo=railway)](https://railway.app)
[![Render](https://img.shields.io/badge/Render-46E3B7?style=flat-square&logo=render&logoColor=black)](https://render.com)
[![Google Fonts](https://img.shields.io/badge/Google_Fonts-4285F4?style=flat-square&logo=google&logoColor=white)](https://fonts.google.com)

</div>

---

<div align="center">

<img src="https://capsule-render.vercel.app/api?type=waving&color=ff5c2b&height=120&section=footer" width="100%"/>

**Made with ❤️ at NIELIT Ropar**

*If this project helped you, please consider giving it a ⭐ on GitHub!*

</div>
