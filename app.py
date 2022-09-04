from flask import Flask
import os
from flask import Flask, abort, request, make_response, jsonify
import functools
from youtube_transcript_api import YouTubeTranscriptApi
from re import sub, search, split
import time
import wrapt_timeout_decorator
import traceback  # デバッグ用
from googletrans import Translator
import datetime
from flask_cors import CORS
# print a nice greeting.


def say_hello(username="World"):
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
CORS(app, origins=["https://example.com",
     "http://localhost:3000", "http://localhost:3001"])


def content_type(value):
    def _content_type(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            if not request.headers.get("Content-Type") == value:
                error_message = {
                    'error': 'not supported Content-Type'
                }
                return make_response(jsonify(error_message), 400)
            return func(*args, **kwargs)
        return wrapper
    return _content_type


def get_video_id(url: str):
    pattern = 'v=.*'
    # pattern  = '5G'
    video_id = search(pattern, url).group()
    video_id = sub('v=', '', video_id)
    if ('&' in video_id):
        pattern = '.*&'
        video_id = search(pattern, video_id).group()
        video_id = sub('&', '', video_id)
    return (video_id)


def english_translator(result_obj):
    unite = ""
    for i in result_obj:
        unite += i['text']
    translator = Translator()
    result = translator.translate(unite, dest="en").text
    words = split('[. ]', result)
    one_phrase_len = int(len(words)/len(result_obj)) + 1
    for i, content in enumerate(result_obj):
        if (i != len(result_obj) - 1):
            content['text'] = ' '.join(
                words[i * one_phrase_len:i * one_phrase_len + one_phrase_len])
        else:
            content['text'] = ' '.join(words[i * one_phrase_len:])
    return result_obj


def obj2vtt(objs):
    vtt_file = 'WEBVTT\n\n'
    for i, obj in enumerate(objs):
        vtt_file += 'cue-id-{}\n'.format(i)
        start_timestamp = datetime.timedelta(seconds=obj['start'])
        end_timestamp = start_timestamp + \
            datetime.timedelta(seconds=obj['duration'])
        vtt_file += '{} --> {}\n{}\n\n'.format(
            start_timestamp, end_timestamp, obj['text'])
    print(vtt_file)
    return vtt_file


@wrapt_timeout_decorator.timeout(dec_timeout=500)
def get_transcript_timeout(video_id):
    # result_str = YouTubeTranscriptApi.get_transcript(video_id)
    # srt = YouTubeTranscriptApi.get_transcript("SW14tOda_kI")
    print(video_id)
    # retrieve the available transcripts
    languages = []
    transcript_list = YouTubeTranscriptApi.list_transcripts(video_id)
    for transcript in transcript_list:
        if(transcript.language == '英語'):
            en_result_str = transcript.fetch()
            languages.append('英語')
        if(transcript.language == '英語 (自動生成)'):
            auto_en_result_str = transcript.fetch()
            languages.append('英語 (自動生成)')
        if(transcript.language == 'スペイン語'):
            es_result_str = transcript.translate('en').fetch()
            languages.append('スペイン語')
        if(transcript.language == 'フランス語'):
            fr_result_str = transcript.translate('en').fetch()
            languages.append('フランス語')
        if(transcript.language == 'ドイツ語'):
            de_result_str = transcript.translate('en').fetch()
            languages.append('ドイツ語')
        if(transcript.language == 'イタリア語'):
            it_result_str = transcript.translate('en').fetch()
            languages.append('イタリア語')
        if(transcript.language == '日本語'):
            ja_result_str = transcript.translate('en').fetch()
            languages.append('日本語')
    if('英語' in languages):
        return obj2vtt(en_result_str)
    elif('英語 (自動生成)' in languages):
        return obj2vtt(auto_en_result_str)
    elif('スペイン語' in languages):
        return obj2vtt(es_result_str)
    elif('フランス語' in languages):
        return obj2vtt(fr_result_str)
    elif('ドイツ語' in languages):
        return obj2vtt(de_result_str)
    elif('イタリア語' in languages):
        return obj2vtt(it_result_str)
    elif('日本語' in languages):
        return obj2vtt(ja_result_str)
    else:
        for transcript in transcript_list:
            return obj2vtt(transcript.translate('en').fetch())
        
    return ""


def proc(video_id):
    try:
        result = get_transcript_timeout(video_id)
    except TimeoutError as e:
        result = e.__class__.__name__
        print(result)
        print(traceback.format_exception_only(type(e), e)[0].rstrip('\n'))
    else:
        print('no errors')
    return result


# add a rule for the index page.
app.add_url_rule('/', 'index', (lambda: header_text +
                 say_hello() + instructions + footer_text))

# add a rule when the page is accessed with a name appended to the site
# URL.
app.add_url_rule('/<username>', 'hello', (lambda username: header_text +
                 say_hello(username) + home_link + footer_text))


@app.route('/youtubeDlSubtitles', methods=['POST'])
@content_type('application/json')
def youtubeDlSubtitles():
    print(request.get_json())
    url = request.json['url']
    print(url)
    video_id = get_video_id(url)
    result_str = ""
    result_str = proc(video_id)

    return str(result_str)


# run the app.
if __name__ == "__main__":
    # Setting debug to True enables debug output. This line should be
    # removed before deploying a production app.
    app.debug = True
    app.run(host='127.0.0.1', port=5000)
