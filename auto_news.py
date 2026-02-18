import firebase_admin
from firebase_admin import credentials, db
import requests
import google.generativeai as genai
import datetime

# --- CONFIGURATION (FILL THESE IN) ---
import firebase_admin
from firebase_admin import credentials, db
import requests
import google.generativeai as genai
import datetime
import os
FIREBASE_KEY_PATH = "firebase_key.json" # The file you downloaded from Firebase

# IMPORTANT: Use your specific Asian database URL
DATABASE_URL = "https://news-website-da961-default-rtdb.asia-southeast1.firebasedatabase.app"

# --- SETUP ---
# 1. Initialize Firebase
cred = credentials.Certificate(FIREBASE_KEY_PATH)
firebase_admin.initialize_app(cred, {
    'databaseURL': DATABASE_URL
})

# 2. Configure AI
genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel('gemini-pro')

def fetch_and_publish():
    print("1. Fetching latest news...")
    # Fetch top business/tech news from US (you can change category/country)
    url = f"https://newsapi.org/v2/top-headlines?country=us&category=technology&apiKey={NEWS_API_KEY}"
    response = requests.get(url)
    data = response.json()

    if data['status'] != 'ok' or not data['articles']:
        print("No news found!")
        return

    # Get the top article
    article = data['articles'][0]
    original_title = article['title']
    original_desc = article['description'] or "No description available."
    
    print(f"Found Article: {original_title}")

    # 3. Use AI to Rewrite
    print("2. rewriting with AI...")
    
    prompt = f"""
    You are a professional news reporter. Rewrite the following news story into a short, engaging blog post (approx 100 words).
    Make the title catchy but factual.
    
    Original Title: {original_title}
    Original Context: {original_desc}
    
    Output format:
    TITLE: (New Title Here)
    CONTENT: (New Content Here)
    """

    ai_response = model.generate_content(prompt)
    text_result = ai_response.text

    # Parse AI response (Simple parsing logic)
    try:
        lines = text_result.split('\n')
        new_title = lines[0].replace("TITLE:", "").strip().replace("*", "")
        new_content = "\n".join(lines[1:]).replace("CONTENT:", "").strip()
    except:
        # Fallback if AI formatting fails
        new_title = original_title
        new_content = original_desc

    # 4. Push to Firebase
    print("3. Publishing to Firebase...")
    
    now = datetime.datetime.now()
    date_string = now.strftime("%B %d, %Y, %I:%M %p")

    ref = db.reference('posts')
    ref.push({
        'title': new_title,
        'content': new_content,
        'date': date_string,
        'timestamp': {".sv": "timestamp"} # Server timestamp
    })

    print("SUCCESS: News published automatically!")

if __name__ == "__main__":

    fetch_and_publish()
