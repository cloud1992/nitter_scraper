import time

from nitter_scraper.scrap_tweets import get_tweets

url = "https://nitter.net/search?f=tweets&q=btc+OR+ETH+OR+ada+OR+matic&since=2021-10-10&until=&near="
# tweets = get_tweets(search_kind="user", username="lucas_uzal", pages=30)
tweets = get_tweets(search_kind="search", address=url, pages=2)

for tweet in tweets:
    print(tweet)
    print("-----------------------")
    time.sleep(0.5)
