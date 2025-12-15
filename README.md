# Voice of the Customer 2.0: AI-Driven Listening for Strategic Banking Insights

A Flutter-based mobile and web application that provides banking insights powered by real customer feedback and discussions from Reddit. The platform features an AI-powered chatbot and data visualization tools to help understand customer sentiment and trending topics in banking.

In a world where consumers constantly share their experiences online, banks need smarter ways to tune in. This project invites teams to design an AI-driven solution that empowers banks to proactively understand what people are saying about their products, services, and brand - across the digital ecosystem - and convert that into actionable insights. The goal is to create a solution that continuously monitors, interprets, and translates digital conversations into structured intelligence that banks can use to improve customer experiences, develop new offerings, strengthen trust, and assess their public reputation. One approach could be to treat this as a classification problem, though other strategies are possible.

---

## 👥 Team Members

| Name | GitHub Handle | Contribution |
|-----|--------------|--------------|
| Surabhi Kuchibhotla | @surabhikuchibhotla  | Manage team and tasks (PM); ML testing |
| Charmi Buddaluru | @charmib7  | Data collection; ML Training & Testing |
| Enzo Weiss | @enzoweiss21 | App development; Data collection |
| Louisa Anjanette Auwlia | @anjanetttee | Product owner (PO); ML testing |
| Yasmin Kabir | @yasminkabir | ML model training and evaluation |
| Minakshi Thapa | @safalta1 | Data collection |
| Sharika Khaton | @skhaton | ML testing |

---

## 🎯 Project Highlights

- Utilized **GitHub** and **Google Colab** for collaborative code development, version control, and model experimentation.
- Used **Figma** and **Notion** to support product design, documentation, and project management workflows.
- Built the technical pipeline using **Python, Flutter, AWS, and Hugging Face** to support machine learning development, application integration, and deployment considerations.
- Developed a machine learning model using **Hugging Face RoBERTa-BERT** to extract **thematic categories** from scraped Reddit posts related to banking experiences.
- Achieved a **67% F1 score**, demonstrating the model’s effectiveness in identifying meaningful customer sentiment categories from noisy, real-world social media data.
- Generated actionable insights to surface the top five **banking-related customer insights**, enabling data-driven product and business decisions.
- Implemented **train–validation splitting, class balancing, and iterative model evaluation** to address real-world data imbalance and model performance constraints.
---

## 🌎 **Project Overview**

This project was developed as part of the **Break Through Tech AI Program – AI Studio.**
* Host Company: **Stealth Company**
* **Project Objective:** To build an AI-driven system capable of extracting structured insights from unstructured online banking-related conversations.
* **Scope:** Focused on categorizing and analyzing customer feedback from Reddit posts to surface key themes and insights relevant to banking institutions.

#### Real-World Significance
Banks receive vast amounts of unstructured feedback across digital platforms, making it difficult to extract actionable insights manually. This project demonstrates how machine learning can be used to systematically analyze customer sentiment and themes at scale, supporting improved decision-making and customer-centric product development.

---
## ⭐️ Features

- **Interactive Chat Interface**: Ask questions about banking insights and get AI-powered responses based on real customer discussions
- **Data Visualization**: View top 5 banking topics with detailed analytics including:
  - Weighted Popularity metrics
  - Post count statistics
  - Average engagement rates
- **Real-time Insights**: Access the latest banking trends and customer feedback
- **Cross-platform**: Available on iOS, Android, Web, macOS, Linux, and Windows

## 🏗️ Architecture

### Frontend (Flutter)
- **Framework**: Flutter 3.3.0+
- **Main Pages**:
  - Home: Welcome page with navigation instructions
  - Chat: AI-powered chatbot interface
  - Insights: Data visualization with bar charts

### Backend (Python FastAPI)
- **Framework**: FastAPI with Uvicorn
- **Key Components**:
  - Reddit scraper for banking-related discussions
  - OpenAI integration for chat responses
  - Vector search using Supabase (pgvector)
  - Synthetic LLM insights API

## 📋 Prerequisites

- Flutter SDK (>=3.3.0 <4.0.0)
- Python 3.8+
- Supabase account (for vector storage)
- OpenAI API key (for chat functionality)
- Gemini API key (for embeddings, optional)

## 🚀 Getting Started

### Backend Setup

1. Navigate to the backend directory:
```bash
cd backend
```

2. Create a virtual environment:
```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Set up environment variables:
Create a `.env` file in the `backend` directory:
```env
OPENAI_API_KEY=your_openai_api_key
GEMINI_API=your_gemini_api_key
PROJECT_URL=your_supabase_url
SUPABASE_API=your_supabase_key
```

5. Start the backend server:
```bash
uvicorn app.main:app --reload --port 8000
```

The API will be available at `http://127.0.0.1:8000`

### Frontend Setup

1. Install Flutter dependencies:
```bash
flutter pub get
```

2. Run the application:
```bash
# For web
flutter run -d chrome

# For iOS
flutter run -d ios

# For Android
flutter run -d android
```

3. Configure backend URL (optional):
By default, the app connects to `http://127.0.0.1:8000`. To change this, set the environment variable:
```bash
flutter run -d chrome --dart-define=VOC_BACKEND_URL=http://your-backend-url:8000
```

## 📡 API Endpoints

### Health Check
```
GET /health
```
Returns server status.

### Reddit Scraper
```
GET /reddit/{subreddit}?sort=hot|new|top|rising&time_filter=day&limit=20
```
Fetches posts from a specified subreddit.

### Chat
```
POST /chat
Body: { "message": "your question here" }
```
Sends a message to the AI chatbot and receives a contextual response.

### Banking Insights
```
GET /llm/banking-insights
```
Returns synthetic banking insights data for visualization.

## 🗄️ Database Setup

### Supabase Configuration

1. Enable the pgvector extension:
```sql
CREATE EXTENSION IF NOT EXISTS vector;
```

2. Create the posts table (see `backend/supabase_vector_search.sql` for full schema):
```sql
CREATE TABLE posts (
  id SERIAL PRIMARY KEY,
  title TEXT NOT NULL,
  body TEXT NOT NULL,
  embedding vector(768)
);
```

3. For embedding CSV data, see `backend/EMBEDDING_README.md`

## 📊 Data Sources

The application uses:
- **Reddit**: Scraped banking-related discussions from various subreddits
- **Vector Search**: Semantic search using embeddings stored in Supabase
- **Synthetic Data**: LLM-generated insights for demonstration purposes

## 🛠️ Development

### Project Structure

```
stealthbanking/
├── lib/
│   ├── main.dart              # Main Flutter app entry point
│   └── data/
│       ├── chat_service.dart  # Chat API client
│       ├── insights_repository.dart  # Insights API client
│       └── banking_insights.dart    # Data models
├── backend/
│   ├── app/
│   │   ├── main.py            # FastAPI application
│   │   ├── chatbot.py         # OpenAI chat integration
│   │   └── scraper.py         # Reddit scraper
│   ├── requirements.txt       # Python dependencies
│   └── EMBEDDING_README.md    # Embedding setup guide
└── README.md                  # This file
```

### Key Technologies

- **Frontend**: Flutter, Material Design 3
- **Backend**: FastAPI, Python
- **AI/ML**: OpenAI GPT, Google Gemini (embeddings)
- **Database**: Supabase (PostgreSQL with pgvector)
- **Data Source**: Reddit API

## 🚢 Deployment

### Web Deployment (Vercel)

See the deployment documentation:
- `VERCEL_DEPLOY.md` - General deployment guide
- `VERCEL_PUBLIC_DEPLOY.md` - Public deployment instructions
- `VERCEL_SETTINGS.md` - Vercel configuration
- `VERCEL_ALTERNATIVE.md` - Alternative deployment methods

### Backend Deployment

The FastAPI backend can be deployed to any Python hosting service:
- Heroku
- Railway
- Render
- AWS/GCP/Azure

Ensure environment variables are properly configured in your deployment platform.

## 📝 Notes

- The app uses CORS middleware for local development and Flutter web integration
- Synthetic data is stored in `backend/app/fake_llm_data.json`
- Reddit scraping may be rate-limited; adjust delays as needed
- Vector embeddings use Gemini's `embedding-001` model (768 dimensions)

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## 📄 License

This project is private and not licensed for public use.

## 🔗 Resources

- [Flutter Documentation](https://docs.flutter.dev/)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Supabase Documentation](https://supabase.com/docs)
- [OpenAI API Documentation](https://platform.openai.com/docs)

---

**Built with ❤️ for banking insights**
