# YouTube Data Scraper and Visualizer

This project scrapes YouTube data based on user queries and provides visualizations for the results. It stores data in a MySQL database and checks for existing data to provide faster results on subsequent searches.

## Features
- Scrapes YouTube video data using Selenium
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
        CREATE TABLE `search` (
            `id` int NOT NULL AUTO_INCREMENT,
            `query` varchar(255) NOT NULL,
            `last_searched` datetime NOT NULL,
            PRIMARY KEY (`id`)
        );

        CREATE TABLE `results` (
            `id` int NOT NULL AUTO_INCREMENT,
            `title` varchar(255) NOT NULL,
            `channel_name` varchar(255) NOT NULL,
            `subscribers` int NOT NULL,
            `views` int NOT NULL,
            `likes` int NOT NULL,
            `likes_percent` float NOT NULL,
            `duration_minutes` float NOT NULL,
            `upload_date` date NOT NULL,
            `comments` int NOT NULL,
            `video_link` varchar(255) NOT NULL,
            `sId` int NOT NULL,
            PRIMARY KEY (`id`),
            KEY `sId` (`sId`),
            CONSTRAINT `results_ibfk_1` FOREIGN KEY (`sId`) REFERENCES `search` (`id`)
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

## Running the Application
1. Run the Flask application:
    ```bash
    python app.py
    ```
2. Access the application at `http://localhost:5000`.

## Usage
1. Enter a query, sort criteria, and maximum results in the search form.
2. View search results, visualizations, and stored data.


## Contributing
Contributions are welcome! Please fork the repository and submit pull requests.
.
