import os
import json
from requests import request
from pprint import pprint
from feedgen.feed import FeedGenerator

class Episode:
    def __init__(
        self,
        video_id,
        title,
        description,
        channel_id,
        channel_title,
        thumbnail,
        published_at,
        publish_time):

        self.video_id = video_id
        self.title = title
        self.description = description
        self.channel_id = channel_id
        self.channel_title = channel_title
        self.thumbnail = thumbnail
        self.published_at = published_at
        self.publish_time = publish_time
        
class Podcrafter:
    def __init__(self, apikey):
        self.apikey = apikey
        self.config = self.get_config()
        self.episodes = self.get_episodes()
        self.feed = self.get_feed()
        self.rss = self.get_rss()
        self.atom = self.get_atom()

    def get_rss(self):
        return self.feed.rss_str(pretty=True)

    def get_atom(self):
        return self.feed.atom_str(pretty=True)

    def get_rss_file(self, filepath):
        return self.feed.rss_file(filepath)

    def get_atom_file(self, filepath):
        return self.feed.atom_file(filepath)

    def get_feed(self):
        fg = FeedGenerator()
        fg.id('https://github.com/JosephSamela/podcrafter')
        fg.title('podcrafter')
        fg.author( {'name':'podcrafter','email':'https://github.com/JosephSamela/podcrafter'} )
        fg.link( href='https://github.com/JosephSamela/podcrafter', rel='alternate' )
        fg.logo('https://github.com/JosephSamela/podcrafter/blob/main/thumbnail.jpg')
        fg.subtitle('Custom podcast feed of your favorite youtube shows!')
        fg.language('en')

        for episode in self.episodes:
            fe = fg.add_entry()
            fe.id(episode.video_id)
            fe.title(episode.title)
            fe.author(name=episode.channel_title)
            fe.description(episode.description)
            fe.published(episode.published_at)
            fe.enclosure(f'https://www.youtube.com/watch?v={episode.video_id}', 0, 'video/mpeg')

        return fg

    def get_episodes(self):
        episodes = []
        for channel in self.config:
                es = self.find_episodes(
                    channel_id= channel['channel_id'],
                    keywords= channel['keywords']
                )
                for e in es:
                    episodes.append(e)
        return episodes

    def get_config(self, path='./config.json'):
        with open(path, 'r') as config:
            return json.load(config)

    def get_channel_list(self, channel_id, limit=25):
        response = request(
            method='GET',
            url=f'https://www.googleapis.com/youtube/v3/search?order=date&part=snippet&channelId={channel_id}&maxResults={limit}&key={self.apikey}',
            headers={'Authorization': self.apikey}
        )
        return response.json()['items']

    def find_episodes(self, channel_id, keywords):
        episodes = []
        channel_list = self.get_channel_list(channel_id)
        
        for video in channel_list:
            for keyword in keywords:
                if keyword in video['snippet']['title']:
                    episodes.append(
                        Episode(
                            video_id      = video['id']['videoId'],
                            title         = video['snippet']['title'],
                            description   = video['snippet']['description'],
                            channel_id    = video['snippet']['channelId'],
                            channel_title = video['snippet']['channelTitle'],
                            thumbnail     = video['snippet']['thumbnails']['high']['url'],
                            published_at  = video['snippet']['publishedAt'],
                            publish_time  = video['snippet']['publishTime']
                        )
                    )
        return episodes

if __name__ == "__main__":

    apikey = os.getenv('YOUTUBE_API_KEY')

    if apikey is not None:
        p = Podcrafter(apikey)

        for e in p.episodes:
            print(f'{e.channel_title} | {e.title}')
        
        p.get_rss_file('rss.xml')
        p.get_atom_file('atom.xml')
    else:
        raise('API KEY NOT FOUND! Please specify youtube API key as environment variable "YOUTUBE_API_KEY".')