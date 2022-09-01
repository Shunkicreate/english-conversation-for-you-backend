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
            content['text'] = ' '.join(words[i * one_phrase_len:i * one_phrase_len + one_phrase_len])
        else:
            content['text'] = ' '.join(words[i * one_phrase_len:])
    return result_obj

def obj2vtt(objs):
    vtt_file = 'WEBVTT\n\n'
    for i, obj in enumerate(objs):
        vtt_file += 'cue-id-{}\n'.format(i)
        start_timestamp = datetime.timedelta(seconds=obj['start'])
        end_timestamp = start_timestamp + datetime.timedelta(seconds=obj['duration'])
        vtt_file += '{} --> {}\n{}\n\n'.format(start_timestamp, end_timestamp, obj['text'])
    print(vtt_file)
    return vtt_file

@wrapt_timeout_decorator.timeout(dec_timeout=500)
def get_transcript_timeout(video_id, languages=['en']):
    print(video_id, languages)
    result_str = YouTubeTranscriptApi.get_transcript(
        video_id, languages=languages)
    if (not 'en' in languages):
        result_str = english_translator(result_str)
        # translator = Translator()
        # for i in result_str:
        #     print(i['text'])
        #     i['text'] = translator.translate(i['text'], dest="en").text
        #     print(i['text'])
        # print(result_str.translate('en'))
        # result_str = result_str.translate('en')
        # result_str = translator.translate(result_str, dest="en")
    result_str = obj2vtt(result_str)
    return result_str


def proc(video_id, languages=['en']):
    try:
        result = get_transcript_timeout(video_id, languages)
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


@app.route('/youtubeDlSubtitles', methods=['GET'])
@content_type('application/json')
def youtubeDlSubtitles():
    url = request.json['url']
    print(url)
    # print(srt.translate('en'))
    video_id = get_video_id(url)
    result_str = ""
    try:
        result_str = proc(video_id)
    except Exception as e:
        print(e)
    if (result_str == ""):
        try:
            result_str = proc(video_id, languages=['ja'])
        except Exception as e:
            print(e)

    # for transcript in transcript_list:
    # #英語の字幕を日本語に翻訳して出力
    #     print(transcript.translate('en').fetch())
    return str(result_str)


# run the app.
if __name__ == "__main__":
    # Setting debug to True enables debug output. This line should be
    # removed before deploying a production app.
    app.debug = True
    app.run()
