from flask import Flask
import os
from flask import Flask, abort, request, make_response, jsonify
import functools
from youtube_transcript_api import YouTubeTranscriptApi
from re import sub, search
import time
import timeout_decorator
# print a nice greeting.
def say_hello(username = "World"):
    return '<p>Hello %s!</p>\n' % username

# some bits of text for the page.
header_text = '''
    <html>\n<head> <title>EB Flask Test</title> </head>\n<body>'''
instructions = '''
    <p><em>Hint</em>: This is a RESTful web service! Append a username
    to the URL (for example: <code>/Thelonious</code>) to say hello to
    someone specific.</p>\n'''
home_link = '<p><a href="/">Back</a></p>\n'
footer_text = '</body>\n</html>'

# EB looks for an 'app' callable by default.
app = Flask(__name__)

def content_type(value):
    def _content_type(func):
        @functools.wraps(func)
        def wrapper(*args,**kwargs):
            if not request.headers.get("Content-Type") == value:
                error_message = {
                    'error': 'not supported Content-Type'
                }
                return make_response(jsonify(error_message), 400)

            return func(*args,**kwargs)
        return wrapper
    return _content_type

def get_video_id(url:str):
    pattern  = 'v=.*' 
    # pattern  = '5G' 
    video_id = search(pattern, url).group()
    video_id = sub('v=', '', video_id)
    if('&' in video_id):
        pattern = '.*&'
        video_id  = search(pattern, video_id).group()
        video_id = sub('&', '', video_id)
    return(video_id)

@timeout_decorator.timeout(10, timeout_exception=StopIteration)
def get_transcript_timeout(video_id, languages = ['en']):
    return YouTubeTranscriptApi.get_transcript(video_id,languages=[languages])

# add a rule for the index page.
app.add_url_rule('/', 'index', (lambda: header_text +
    say_hello() + instructions + footer_text))

# add a rule when the page is accessed with a name appended to the site
# URL.
app.add_url_rule('/<username>', 'hello', (lambda username:
    header_text + say_hello(username) + home_link + footer_text))

@app.route('/youtubeDlSubtitles', methods=['GET'])
@content_type('application/json')
def youtubeDlSubtitles():
    url = request.json['url']
    print(url)
    video_id = get_video_id(url)
    srt = get_transcript_timeout('yKrTY4AsB2c',languages=['ja'])
    print(srt.translate('en'))
    try:
        srt = get_transcript_timeout(video_id)
        
    except Exception as e:
        return(e)
    # for transcript in transcript_list:
    # #英語の字幕を日本語に翻訳して出力
    #     print(transcript.translate('en').fetch())
    return srt
# run the app.
if __name__ == "__main__":
    # Setting debug to True enables debug output. This line should be
    # removed before deploying a production app.
    app.debug = True
    app.run()