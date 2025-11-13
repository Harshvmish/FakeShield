# FakeShield - Scam Message Detector

## Overview
FakeShield is a Flask web application that detects fake or scam messages in English, Hindi, and Hinglish using Natural Language Processing (NLP). The application uses TF-IDF vectorization and Naive Bayes classification to identify potentially malicious messages.

## Project Status
**Status:** Production Ready
**Last Updated:** November 13, 2025
**Deployment Target:** Render

## Features
- Multi-language support (English, Hindi, Hinglish)
- Real-time scam detection with confidence scores
- Language detection with Hinglish support
- Detailed analysis with reasoning for predictions
- Educational content about scam patterns
- Prediction logging to CSV file
- Mobile-responsive design
- Bottom navigation for easy access

## Technology Stack
- **Backend:** Flask 3.0.3
- **ML Libraries:** scikit-learn 1.5.1, numpy 1.26.4
- **Language Detection:** langdetect 1.0.9
- **Production Server:** Gunicorn 21.2.0
- **Python Version:** 3.11.9

## Project Structure
```
FakeShield/
├── app.py                 # Main Flask application
├── requirements.txt       # Python dependencies
├── runtime.txt           # Python version specification
├── templates/            # HTML templates
│   ├── index.html       # Message input page
│   ├── result.html      # Detection result page
│   └── learn.html       # Learning center
├── static/              # Static assets
│   └── style.css        # Shared CSS styling
└── logs.csv             # Prediction logs (auto-generated)
```

## Key Components

### Machine Learning Model
- **Algorithm:** Multinomial Naive Bayes
- **Vectorization:** TF-IDF with bigrams (1-2 word patterns)
- **Training Data:** 60+ multilingual examples
- **Features:** 500 max features
- **Preprocessing:** Lowercase, punctuation removal, whitespace normalization

### Routes
- `/` - Home page with message input
- `/result` - Detection results display
- `/learn` - Educational content about scams
- `/predict` (POST) - API endpoint for predictions

### Language Detection
- Uses langdetect library for base detection
- Custom Hinglish detection heuristics
- Supports English, Hindi, and Hinglish mixed scripts

## Render Deployment
The application is fully configured for Render deployment:
- PORT environment variable support
- Host binding to 0.0.0.0
- Gunicorn for production serving
- Python 3.11.9 runtime specified

## Recent Changes
- Initial project creation (Nov 13, 2025)
- Implemented complete Flask backend with NLP model
- Created responsive frontend with three pages
- Added multilingual training dataset
- Configured for Render deployment
- Implemented session-based result passing
- Added prediction logging functionality

## Architecture Decisions
1. **Session Storage:** Using Flask sessions to pass prediction data between routes (simple, stateless deployment)
2. **Model Training:** Model trains on app startup from synthetic dataset (fast, no external dependencies)
3. **CSV Logging:** Simple file-based logging for prediction tracking
4. **Client-Side Navigation:** JavaScript fetch API for seamless UX
5. **Responsive Design:** Mobile-first CSS with bottom navigation

## Running Locally
```bash
python app.py
```
The app will run on http://0.0.0.0:5000

## Running on Render
Deploy with:
- Build Command: (none required)
- Start Command: `gunicorn app:app`
- Environment: Python 3.11.9

## User Preferences
None specified yet.
