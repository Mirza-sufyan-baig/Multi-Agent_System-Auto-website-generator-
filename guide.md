# 📘 AutoDev Studio: System Architecture & Developer Guide

## 1. System Overview
**AutoDev Studio** is a Multi-Agent System (MAS) designed to autonomously build, fix, and deploy web applications. Unlike standard chatbots, it uses a graph-based architecture (**LangGraph**) where agents have distinct roles, responsibilities, and the ability to reject/fix each other's work (Self-Healing).

*   **Goal:** Create a "Lovable.dev" or "Bolt.new" clone that generates production-ready code.
*   **Core Tech:** Python (FastAPI), LangGraph, LangChain, TailwindCSS, Vanilla JS.
*   **Key Differentiator:** The **Self-Healing Deployment Loop** (The Deployer acts as QA).

---

## 2. The Agent Roster (The "Employees")

Each agent acts as a specialized worker in a software agency.

### 🤖 1. Manager Agent (`src/agents/manager.py`)
*   **Role:** Product Manager & Client Interface.
*   **Responsibility:**
    *   Talks to the user.
    *   Classifies intent (Discovery vs. Execution vs. Editing).
    *   Maintains the "Context" (merges new requirements with old ones).
    *   **Crucial:** It is the *only* agent that speaks to the user.
*   **Tech:** LLM (Generative).
*   **Output:** JSON Object `{status, response, requirements}`.

### 🏗️ 2. Architect Agent (`src/agents/architect.py`)
*   **Role:** Tech Lead & UI/UX Designer.
*   **Responsibility:**
    *   Translates vague requirements into a technical plan (`plan.md`).
    *   Enforces the "2025 Design System" (Bento grids, Glassmorphism, Tailwind).
    *   **Crucial:** Generates the **Task List** that the Developer *must* follow.
*   **Tech:** LLM (Generative).
*   **Output:** Markdown Plan + List of Tasks.

### 💻 3. Developer Agent (`src/agents/developer.py`)
*   **Role:** Senior Frontend Developer.
*   **Responsibility:**
    *   Reads the Plan and existing files.
    *   Writes actual code (`index.html`, `script.js`).
    *   Uses **Regex** to ensure files are written correctly.
    *   **Crucial:** Handles "Urgent Fix Requests" from the Deployer.
*   **Tech:** LLM (Generative).
*   **Output:** Physical files written to `workspace/`.

### 🚀 4. Deployer Agent (`src/agents/deployer.py`)
*   **Role:** DevOps & QA Engineer.
*   **Responsibility:**
    *   **Validation:** Checks if `index.html` exists and is not empty.
    *   **Deployment:** Spins up a Python HTTP server on a dynamic port (8001+).
    *   **Self-Healing:** If validation fails, it **rejects** the build and sends it back to the Developer.
*   **Tech:** **Deterministic Python Logic** (No LLM).
*   **Why Python?** To prevent hallucinations. A file either exists or it doesn't.

---

## 3. The Workflow Logic (The Assembly Line)

The system runs on a **State Graph** defined in `src/graph.py`.

### A. The Happy Path (Success)
1.  **User:** "Build a coffee shop site."
2.  **Manager:** Classifies as `EXECUTION`. Passes requirements to Architect.
3.  **Architect:** Creates `plan.md` and defines tasks: `[Create index.html]`.
4.  **Developer:** Reads task, generates HTML code.
5.  **Deployer:** Checks folder -> Finds `index.html` -> Starts Server on Port 8001.
6.  **Manager:** Receives URL -> Tells User: "Site is ready at localhost:8001".

### B. The Self-Healing Path (Failure & Fix)
1.  **Developer:** Hallucinates and forgets to write `index.html`.
2.  **Deployer:**
    *   Check: `os.path.exists("index.html")` -> **False**.
    *   Action: Sets status to `NEEDS_FIX`. Adds `fix_request` to state.
3.  **Graph Router:** Sees `NEEDS_FIX` -> Sends back to **Developer**.
4.  **Developer:**
    *   Input: "URGENT: index.html is missing."
    *   Action: Prioritizes this fix and writes the file.
5.  **Deployer:** Check -> **True**. Starts Server. Success.

---

## 4. File Structure Overview

*   **`app.py`**: The Brain. Handles WebSockets, API endpoints, and static file serving.
*   **`src/graph.py`**: The Orchestrator. Connects nodes and defines the loops.
*   **`src/nodes.py`**: The Logic Wrappers. Bridges the raw Agents to the Graph state.
*   **`src/prompts.py`**: The Persona Definitions. Controls the "vibe" and rules (e.g., using Tailwind brackets `bg-[#...]`).
*   **`static/`**: The Frontend.
    *   `index.html`: The layout (Sidebar + Chat + Preview).
    *   `js/app.js`: Connects to WebSocket, handles Iframe reloading.

---

## 5. Presentation Talking Points (Cheat Sheet)

Use these points to impress your professors/judges:

1.  **The Problem with LLMs:** "LLMs are great at writing code, but they are 'fire and forget'. They often say they did something (hallucination) when they actually didn't."
2.  **Our Solution (Self-Healing):** "We didn't just build a chatbot. We built a **Closed-Loop System**. Our 'Deployer' agent is deterministic—it verifies the file actually exists on the disk. If not, it autonomously forces the Developer agent to fix it."
3.  **Modular Architecture:** "We separated the *Planner* (Architect) from the *Coder* (Developer). This mimics a real software team. The Planner ensures the design is modern (2025 style), while the Developer focuses on syntax."
4.  **Modern UX:** "We built a React-like Single Page Application using Vanilla JS that supports real-time preview, device toggling, and project history, similar to industry leaders like Bolt.new."

---

## 6. How to Demo

1.  **Start:** Run `python app.py`. Open `localhost:3000`.
2.  **Create:** Click `+`. Prompt: *"Build a portfolio for a photographer named Alex. Dark theme."*
3.  **Show:** Watch the logs. Point out "Architect designing..." and "Developer writing...".
4.  **Result:** When the site loads, click the "Mobile" icon to show responsiveness.
5.  **Edit:** Type *"Change the background to dark blue."* Show that it updates the existing site without breaking it.

