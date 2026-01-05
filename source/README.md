# HintEval: A Framework for Hint Generation and Evaluation

## Overview
**HintEval** is a comprehensive framework designed for the generation and systematic evaluation of hints. The goal of this system is to provide a standardized environment where users can generate hints using various strategies (based on the HintEval-Dataset) and evaluate their effectiveness, quality, and pedagogical value.

The framework consists of:
* **Backend:** A FastAPI-powered Python service that handles hint generation logic, dataset processing, and evaluation metrics.
* **Frontend:** A modern web interface for interactive hint generation and visualization.

---

## Getting Started

Follow these steps to set up your local environment and run the entire framework.

### 1. Prerequisites
Ensure you have the following installed:
* **Python 3.8+**
* **Node.js & npm** (The `main.py` script will trigger npm commands)

### 2. Set Up the Virtual Environment
To keep the project dependencies isolated, create and activate a virtual environment.

**Create the environment:**
```bash
# Windows
python -m venv venv

# macOS / Linux
python3 -m venv venv


**Activate the environment:**
```bash
# Windows
.\venv\Scripts\activate

# macOS / Linux
source venv/bin/activate
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Run the System

Navigate to the app.py file and execute it.