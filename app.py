from flask import Flask, render_template, request, jsonify
from pytubefix import YouTube
from pytubefix.cli import on_progress
import os
from moviepy.editor import VideoFileClip
import re
import traceback

app = Flask(__name__)

# Create downloads directory if it doesn't exist
DOWNLOADS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'downloads')
if not os.path.exists(DOWNLOADS_DIR):
    os.makedirs(DOWNLOADS_DIR)

def is_valid_youtube_url(url):
    # Regular expression pattern for YouTube URLs
    youtube_regex = r'(https?://)?(www\.)?(youtube|youtu|youtube-nocookie)\.(com|be)/(watch\?v=|embed/|v/|.+\?v=)?([^&=%\?]{11})'
    
    youtube_match = re.match(youtube_regex, url)
    return bool(youtube_match)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/download', methods=['POST'])
def download():
    try:
        url = request.form['url']
        format_type = request.form['format']
        
        # Validate YouTube URL
        if not is_valid_youtube_url(url):
            return jsonify({'error': 'Please enter a valid YouTube URL'}), 400
        
        try:
            # Initialize YouTube object
            yt = YouTube(url, on_progress_callback=on_progress)
            
            # Get video title and sanitize it for filename
            title = "".join(x for x in yt.title if x.isalnum() or x in (' ', '-', '_')).strip()
            
            if format_type == 'mp3':
                # Get the highest resolution stream
                stream = yt.streams.get_highest_resolution()
                video_path = stream.download(output_path=DOWNLOADS_DIR)
                
                # Convert to MP3
                video_clip = VideoFileClip(video_path)
                audio_path = os.path.join(DOWNLOADS_DIR, f"{title}.mp3")
                video_clip.audio.write_audiofile(audio_path)
                video_clip.close()
                
                # Clean up the video file
                try:
                    os.remove(video_path)
                except:
                    pass
                    
                return jsonify({'success': True})
            else:
                # Get the highest resolution stream for MP4
                stream = yt.streams.get_highest_resolution()
                video_path = stream.download(output_path=DOWNLOADS_DIR, filename=f"{title}.mp4")
                return jsonify({'success': True})
                
        except Exception as e:
            print(f"Error processing video: {str(e)}")
            print(traceback.format_exc())
            return jsonify({'error': f'Error processing video: {str(e)}'}), 400
            
    except Exception as e:
        print(f"Unexpected error: {str(e)}")
        print(traceback.format_exc())
        return jsonify({'error': f'An unexpected error occurred: {str(e)}'}), 400

if __name__ == '__main__':
    app.run(debug=True) 