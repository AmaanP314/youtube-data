from quart import Quart, request, render_template, redirect, url_for, jsonify, request
from youtube_search import search_youtube, viz_combined, analyze_comments, sentiment_viz
import pandas as pd
import asyncio
import shelve
from urllib.parse import urlparse, parse_qs
from video_search import process_video, generate_wordcloud

app = Quart(__name__)
app.secret_key = 'YOUR_SECRET_KEY'

@app.route('/')
async def index():
    return await render_template('index.html')

@app.route('/search', methods=['POST'])
async def search():
    try:
        form_data = await request.form
        query = form_data.get('query', '').strip()
        sort_by = form_data.get('sort_by', 'relevance')
        max_results = int(form_data.get('max_results', 5))
        max_comments = int(form_data.get('max_comments', 10))  
        order_by = form_data.get('order_by', 'relevance')
        if not query:
            return await render_template('index.html', error="Search query cannot be empty.")
        return redirect(url_for('results', query=query, sort_by=sort_by, max_results=max_results, max_comments=max_comments, order_by=order_by))
    
    except Exception as e:
        return await render_template('index.html', error=f"Error: {e}")

@app.route('/results')
async def results():
    try:
        query = request.args.get('query', '').strip()
        sort_by = request.args.get('sort_by', 'relevance')
        max_results = int(request.args.get('max_results', 5))
        max_comments = int(request.args.get('max_comments', 10))  
        order_by = request.args.get('order_by', 'relevance')

        if not query:
            return await render_template('index.html', error="Search query cannot be empty.")
        
        results = await search_youtube(query, sort_by=sort_by, max_results=max_results, max_com=max_comments, order=order_by)
        if results is None:
            return await render_template('results.html', error="No data found for the query.")
        data, comments = results
        df = data
        df = df.drop(columns=['Video_link'])
        with shelve.open('data_shelve') as db:
            db['query_data'] = {'df': df, 'comments': comments}

        if df is None or df.empty:
            return await render_template('results.html', query=query, error="No data found for the query.")

        df.index = df.index + 1
        df_html = df.to_html(classes='table table-striped', index=True, escape=False)

        return await render_template(
            'results.html',
            query=query,
            table=df_html,
            total_plot=None,
            engagement_rate_plot=None,
            composite_score_plot=None,
            sentiment_plot=None
        )

    except ValueError:
        return await render_template('results.html', error="Invalid input values for query or max results.")
    except Exception as e:
        return await render_template('results.html', error=f"Unexpected error: {str(e)}")


@app.route('/fetch_visualizations')
async def fetch_visualizations():
    try:
        with shelve.open('data_shelve') as db:
            data = db.get('query_data')
            df = data['df']
        if df is None:
            return jsonify({"error": "No data available for the given query"})
        df['Title'] = df['Title'].str.extract(r'<a [^>]*>(.*?)</a>', expand=False)
        visualizations = await generate_visualizations(df)
        return jsonify(visualizations)

    except Exception as e:
        return jsonify({"error": f"Error generating visualizations: {e}"})

async def generate_visualizations(df):
    total_plot = await viz_combined(df, plot_type='total')
    engagement_rate_plot = await viz_combined(df, plot_type='engagement_rate')
    composite_score_plot = await viz_combined(df, plot_type='composite_score')

    return {
        "total_plot": total_plot,
        "engagement_rate_plot": engagement_rate_plot,
        "composite_score_plot": composite_score_plot
    }

@app.route("/sentiment_analysis")
async def sentiment_analysis():
    try:
        with shelve.open('data_shelve') as db:
            data = db.get('query_data')
            df = data['df']
            comments = data['comments']

        if df.empty or df is None:
            return jsonify({"error": "Invalid or missing DataFrame in session."})
        tasks = [analyze_comments(comment) for comment in comments]
        sentiment_results = await asyncio.gather(*tasks)
        df_senti = pd.DataFrame(sentiment_results)
        return jsonify({'senti_plot':await sentiment_viz(df_senti)})
    except Exception as e:
        return jsonify({"error in fetching comments sentiment": f"{e}"})

@app.route('/<path:video_url>', methods=['GET'])
async def video_redirect(video_url):
    query_str = request.query_string.decode('utf-8')
    
    if not video_url.startswith("http"):
        full_url = "https://" + video_url
    else:
        full_url = video_url
    
    if query_str:
        full_url = f"{full_url}?{query_str}"
    print(query_str)
    parsed = urlparse(full_url)
    print(parsed)
    
    if parsed.netloc == "www.youtube.com" and parsed.path == "/watch":
        video_id = parse_qs(parsed.query).get('v', [None])[0]
        print(video_id)
        if not video_id:
            return "Invalid YouTube URL: missing video id", 400
        
        results = await process_video(video_id)
        if results is None:
            return await render_template('video_results.html', video_id=video_id, title=None, error="No data found for the videoId.")
        data, com_rel, com_time = results
        if com_rel is None:
            all_com = com_time if com_time is not None else []
        elif com_time is None:
            all_com = com_rel
        else:
            all_com = com_rel + com_time
        word_cloud = await generate_wordcloud(all_com) if all_com else None
        df = data
        df = df.drop(columns=['Video_link'])
        with shelve.open('data_shelve') as db:
            db['vid_data'] = {'df_vid': df, 'com_rel': com_rel, 'com_time': com_time}
        title = df['Title'].str.extract(r'<a [^>]*>(.*?)</a>', expand=False).values[0]
        df.index = df.index + 1
        df_html = df.to_html(classes='table table-striped', index=True, escape=False)
        return await render_template(
            'video_results.html',
            video_id=video_id,
            title=title,
            table=df_html,
            com_word_cloud=word_cloud,
            com_rel=len(com_rel) if com_time else 0,
            com_time=len(com_time) if com_time else 0,
            senti_rel=None,
            senti_time=None
        )
    else:
        return "Not Found", 404

@app.route("/senti_rel")
async def sentiment_relevant():
    try:
        with shelve.open('data_shelve') as db:
            data = db.get('vid_data')
            df = data['df_vid']
            comments = data['com_rel']
        if not comments:
            return jsonify({"error": "No relevant comments found for the video."})
        if df.empty or df is None:
            return jsonify({"error": "Invalid or missing DataFrame in session."})
        sentiment_results = await analyze_comments(comments)
        df_senti = pd.DataFrame([sentiment_results])
        return jsonify({'senti_rel':await sentiment_viz(df_senti, type='single')})
    except Exception as e:
        return jsonify({"error in fetching comments sentiment": f"{e}"})
    
@app.route("/senti_time")
async def sentiment_time():
    try:
        with shelve.open('data_shelve') as db:
            data = db.get('vid_data')
            df = data['df_vid']
            comments = data['com_time']
        if not comments:
            return jsonify({"error": "No relevant comments found for the video."})
        if df.empty or df is None:
            return jsonify({"error": "Invalid or missing DataFrame in session."})
        sentiment_results = await analyze_comments(comments)
        df_senti = pd.DataFrame([sentiment_results])
        return jsonify({'senti_time':await sentiment_viz(df_senti, type='single')})
    except Exception as e:
        return jsonify({"error in fetching comments sentiment": f"{e}"})


if __name__ == '__main__':
    app.run(debug=True)
