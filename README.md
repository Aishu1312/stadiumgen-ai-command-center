# WorldCup AI Command Center ⚽

> "The Intelligent Stadium Companion powered by Generative AI"

![WorldCup AI Command Center](https://images.unsplash.com/photo-1518605368461-1e96f01df22e?q=80&w=1200&auto=format&fit=crop) *(Placeholder Image)*

## Overview
A hackathon-winning, production-ready Streamlit application built for the FIFA World Cup 2026. This GenAI-powered smart stadium ecosystem enhances the experience for fans, organizers, volunteers, and security teams.

## 🌟 Features

- **AI Stadium Assistant**: Multilingual AI chatbot using Gemini API.
- **Smart Navigation**: Interactive stadium map with shortest paths.
- **Crowd Intelligence**: Simulated crowd density heatmaps and queue predictions.
- **AI Transport Planner**: Best routes, ETAs, and carbon emission estimates.
- **Smart Accessibility**: Features for visually impaired and wheelchair users.
- **Sustainability Intelligence**: Real-time tracking of waste and energy.
- **Emergency AI Command**: Priority scoring and AI SOP generation for incidents.
- **Organizer Dashboard**: Live analytics and predictive insights.

## 🏗️ Architecture

```text
WorldCup AI Command Center/
├── app.py                     # Main Streamlit application
├── pages/                     # App Views
├── components/                # Reusable UI Components
├── utils/                     # Data Simulators
├── ai/                        # GenAI integration
├── assets/                    # Styling & Images
└── ...
```

## 🛠️ Tech Stack

- **Frontend**: Streamlit, Custom CSS (Glassmorphism), Streamlit Option Menu, Lottie
- **Backend**: Python
- **AI**: Google Gemini API (`google-generativeai`)
- **Data & Visualization**: Plotly, Folium, Pandas, Numpy

## 🚀 Installation & Deployment

1. **Clone the repository**
2. **Install requirements**:
   ```bash
   pip install -r requirements.txt
   ```
3. **Configure Environment**:
   - Rename `.env.example` to `.env` and add your `GEMINI_API_KEY`.
4. **Run the App**:
   ```bash
   streamlit run app.py
   ```

## 🔮 Future Scope
- Integration with live stadium APIs (IoT sensors).
- Digital Twin 3D view.
- Real-time facial emotion recognition for crowd panic detection.
