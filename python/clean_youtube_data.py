import pandas as pd
import re


def parse_duration_to_minutes(duration):
    """
    Converts YouTube ISO 8601 duration format into minutes.
    Example:
    PT12M30S -> 12.5
    PT1H5M20S -> 65.33
    PT45S -> 0.75
    """
    if pd.isna(duration):
        return 0

    pattern = r"PT(?:(\d+)H)?(?:(\d+)M)?(?:(\d+)S)?"
    match = re.match(pattern, duration)

    if not match:
        return 0

    hours = int(match.group(1)) if match.group(1) else 0
    minutes = int(match.group(2)) if match.group(2) else 0
    seconds = int(match.group(3)) if match.group(3) else 0

    total_minutes = hours * 60 + minutes + seconds / 60
    return round(total_minutes, 2)


def clean_channels():
    channels_df = pd.read_csv("data/raw/channels.csv")

    numeric_columns = ["subscriber_count", "total_views", "video_count"]

    for col in numeric_columns:
        channels_df[col] = pd.to_numeric(channels_df[col], errors="coerce").fillna(0).astype(int)

    channels_df["channel_created_date"] = pd.to_datetime(
        channels_df["channel_created_date"],
        errors="coerce"
    ).dt.date

    channels_df.to_csv("data/processed/channels_clean.csv", index=False)

    print("Created: data/processed/channels_clean.csv")


def clean_videos():
    videos_df = pd.read_csv("data/raw/videos.csv")

    numeric_columns = ["view_count", "like_count", "comment_count"]

    for col in numeric_columns:
        videos_df[col] = pd.to_numeric(videos_df[col], errors="coerce").fillna(0).astype(int)

    videos_df["published_date"] = pd.to_datetime(
        videos_df["published_at"],
        errors="coerce"
    ).dt.date

    videos_df["published_month"] = pd.to_datetime(
        videos_df["published_at"],
        errors="coerce"
    ).dt.to_period("M").astype(str)

    videos_df["published_day_name"] = pd.to_datetime(
        videos_df["published_at"],
        errors="coerce"
    ).dt.day_name()

    videos_df["duration_minutes"] = videos_df["duration"].apply(parse_duration_to_minutes)

    videos_df["engagement_rate"] = (
    (videos_df["like_count"] + videos_df["comment_count"]) * 100.0
    / videos_df["view_count"].replace(0, float("nan"))
)

    videos_df["engagement_rate"] = videos_df["engagement_rate"].fillna(0).round(2)

    clean_columns = [
        "video_id",
        "channel_id",
        "channel_name",
        "title",
        "published_date",
        "published_month",
        "published_day_name",
        "category_id",
        "duration_minutes",
        "view_count",
        "like_count",
        "comment_count",
        "engagement_rate",
    ]

    videos_df = videos_df[clean_columns]

    videos_df.to_csv("data/processed/videos_clean.csv", index=False)

    print("Created: data/processed/videos_clean.csv")


def main():
    clean_channels()
    clean_videos()
    print("Data cleaning completed successfully.")


if __name__ == "__main__":
    main()