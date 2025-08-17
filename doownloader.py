from pytubefix import YouTube, Playlist
from pytubefix.cli import on_progress
import os

url = input("Enter the URL: ")
save_path = "C:\\Users\\joaobreno\\Music\\Audiolivros"

# Se o usuário não digitar nada, usa a pasta atual
if not save_path:
    save_path = os.getcwd()

def video(url):
    yt = YouTube(url, on_progress_callback=on_progress)
    print(f"📹 Baixando vídeo: {yt.title}")

    ys = yt.streams.get_highest_resolution()
    ys.download(output_path=save_path)

def audio(url):
    yt = YouTube(url, on_progress_callback=on_progress)
    print(f"🎵 Baixando áudio: {yt.title}")

    ys = yt.streams.get_audio_only()
    ys.download(output_path=save_path)

def playlist(url):
    pl = Playlist(url)
    print(f"📂 Playlist: {pl.title} - {len(pl.videos)} vídeos")
    for video in pl.videos:
        print(f"🎵 {video.title}")
        ys = video.streams.get_audio_only()
        ys.download(output_path=save_path)

audio(url)
