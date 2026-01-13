# 💡 HintEval: Generation & Evaluation Framework

## 📖 Overview
**HintEval** is a comprehensive framework designed for the generation and systematic evaluation of hints. The goal of this system is to provide a standardized environment where users can generate hints using various strategies (based on the HintEval-Dataset) and evaluate their effectiveness, quality, and pedagogical value.

The framework consists of two core components:
* 🐍 **Backend:** A **FastAPI**-powered Python service that handles hint generation logic, dataset processing, and evaluation metrics.
* ⚛️ **Frontend:** A modern web interface (Node.js) for interactive hint generation and visualization.

---

## 🚀 Getting Started

Follow these steps to set up your local environment and run the entire framework.

### 1. Prerequisites
Before proceeding, ensure you have the following installed on your machine:
* **Python 3.11.9**
* **Node.js & npm** (The `app.py` script will trigger necessary npm commands)

### 2. Set Up the Virtual Environment
To keep project dependencies isolated, we recommend creating and activating a virtual environment.

**Create the environment:**
```bash
# Windows
python -m venv venv

# macOS / Linux
python3 -m venv venv
```

**Activate the environment:**
```bash
# Windows
.\venv\Scripts\activate

# macOS / Linux
source venv/bin/activate
```

### 3. Install Dependencies
Once the environment is active, install the required Python packages:

```bash
pip install -r requirements.txt
```

### 4. Configure Environment Variables
Create a file named `.env` inside the `/source/backend` folder. You will need to populate it with your specific API keys and database credentials.

**Copy and paste the following into your `.env` file:**

```env
# AI Model Configuration
TOGETHER_API_KEY="key_here"
TOGETHER_BASE_URL="https://api.together.xyz/v1"

# Database Configuration
DB_HOST="your_hostname"
DB_NAME="your_name"
DB_USER="your_user"
DB_PASS="your_password"
```

> **Note:** Ensure `TOGETHER_API_KEY` contains your valid provider key and the `DB_*` variables match your PostgreSQL (or relevant DB) setup.

### 5. Run the System
Navigate to the directory containing `app.py` and execute the script. This will initialize both the backend and frontend services.

```bash
python app.py
```