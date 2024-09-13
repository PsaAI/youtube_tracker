# app.py

import feedparser
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import Base, Video
import os
from datetime import datetime
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)

# List of YouTube channel IDs to track
channel_ids = [
    'UChpleBmo18P08aKCIgti38g',  # Matt Wolfe
    'UCui4jxDaMb53Gdh-AZUTPAg',  # Liam Ottley
    # Add more channel IDs here
]

# Database setup
DATABASE_URL = os.environ.get('DATABASE_URL')

if not DATABASE_URL:
    raise Exception("DATABASE_URL environment variable not set.")

engine = create_engine(DATABASE_URL)
Base.metadata.create_all(engine)
Session = sessionmaker(bind=engine)
session = Session()

def fetch_videos(channel_id):
    try:
        rss_url = f'https://www.youtube.com/feeds/videos.xml?channel_id={channel_id}'
        feed = feedparser.parse(rss_url)

        if feed.bozo:
            logging.error(f"Error parsing feed for channel {channel_id}")
            return []

        videos = []
        for entry in feed.entries:
            video = {
                'video_id': entry.yt_videoid,
                'title': entry.title,
                'link': entry.link,
                'published_at': datetime.strptime(entry.published, '%Y-%m-%dT%H:%M:%S%z'),
                'channel_id': channel_id
            }
            videos.append(video)
        return videos
    except Exception as e:
        logging.error(f"An error occurred while fetching videos for channel {channel_id}: {e}")
        return []

def save_new_videos(videos):
    new_videos = []
    for video in videos:
        exists = session.query(Video).filter_by(video_id=video['video_id']).first()
        if not exists:
            new_video = Video(
                video_id=video['video_id'],
                title=video['title'],
                link=video['link'],
                published_at=video['published_at'],
                channel_id=video['channel_id']
            )
            session.add(new_video)
            new_videos.append(new_video)
    session.commit()

    if new_videos:
        logging.info(f"Added {len(new_videos)} new videos.")
    else:
        logging.info("No new videos found.")

if __name__ == '__main__':
    for channel_id in channel_ids:
        logging.info(f"Fetching videos for channel: {channel_id}")
        videos = fetch_videos(channel_id)
        save_new_videos(videos)
    logging.info("Video records updated.")
