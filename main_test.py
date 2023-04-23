from nitter_scraper.scrap_tweets import get_tweets

url = "https://nitter.net/search?f=tweets&q=btc+ETH&since=&until=&near="
tweets = get_tweets(search_kind="user", username="ArturoCollado2", pages=30)
# tweets = get_tweets(search_kind="search", address=url, pages=20)

for tweet in tweets:
    print(tweet)
    print("-----------------------")
