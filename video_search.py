from youtube_search import fetch_video_details, fetch_comments_data, fetch_channel_details
import pandas as pd  
import isodate
import base64
import io
from wordcloud import WordCloud

async def process_video(video_id):
    video = await fetch_video_details(video_id)
    
    com_cnt = int(video['statistics']['commentCount']) if 'commentCount' in video['statistics'] else 0
    com_data_rel, com_data_time = None, None
    if com_cnt > 40:
        com_data_rel = await fetch_comments_data(video_id, 20, "relevance")
        com_data_time = await fetch_comments_data(video_id, 20, "time")
    elif com_cnt > 20:
        com_data_rel = await fetch_comments_data(video_id, 20, "relevance")
        remaining_comments = com_cnt - 20
        com_data_time = await fetch_comments_data(video_id, remaining_comments, "time")
    else:
        com_data_rel = await fetch_comments_data(video_id, com_cnt, "relevance")

    comments_rel = [item["snippet"]["topLevelComment"]["snippet"]["textOriginal"] for item in com_data_rel["items"]] if com_data_rel else None
    comments_time = [item["snippet"]["topLevelComment"]["snippet"]["textOriginal"] for item in com_data_time["items"]] if com_data_time else None

    video_id = video["id"]
    snippet = video["snippet"]
    statistics = video.get("statistics", {})
    content_details = video.get("contentDetails", {})
    channel_title = snippet["channelTitle"]
    channel_details = await fetch_channel_details(snippet["channelId"])
    video_link = f"https://www.youtube.com/watch?v={video_id}"
    
    duration_str = content_details.get('duration', 'PT0S')
    duration = isodate.parse_duration(duration_str)
    total_seconds = int(duration.total_seconds())
    hours = total_seconds // 3600
    minutes = (total_seconds % 3600) // 60
    seconds = total_seconds % 60
    formatted_duration = f"{hours:02}:{minutes:02}:{seconds:02}"
    video_info = {
        "Title": snippet["title"],
        "Views": int(statistics.get("viewCount", 0)),
        "Likes": int(statistics.get("likeCount", 0)),
        "Comments": int(statistics.get("commentCount", 0)),
        "Upload_date": snippet.get("publishedAt", "N/A"),
        "Duration": formatted_duration,
        "Channel": channel_title,
        "Subscribers": int(channel_details.get("subscriberCount", 0)),
        'Video_link': video_link
    }
    df = pd.DataFrame([video_info])
    try:
        df['Upload_date'] = pd.to_datetime(df['Upload_date'].str.split('T').str[0])
        df['Likes(%)'] = (df['Likes']) / (df['Views']) * 100
        df = df[['Title', 'Channel', 'Subscribers', 'Views', 'Likes', 'Likes(%)', 'Duration', 'Upload_date', 'Comments', 'Video_link']]
        df['Title'] = df.apply(lambda row: f'<a href="{row["Video_link"]}" target="_blank">{row["Title"]}</a>', axis=1)
        return df, comments_rel, comments_time
    except Exception as e:
        print(f"An error occurred while processing the data: {e}")
        return None
    
async def generate_wordcloud(comments):
    text = " ".join(comments)
    wordcloud = WordCloud(width=800, height=400, background_color='white').generate(text)
    img = io.BytesIO()
    wordcloud.to_image().save(img, format='PNG')
    img.seek(0)
    img_base64 = base64.b64encode(img.getvalue()).decode('utf8')
    return img_base64