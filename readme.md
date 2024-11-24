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

Celebrity Impersonation - Working Mechanism
Core Workflow

Celebrity Selection
pythonCopy# System maintains a database of celebrity profiles:
celebrities = [
    {
        "id": 1,
        "name": "Elon Musk",
        "background": "Tech visionary...",
        "tone": "Raw, unfiltered...",
        "speaking_style": "Blunt technical metaphors...",
        "emotional_range": [...],
        "example_tweets": [...]
    },
    # More celebrities...
]

Request Processing
pythonCopy@api_view(['POST'])
def generate_impersonation(request):
    # Extract data
    celebrity_id = request.data.get('celebrity_id')
    tweet = request.data.get('tweet')

    # Find matching celebrity profile
    celebrity = next((c for c in celebrities if c['id'] == celebrity_id), None)

Impersonation Generation
pythonCopy# Initialize AI agent with specific settings
agent = CelebrityImpersonationAgent(
    api_key=settings.GOOGLE_API_KEY,
    temperature=0.7  # Controls response creativity
)

# Generate response using celebrity profile
response = agent.impersonate(tweet, celebrity)

Response Storage
pythonCopy# Store generated response
new_impersonation = {
    "id": len(impersonations) + 1,
    "celebrity_name": celebrity['name'],
    "input_tweet": tweet,
    "response": response
}
impersonations.append(new_impersonation)


Key Components
1. Celebrity Profiles

Contains personality traits
Writing style patterns
Example tweets for reference
Emotional range indicators

2. Impersonation Agent

Uses celebrity profile data
Analyzes input tweet
Generates contextual response
Maintains celebrity's tone and style

3. Response Generation
Input → Processing → Output

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





