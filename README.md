# 🚀 AutoDev – Autonomous Multi-Agent Software Development System

AutoDev is an **agentic AI-based autonomous software development system** that transforms **high-level natural language requirements** into a **fully functional and deployed web application**.  
Unlike traditional AI coding assistants, AutoDev behaves like a **self-governing software agency**, powered by multiple specialized AI agents.

---

## 🧠 What is AutoDev?

AutoDev simulates a **real-world software development team** using AI agents.  
Each agent is responsible for a specific role in the software development lifecycle, enabling **end-to-end automation** while keeping the **human user in control**.

Instead of a single AI model doing everything, AutoDev uses:
- Multiple agents
- Persistent shared memory
- A state-machine-driven execution flow

---

## 🤖 Multi-Agent System

AutoDev consists of the following AI agents:

### 👨‍💼 Product Manager Agent
- Interacts directly with the user
- Refines vague ideas into concrete requirements
- Requires **explicit user permission** (`Proceed`) before execution

### 🧠 Architect Agent
- Designs the system architecture
- Generates:
  - `filestructure.json`
  - `tasks.md`
- Selects a lightweight, serverless tech stack

### 👨‍💻 Developer Agent
- Implements the project iteratively
- Writes HTML, CSS, and JavaScript
- Maintains awareness of the entire project context

### 🚀 Deployer Agent
- Deploys the project locally
- Starts a lightweight HTTP server
- Provides a live preview of the application

---

## 🏗️ System Architecture

AutoDev follows a **three-layer architecture**:

### 🖥️ Frontend (Interaction Layer)
- Chat interface for user communication
- Live preview pane for the running application
- Terminal/log pane showing agent activity

### ⚙️ Backend (Orchestration Layer)
- Built using **FastAPI**
- Uses **LangGraph** for state-machine orchestration
- Coordinates agent execution and shared state

### 🧠 Inference Layer (AI Models)
- Fast models for chat and intent recognition
- High-reasoning models for planning and coding
- Dynamic model routing based on task complexity

---

## 🔄 Execution Workflow

1. User provides a project idea
2. Manager agent gathers and refines requirements
3. User confirms execution (`Proceed`)
4. Architect agent creates structure and task plan
5. Developer agent writes code task-by-task
6. Deployer agent launches the application
7. Live preview is displayed to the user

The system supports **feedback loops**, allowing agents to revisit previous states if needed.

---

## ✨ Key Features

- ✅ Fully autonomous software generation
- ✅ Multi-agent coordination
- ✅ Persistent shared state (blackboard)
- ✅ Human-in-the-loop governance
- ✅ Zero-configuration deployment
- ✅ Modular and scalable design

---

## 🛠️ Tech Stack

- **Backend:** FastAPI, LangGraph  
- **Frontend:** HTML5, Tailwind CSS (CDN), Vanilla JavaScript  
- **AI Models:** Llama, Qwen, Kimi, Gemini  
- **Deployment:** Python HTTP Server  

---

## 📌 Why AutoDev?

AutoDev demonstrates the real-world application of **Agentic AI** by:
- Reducing developer cognitive load
- Eliminating context switching
- Automating the complete software lifecycle
- Enabling rapid prototyping and experimentation

---

## 🙌 Acknowledgements

Inspired by modern **Agentic AI architectures** and multi-agent orchestration frameworks.


