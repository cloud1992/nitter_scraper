from typing import Optional

import requests
from bs4 import BeautifulSoup

from nitter_scraper.schema import Tweet  # noqa: I100, I202
from nitter_scraper.utils import (  # noqa: I100, I202
    pagination_parser,
    parse_tweet,
    timeline_parser,
)


def get_tweets(
    search_kind: str,
    username: str = "elonmusk",
    pages: int = 25,
    break_on_tweet_id: Optional[int] = None,
    address=None,
) -> Tweet:
    """Gets the target users tweets

    Args:
        username: Targeted users username.
        pages: Max number of pages to lookback starting from the latest tweet.
        break_on_tweet_id: Gives the ability to break out of a loop if a tweets id is found.
        address: The address to scrape from. The default is https://nitter.net which should
            be used as a fallback address.

    Yields:
        Tweet Objects

    """
    if search_kind == "user":
        address = "https://nitter.net"
        url = f"{address}/{username}"
    else:
        url = address

    def gen_tweets(pages):
        response = requests.get(url)

        while pages > 0:
            if response.status_code == 200:
                print("-----------------------New-Tweet-----------------------")
                html = response.content
                soup = BeautifulSoup(html, "html.parser")
                timeline = timeline_parser(soup)
                # print(f"Timeline: {timeline}")

                next_url = pagination_parser(timeline, address, username, search_kind)
                print(f"Next URL: {next_url}")

                timeline_items = timeline.find_all("div", class_="timeline-item")

                print(f"El numero de timeline_items es: {len(timeline_items)}")

                for item in timeline_items:
                    # print(f"Item: {item}")
                    if "show-more" in item.get("class"):
                        print(f"Item: {item}")
                        continue

                    tweet_data = parse_tweet(item)
                    tweet = Tweet.from_dict(tweet_data)

                    if tweet.tweet_id == break_on_tweet_id:
                        pages = 0
                        break

                    yield tweet

            response = requests.get(next_url)
            pages -= 1

    yield from gen_tweets(pages)
