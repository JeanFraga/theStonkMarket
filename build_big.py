from functions.workerdb_compilers import insert_new_data, clear_worker_dbs
from classes.reddit_scrapper import RedditScrapper

subreddits = ['dankmemes']
years = [2019]
months = range(1,13)

def main():
    global years
    global subreddits
    global months

    clear_worker_dbs()
    redditScrapper = RedditScrapper()

    for subreddit in subreddits:
        for year in years:
            for month in months:
                redditScrapper.scrap_month(subreddit, year, month)


if __name__ == "__main__": main()