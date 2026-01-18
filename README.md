# Docent AI

## Overview

Docent AI is a full-stack document intelligence platform that enables users to query, summarize, and explore large document collections using a **multi-agent workflow**. The platform combines a retrieval-augmented generation (RAG) pipeline with LLM-powered response synthesis and orchestrates tasks using a custom multi-agent system composed of a planner, executor, and evaluator.

The project is designed for **modularity**, **reliability**, and **maintainable development workflows**, showcasing end-to-end expertise in full-stack development, AI/ML integration, system design, containerization, and CI/CD.

## Key Features

- **Full-stack Application**: React (Vite + TypeScript) frontend with FastAPI backend
- **Multi-Agent Workflow**: Planner, executor, and evaluator agents for intelligent task orchestration
- **RAG Pipeline**: Document ingestion, vector search, and LLM-based response generation
- **Enterprise Features**: API authentication, rate limiting, and comprehensive logging
- **Containerized Deployment**: Docker support for consistent environments
- **CI/CD Pipeline**: GitHub Actions for automated testing, building, and deployment to AWS

## Architecture

### System Components

```
┌─────────────────────────────────────────────────────────────┐
│                         Frontend (React)                     │
│                  (Vite + TypeScript + Tailwind)             │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│                    API Gateway (FastAPI)                    │
├─────────────────────────────────────────────────────────────┤
│  Auth │ Rate Limiting │ Logging │ Tracing                   │
└─────────┬──────────────┬──────────────┬─────────────────────┘
          │              │              │
    ┌─────▼──┐     ┌─────▼──┐    ┌─────▼──┐
    │ Multi- │     │  RAG   │    │  LLM   │
    │ Agent  │     │Pipeline│    │ Module │
    │Orchestr.     │        │    │        │
    └─────────┘     └─────────┘    └────────┘
          │
    ┌─────▼──────────────┐
    │  Vector Database   │
    │    (FAISS)         │
    └────────────────────┘
```

### Core Components

**Frontend**
- React with Vite for fast development and optimized builds
- TypeScript for type safety
- Tailwind CSS for responsive UI
- Query submission, document exploration, and result visualization

**Backend Services**
- FastAPI with async/await for high-performance API endpoints
- Modular architecture with clear separation of concerns
- Services for document management and query processing

**Multi-Agent Orchestration**
- **Planner**: Analyzes user queries and determines processing steps
- **Executor**: Performs actions like document retrieval and LLM calls
- **Evaluator**: Validates results and determines if further processing is needed
- **Verifier**: Cross-checks outputs for quality and accuracy

**Data Pipeline**
- Document ingestion with support for PDFs and multiple formats
- Embedding generation using sentence transformers
- Vector storage with FAISS for efficient similarity search
- LLM integration for context-aware response generation

**Observability**
- Structured logging with contextual information
- Timing metrics for performance monitoring
- Distributed tracing support

## Project Structure

```
docent-ai/
├── .github/
│   └── workflows/
│       ├── build-test-deploy.yml    # Unified Workflow documentation
├── backend/
│   ├── app/
│   │   ├── main.py                  # Application entry point
│   │   ├── agents/                  # Multi-agent orchestration
│   │   │   ├── planner.py
│   │   │   ├── executor.py
│   │   │   ├── evaluator.py
│   │   │   └── verifier.py
│   │   ├── api/                     # API routes
│   │   │   ├── router.py
│   │   │   └── routes/
│   │   │       ├── documents.py
│   │   │       ├── query.py
│   │   │       └── health.py
│   │   ├── rag/                     # RAG pipeline
│   │   │   ├── loader.py
│   │   │   ├── chunker.py
│   │   │   ├── embeddings.py
│   │   │   ├── vectorstore.py
│   │   │   └── ingest.py
│   │   ├── llm/                     # LLM integration
│   │   │   ├── client.py
│   │   │   └── prompts/
│   │   ├── services/                # Business logic
│   │   ├── auth/                    # Authentication & rate limiting
│   │   ├── tools/                   # Tool registry for agents
│   │   ├── observability/           # Logging & tracing
│   │   ├── core/                    # Configuration
│   │   └── schemas/                 # Data models
│   ├── storage/                     # Local storage for documents
│   ├── Dockerfile
│   ├── requirements.txt
│   └── .env.example
├── frontend/
│   ├── src/
│   │   ├── main.tsx
│   │   ├── App.tsx
│   │   ├── components/              # Reusable React components
│   │   ├── pages/                   # Page components
│   │   ├── services/                # API client
│   │   ├── types/                   # TypeScript interfaces
│   │   └── assets/
│   ├── public/
│   ├── package.json
│   ├── vite.config.ts
│   ├── tailwind.config.js
│   ├── tsconfig.json
│   ├── Dockerfile
│   └── index.html
├── docker-compose.yml               # Local 
```

## Getting Started

### Prerequisites

- **Python** 3.11 or higher
- **Node.js** 18 or higher
- **Docker** & **Docker Compose**
- **Git**

### Installation

#### 1. Clone the Repository

```bash
git clone https://github.com/yourusername/docent-ai.git
cd docent-ai
```

#### 2. Backend Setup

Navigate to the backend directory:

```bash
cd backend
```

Install Python dependencies:

```bash
pip install -r requirements.txt
```

Create a `.env` file with required environment variables:

```bash
cp .env.example .env
```

Edit `.env` and add your configuration:

```env
OPENAI_API_KEY=your_api_key_here
DATABASE_URL=postgresql://user:password@localhost/docent_ai
REDIS_URL=redis://localhost:6379
LOG_LEVEL=INFO
```

Run the backend server:

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

The API will be available at `http://localhost:8000`

#### 3. Frontend Setup

Navigate to the frontend directory:

```bash
cd frontend
```

Install Node.js dependencies:

```bash
npm install
```

Create a `.env.local` file:

```env
VITE_API_BASE=http://localhost:8000
```

Start the development server:

```bash
npm run dev
```

The application will be available at `http://localhost:5173`

### Local Development with Docker Compose

Build and run both services using Docker Compose:

```bash
docker-compose up --build
```

This will start:
- Backend API on `http://localhost:8000`
- Frontend on `http://localhost:3000`

The services are configured with health checks and automatic restart.

### Available Scripts

**Backend**
```bash
uvicorn app.main:app --reload        # Start development server
pytest                                 # Run tests
black app/                             # Format code
flake8 app/                            # Lint code
```

**Frontend**
```bash
npm run dev                            # Start dev server
npm run build                          # Build for production
npm run lint                           # Run ESLint
npm test                               # Run tests
npm run preview                        # Preview production build
```

## Multi-Agent Workflow

The system uses a sophisticated multi-agent orchestration pattern:

### Workflow Steps

1. **User Query Reception** → Frontend sends query to backend
2. **Planning** → Planner agent analyzes query and creates action plan
3. **Execution** → Executor agent performs planned actions
   - Document retrieval from vector database
   - LLM-based processing and synthesis
4. **Evaluation** → Evaluator agent validates results
5. **Verification** → Verifier agent ensures quality and accuracy
6. **Response Generation** → Final response is structured and returned

### Example Query Flow

```
User Query: "Summarize the key findings in the uploaded documents"
    ↓
Planner: "I need to: 1) retrieve all documents, 2) extract key sections, 3) summarize"
    ↓
Executor: Retrieves documents from vector store and calls LLM
    ↓
Evaluator: Checks if summary is complete and relevant
    ↓
Verifier: Validates factual accuracy against source documents
    ↓
Response: Structured summary with citations
```

## RAG Pipeline

The Retrieval-Augmented Generation pipeline enables intelligent document processing:

### Pipeline Stages

1. **Document Ingestion**
   - Accepts PDF and text documents
   - Extracts text and metadata
   - Stores in structured format

2. **Chunking**
   - Splits documents into semantic chunks
   - Preserves context and document metadata
   - Configurable chunk size and overlap

3. **Embedding Generation**
   - Uses SentenceTransformer models
   - Creates vector embeddings for semantic search
   - Efficient batch processing

4. **Vector Storage**
   - Stores embeddings in FAISS index
   - Enables fast similarity search
   - Persistent storage for vector database

5. **Retrieval**
   - Semantic search based on query embeddings
   - Configurable similarity threshold and result limits
   - Document ranking and relevance scoring

6. **Response Generation**
   - Passes retrieved context to LLM
   - Generates grounded, contextual responses
   - Citations and source tracking

## API Endpoints

### Document Management
- `POST /api/v1/documents/upload` - Upload a document
- `GET /api/v1/documents` - List all documents
- `DELETE /api/v1/documents/{id}` - Delete a document

### Query Processing
- `POST /api/v1/query` - Submit a query
- `GET /api/v1/query/{id}` - Get query results

### Health & Status
- `GET /api/v1/health` - Health check

## CI/CD Pipeline

The project uses GitHub Actions for automated testing, building, and deployment.

### Workflow Overview

**Trigger**: Push to `main`/`develop` or pull request

1. **Testing Phase**
   - Backend: Python linting, formatting checks, unit tests
   - Frontend: ESLint, TypeScript compilation, tests

2. **Build Phase**
   - Build Docker images for backend and frontend
   - Push to Amazon ECR

3. **Deployment Phase** (main branch only)
   - Update ECS task definitions
   - Deploy to AWS ECS cluster
   - Run smoke tests
   - Notify on completion

See [.github/workflows/README.md](.github/workflows/README.md) for detailed configuration instructions.

## Deployment to AWS

### Prerequisites

1. AWS Account with appropriate permissions
2. ECR repositories for backend and frontend
3. ECS cluster and service configured
4. GitHub OIDC provider configured for AWS

### Quick Setup

1. Configure GitHub secrets:
   ```
   AWS_ACCOUNT_ID
   AWS_ROLE_TO_ASSUME
   VITE_API_BASE
   API_URL
   FRONTEND_URL
   ```

2. Update AWS region in workflow if needed

3. Push to `main` branch to trigger deployment

For detailed AWS setup instructions, see [.github/workflows/README.md](.github/workflows/README.md)

## Environment Variables

### Backend (.env)

```env
# LLM Configuration
OPENAI_API_KEY=your_api_key
LLM_MODEL=gpt-4

# Database
DATABASE_URL=postgresql://user:password@localhost/docent_ai

# Redis (optional, for caching)
REDIS_URL=redis://localhost:6379

# Application
LOG_LEVEL=INFO
DEBUG=false

# API Configuration
API_PORT=8000
API_HOST=0.0.0.0
```

### Frontend (.env.local)

```env
VITE_API_BASE=http://localhost:8000
```

## Development Workflow

### Code Quality

The project enforces code quality through:

- **Linting**: flake8 for Python, ESLint for TypeScript
- **Formatting**: black for Python, Prettier for TypeScript
- **Type Safety**: mypy for Python, TypeScript for frontend
- **Testing**: pytest for backend, Jest for frontend

### Running Quality Checks

**Backend**
```bash
black app/
isort app/
flake8 app/
pytest
```

**Frontend**
```bash
npm run lint
npm run build
npm test
```

## Monitoring & Logging

The platform includes comprehensive observability:

- **Structured Logging**: JSON-formatted logs with context
- **Timing Metrics**: Performance monitoring for agent steps
- **Distributed Tracing**: Request tracing across services
- **CloudWatch Integration**: AWS CloudWatch log groups

View logs:
```bash
docker-compose logs -f backend
docker-compose logs -f frontend
```