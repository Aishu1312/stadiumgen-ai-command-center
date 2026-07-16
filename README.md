# WorldCup AI Command Center ⚽

> "The Intelligent Stadium Companion powered by Generative AI"

![WorldCup AI Command Center](assets/hero_image.png)

## Overview
A **production-grade, hackathon-winning** Streamlit application built for the FIFA World Cup 2026. This GenAI-powered smart stadium ecosystem enhances the experience for fans, organizers, volunteers, and security teams.

Recently upgraded with Enterprise-grade Architecture, Premium Glassmorphism UI, and strict Streamlit caching optimizations.

## 🌟 Features

- **AI Stadium Assistant**: Native streaming multilingual AI chatbot using Groq API.
- **Smart Navigation**: Interactive Folium stadium map with shortest paths.
- **Crowd Intelligence**: Plotly heatmaps and queue predictions (Cached).
- **AI Transport Planner**: Best routes, ETAs, and streaming travel advice.
- **Smart Accessibility**: Voice-guided generation and high-contrast modes.
- **Sustainability Intelligence**: Real-time tracking of waste and eco-reports.
- **Emergency AI Command**: Instant AI SOP generation for incidents.
- **Organizer Dashboard**: Live analytics and predictive time-series insights.

## 🏗️ Architecture

```text
WorldCup AI Command Center/
├── app.py                     # Main Entry with Session Initialization
├── pages/                     # 10 Interactive Streamlit Modules
├── config/                    # Configuration
│   ├── settings.py            # Global Settings
│   └── constants.py           # Static strings & AI Prompts
├── models/                    # Data Structures
│   └── data_models.py         # Data Classes
├── services/                  # Business Logic
│   ├── ai_service.py          # Groq AI API Wrapper (Streaming, Retry)
│   └── data_service.py        # Cached Mock Data Generation
├── components/                # Reusable UI
│   └── ui.py                  # Cards, KPIs, Skeletons, Toasts
└── assets/                    # Styling & Images
    └── style.css              # Premium Glassmorphism Theme
```

## 🛠️ Tech Stack

- **Frontend**: Streamlit, Custom CSS (Glassmorphism), Streamlit Folium
- **Backend**: Python 3.9+
- **AI**: Groq API (`groq`)
- **Optimization**: `@st.cache_data`, `@st.cache_resource`, `tenacity` retry logic
- **Data & Visualization**: Plotly, Folium, Pandas, Numpy

## 🚀 Installation & Deployment

This repository is strictly optimized for **Streamlit Community Cloud**.

1. **Clone the repository**
2. **Install requirements**:
   ```bash
   pip install -r requirements.txt
   ```
3. **Configure Environment**:
   - Create a `.env` file (or add to Streamlit Secrets):
     ```toml
     GROQ_API_KEY = "your_actual_api_key_here"
     ```
4. **Run the App**:
   ```bash
   streamlit run app.py
   ```

## 🔮 Future Scope
- Integration with live stadium APIs (IoT sensors).
- LangChain + FAISS Vector Database for RAG.
- Real-time facial emotion recognition for crowd panic detection.

## License
MIT License
