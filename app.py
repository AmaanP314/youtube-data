from quart import Quart, request, render_template, redirect, url_for, jsonify
from youtube_search import search_youtube, viz_combined, analyze_comments, sentiment_viz
import pandas as pd
import asyncio
import shelve

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

        data, comments = await search_youtube(query, sort_by=sort_by, max_results=max_results, max_com=max_comments, order=order_by)
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
        print(df_senti)
        return jsonify({'senti_plot': sentiment_viz(df_senti)})
    except Exception as e:
        return jsonify({"error in fetching comments sentiment": f"{e}"})

if __name__ == '__main__':
    app.run(debug=True)
