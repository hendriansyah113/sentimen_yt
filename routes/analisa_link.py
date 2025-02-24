from flask import Blueprint, render_template, request
from youtube_analysis import get_comments, analyze_sentiment

# Inisialisasi Blueprint
analisa_link_bp = Blueprint('analisa_link', __name__)

# Route untuk Analisa Link
@analisa_link_bp.route('/analisa-link', methods=['GET', 'POST'])
def analisa_link():
    analyzed_comments = []
    sentiment_summary = {}
    video_title = None
    
    if request.method == 'POST':
        video_url = request.form['video_url']
        video_id = video_url.split('v=')[1]
        
        comments = get_comments(video_id)
        analyzed_comments, sentiment_summary = analyze_sentiment(comments)
    
    return render_template('analisa_link.html', comments=analyzed_comments, summary=sentiment_summary, video_title=video_title)
