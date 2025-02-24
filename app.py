from flask import Flask, render_template, request
from googleapiclient.discovery import build
from textblob import TextBlob

app = Flask(__name__)

# Masukkan API Key di sini
API_KEY = 'AIzaSyBcemb0JmRgT70ivMJR2ooyR3_Lwlnse_0'
YOUTUBE_API_SERVICE_NAME = 'youtube'
YOUTUBE_API_VERSION = 'v3'

# Fungsi untuk mengambil komentar dari YouTube
def get_comments(video_id):
    youtube = build(YOUTUBE_API_SERVICE_NAME, YOUTUBE_API_VERSION, developerKey=API_KEY)
    comments = []

    request = youtube.commentThreads().list(
        part='snippet',
        videoId=video_id,
        maxResults=10000
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

# Route Utama
@app.route('/', methods=['GET', 'POST'])
def index():
    analyzed_comments = []
    sentiment_summary = {}
    
    if request.method == 'POST':
        video_url = request.form['video_url']
        video_id = video_url.split('v=')[1]
        
        comments = get_comments(video_id)
        analyzed_comments, sentiment_summary = analyze_sentiment(comments)
    
    return render_template('index.html', comments=analyzed_comments, summary=sentiment_summary)

if __name__ == '__main__':
    app.run(debug=True)
