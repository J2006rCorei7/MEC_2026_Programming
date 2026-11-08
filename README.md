# 🚚 Urban Food Crisis Response & Routing System

> **Metropolitan Engineering Competition (MEC 2026)**  
> **Theme:** Feeding the Future: Designing Smart Infrastructure for Urban Food Security  
> **Location:** George Vari Engineering and Computing Centre | **Date:** November 7 & 8, 2026

---

## 📖 Table of Contents

- [About the Project](#-about-the-project)
- [Key Features](#-key-features)
- [System Architecture & Core Logic](#-system-architecture--core-logic)
- [Tech Stack & Dependencies](#-tech-stack--dependencies)
- [Project Structure](#-project-structure)
- [Getting Started](#-getting-started)
  - [Prerequisites](#prerequisites)
  - [Environment Setup](#environment-setup)
  - [Database Initialization](#database-initialization)
  - [Running the Application](#running-the-application)
- [API Endpoints](#-api-endpoints)
- [Dataset Compatibility](#-dataset-compatibility)
- [Generative AI Disclosure & Citation Notice](#-generative-ai-disclosure--citation-notice)
- [License](#-license)

---

## 🎯 About the Project

The **Urban Food Crisis Response and Routing System** is an engineering solution designed to coordinate emergency food delivery across urban road networks during severe shortages and crisis events.

The system addresses the complexities of urban emergency logistics:
- Distinguishing between urgent requests (e.g., hospitals, high-density shelters) and standard food relief.
- Routing vehicles along weighted road network graphs using spatial optimization algorithms ($A^*$ and Dijkstra).
- Matching inventory and vehicle constraints (refrigerated vs. regular capacity, fuel limits) without over-allocating hub stock.
- Maintaining continuous audit logging across crisis life cycles through a state machine model.

---

## ✨ Key Features

- **Dynamic Priority Scoring:** Evaluates emergency requests based on affected population size, missing food quantities (hot vs. cold), delivery deadlines, target proximity, and location category multipliers (Hospitals: $1.7\times$, Shelters: $1.5\times$, Community: $1.1\times$).
- **Heap-Based Priority Queue:** Automatically orders and re-evaluates high-urgency requests using Python's `heapq` module to prevent request starvation.
- **$A^*$ & Dijkstra Shortest Path Routing:** Computes geographical travel paths using Haversine distance heuristics over weighted node-edge road networks while respecting road closures.
- **Greedy Resource Matching:** Allocates supply hubs and delivery trucks according to capacity, refrigeration requirements, and available fuel ($8\text{ km/L}$ consumption model).
- **Crisis State Machine:** Manages state transitions across `Open`, `Prioritized`, `Resource Assigned`, `In Progress`, `Re-Routing`, `Delivered`, `Resolved`, `Delayed`, and `Failed`, complete with timestamped log audit trails.
- **Live Interactive Dashboard & User Portal:** Features a Leaflet.js map display, route polyline overlays, and request tracking tables.

---

## 🧠 System Architecture & Core Logic

### Priority Scoring Equation
$$
\text{Score} = \left[ 0.5 \cdot (1.01^{\text{people}}) + 0.8 \cdot (\Delta\text{Hot}) + 1.2 \cdot (\Delta\text{Cold}) + 0.5 \cdot (\text{Distance}) + \text{Urgency} \right] \times \text{Category Factor}
$$

### Resource Dispatch Flow
1. **Request Ingestion:** Incoming emergency request registered via `/api/request/`.
2. **Path Resolution:** Algorithmic calculation of the closest available supply hub using $A^*$.
3. **Queue Sorting:** Max-priority score evaluation pushes the request into the dispatch heap queue.
4. **Allocation Matching:** Exhaustive search pairs valid trucks ($V_1 - V_{12}$) with inventory hubs ($P_0 - P_2$).
5. **State Transition:** Logs timestamped state progress into SQLite database and feeds the interactive map interface.

---

## 🛠 Tech Stack & Dependencies

- **Language:** Python 3.11+
- **Backend Framework:** Flask 3.1.3, Flask-RESTful 0.3.10, Flask-CORS 6.0.5
- **ORM & Database:** SQLAlchemy 2.1.8, Flask-SQLAlchemy 3.1.1, SQLite
- **Frontend Technologies:** HTML5, CSS3, JavaScript (ES6+), Leaflet.js (v1.9+)
- **Data Structures:** Custom `Node`, `Edge`, `Poi`, `Truck`, and `Hub` representations

---

## 📁 Project Structure

```
MEC 2026/
├── README.md                   # Project documentation & execution guide
├── requirements.txt            # Python dependencies
├── main.py                     # Flask backend API server & application setup
├── routing.py                  # A* algorithm & spatial heuristic functions
├── dispatcher.py               # Priority calculation, queueing, & resource allocation
├── crisis_state.py             # Crisis state machine & transition rules
├── Dataparse.py                # Data parser & object definitions (Node, Edge, POI, Hub, Truck)
├── databaseInfo.py             # Database query layer & SQLite interaction methods
├── createdb.py                 # Script to create and reset the SQLite database schema
├── dataset/
│   ├── toronto-downtown.json   # Dataset 1: Toronto Downtown road network & resources
│   └── city-dataset-2.json     # Dataset 2: Evaluation road network (Day 2 adaptation test)
└── frontEnd/
    ├── frontEndManagement.html # Admin & Dispatcher live monitoring interface
    ├── frontEndUser.html       # Public emergency food request submission portal
    ├── script.js               # Frontend fetch requests & UI event handlers
    ├── mapScript.js            # Leaflet map setup, route drawing, & marker overlay
    └── styles.css              # Styling for dashboard UI and modal components
```

---

## 🚀 Getting Started

### Prerequisites

- **Python 3.11** or higher installed on your machine.
- **Git** (optional, for cloning).

### Environment Setup

1. Open your terminal or command prompt and navigate to the project directory:
   ```bash
   cd "MEC 2026"
   ```

2. Create a virtual environment:
   ```bash
   python -m venv venv
   ```

3. Activate the virtual environment:
   - **macOS / Linux:**
     ```bash
     source venv/bin/activate
     ```
   - **Windows:**
     ```cmd
     venv\Scripts\activate
     ```

4. Install the required dependencies:
   ```bash
   pip install -r requirements.txt
   ```

### Database Initialization

Before running the server for the first time, initialize the database schema:

```bash
python createdb.py
```

### Running the Application

1. Start the Flask server:
   ```bash
   python main.py
   ```

2. Access the system in your web browser:
   - **User Emergency Request Portal:** [http://127.0.0.1:5000/](http://127.0.0.1:5000/)
   - **Management & Dispatcher Dashboard:** [http://127.0.0.1:5000/management](http://127.0.0.1:5000/management)

---

## 🔌 API Endpoints

| Method | Endpoint | Description |
| :--- | :--- | :--- |
| `GET` | `/` | Renders the User Request Portal |
| `GET` | `/management` | Renders the Management & Dispatcher Dashboard |
| `GET` | `/api/request/` | Fetches all current emergency food requests |
| `POST` | `/api/request/` | Submits a new emergency request and triggers route optimization |
| `GET` | `/requests/<id>` | Fetches data and route path for a specific request by ID |
| `GET` | `/api/routes/` | Returns list of all graph network nodes for rendering |

---

## 🌐 Dataset Compatibility

The system is designed to seamlessly process interchangeable competition datasets without altering core logic:
- **Dataset 1 (`toronto-downtown.json`):** Dense urban grid representing Toronto's core.
- **Dataset 2 (`city-dataset-2.json`):** Sparser regional network used to evaluate solution adaptability.

To load a different dataset, update the dataset file in the `dataset/` directory before starting the application.

---

## 📜 Generative AI Disclosure & Citation Notice

In compliance with **Section 2.1 & Section 4.3 of the MEC 2026 Competition Rules**:
- **Usage Scope:** Generative AI tools were utilized for boilerplate code formatting, API route structure debugging, documentation generation, and CSS layout polish.
- **Review & Verification:** All AI-assisted components were manually reviewed, validated against dataset schemas, and modified by the team. Core routing logic ($A^*$), state machine flow, priority scoring equations, and resource allocation logic were original engineering implementations.

---

## 📄 License

Developed for the **21st Metropolitan Engineering Competition (MEC 2026)**. All rights reserved by the project team.