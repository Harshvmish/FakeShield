from flask import Flask, render_template, request, jsonify, session, redirect, url_for
import re
import string
from datetime import datetime
import csv
import os
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.naive_bayes import MultinomialNB
from sklearn.pipeline import Pipeline
import numpy as np

from langdetect import detect, LangDetectException

app = Flask(__name__)
app.secret_key = "dev-key"

training_data = [
    ("Congratulations! You've won $1,000,000! Click here to claim now!", "scam", "en"),
    ("Your account has been suspended. Verify immediately or lose access.", "scam", "en"),
    ("URGENT: Your package is waiting. Pay $5 customs fee now!", "scam", "en"),
    ("Limited time offer! Get rich quick with this amazing opportunity!", "scam", "en"),
    ("You have inherited $10 million from a distant relative. Send details.", "scam", "en"),
    ("Your bank account needs verification. Click this link immediately.", "scam", "en"),
    ("Free iPhone! Just pay shipping. Only 2 left in stock!", "scam", "en"),
    ("Act now! Triple your income working from home!", "scam", "en"),
    ("FINAL NOTICE: Legal action will be taken unless you pay now.", "scam", "en"),
    ("You won the lottery! Send your bank details to claim prize.", "scam", "en"),
    ("Hi! Are we still meeting for coffee tomorrow at 3pm?", "safe", "en"),
    ("The project deadline has been extended to next Friday.", "safe", "en"),
    ("Thanks for your help today. I really appreciate it!", "safe", "en"),
    ("Can you pick up some milk on your way home?", "safe", "en"),
    ("Meeting scheduled for Monday 10am in conference room B.", "safe", "en"),
    ("Happy birthday! Hope you have a wonderful day!", "safe", "en"),
    ("The report is ready for your review. Please check your email.", "safe", "en"),
    ("Dinner tonight at 7pm? Let me know if you can make it.", "safe", "en"),
    ("Your Amazon order has shipped and will arrive tomorrow.", "safe", "en"),
    ("Reminder: Doctor appointment on Wednesday at 2pm.", "safe", "en"),
    
    ("बधाई हो! आपने 10 लाख रुपये जीते हैं! अभी क्लेम करें!", "scam", "hi"),
    ("आपका खाता निलंबित कर दिया गया है। तुरंत वेरीफाई करें!", "scam", "hi"),
    ("जरूरी: आपका पैकेज इंतजार कर रहा है। अभी 500 रुपये भुगतान करें!", "scam", "hi"),
    ("सीमित समय का ऑफर! इस अद्भुत अवसर से जल्दी अमीर बनें!", "scam", "hi"),
    ("आपके बैंक खाते को वेरिफिकेशन की जरूरत है। यह लिंक क्लिक करें!", "scam", "hi"),
    ("मुफ्त आईफोन! बस शिपिंग का भुगतान करें!", "scam", "hi"),
    ("अभी करें! घर से काम करके अपनी आय तीन गुना करें!", "scam", "hi"),
    ("अंतिम नोटिस: भुगतान न करने पर कानूनी कार्रवाई होगी।", "scam", "hi"),
    ("नमस्ते! क्या हम कल 3 बजे कॉफी के लिए मिल रहे हैं?", "safe", "hi"),
    ("प्रोजेक्ट की समय सीमा अगले शुक्रवार तक बढ़ा दी गई है।", "safe", "hi"),
    ("आज आपकी मदद के लिए धन्यवाद। मैं वास्तव में इसकी सराहना करता हूं!", "safe", "hi"),
    ("घर आते समय कुछ दूध ले आना?", "safe", "hi"),
    ("सोमवार सुबह 10 बजे कॉन्फ्रेंस रूम बी में मीटिंग है।", "safe", "hi"),
    ("जन्मदिन मुबारक हो! आपका दिन शानदार हो!", "safe", "hi"),
    
    ("Congratulations bhai! Aapne 5 lakh jeete hain! Abhi claim karo!", "scam", "hinglish"),
    ("Your account suspend ho gaya hai. Turant verify karo!", "scam", "hinglish"),
    ("URGENT: Aapka package wait kar raha hai. 500 rupay payment karo abhi!", "scam", "hinglish"),
    ("Limited offer hai! Isse jaldi ameer bano!", "scam", "hinglish"),
    ("Aapke bank account ko verification chahiye. Is link pe click karo!", "scam", "hinglish"),
    ("Free iPhone milega! Bas shipping pay karo!", "scam", "hinglish"),
    ("Abhi karo! Ghar se kaam karke income triple karo!", "scam", "hinglish"),
    ("Final notice hai! Payment nahi kiya toh legal action hoga.", "scam", "hinglish"),
    ("Hi! Kya hum kal 3 baje coffee ke liye mil rahe hain?", "safe", "hinglish"),
    ("Project ki deadline next Friday tak extend ho gayi hai.", "safe", "hinglish"),
    ("Aaj tumhari help ke liye thanks yaar!", "safe", "hinglish"),
    ("Ghar aate time thoda milk le aana?", "safe", "hinglish"),
    ("Monday 10am ko conference room B mein meeting hai.", "safe", "hinglish"),
    ("Happy birthday! Tumhara din awesome ho!", "safe", "hinglish"),
]

messages = [msg for msg, _, _ in training_data]
labels = [label for _, label, _ in training_data]

model = Pipeline([
    ('tfidf', TfidfVectorizer(lowercase=True, max_features=500, ngram_range=(1, 2))),
    ('classifier', MultinomialNB())
])

model.fit(messages, labels)

def preprocess_text(text):
    text = text.lower()
    text = re.sub(f'[{re.escape(string.punctuation)}]', ' ', text)
    text = ' '.join(text.split())
    return text

def detect_language(text):
    try:
        lang_code = detect(text)
        
        hinglish_indicators = ['hai', 'hain', 'ho', 'ka', 'ki', 'ke', 'aap', 'karo', 'kar', 'se', 'mein', 'pe']
        english_words = len([w for w in text.lower().split() if w.isascii() and w.isalpha()])
        hindi_words = len([w for w in text.split() if not w.isascii()])
        
        if english_words > 0 and hindi_words > 0:
            return "Hinglish"
        elif any(indicator in text.lower().split() for indicator in hinglish_indicators) and english_words > 0:
            return "Hinglish"
        
        lang_map = {
            'en': 'English',
            'hi': 'Hindi',
            'ne': 'Hinglish',
            'mr': 'Hindi'
        }
        return lang_map.get(lang_code, 'English')
    except:
        return "English"

def get_scam_reasons(text, prediction):
    reasons = []
    text_lower = text.lower()
    
    scam_keywords = {
        'en': ['urgent', 'congratulations', 'won', 'prize', 'lottery', 'claim', 'suspended', 
               'verify', 'account', 'click here', 'act now', 'limited time', 'million', 
               'inheritance', 'free', 'pay now', 'customs fee', 'legal action', 'final notice'],
        'hi': ['बधाई', 'जीते', 'क्लेम', 'निलंबित', 'वेरीफाई', 'खाता', 'जरूरी', 'अभी', 
               'सीमित', 'लाख', 'मुफ्त', 'भुगतान', 'कानूनी', 'अंतिम'],
        'hinglish': ['claim', 'verify', 'urgent', 'abhi', 'jaldi', 'free', 'turant', 
                     'suspend', 'payment', 'legal', 'final', 'congratulations', 'jeete']
    }
    
    all_keywords = scam_keywords['en'] + scam_keywords['hi'] + scam_keywords['hinglish']
    found_keywords = [kw for kw in all_keywords if kw in text_lower]
    
    if prediction == "scam":
        if found_keywords:
            reasons.append(f"Contains suspicious keywords: {', '.join(found_keywords[:3])}")
        if any(word in text_lower for word in ['click', 'link', 'verify', 'account']):
            reasons.append("Requests immediate action or verification")
        if any(word in text_lower for word in ['won', 'prize', 'lottery', 'million', 'inheritance']):
            reasons.append("Promises unrealistic rewards or prizes")
        if any(word in text_lower for word in ['urgent', 'final', 'immediately', 'now', 'abhi', 'turant']):
            reasons.append("Creates sense of urgency")
        if any(word in text_lower for word in ['suspended', 'blocked', 'legal action', 'expire']):
            reasons.append("Uses threatening or fear-inducing language")
        
        if not reasons:
            reasons.append("Message pattern matches known scam templates")
    else:
        reasons.append("No suspicious keywords or patterns detected")
        reasons.append("Message appears to be normal communication")
        reasons.append("Language is conversational and genuine")
    
    return reasons[:4]

def log_prediction(message, prediction, confidence, language):
    log_file = 'logs.csv'
    file_exists = os.path.isfile(log_file)
    
    try:
        with open(log_file, 'a', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            if not file_exists:
                writer.writerow(['Timestamp', 'Message', 'Prediction', 'Confidence', 'Language'])
            writer.writerow([
                datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                message[:100],
                prediction,
                f"{confidence:.2f}%",
                language
            ])
    except Exception as e:
        print(f"Logging error: {e}")

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/result')
def result():
    prediction = session.get('prediction', 'Safe Message')
    confidence = session.get('confidence', 0)
    language = session.get('language', 'English')
    reasons = session.get('reasons', [])
    message = session.get('message', '')
    
    return render_template('result.html', 
                         prediction=prediction,
                         confidence=confidence,
                         language=language,
                         reasons=reasons,
                         message=message)

@app.route('/learn')
def learn():
    return render_template('learn.html')

@app.route('/predict', methods=['POST'])
def predict():
    try:
        data = request.get_json()
        message = data.get('message', '').strip()
        
        if not message:
            return jsonify({'error': 'Message is required'}), 400
        
        preprocessed = preprocess_text(message)
        
        prediction_label = model.predict([preprocessed])[0]
        probabilities = model.predict_proba([preprocessed])[0]
        
        scam_idx = list(model.named_steps['classifier'].classes_).index('scam')
        confidence = probabilities[scam_idx] * 100
        
        if prediction_label == "safe":
            confidence = probabilities[1 - scam_idx] * 100
        
        prediction_text = "Likely Scam" if prediction_label == "scam" else "Safe Message"
        
        language = detect_language(message)
        
        reasons = get_scam_reasons(message, prediction_label)
        
        log_prediction(message, prediction_text, confidence, language)
        
        session['prediction'] = prediction_text
        session['confidence'] = round(confidence, 2)
        session['language'] = language
        session['reasons'] = reasons
        session['message'] = message
        
        return jsonify({
            'prediction': prediction_text,
            'confidence': round(confidence, 2),
            'language': language,
            'reasons': reasons
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == "__main__":
    import os
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
