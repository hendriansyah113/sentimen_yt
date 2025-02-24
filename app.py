from flask import Flask, render_template, request
from googleapiclient.discovery import build
from textblob import TextBlob
from collections import Counter
import re
from routes.analisa_link import analisa_link_bp  # Import Blueprint

app = Flask(__name__)

# Masukkan API Key di sini
API_KEY = 'AIzaSyBcemb0JmRgT70ivMJR2ooyR3_Lwlnse_0'
YOUTUBE_API_SERVICE_NAME = 'youtube'
YOUTUBE_API_VERSION = 'v3'

# Fungsi untuk mencari video berdasarkan keyword
def search_videos(keyword):
    youtube = build(YOUTUBE_API_SERVICE_NAME, YOUTUBE_API_VERSION, developerKey=API_KEY)
    request = youtube.search().list(
        part='snippet',
        q=keyword,
        type='video',
        order='viewCount',
        maxResults=1
    )
    response = request.execute()
    
    video_id = None
    video_title = None
    if response['items']:
        video_id = response['items'][0]['id']['videoId']
        video_title = response['items'][0]['snippet']['title']
    
    return video_id, video_title

# Fungsi untuk mengambil komentar dari video YouTube
def get_comments(video_id):
    youtube = build(YOUTUBE_API_SERVICE_NAME, YOUTUBE_API_VERSION, developerKey=API_KEY)
    comments = []

    request = youtube.commentThreads().list(
        part='snippet',
        videoId=video_id,
        maxResults=50
    )
    response = request.execute()

    for item in response['items']:
        comment = item['snippet']['topLevelComment']['snippet']['textDisplay']
        comments.append(comment)

    return comments

# Fungsi Analisis Sentimen
def analyze_sentiment(comments):
    sentiment_results = {"positif": 0, "negatif": 0, "netral": 0}
    analyzed_comments = []

    for comment in comments:
        analysis = TextBlob(comment)
        polarity = analysis.sentiment.polarity
        
        if polarity > 0:
            sentiment = "positif"
            sentiment_results["positif"] += 1
        elif polarity < 0:
            sentiment = "negatif"
            sentiment_results["negatif"] += 1
        else:
            sentiment = "netral"
            sentiment_results["netral"] += 1

        analyzed_comments.append({"text": comment, "sentiment": sentiment})

    return analyzed_comments, sentiment_results

# Fungsi untuk Menghitung Frekuensi Kata
def get_word_frequencies(comments):
    all_comments = " ".join(comments)
    
    # Bersihkan teks: hilangkan simbol, angka, dan huruf kapital
    words = re.findall(r'\b[a-zA-Z]{3,}\b', all_comments.lower())
    
    # Hitung frekuensi kata
    word_count = Counter(words)
    
    # Ambil 10 kata paling sering muncul
    most_common_words = word_count.most_common(10)
    
    # Format data untuk Chart.js
    word_data = []
    for word, freq in most_common_words:
        word_data.append({"word": word, "freq": freq})
        
    return word_data

# Route Utama
@app.route('/', methods=['GET', 'POST'])
def index():
    analyzed_comments = []
    sentiment_summary = {}
    video_title = None
    word_data = []

    if request.method == 'POST':
        keyword = request.form['keyword']
        video_id, video_title = search_videos(keyword)
        
        if video_id:
            comments = get_comments(video_id)
            analyzed_comments, sentiment_summary = analyze_sentiment(comments)
            
            # Dapatkan Data Word Cloud
            word_data = get_word_frequencies(comments)
    
    return render_template('index.html', comments=analyzed_comments, summary=sentiment_summary, video_title=video_title, word_data=word_data)

# Register Blueprint
app.register_blueprint(analisa_link_bp)

if __name__ == '__main__':
    app.run(debug=True)
