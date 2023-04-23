from nitter_scraper.scrap_tweets import get_tweets


url = "https://nitter.net/search?f=tweets&q=BTC+or+btc+or+NFT&since=2023-04-21&until=&near="
# tweets = get_tweets(search_kind="user", username="elonmusk", pages=2)
tweets = get_tweets(search_kind="search", address=url, pages=2)
# i = 0
for tweet in tweets:
    print(tweet)
    # i += 1
    # if i == 2:
    #     break
