from re import sub, search
url = r'https://www.youtube.com/watch?v=PpqYYn2K1mQ&list=RDPpqYYn2K1mQ&start_radio=1'
pattern  = 'v=.*' 
# pattern  = '5G' 
video_id = search(pattern, url).group()
video_id = sub('v=', '', video_id)
pattern = '.*&'
video_id  = search(pattern, video_id).group()
video_id = sub('&', '', video_id)
print(video_id)