# 🌐 NetSage AI
### AI-Assisted Cisco Packet Tracer Troubleshooting Assistant with Human Review

![Python](https://img.shields.io/badge/Python-3.12+-blue?logo=python&logoColor=white)
![Streamlit](https://img.shields.io/badge/Streamlit-1.35+-red?logo=streamlit&logoColor=white)
![Gemini](https://img.shields.io/badge/Google_Gemini-1.5_Flash-green?logo=google&logoColor=white)
![Plotly](https://img.shields.io/badge/Plotly-5.x-blueviolet?logo=plotly&logoColor=white)
![Pydantic](https://img.shields.io/badge/Pydantic-v2-orange)
![License](https://img.shields.io/badge/License-MIT-lightgrey)

---

## 📋 Project Overview

**NetSage AI** is a production-quality AI web application designed to help junior network engineers troubleshoot Cisco Packet Tracer networking labs. It combines:

- **14 deterministic rule checks** that fire instantly without any API calls
- **Google Gemini LLM** that provides structured, OSI-layer-aware diagnosis
- **Mandatory human review** – no AI output is ever automatically accepted
- **Analytics dashboard** tracking AI accuracy, corrections, and issue trends

### The Human-in-the-Loop Guarantee

> Every AI diagnosis must be reviewed by a human engineer who can Accept, Edit, or Reject it. The application stores all corrections and uses them to demonstrate responsible AI practice.

---

## ✨ Features

| Feature | Description |
|---|---|
| 🔍 **AI Diagnosis** | Gemini 1.5 Flash with structured JSON output + Pydantic validation |
| ⚙️ **Rule Checker** | 14 regex/keyword rules for instant pre-diagnosis |
| 👤 **Human Review** | Accept / Edit / Reject workflow with CSV logging |
| 📊 **Dashboard** | 8 interactive Plotly charts + KPI metrics |
| 📁 **Dataset Manager** | View / Add / Edit / Delete / Upload / Validate cases |
| 📜 **JSON Logging** | Every AI call, response, and review logged to `/logs` |
| 🎭 **Demo Mode** | Works without an API key using pre-generated responses |
| ⬇️ **Export** | Download diagnosis as JSON, datasets as CSV |

---

## 🏗️ Architecture

```
NetSage-AI/
├── app.py                          # Home page + global CSS
├── requirements.txt
├── README.md
├── .env.example
├── assets/                         # Static assets
├── data/
│   ├── cases.csv                   # 30+ realistic Cisco PT cases
│   └── human_review_log.csv        # Human review records
├── prompts/
│   ├── diagnose_prompt.md          # Gemini system prompt
│   └── few_shot_examples.md        # 3 annotated examples
├── modules/
│   ├── ai_engine.py                # Gemini API + retry + Pydantic
│   ├── rule_checker.py             # 14 deterministic rules
│   ├── diagnosis.py                # Orchestrator
│   ├── dashboard.py                # Plotly chart builders
│   ├── csv_manager.py              # CSV CRUD
│   ├── prompt_loader.py            # .md file loader + composer
│   ├── logger.py                   # JSON event logger
│   └── utils.py                    # Shared helpers
├── pages/
│   ├── 1_AI_Diagnosis.py
│   ├── 2_Human_Review.py
│   ├── 3_Dashboard.py
│   ├── 4_Dataset_Manager.py
│   └── 5_About.py
├── output/                         # Downloaded files
└── logs/                           # JSON log files (auto-created)
```

---

## 🚀 Installation

### Prerequisites
- Python 3.12 or higher
- A Google Gemini API key ([get one free](https://aistudio.google.com/app/apikey))

### Steps

```bash
# 1. Navigate to the project directory
cd NetSage-AI

# 2. Create a virtual environment (recommended)
python -m venv .venv

# Activate on Windows
.venv\Scripts\activate

# Activate on macOS/Linux
source .venv/bin/activate

# 3. Install all dependencies
pip install -r requirements.txt

# 4. Configure your API key
copy .env.example .env
# Open .env and replace: GEMINI_API_KEY=your_actual_key_here

# 5. Launch the application
streamlit run app.py
```

The app will open at `http://localhost:8501`

---

## 🔐 Environment Variables

Create a `.env` file in the project root (copy from `.env.example`):

| Variable | Required | Default | Description |
|---|---|---|---|
| `GEMINI_API_KEY` | Yes* | — | Your Google Gemini API key |
| `GEMINI_MODEL` | No | `gemini-1.5-flash` | Gemini model to use |
| `LOG_LEVEL` | No | `INFO` | Logging verbosity |

> *If `GEMINI_API_KEY` is not set, the app runs in **Demo Mode** with pre-generated responses.

---

## 📖 How to Use

### 1. AI Diagnosis Page
1. Enter the network symptom description
2. Add topology notes (optional but improves accuracy)
3. Paste your Cisco `show` command outputs
4. Click **Run Diagnosis**
5. Review the rule checker findings and AI diagnosis cards
6. Download the diagnosis JSON or proceed to Human Review

### 2. Human Review Page
1. All pending diagnoses appear here after running AI Diagnosis
2. Read the AI's root cause, evidence, and fix steps
3. Choose: **Accept**, **Edit**, or **Reject**
4. If editing: modify the root cause, OSI layer, fix steps as needed
5. Add reviewer comments and submit
6. The review is saved to `human_review_log.csv`

### 3. Dashboard
- View live charts of issue types, OSI layer distribution, severity breakdown
- Track AI accuracy (acceptance rate) over time
- See the Responsible AI section for correction statistics

### 4. Dataset Manager
- Browse, search, and filter the 30+ built-in cases
- Add custom cases via the form
- Edit or delete existing rows
- Upload a CSV to import bulk cases
- Run the validation tool to check data integrity

---

## 🧠 AI Diagnosis Methodology

The AI engine follows OSI layer methodology:

```
Layer 1 (Physical) → Interface status, cable issues, clock rate
Layer 2 (Data Link) → VLANs, trunking, port security, STP, MAC
Layer 3 (Network)  → IP addressing, routing, NAT, subnetting
Layer 4 (Transport)→ ACLs filtering TCP/UDP ports
Layer 7 (Application)→ DHCP, DNS, HTTP, FTP services
```

The prompt instructs Gemini to:
- Never hallucinate — only use provided `show` output evidence
- Always assign a confidence score (0–100)
- Always suggest the next diagnostic command
- Return strictly valid JSON

---

## ⚙️ Rule Checker Rules

| Rule | Detection |
|---|---|
| `INTERFACE_SHUTDOWN` | `administratively down` in show output |
| `DUPLICATE_IP` | `%IP-4-DUPADDR` or duplicate address keywords |
| `WRONG_SUBNET_MASK` | `/8` or `/16` masks in /24 environments |
| `GATEWAY_MISMATCH` | Gateway mismatch keywords in symptom |
| `MISSING_DEFAULT_ROUTE` | No `S*` or `0.0.0.0/0` in routing table |
| `MISSING_VLAN` | Access VLAN not in VLAN database |
| `TRUNK_ACCESS_CONFLICT` | Both trunk and access mode on same port |
| `MISSING_TRUNK` | No trunking ports when expected |
| `VLAN_NOT_ALLOWED_ON_TRUNK` | Restricted VLAN allowed list on trunk |
| `DHCP_DISABLED` | `no service dhcp` or missing pool |
| `DHCP_POOL_MISSING` | `no ip dhcp pool` in config |
| `DNS_NOT_CONFIGURED` | DNS 0.0.0.0 or no name-server |
| `NAT_INSIDE/OUTSIDE_MISSING` | NAT config without interface markers |
| `OSPF_AREA_MISMATCH` | Different area IDs across routers |
| `OSPF_STUCK_STATE` | Neighbor in INIT/EXSTART state |
| `PORT_SECURITY_VIOLATION` | `Secure-shutdown` port status |
| `WRONG_VLAN_ASSIGNMENT` | Wrong VLAN keywords in symptom |

---

## 📊 Dataset

The built-in `cases.csv` contains **30 realistic Cisco Packet Tracer cases** covering:

VLAN · DHCP · DNS · ACL · Static Routing · OSPF · NAT · Wireless · Port Security · Trunking · Inter-VLAN Routing · Default Gateway · Duplicate IP · Subnet Mask · Gateway Mismatch · Missing Route · Interface Down · Incorrect VLAN Assignment · Access Port Issues · STP

Each case includes realistic Cisco `show` command outputs, expected fault description, and correct answer.

---

## 🔮 Future Improvements

- [ ] PDF export of diagnosis reports
- [ ] Multi-user authentication
- [ ] RAG (retrieval-augmented generation) from Cisco documentation
- [ ] Voice input for symptom description
- [ ] Integration with Cisco DevNet APIs for live device data
- [ ] Email alerts for critical severity diagnoses
- [ ] Case similarity search using embeddings
- [ ] Automated test suite for rule checker rules

---

## 📄 License

MIT License — free for educational and personal use.

---

## 👤 Author

Built as a university/hackathon demonstration project showcasing responsible AI in network engineering.
