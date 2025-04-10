# 📚 Bookstore Management Web App

A simple Flask web application backed by PostgreSQL for managing a bookstore inventory, built as a personal project to demonstrate full-stack development skills and hands-on database integration.

---

## 🚀 Features

- View a catalog of available books
- Create orders and calculate total purchase price
- Automatically update stock quantity upon purchase
- Organized and modular project structure
- Deployable on [Render.com](https://render.com)

---

## 🛠 Tech Stack

- **Backend**: Python, Flask  
- **Frontend**: HTML (Jinja2 templating)  
- **Database**: PostgreSQL  
- **Deployment**: Render  
- **Version Control**: Git & GitHub  

---

## 📁 Project Structure

bookstore_app/
├── app/
│   ├── __init__.py       # App factory function
│   ├── routes.py         # Application routes using Blueprint
│   ├── services/         # Business logic (e.g., order creation, inventory updates)
│   │   └── order_service.py
│   └── templates/        # HTML templates
│       └── index.html    # Homepage template
├── main.py               # Entry point for local dev
├── requirements.txt      # Python dependencies
├── .render.yaml          # Render deployment config
└── README.md             # Project overview and setup instructionsd

---

## 🔧 Setup & Installation (Local)

1. Clone the repository:
   git clone https://github.com/ReginaldCosensIII/bookstore_app.git
   cd bookstore_app

2. Create a virtual environment:
   python -m venv venv
   source venv/bin/activate  # On Windows use venv\Scripts\activate

3. Install dependencies:
   pip install -r requirements.txt

4. Set environment variables:
   DATABASE_URL=your_postgres_connection_url

5. Run the app locally

---

🌐 Deployment
This app is deployed on Render.
The .render.yaml file handles the configuration:

services:
  - type: web
    name: bookstore-app
    env: python
    buildCommand: "pip install -r requirements.txt"
    startCommand: "gunicorn app:app"
    envVars:
      - key: DATABASE_URL
        fromDatabase:
          name: bookstore-db
          property: connectionString

databases:
  - name: bookstore-db

---

🧠 Author
Reginald Cosens III
GitHub:  @ReginaldCosensIII
Email:   ReginaldCosensIII@gmail.com

---

📌 Future Improvements
-  Add user authentication system (admin & customer roles)
-  Improve UI with CSS framework (e.g., Bootstrap or Tailwind)
-  Add RESTful API support
-  Implement order history and customer profiles
-  Add pagination and search functionality

---

📜 License
This project is for educational and demonstration purposes.
