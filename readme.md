# Bluesky AI Assistant Bot

An intelligent bot for Bluesky that processes mentions and provides AI-powered responses through various specialized agents. The project combines a Node.js server for Bluesky interaction and a Django-based ML API for intelligence features.

## 🚀 Features

- **Screenshot + Research Agent**: Analyzes shared content and provides contextual insights
- **Persona Simulation**: Generates responses mimicking specific writing styles or personalities
- **Thread Generation**: Creates engaging thread breakdowns on various topics
- **Fact Checking**: Verifies claims with supporting references
- **Sentiment Analysis**: Provides emotional context analysis for conversations
- **Meme Generation**: Suggests creative captions and meme formats
- **Context Translation**: Simplifies complex discussions into accessible language

## 🏗️ Project Structure

```
/
├── server/          # Node.js Bluesky Bot Server
│   ├── src/         # Source code
│   ├── package.json # Dependencies
│   └── yarn.lock    # Yarn lockfile
│
└── ML/             # Django ML API Service
    ├── api/        # API endpoints
    ├── models/     # ML models
    └── manage.py   # Django management script
```

## 🛠️ Technical Stack

### Server (Bluesky Bot)
- Node.js
- Yarn package manager
- Bluesky API integration
- WebSocket for real-time monitoring

### ML API (Intelligence Layer)
- Django REST Framework
- Python ML libraries
- Model serving infrastructure

## 🚦 Getting Started

### Prerequisites
- Node.js (v14 or higher)
- Python 3.8+
- Yarn package manager
- Bluesky account credentials
- Required ML model dependencies

### Installation

1. **Set up the Server**
```bash
cd server
yarn install
```

2. **Set up the ML API**
```bash
cd ML
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### Configuration

1. **Server Environment Variables**
```env
BLUESKY_IDENTIFIER=your-handle.bsky.social
BLUESKY_PASSWORD=your-app-password
ML_API_URL=http://localhost:8000
```

2. **ML API Environment Variables**
```env
DEBUG=True
SECRET_KEY=your-secret-key
ALLOWED_HOSTS=localhost,127.0.0.1
```

## 🔄 Usage Flow

1. Bot monitors Bluesky for new mentions
2. Mention triggers appropriate agent based on content
3. Request is sent to ML API for processing
4. Response is generated and posted back to Bluesky

## 🤖 Available Agents

### Screenshot + Research Agent
- Captures visual content
- Performs context analysis
- Generates insightful summaries

```python
# Example usage
@mention analyze_context [url]
```

### Impersonation Agent
- Analyzes writing patterns
- Mimics specific styles
- Generates contextual responses

```python
# Example usage
@mention simulate_style [persona_name]
```

### Thread Generator
- Identifies key points
- Structures coherent threads
- Optimizes for engagement

```python
# Example usage
@mention create_thread [topic] [length]
```

### Fact Checker
- Verifies claims
- Provides sources
- Highlights inaccuracies

```python
# Example usage
@mention fact_check [claim]
```

## 🧪 Testing

### Server Tests
```bash
cd server
yarn test
```

### ML API Tests
```bash
cd ML
python manage.py test
```





