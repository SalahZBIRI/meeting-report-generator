# Meeting Report Generator

> Developed by **Salah Eddine ZBIRI** — based on the FastAPI + Docker template.  
> Implements the **"Report Generator"** project with a full AI-powered meeting transcription and summarization pipeline.

---

## Project Overview

The **Meeting Report Generator** is an end-to-end API designed to automatically create structured, readable meeting reports from raw audio files.

It combines **speech recognition**, **intelligent summarization**, and **document generation** within a scalable **FastAPI + Docker** architecture.

---

## Workflow Overview

1. **Audio Transcription (Speech-to-Text)**  
   - Uses **OpenAI Whisper** to transcribe uploaded audio files into raw text.  
   - Handles multiple speakers and different accents.  
   - Outputs a full, timestamped transcript.

2. **Structured Report Generation (Summarization)**  
   - The transcribed text is processed by an **LLM (LLaMA-3.1 via Groq API)**.  
   - The model extracts:
     - Key discussion points  
     - Decisions made  
     - Actions to take  
   - Uses an **intelligent quota manager** to handle token limits and API rate restrictions dynamically.

3. **PDF Report Creation**  
   - Generates a clean, well-structured report.  
   - Combines transcription and summary into a final downloadable `.pdf`.

---

## System Architecture

The system is fully modular, allowing clear separation between the different responsibilities:

```
app/
├── api/               # Routers (auth, report, health)
├── core/              # Config, environment, and security
├── db/                # Database session and ORM base
├── models/            # SQLAlchemy models (User, Report)
├── schemas/           # Pydantic schemas
├── services/
│   ├── whisper_service.py     # Handles audio transcription
│   ├── summarizer_service.py  # LLM summarization (LLaMA/Groq)
│   ├── pdf_service.py         # Report generation (PyMuPDF / ReportLab)
│   └── report_service.py      # Orchestrates the workflow
└── utils/             # Caching, error handling, quota management
```

---

## 🐳 Installation (Docker Only)

> The project runs entirely inside Docker — no local installation needed.

### Prerequisites
- **Docker** and **Docker Compose** installed on your system.
- A `.env` file created from .env.example and completed with your API keys and environment variables

Example `.env` file:
```env
DEBUG=true
SECRET_KEY=your-secret-key
GROQ_API_KEY=your-groq-api-key
...
```

---

### Launch the Application

```bash
# Clone the repository
git clone https://github.com/SalahZBIRI/meeting-report-generator.git
cd meeting-report-generator

# Build and run the containers
docker-compose up --build
```

Once launched, the API will be available at:  
👉 [http://localhost:8000](http://localhost:8000)

**Swagger UI:** [http://localhost:8000/docs](http://localhost:8000/docs)  
**ReDoc:** [http://localhost:8000/redoc](http://localhost:8000/redoc)


---

## Test the API with `curl`

You can generate a meeting report directly from your terminal by uploading an audio file (for example `audio.wav`):

```bash
curl -X POST "http://localhost:8000/report/generate" -F "file=@audio.wav"
```

> Make sure the file `audio.wav` is located in your current working directory before running the command.

---


## API Endpoints

| Method | Endpoint           | Description                              |
|--------|--------------------|------------------------------------------|
| POST   | `/report/upload`   | Upload audio file → Generate meeting PDF |
| GET    | `/health`          | API health check                         |

---


## 👨‍💻 Author

**Salah Eddine ZBIRI**  
📧 zbirisalah10@gmail.com  
🔗 [GitHub Profile](https://github.com/SalahZBIRI)

---

## License

This project is distributed under the **MIT License**.
