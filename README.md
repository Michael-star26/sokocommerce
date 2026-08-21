# 🌿 SokoGreen

> **Farm-Fresh Organic Grocery Platform**
> *Direct B2B & B2C supply chain connecting local organic agriculture with enterprise & retail markets.*

---

##  Summary

**SokoGreen** is an end-to-end e-commerce solution engineered for high-availability organic grocery delivery. Built on a modular micro-architecture (**Flask REST API** + **Angular 17+**), the platform guarantees seamless order processing, automated inventory tracking, and localized mobile payment integrations.

---

##  Live Environments

* **Production API:** `[https://sokogreen.onrender.com](https://sokogreen.onrender.com)`
* **Web Portal:** `[https://sokofrontend.vercel.app](https://sokofrontend.vercel.app)`

---

##  Technology Stack

| Layer | Technology | Infrastructure / Purpose |
| --- | --- | --- |
| **Frontend** | Angular 17+ | Vercel Global Edge Network |
| **Backend** | Python 3.11 / Flask 3.x | Render Cloud Service |
| **Database** | PostgreSQL | Managed Relational DB |
| **Auth** | Flask-JWT-Extended | Role-Based Access Control (RBAC) |
| **Payments** | Safaricom Daraja API | Automated M-Pesa STK Push |

---

##  System Features

* **Real-Time Catalog Management:** Automated stock sync across 6 core product categories.
* **Enterprise Security:** JWT-based user authentication supporting `USER`, `ADMIN`, and `SUPER_ADMIN` tiers.
* **Instant Checkout:** Integrated mobile payment gateway with real-time callback processing.
* **Cross-Origin Compliance:** Secure CORS configuration supporting multi-region client origins.

---

##  Quick Deployment & Run

### Backend API

```bash
# 1. Install Dependencies
pip install -r requirements.txt

# 2. Seed Initial Database & Master Accounts
python seed.py

# 3. Launch Application Server
gunicorn app:app

```

---

## 🔒 Master Test Accounts

| Access Tier | Account Email | Password |
| --- | --- | --- |
| **Super Admin** | `superadmin@sokocommerce.com` | `SuperAdmin123!` |
| **Manager / Admin** | `admin@sokocommerce.com` | `AdminPass123!` |
| **Client / User** | `johndoe@example.com` | `UserPass123!` |
