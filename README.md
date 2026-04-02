# 📈 Stock Intelligence API

📄 **Swagger Docs:**  
https://stock-management-system-qgvh.onrender.com/docs

🚀 **Live API:**  
https://stock-management-system-qgvh.onrender.com

🚀 **Postman Collection Video:**  
https://stock-management-system-qgvh.onrender.com

---

## 📌 Overview

A **production-ready FastAPI backend** for stock analysis, portfolio management, and user tracking.

This API provides powerful features such as:

- Secure authentication
- Stock analytics & insights
- Risk assessment
- Performance tracking
- Portfolio management
- Trend-based predictions

---

## 🚀 Features

- 🔐 JWT-based Authentication (Register, Login, Refresh, Logout)
- 📊 Stock Data Ingestion & Historical Tracking
- ⭐ Follow / Unfollow Stocks
- 📉 Risk Analysis Engine
- 📈 Performance Tracking & Comparison
- 🔮 Basic Price Prediction (Trend-Based)
- 💼 Portfolio Management
- ⚡ Redis Caching Support (Optional)
- 🧠 Insight Generation for Stock Comparison

---

## 🏗️ Tech Stack

| Layer          | Technology |
| -------------- | ---------- |
| Backend        | FastAPI    |
| Database       | PostgreSQL |
| ORM            | SQLAlchemy |
| Authentication | JWT        |
| Caching        | Redis      |
| Server         | Uvicorn    |

---

## 📁 Project Structure

app/
│── config/
│── core/
│── crud/
│── db/
│── models/
│── routes/
│── schemas/
│── services/
│── utils/
│
└── main.py

---

## 🧩 Database Models

### 👤 User

- username
- email
- hashed_password
- role_id
- followed_stocks

---

### 🔐 Role

- name
- description
- users (relationship)

---

### 🏢 Company

- symbol (e.g., INFY.NS)
- name
- sector

---

### 📊 StockData

- date
- open, high, low, close
- volume

**Calculated Metrics:**

- daily_return
- moving averages (7d, 20d, 50d)
- 52-week high/low
- volatility

---

### ⭐ UserStock

- user ↔ company relationship
- tracks followed stocks

---

### 💼 Portfolio

- user_id
- company_id
- quantity
- buy_price
- created_at

---

## 🔑 Authentication APIs

| Method | Endpoint         | Description          |
| ------ | ---------------- | -------------------- |
| POST   | `/auth/register` | Register user        |
| POST   | `/auth/login`    | Login user           |
| POST   | `/auth/refresh`  | Refresh access token |
| POST   | `/auth/logout`   | Logout user          |
| GET    | `/auth/users`    | Get all users        |

---

## 📊 Stock APIs

| Method | Endpoint                       | Description          |
| ------ | ------------------------------ | -------------------- |
| POST   | `/stocks/load-all/`            | Load stock data      |
| GET    | `/stocks/data/{symbol}`        | Get stock data       |
| GET    | `/stocks/companies`            | List all companies   |
| GET    | `/stocks/summary/{symbol}`     | 52-week summary      |
| GET    | `/stocks/compare`              | Compare two stocks   |
| GET    | `/stocks/top-movers`           | Top gainers & losers |
| GET    | `/stocks/risk/{symbol}`        | Risk analysis        |
| GET    | `/stocks/performance/{symbol}` | Performance metrics  |
| GET    | `/stocks/predict/{symbol}`     | Price prediction     |

---

## ⭐ User Stock APIs

| Method | Endpoint                    | Description         |
| ------ | --------------------------- | ------------------- |
| POST   | `/stocks/follow/{symbol}`   | Follow a stock      |
| DELETE | `/stocks/unfollow/{symbol}` | Unfollow a stock    |
| GET    | `/stocks/my-stocks`         | Get followed stocks |

---

## 💼 Portfolio APIs

| Method | Endpoint      | Description        |
| ------ | ------------- | ------------------ |
| GET    | `/portfolio/` | Get user portfolio |
| POST   | `/portfolio/` | Add portfolio item |

---

## 📦 Standard API Response

All responses follow this structure:

```json
{
  "success": true,
  "message": "Request successful",
  "data": {}
}
```

## ⚙️ Setup & Installation

### 1. Clone Repository

```bash
git clone https://github.com/itmepayal/STOCK_MANAGEMENT_SYSTEM.git
cd STOCK_MANAGEMENT_SYSTEM
```

### 2. Create Virtual Environment

```bash
python -m venv env
```

Activate Environment

Linux / Mac

```bash
source env/bin/activate
```

Windows

```bash
env\Scripts\activate
```

Install Dependencies

```bash
pip install -r requirements.txt
```

## ▶️ Run Locally

```bash
uvicorn app.main:app --reload
```

Swagger
http://localhost:8000/docs

## 🔐 Environment Variables

| Variable                    | Value                                                |
| --------------------------- | ---------------------------------------------------- |
| DATABASE_URL                | postgresql://<username>:<password>@<host>/<database> |
| SECRET_KEY                  | your_secret_key_here                                 |
| ALGORITHM                   | HS256                                                |
| ACCESS_TOKEN_EXPIRE_MINUTES | 15                                                   |
| REFRESH_TOKEN_EXPIRE_DAYS   | 7                                                    |
| REDIS_URL                   | redis://<user>:<password>@<host>:<port>              |

## 👨‍💻 Author

Payal Yadav
