# Stitch 🧵

AI-powered social media content generation and scheduling platform.

## Features

- **AI Content Generation** - Generate engaging social media posts using Claude
- **LinkedIn Integration** - OAuth authentication and direct posting
- **Campaign Management** - Organize content into campaigns
- **Content Calendar** - Schedule and manage post timing

## Tech Stack

- **Backend**: FastAPI (Python 3.12)
- **Frontend**: Next.js 14 + Tailwind CSS
- **Database**: PostgreSQL 16
- **Cache**: Redis 7
- **AI**: Anthropic Claude API

## Quick Start

### Prerequisites
- Docker & Docker Compose
- LinkedIn Developer App (for OAuth)
- Anthropic API Key

### Setup

1. Clone the repo
```bash
git clone https://github.com/yourusername/stitch.git
cd stitch
```

2. Configure environment
```bash
cp .env.example .env
# Edit .env with your credentials
```

3. Start services
```bash
docker compose up -d
```

4. Access the app
- Frontend: http://localhost:3002
- API: http://localhost:8001
- API Docs: http://localhost:8001/docs

## Development

### Backend
```bash
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

### Frontend
```bash
cd frontend
npm install
npm run dev
```

## Deployment

See [Coolify deployment guide](docs/coolify-deployment.md) for production setup.

## License

MIT
