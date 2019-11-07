from classes.reddit_scrapper import RedditScrapper
from multiprocessing import freeze_support

def main():
    rs = RedditScrapper()
    rs.set_current_subreddit('dankmemes')
    rs.scoringdb_update()

if __name__ == "__main__":
    main()