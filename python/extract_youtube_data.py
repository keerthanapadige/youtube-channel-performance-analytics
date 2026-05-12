import os
import requests
import pandas as pd
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("YOUTUBE_API_KEY")

if not API_KEY:
    raise ValueError("YOUTUBE_API_KEY is missing. Add it to your .env file.")

BASE_URL = "https://www.googleapis.com/youtube/v3"


# Start with known public channel IDs.
# You can change these later.
CHANNEL_IDS = [
    "UC_x5XG1OV2P6uZZ5FSM9Ttw",  # Google Developers
    "UCWv7vMbMWH4-V0ZXdmDpPBA",  # Programming with Mosh
    "UC8butISFwT-Wl7EV0hUK0BQ",  # freeCodeCamp
]


def get_channel_details(channel_ids):
    url = f"{BASE_URL}/channels"

    params = {
        "part": "snippet,statistics,contentDetails",
        "id": ",".join(channel_ids),
        "key": API_KEY,
    }

    response = requests.get(url, params=params)
    response.raise_for_status()

    data = response.json()

    channels = []

    for item in data.get("items", []):
        channels.append({
            "channel_id": item["id"],
            "channel_name": item["snippet"].get("title"),
            "channel_created_date": item["snippet"].get("publishedAt"),
            "country": item["snippet"].get("country"),
            "subscriber_count": item["statistics"].get("subscriberCount"),
            "total_views": item["statistics"].get("viewCount"),
            "video_count": item["statistics"].get("videoCount"),
            "uploads_playlist_id": item["contentDetails"]["relatedPlaylists"]["uploads"],
        })

    return pd.DataFrame(channels)


def get_video_ids_from_uploads_playlist(playlist_id, max_pages=2):
    """
    Gets video IDs from a channel's uploads playlist.
    max_pages=2 means up to 100 videos because each page can return 50.
    """
    url = f"{BASE_URL}/playlistItems"

    video_ids = []
    next_page_token = None
    page_count = 0

    while page_count < max_pages:
        params = {
            "part": "contentDetails",
            "playlistId": playlist_id,
            "maxResults": 50,
            "key": API_KEY,
        }

        if next_page_token:
            params["pageToken"] = next_page_token

        response = requests.get(url, params=params)
        response.raise_for_status()

        data = response.json()

        for item in data.get("items", []):
            video_ids.append(item["contentDetails"]["videoId"])

        next_page_token = data.get("nextPageToken")
        page_count += 1

        if not next_page_token:
            break

    return video_ids


def get_video_details(video_ids):
    """
    Gets video details/statistics.
    YouTube videos.list accepts up to 50 video IDs per request.
    """
    url = f"{BASE_URL}/videos"

    all_videos = []

    for i in range(0, len(video_ids), 50):
        batch = video_ids[i:i + 50]

        params = {
            "part": "snippet,statistics,contentDetails",
            "id": ",".join(batch),
            "key": API_KEY,
        }

        response = requests.get(url, params=params)
        response.raise_for_status()

        data = response.json()

        for item in data.get("items", []):
            stats = item.get("statistics", {})
            snippet = item.get("snippet", {})

            all_videos.append({
                "video_id": item["id"],
                "channel_id": snippet.get("channelId"),
                "channel_name": snippet.get("channelTitle"),
                "title": snippet.get("title"),
                "published_at": snippet.get("publishedAt"),
                "category_id": snippet.get("categoryId"),
                "duration": item.get("contentDetails", {}).get("duration"),
                "view_count": stats.get("viewCount", 0),
                "like_count": stats.get("likeCount", 0),
                "comment_count": stats.get("commentCount", 0),
            })

    return pd.DataFrame(all_videos)


def main():
    channels_df = get_channel_details(CHANNEL_IDS)

    print("Channel data extracted:")
    print(channels_df[["channel_name", "subscriber_count", "video_count"]])

    all_video_ids = []

    for playlist_id in channels_df["uploads_playlist_id"]:
        video_ids = get_video_ids_from_uploads_playlist(playlist_id, max_pages=2)
        all_video_ids.extend(video_ids)

    print(f"Total video IDs collected: {len(all_video_ids)}")

    videos_df = get_video_details(all_video_ids)

    channels_df.to_csv("data/raw/channels.csv", index=False)
    videos_df.to_csv("data/raw/videos.csv", index=False)

    print("CSV files created:")
    print("data/raw/channels.csv")
    print("data/raw/videos.csv")


if __name__ == "__main__":
    main()