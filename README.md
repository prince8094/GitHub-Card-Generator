# GitHub Card Generator 🚀

A full-stack application that generates beautiful, customized profile cards for GitHub users. Simply enter a GitHub username to get a dynamically generated card displaying their stats, top languages, and more!

## 🌟 Live Demo
- **Frontend:** [https://frontend-394280732575.us-central1.run.app](https://frontend-394280732575.us-central1.run.app)
- **Backend API:** [https://backend-394280732575.us-central1.run.app](https://backend-394280732575.us-central1.run.app)

---

## 🛠️ Technologies Used
- **Frontend:** HTML5, CSS3, Vanilla JavaScript
- **Backend:** Python 3.12, FastAPI, Uvicorn
- **Dependency Management:** `uv`
- **Deployment & Infrastructure:** Docker, Google Cloud Run, Google Artifact Registry

---

## 💻 Local Development

### Prerequisites
- Docker and Docker Compose
- Python 3.12 (if running locally without Docker)
- A GitHub Personal Access Token (for increasing API rate limits)
- A Google API Key (if using specific generative AI features)

### Setup Instructions

1. **Clone the repository:**
   ```bash
   git clone https://github.com/prince8094/GitHub-Card-Generator.git
   cd GitHub-Card-Generator
   ```

2. **Configure Environment Variables:**
   Copy the example environment file and fill in your keys in the `backend` directory:
   ```bash
   cp backend/.env.example backend/.env
   ```
   Open `backend/.env` and add your `GITHUB_TOKEN` and `GOOGLE_API_KEY`.

3. **Run using Docker Compose:**
   You can easily spin up both the frontend and backend using Docker Compose from the root directory:
   ```bash
   docker-compose up --build
   ```

4. **Access the Application:**
   - **Frontend:** `http://localhost:80`
   - **Backend API:** `http://localhost:8080`

---

## 🚀 Deployment

This application is configured for seamless deployment to **Google Cloud Run** as two separate services (frontend and backend). 

The Cloud Run deployment configuration uses:
- Buildpacks / Dockerfile builds via Cloud Build
- Custom `.dockerignore` and `.gcloudignore` files to keep source uploads blazing fast.

---

## 📄 License
This project is open-source and available under the MIT License.