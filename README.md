# أثر (Athar) — Wikimedia Community Dashboard

An open-source analytics & activity dashboard for Wikimedia affiliates.
Aggregates cross-wiki CentralAuth metrics, tracks Meta-Wiki community rosters,
and logs events. Built with Flask, ToolsDB, and Wikimedia Codex on Toolforge.

---

## 🚀 Quickstart for Students (Day 1)

### 1. Clone your Fork

```bash
git clone https://github.com/bonnjalal/Athar.git
cd Athar
git remote add upstream https://github.com/bonnjalal/Athar.git
git fetch upstream
```

### 2. Set Up Virtual Environment & Dependencies

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 3. Configure Local Environment

```bash
cp .env.example .env
```

_(Notice that `MOCK_AUTH=True` is enabled by default so you can test project
creation immediately!)_

### 4. Run the Application

```bash
python3 run.py
```

Open [http://127.0.0.1:5000](http://127.0.0.1:5000) in your browser.

---

## 🌿 Contribution Workflow

Always create feature branches off `dev`:

```bash
git checkout dev
git pull upstream dev
git checkout -b task-<number>-<short-description>
```

Submit your Pull Request targeting `base: dev`.
