import datetime
import json
import os
import time
from datetime import timedelta

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from nitter_scraper.scrap_tweets import get_tweets

today = datetime.datetime.today()
yesterday = (today - timedelta(days=1)).date()
date = yesterday.strftime("%Y-%m-%d")


url = (
    "https://nitter.it/search?f=tweets&q=%28will+OR+going+OR+gonna+OR+"
    "forecast+OR+outlook+OR+predict+OR+prediction%29+%28SP500+OR+SPY+"
    "OR+SPX%29+min_faves%3A2+since%3A2019-06-12+until%3A2023-05-4+"
    "lang%3Aen&since=&until=&near="
)

tweets = get_tweets(search_kind="search", extension="it", address=url, pages=20000000)

daily_tweets = {}
for i, tweet in enumerate(tweets):
    try:
        tweet = tweet.dict()

        tweet_likes = tweet.get("like_count")
        tweet_retweets = tweet.get("retweet_count")
        tweet_replies = tweet.get("replies_count")
        tweet_id = tweet.get("tweet_id")
        tweet_user = tweet.get("username")
        daily_tweets[tweet_id] = [{"likes": tweet_likes, "retweets": tweet_retweets, "replies": tweet_replies}, tweet_user]

        print(f"tweet number {i} and tweet date {tweet.get('date')}")
        tweet["date"] = tweet.get("date").strftime("%Y-%m-%d %H:%M:%S")
        with open("tweets_SP500.json", "a") as f:
            json.dump(tweet, f)
            f.write("\n")

        time.sleep(0.005)
    except Exception as e:
        print(f"Ocurrio una excepcion {e}")

sorted_tweets = sorted(daily_tweets.items(), key=lambda x: sum(x[1][0].values()), reverse=True)
print(sorted_tweets)

driver = webdriver.Chrome()
url_to_look = []
for tweet_id, stats in sorted_tweets:
    print(f"Tweet {tweet_id}: {stats}")
    url_tweet = f"https://nitter.net/{stats[1]}/status/{tweet_id}"
    url_to_look.append(url_tweet)

    driver.get(url_tweet)
    wait = WebDriverWait(driver, timeout=20, poll_frequency=0.1)

    # element = wait.until(
    #     EC.visibility_of_element_located((By.XPATH, '//article[@data-testid="tweet"]'))
    #     )
    element = wait.until(EC.visibility_of_element_located((By.CLASS_NAME, "timeline-item")))
    screenshot_as_bytes = element.screenshot_as_png
    title = driver.title

    with open(os.path.join("images", f"{stats[1]}.png"), "wb") as f:
        f.write(screenshot_as_bytes)
        print("image has been saved.")
