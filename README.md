# YouTube Video Recommender

This project allows users to analyze and recommend YouTube videos based on specific queries. It fetches video data using the YouTube Data API v3, processes and visualizes the data, and performs sentiment analysis on video comments to provide recommendations.

## Table of Contents
- [Features](#features)
- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Configuration](#configuration)
- [Running the Application](#running-the-application)
- [Webpage](#webpage)
- [Usage](#usage)
- [Project Structure](#project-structure)
- [Contributing](#contributing)
- [Contact](#contact)

## Features
- Fetches video data using the YouTube Data API v3.
- Analyzes video metadata and comments.
- Implements **asynchronous requests** and `await` to handle API calls efficiently, addressing the synchronous behavior of the previous version.
- Visualizations and data processing are now performed asynchronously, reducing page load times and enhancing user experience.
- Uses **AJAX** for real-time retrieval and rendering of results without requiring a full page refresh.
- Provides visualizations for key metrics:
  - Total views, likes, and comments.
  - Engagement rate.
  - Composite score.
- Performs **sentiment analysis** on video comments and visualizes the results.
- Suggests relevant videos based on data analysis and sentiment.

## Prerequisites
- Python 3.7 or higher.
- Required Python packages (listed in `requirements.txt`).
- A YouTube Data API v3 key (see the [Configuration](#configuration) section for details).

## Installation
1. Clone the repository:
    ```bash
    git clone https://github.com/AmaanP314/youtube-data.git
    cd youtube-data
    ```
2. Install the required Python packages:
    ```bash
    pip install -r requirements.txt
    ```

## Configuration
1. **Obtain a YouTube API key:**
   - Follow the instructions at [YouTube Data API v3 Documentation](https://developers.google.com/youtube/v3/getting-started) to create a project and generate an API key.

2. **Add the YouTube API key:**
   - Open `youtube_search.py` and locate the following lines:
     ```python
     video_api = "YOUR_YOUTUBE_API_KEY"
     comments_api = "YOUR_YOUTUBE_API_KEY"
     ```
   - Replace `YOUR_YOUTUBE_API_KEY` with your actual API key. The same key can be used for both `video_api` and `comments_api`.

3. **Set a secret key for the Flask app:**
   - Open `app.py` and locate the line:
     ```python
     app.secret_key = "your_secret_key"
     ```
   - Replace `"your_secret_key"` with a random string of characters for enhanced security.

## Running the Application
1. Run the Flask application:
    ```bash
    python app.py
    ```
2. Access the application at `http://localhost:5000`.

## Webpage
Check out the live project: [YouTube Video Recommender](https://youtube-data-analysis-n32d.onrender.com)

**Note:**
- The website is hosted on Render, so the initial load time may take 30 seconds to 1 minute.
- This live demo showcases the project's features but excludes database integration due to cost considerations on the free hosting tier.

## Usage
1. Enter a query, sorting criteria, and maximum results in the search form.
2. View the fetched results, visualizations, and sentiment analysis.
3. Explore recommended videos based on data-driven insights.

## Project Structure
    youtube-data/
    │
    ├── app.py # Main Flask application
    ├── youtube_search.py # Script to fetch and analyze YouTube data
    ├── requirements.txt # Python dependencies
    ├── static/
    │       ├── styles.css # CSS styles
    │       └── visualizations/ # Generated plots
    ├── templates/ # HTML templates
    │       ├── results.html # Results page template
    │       └── search.html # Search page template
    └── README.md # Project documentation

## Contributing
Contributions are welcome! Please fork the repository and submit pull requests.

## Contact
Amaan Poonawala - [GitHub](https://github.com/amaanp314) | [LinkedIn](https://www.linkedin.com/in/amaan-poonawala)

Feel free to reach out for any questions or feedback.
