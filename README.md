# How to use this package

## preinstallation
1. create account on reddit and add your app to get reddit client ID and Secret key for the usage of (Reddit API)[https://www.reddit.com/dev/api/]

## Installation
1. clone this repo to your local: `git clone git@github.com:ethanhan777/subreddit-data-collection.git [name_of_your_project]`
2. Create .env file and add details:
```
REDDIT_CLIENT_ID=[your_reddit_client_id]
REDDIT_CLIENT_SECRET=[your_reddit_secret_key]
REDDIT_USER_AGENT=ResearchBot
```

## Running the script
1. open docker desktop app to run this container
2. open terminal and run docker up command: `docker-compose up --build`
3. the command will take about 5~10 minutes to complete the data extraction and will save the resutl in csv format
4. to download the csv file, go to docker desktop app > the container (reddit-app) > view files > app > select the files and save.