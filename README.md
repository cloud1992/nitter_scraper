# nitter_scraper
Nitter scrape using BeautifulSoup

### Basic usage

There are two type of searchs: username search and general search

For username search
```
from nitter_scraper.scrap_tweets import get_tweets

tweets = get_tweets(search_kind="user", username="lucas_uzal", pages=10)
for tweet in tweets:
    print(tweet)
    print("-----------------------")
    time.sleep(0.5)
```

For general search you need to build the url e.g

```
from nitter_scraper.scrap_tweets import get_tweets
url = "https://nitter.net/search?f=tweets&q=btc+OR+ETH+OR+ada+OR+matic&since=2021-10-10&until=&near="
tweets = get_tweets(search_kind="search", address=url, pages=10)
for tweet in tweets:
    print(tweet)
    print("-----------------------")
    time.sleep(0.5)
```
