from pytubefix import YouTube, Playlist
from pytubefix.cli import on_progress

url = "https://www.youtube.com/watch?v=PxwYcaahdq0&list=RDPxwYcaahdq0&start_radio=1"

def video(url):
    yt = YouTube(url, on_progress_callback=on_progress)
    print(yt.title)

    ys = yt.streams.get_highest_resolution()
    ys.download()

def audio(url):
    yt = YouTube(url, on_progress_callback=on_progress)
    print(yt.title)

    ys = yt.streams.get_audio_only()
    ys.download()

def playlist(url):
    pl = Playlist(url)
    for video in pl.videos:
        ys = video.streams.get_audio_only()
        ys.download()

