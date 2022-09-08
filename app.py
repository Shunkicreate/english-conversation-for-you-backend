from flask import Flask, request, make_response, jsonify
import functools
from youtube_transcript_api import YouTubeTranscriptApi
from re import sub, search, split
import wrapt_timeout_decorator
import traceback  # デバッグ用
import datetime
from flask_cors import CORS

def say_hello(username="World"):
    return '<p>Hello %s!</p>\n' % username

header_text = '''
    <html>\n<head> <title>EB Flask Test</title> </head>\n<body>'''
instructions = '''
    <p><em>Hint</em>: This is a RESTful web service! Append a username
    to the URL (for example: <code>/Thelonious</code>) to say hello to
    someone specific.</p>\n'''
home_link = '<p><a href="/">Back</a></p>\n'
footer_text = '</body>\n</html>'

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

def shorterVTT(objs, lengths):
    newobj = []
    for i in range(0, len(objs) - lengths + 1, lengths):
        addobj = {
            'start': 0,
            'text': "",
            'duration': 0
        }
        for j in range(i, i + lengths):
            if (i == j):
                addobj['start'] += objs[j]['start']
            addobj['text'] += objs[j]['text']
            addobj['duration'] += objs[j]['duration']
        newobj.append(addobj)
    remainder = len(objs) % lengths
    if(remainder):
        addobj = {
            'start': 0,
            'text': "",
            'duration': 0
        }
        for i in range(remainder):
            if (i == 0):
                addobj['start'] += objs[len(objs) - remainder + i]['start']
            addobj['text'] += objs[len(objs) - remainder + i]['text']
            addobj['duration'] += objs[len(objs) - remainder + i]['duration']
        newobj.append(addobj)
            
    return newobj

def obj2vtt(objs):
    obj = shorterVTT(objs, 2)
    vtt_file = 'WEBVTT\n\n'
    for i, obj in enumerate(objs):
        vtt_file += 'cue-id-{}\n'.format(i)
        start_timestamp = datetime.timedelta(seconds=obj['start'])
        end_timestamp = start_timestamp + \
            datetime.timedelta(seconds=obj['duration'])
        vtt_file += '{} --> {}\n{}\n\n'.format(
            start_timestamp, end_timestamp, obj['text'])
    return vtt_file


@wrapt_timeout_decorator.timeout(dec_timeout=500)
def get_transcript_timeout(video_id):
    languages = []
    transcript_list = YouTubeTranscriptApi.list_transcripts(video_id)
    for transcript in transcript_list:
        if (transcript.language == '英語'):
            en_result_str = transcript.fetch()
            languages.append('英語')
        if (transcript.language == '英語 (自動生成)'):
            auto_en_result_str = transcript.fetch()
            languages.append('英語 (自動生成)')
        if (transcript.language == 'スペイン語'):
            es_result_str = transcript.translate('en').fetch()
            languages.append('スペイン語')
        if (transcript.language == 'フランス語'):
            fr_result_str = transcript.translate('en').fetch()
            languages.append('フランス語')
        if (transcript.language == 'ドイツ語'):
            de_result_str = transcript.translate('en').fetch()
            languages.append('ドイツ語')
        if (transcript.language == 'イタリア語'):
            it_result_str = transcript.translate('en').fetch()
            languages.append('イタリア語')
        if (transcript.language == '日本語'):
            ja_result_str = transcript.translate('en').fetch()
            languages.append('日本語')
    if ('英語' in languages):
        return obj2vtt(en_result_str)
    elif ('英語 (自動生成)' in languages):
        return obj2vtt(auto_en_result_str)
    elif ('スペイン語' in languages):
        return obj2vtt(es_result_str)
    elif ('フランス語' in languages):
        return obj2vtt(fr_result_str)
    elif ('ドイツ語' in languages):
        return obj2vtt(de_result_str)
    elif ('イタリア語' in languages):
        return obj2vtt(it_result_str)
    elif ('日本語' in languages):
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

app.add_url_rule('/', 'index', (lambda: header_text +
                 say_hello() + instructions + footer_text))

app.add_url_rule('/<username>', 'hello', (lambda username: header_text +
                 say_hello(username) + home_link + footer_text))


@app.route('/youtubeDlSubtitles', methods=['POST'])
@content_type('application/json')
def youtubeDlSubtitles():
    url = request.json['url']
    video_id = get_video_id(url)
    result_str = ""
    result_str = proc(video_id)
    return str(result_str)

if __name__ == "__main__":
    app.debug = True
    app.run(host='127.0.0.1', port=5000 ssl_context=('cert.pem', 'key.pem'))
