# 🖼️ LinkedIn Image Gen Microservice

A high-performance, containerized Python microservice built with **FastAPI** and **Pillow** to dynamically generate professional social media images with custom gradients and precise typography.

![License](https://img.shields.io/badge/license-MIT-blue.svg)
![Python](https://img.shields.io/badge/python-3.11+-blue.svg)
![FastAPI](https://img.shields.io/badge/FastAPI-0.100+-green.svg)
![Docker](https://img.shields.io/badge/docker-ready-blue.svg)

---

## ✨ Features

- **🚀 FastAPI Powered:** High-performance asynchronous API returning raw binary image streams.
- **🎨 Dynamic Gradients:** Every image features a unique, programmatically generated dark diagonal gradient.
- **📏 Precise Layout Engine:** 
  - **Header:** Tiny font, top-left anchored.
  - **Title:** Large font, horizontally centered.
  - **Subtitle:** Medium font, centered below the title.
  - **Footer:** Tiny font, bottom-right anchored with smart bounding-box calculation.
- **🐳 Dockerized:** Includes `Dockerfile` and `docker-compose.yml` for instant deployment.
- **🛡️ Quality Assured:** Build-time testing with `pytest` ensures no broken images are ever deployed.
- **🔄 CI/CD Ready:** Pre-configured GitHub Actions for automated Docker Hub publishing.

---

## 🛠️ Tech Stack

- **Backend:** [FastAPI](https://fastapi.tiangolo.com/)
- **Image Processing:** [Pillow (PIL)](https://python-pillow.org/)
- **Testing:** [pytest](https://docs.pytest.org/)
- **Containerization:** [Docker](https://www.docker.com/) & [Docker Compose](https://docs.docker.com/compose/)
- **CI/CD:** [GitHub Actions](https://github.com/features/actions)

---

## 🚀 Getting Started

### Prerequisites

- Python 3.11+
- Docker (optional)

### Local Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/anushibinj/linkedin-image-gen.git
   cd linkedin-image-gen
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the server:**
   ```bash
   python main.py
   ```
   The API will be available at `http://localhost:8000`.

---

## 🐳 Docker Usage

### Build and Run
```bash
docker-compose up --build
```

### Run Tests (Automatic during Build)
The Docker build will **fail** if any unit tests fail, ensuring production stability.

---

## 🔌 API Reference

### Generate Image

**Endpoint:** `POST /generate`

**Request Body (JSON):**
```json
{
  "header": "TRENDING NOW",
  "title": "Mastering FastAPI",
  "subtitle": "Build high-performance microservices",
  "footer": "github.com/anushibinj"
}
```

**Response:**
Returns a raw `image/png` binary stream.

**Example Request (curl):**
```bash
curl -X POST "http://localhost:8000/generate" \
     -H "Content-Type: application/json" \
     -d '{"title": "Hello World", "subtitle": "Automated Design"}' \
     --output my-image.png
```

---

## 🧪 Testing

Run the test suite locally:
```bash
python -m pytest test_main.py
```

---

## 🚢 CI/CD Deployment

This project includes a GitHub Action in `.github/workflows/docker-publish.yml`. To enable it:

1. Push this repository to GitHub.
2. Add `DOCKER_HUB_USERNAME` and `DOCKER_HUB_TOKEN` to your repository's **Actions Secrets**.
3. On every push to `main`, the image will be built, tested, and pushed to Docker Hub.

---

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.
