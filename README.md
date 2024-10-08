# YouTube Data Analysis

This project scrapes YouTube data based on user queries and provides visualizations for the results. It stores data in a MySQL database and checks for existing data to provide faster results on subsequent searches.

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
- Collects the video data using youtube data api v3
- Stores video data in a MySQL database
- Retrieves data from the database for faster results if query exists
- Provides visualizations for views, likes, and engagement rates

## Prerequisites
- Python 3.7 or higher
- MySQL database
- Required Python packages (listed in `requirements.txt`)

## Installation
1. Clone the repository:
    ```bash
    git clone https://github.com/AmaanP314/youtube-data.git
    cd youtube-data
    ```
2. Install the required packages:
    ```bash
    pip install -r requirements.txt
    ```
3. Set up the MySQL database:
    - Create a database named `youtube_data`.
    - Create the necessary tables:
        ```sql
        CREATE TABLE search (
            id int NOT NULL AUTO_INCREMENT,
            query varchar(255) NOT NULL,
            first_searched datetime NOT NULL,
            last_searched datetime NOT NULL,
            PRIMARY KEY (`id`)
        );

        CREATE TABLE results (
            rId INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
            title VARCHAR(255),
            channel_name VARCHAR(255),
            subscribers BIGINT,
            views BIGINT,
            likes INT,
            likes_percent DECIMAL(8, 6),
            duration_minutes INT,
            upload_date DATE,
            comments INT,
            video_link VARCHAR(255),
            sId INT, foreign key(sId) references search(id)
        );

        ```

## Configuration
- Update the MySQL database configuration in `app.py` and `youtube_search.py`:
    ```python
    app.config['MYSQL_USER'] = 'your_mysql_username'
    app.config['MYSQL_PASSWORD'] = 'your_mysql_password'
    app.config['MYSQL_DB'] = 'youtube_data'
    app.config['MYSQL_CURSORCLASS'] = 'DictCursor'
    ```
- Add your YouTube API key in `youtube_search.py`:
    ```python
    api_key = 'your_youtube_api_key'
    ```

## Running the Application
1. Run the Flask application:
    ```bash
    python app.py
    ```
2. Access the application at `http://localhost:5000`.

## Webpage

Check out the live project: [YouTube Data Analysis](https://youtube-data-analysis-n32d.onrender.com)
the web app is currently under maintanance!

### Note
- The website is hosted on Render, so the initial load time may take 30 seconds to 1 minute.
- The live demo does not include the implementation of the MySQL database. Due to cost considerations, database integration is not enabled on the free hosting tier.

## Usage
1. Enter a query, sort criteria, and maximum results in the search form.
2. View search results, visualizations, and stored data.

## Project Structure

    youtube-data/
    │
    ├── app.py # Main Flask application
    ├── youtube_search.py # Script to scrape YouTube data
    ├── requirements.txt # Python dependencies
    ├── static/
    │       └── styles.css # CSS styles
    ├── templates/ # HTML templates
    │       ├── results.html # Results page template
    │       └── search.html # Search page template
    └── README.md # Project documentation


## Contributing
Contributions are welcome! Please fork the repository and submit pull requests.

## Contact

Amaan Poonawala - [GitHub](https://github.com/amaanp314) | [LinkedIn](https://www.linkedin.com/in/amaan-poonawala)

Feel free to reach out for any questions or feedback.

