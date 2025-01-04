import aiohttp
import matplotlib
import pandas as pd
from tqdm import tqdm
import tensorflow as tf
from matplotlib.ticker import PercentFormatter, FuncFormatter
from transformers import RobertaTokenizer, TFRobertaForSequenceClassification
import matplotlib.pyplot as plt
from collections import Counter
import seaborn as sns   
import isodate
import base64
import io

matplotlib.use('Agg')
sns.set()

API_KEY_COMMENTS = 'YOUR_YOUTUBE_API_KEY'
API_KEY_VIDEO = 'YOUR_YOUTUBE_API_KEY'
BASE_URL = "https://www.googleapis.com/youtube/v3"

model_name = "AmaanP314/youtube-comment-sentiment"
model = TFRobertaForSequenceClassification.from_pretrained(model_name)
tokenizer = RobertaTokenizer.from_pretrained(model_name)

label_map = {0: "Negative", 1: "Neutral", 2: "Positive"}
def batch_sentiment_analysis(texts, batch_size=16):
    inputs = tokenizer(texts, return_tensors="tf", padding=True, truncation=True, max_length=512, truncation_strategy="longest_first")
    logits = model(**inputs).logits
    predictions = tf.argmax(logits, axis=1).numpy()

    return [label_map[pred] for pred in predictions]

def analyze_comments_sentiment(comments):
    results = []
    for i in tqdm(range(0, len(comments), 32)):  
        batch_comments = comments[i:i+32]
        batch_results = batch_sentiment_analysis(batch_comments)
        results.extend(batch_results)
    return results

async def fetch_comments_data(video_id, max_results, order='relevance'):
    url = f"{BASE_URL}/commentThreads?part=snippet&videoId={video_id}&key={API_KEY_COMMENTS}&maxResults={max_results}&order={order}"
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            if response.status == 200:
                return await response.json()
            return None

async def analyze_comments(video_id, max_comments, order):
    data = await fetch_comments_data(video_id, max_comments, order)
    if data:
        texts = [item["snippet"]["topLevelComment"]["snippet"]["textDisplay"] for item in data["items"]]
        sentiment_labels = analyze_comments_sentiment(texts)
        sentiment_counts = Counter(sentiment_labels)
        result = {
            'Positive': sentiment_counts.get('Positive', 0),
            'Negative': sentiment_counts.get('Negative', 0),
            'Neutral': sentiment_counts.get('Neutral', 0)
        }
        return result
    return None

async def fetch_video_data(search_query, max_results, sort_by='relevance'):
    url = f"{BASE_URL}/search?part=snippet&type=video&q={search_query}&key={API_KEY_VIDEO}&maxResults={max_results}&order={sort_by}"
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            response_body = await response.text()
            if response.status == 200:
                data = await response.json()
                if 'items' in data and data['items']:
                    return data
                else:
                    return None
            else:
                print(f"Failed to fetch video data. Status code: {response.status}")
                print(f"Response body: {response_body}")
                return None
            
async def fetch_channel_details(channel_id):
    url = f"{BASE_URL}/channels?part=statistics&id={channel_id}&key={API_KEY_VIDEO}"
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            if response.status == 200:
                result = await response.json()
                if result["items"]:
                    return result["items"][0]["statistics"]
            return {}

async def fetch_video_details(video_id):
    video_details_url = f"{BASE_URL}/videos?part=snippet,statistics,contentDetails&id={video_id}&key={API_KEY_VIDEO}"
    async with aiohttp.ClientSession() as session:
        async with session.get(video_details_url) as response:
            if response.status == 200:
                result = await response.json()
                if result["items"]:
                    video_details = result["items"][0]
                    duration = video_details["contentDetails"]["duration"]
                    duration_seconds = isodate.parse_duration(duration).total_seconds()
                    if duration_seconds > 60:
                        return video_details
            return None

async def get_data(search_query, max_videos, sort_by):
    video_data = await fetch_video_data(search_query=search_query, max_results=max_videos, sort_by=sort_by)
    detailed_video_data = []
    if video_data:
        for video in video_data["items"]:
            video_id = video["id"]["videoId"]
            video_details = await fetch_video_details(video_id=video_id)
            detailed_video_data.append(video_details)
        return detailed_video_data
    return None

async def viz_combined(df, plot_type='total'):
    if len(df) <= 20:
        fig, ax = plt.subplots(figsize=(12, 8))
        bottom_margin = 0.25 + 0.07 * (len(df) // 5)
    elif len(df) <= 40:
        fig, ax = plt.subplots(figsize=(14, 10))
        bottom_margin = 0.17 + 0.05 * (len(df) // 5)
    else:
        fig, ax = plt.subplots(figsize=(18, 14))
        bottom_margin = 0.1 + 0.05 * (len(df) // 5)
        
    colors = ['#03045e','#023e8a','#0077b6','#0096c7','#00b4d8','#48cae4','#90e0ef','#ade8f4']
    sns.set_style('white')

    if plot_type == 'total':
        ax.bar(df.index + 1, df['Views'], color=colors)

        if plot_type == 'total':
            ax2 = ax.twinx()
            ax2.plot(df.index + 1, df['Likes'], color='crimson', marker='D')
            ax2.set_ylabel('Likes', fontsize=13, fontweight='bold')
            ax2.yaxis.set_major_formatter(FuncFormatter(lambda x, _: f'{int(x):,}'))
        else:
            raise ValueError("Invalid plot_type. Use 'total' or 'percent'.")

        ax.set_ylabel('Views', fontsize=13, fontweight='bold')
        plt.title('Views and Likes Graph' if plot_type == 'total' else 'Views and Likes Percentage by Views', fontsize=16, fontweight='bold')

    elif plot_type == 'engagement_rate':
        df['engagement_rate'] = (df['Likes'] + df['Comments']) / df['Views']
        ax.bar(df.index + 1, df['engagement_rate'], color=colors)
        ax.yaxis.set_major_formatter(PercentFormatter(xmax=1.0))
        ax.set_ylim(0, df['engagement_rate'].max() * 1.1)
        ax.set_ylabel('Engagement Rate (%)', fontsize=13, fontweight='bold')
        plt.title('Engagement Rate by Video', fontsize=16, fontweight='bold')

    elif plot_type == 'composite_score':
        df['engagement_rate'] = (df['Likes'] + df['Comments']) / df['Views']
        df['composite_score'] = (df['Views'] * 0.4) + (df['Likes'] * 0.2) + (df['Comments'] * 0.2) + (df['engagement_rate'] * 0.1) + (df['Subscribers'] * 0.1)
        ax.bar(df.index + 1, df['composite_score'], color=colors)
        ax.set_ylabel('Composite Score', fontsize=13, fontweight='bold')
        plt.title('Composite Score by Video', fontsize=16, fontweight='bold')

    else:
        raise ValueError("Invalid plot_type. Use 'total', 'percent', 'engagement_rate', or 'composite_score'.")

    while len(colors) < len(df):
        colors.extend(colors)

    handles = [plt.Line2D([0], [0], color=c, marker='o', label=f"{num}: {name}", markersize=10, linestyle='None') 
               for num, name, c in zip(df.index + 1, df['Title'], colors)]

    legend = ax.legend(handles=handles, title='Title Mapping', loc='upper center', bbox_to_anchor=(0.5, -0.15), ncol=2)
    plt.setp(legend.get_title(), fontsize=13, fontweight='bold')

    ax.set_xlabel('Title Number', fontsize=13, fontweight='bold')
    ax.set_xticks(range(1, len(df) + 1))
    ax.set_xticklabels(range(1, len(df) + 1))
    if plot_type == 'total' or plot_type == 'percent' or plot_type == 'composite_score':
        ax.yaxis.set_major_formatter(FuncFormatter(lambda x, _: f'{int(x):,}'))
    else:
        ax.yaxis.set_major_formatter(FuncFormatter(lambda x, _: f'{x:.2%}'))

    plt.rcParams['font.family'] = 'DejaVu Sans'
    if len(df) > 40:
        plt.tight_layout()

    fig.subplots_adjust(bottom=bottom_margin)
    
    for text in legend.get_texts():
        text.set_fontsize(10)
    legend.get_frame().set_linewidth(0.5)

    img = io.BytesIO()
    plt.savefig(img, format='png')
    plt.close()
    img.seek(0)
    return base64.b64encode(img.getvalue()).decode('utf8')

def sentiment_viz(df):
    ax = df.plot(kind='bar', stacked=True, figsize=(12, 6), color=['#28a745', '#dc3545', '#bfbfbf'])
    plt.title('Sentiment Analysis for Multiple Videos')
    plt.xlabel('Video Index')
    plt.ylabel('Number of Comments')
    plt.xticks(ticks=range(len(df)), labels=[i + 1 for i in range(len(df))], rotation=0)
    plt.legend(['Positive', 'Negative', 'Neutral'])
    plt.tight_layout()
    img = io.BytesIO()
    plt.savefig(img, format='png')
    plt.close()
    img.seek(0)
    return base64.b64encode(img.getvalue()).decode('utf8')

# Main function to search for videos and process data
async def search_youtube(query, sort_by='relevance', max_results=10):
    videos_data = await get_data(search_query=query, 
                                max_videos=max_results, 
                                sort_by=sort_by)
    if not videos_data:
        return None
    structured_data = []
    for video in videos_data:
        try:
            if video:
                video_id = video["id"]
                snippet = video["snippet"]
                statistics = video.get("statistics", {})
                content_details = video.get("contentDetails", {})
                channel_title = snippet["channelTitle"]
                channel_details = await fetch_channel_details(snippet["channelId"])
                video_link = f"https://www.youtube.com/watch?v={video_id}"

                video_info = {
                    "Title": snippet["title"],
                    "Views": int(statistics.get("viewCount", 0)),
                    "Likes": int(statistics.get("likeCount", 0)),
                    "Comments": int(statistics.get("commentCount", 0)),
                    "Upload_date": snippet.get("publishedAt", "N/A"),
                    "Duration(minutes)": int(isodate.parse_duration(content_details['duration']).total_seconds()) // 60,
                    "Channel": channel_title,
                    "Subscribers": int(channel_details.get("subscriberCount", 0)),
                    'Video_link': video_link
                }
                structured_data.append(video_info)
        except Exception as e:
            print(f"Error processing video data: {e}")
            continue
    if not structured_data:
        return None
    df = pd.DataFrame(structured_data)
    try:
        df['Upload_date'] = pd.to_datetime(df['Upload_date'].str.split('T').str[0])
        df['Likes(%)'] = (df['Likes']) / (df['Views']) * 100
        df = df[['Title', 'Channel', 'Subscribers', 'Views', 'Likes', 'Likes(%)', 'Duration(minutes)', 'Upload_date', 'Comments', 'Video_link']]
        df['Title'] = df.apply(lambda row: f'<a href="{row["Video_link"]}" target="_blank">{row["Title"]}</a>', axis=1)
        return df
    except Exception as e:
        print(f"An error occurred while processing the data: {e}")
        return None
