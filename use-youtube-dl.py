import youtube_dl
ydl_opts = {
    
}
with youtube_dl.YoutubeDL(ydl_opts) as ydl:
    ydl.download(['https://www.youtube.com/watch?v=rqdHkPZnEv0'])