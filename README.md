# Product Launch Studio 🚀

Welcome to **Product Launch Studio**, an AI-assisted tool designed to streamline product compliance, listing creation, and asset generation for top e-commerce platforms (Amazon, Flipkart, and Meesho).

This workspace is a monorepo consisting of:
- **FastAPI Backend (`/backend`)**: Orchestrates platform rules validation, AI analysis via Google Gemini, Pillow image cleaning/enhancement, and packaging recommendations.
- **Next.js Frontend (`/frontend`)**: A sleek, high-fidelity React dashboard built with responsive dark-mode styling and features like one-click image downloads.

---

## Project Structure

```text
├── backend/                  # FastAPI Application
│   ├── app/                  # Main backend source code
│   ├── uploads/              # Local storage directory for media uploads (git-ignored)
│   ├── .env.example          # Environment variables template
│   └── requirements.txt      # Python dependencies
│
├── frontend/                 # Next.js Application
│   ├── app/                  # React App Router pages & styles
│   ├── components/           # Reusable UI components
│   └── package.json          # Node dependencies & dev scripts
│
└── .gitignore                # Workspace-level git rules (ignores builds, node_modules, envs)
```

---

## Getting Started

Follow the instructions below to set up and run both environments locally.

### 1. Run the Backend (FastAPI)

1. Open a terminal and navigate to the backend directory:
   ```bash
   cd backend
   ```
2. Create and activate a Python virtual environment:
   ```bash
   python -m venv .venv
   # Windows:
   .venv\Scripts\activate
   # macOS/Linux:
   source .venv/bin/activate
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Copy the `.env.example` file to `.env` and fill in your Gemini/Cloudinary credentials:
   ```bash
   cp .env.example .env
   ```
5. Run the dev server:
   ```bash
   uvicorn app.main:app --reload --port 8000
   ```
   *The interactive docs will be available at `http://localhost:8000/docs`.*

---

### 2. Run the Frontend (Next.js)

1. Open a new terminal and navigate to the frontend directory:
   ```bash
   cd frontend
   ```
2. Install npm dependencies:
   ```bash
   npm install
   ```
3. Run the development server:
   ```bash
   npm run dev
   ```
   *Open [http://localhost:3000](http://localhost:3000) in your browser to view the application.*

---

## Core Features

- **Platform Rules Engine**: Validates product listings against specific guidelines for **Amazon**, **Flipkart**, and **Meesho**.
- **Pillow-based Image Cleaning**: Processes uploaded product images to fit platform specifications (e.g. converting backgrounds, formatting) without visual hallucinations.
- **Gemini-powered Analysis**: Analyzes licenses, extracts details, assesses platform categorization, and estimates sweet-spot pricing.
- **One-click Image Downloads**: Download original or cleaned/enhanced assets directly to your computer with professional glassmorphic overlays.
