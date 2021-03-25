# encoding: utf-8
import urllib.request
import re
import pafy
import vlc
from time import sleep

class MusicPlayer:
    def __init__(self):
        self.base_url = "https://www.youtube.com/"
        self.instance = vlc.Instance()
        self.player = self.instance.media_player_new()
        self.keep_playing = True

    def play_song(self, artist, song):
        self.player.stop()
        search_text = f"{artist.replace(' ', '+')}+{song.replace(' ', '+')}"
        html_data = urllib.request.urlopen(self.base_url + f"results?search_query={search_text}")
        search_results = re.findall(r"watch\?v=(\S{11})", html_data.read().decode())
        if len(search_results) > 0:

            link = f"https://www.youtube.com/watch?v={search_results[0]}"
            video = pafy.new(link)
            best = video.getbestaudio()
            play_link = best.url

            media = self.instance.media_new(play_link)
            media.get_mrl()
            self.player.set_media(media)
            self.player.play()
            sleep(3)

        return None

    def stop(self):
        self.player.stop()



