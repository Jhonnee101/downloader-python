from pytubefix import Playlist, YouTube

url = "https://www.youtube.com/playlist?list=PLW7-tbKCDBCw4RkbwF184CezrZLyHSrg9"
pl = Playlist(url)

for video_url in pl.video_urls:
    print("🎥", video_url)
    yt = YouTube(video_url)
    ys = yt.streams.get_highest_resolution()
    ys.download("./")
