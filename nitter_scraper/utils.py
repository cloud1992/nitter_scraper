from typing import Dict
from datetime import datetime
import re


def timeline_parser(soup):
    return soup.find("div", class_="timeline")


def pagination_parser(timeline, address: str, username: str, search_kind: str) -> str:
    show_more_tag = timeline.find("div", class_="show-more")
    next_page = ""
    if show_more_tag is not None:
        if "timeline-item" in show_more_tag["class"]:
            show_more_div = show_more_tag.find_next_sibling("div", class_="show-more")
            next_page_tag = show_more_div.find("a")
            if next_page_tag is not None:
                next_page = next_page_tag.get("href")
        else:
            next_page_tag = show_more_tag.find("a")
            if next_page_tag is not None:
                next_page = next_page_tag.get("href")
    if search_kind == "user":
        return f"{address}/{username}{next_page}"
    else:
        return f"https://nitter.net/search{next_page}"


def clean_stat(stat):
    return int(stat.replace(",", ""))


def link_parser(tweet_link):
    link = tweet_link.get("href")
    tweet_url = link
    parts = tweet_url.split("/")

    tweet_id = parts[-1].replace("#m", "")
    username = parts[1]
    tweet_url = f"https://nitter.net{tweet_url}"
    return tweet_id, username, tweet_url


def date_parser(tweet_date):
    date_format = "%b %d, %Y · %I:%M %p %Z"
    date = datetime.strptime(tweet_date, date_format)
    return date


def stats_parser(tweet_stats):
    stats = {}
    for ic in tweet_stats.find_all("div", class_="icon-container"):
        # print(f"ic: {ic}")
        key = ic.find("span").get("class")[0].replace("icon", "").replace("-", "")
        # print(f"span_icon: {key}")
        value = ic.text
        stats[key] = value
    return stats


def attachment_parser(attachments):
    photos, videos = [], []
    if attachments:
        photos = [i.attrs["src"] for i in attachments.find("img")]
        videos = [i.attrs["src"] for i in attachments.find("source")]
    return photos, videos


def url_parser(links):
    return sorted(filter(lambda link: "http://" in link or "https://" in link, links))


def cashtag_parser(text):
    cashtag_regex = re.compile(r"\$[^\d\s]\w*")
    return cashtag_regex.findall(text)


def hashtag_parser(text):
    hashtag_regex = re.compile(r"\#[^\d\s]\w*")
    return hashtag_regex.findall(text)


def parse_tweet(soup) -> Dict:
    data = {}
    id, username, url = link_parser(soup.find("a", class_="tweet-link"))
    data["tweet_id"] = id
    data["tweet_url"] = url
    data["username"] = username

    retweet = soup.find("div", class_="retweet-header")
    data["is_retweet"] = True if retweet else False

    body = soup.find("div", class_="tweet-body")

    pinned = body.find("div", class_="pinned")
    data["is_pinned"] = True if pinned else False

    data["time"] = date_parser(body.find("span", class_="tweet-date").find("a").get("title"))

    content = body.find("div", class_="tweet-content")
    data["text"] = content.text

    stats = stats_parser(soup.find("div", class_="tweet-stats"))

    if stats.get("comment"):
        data["replies"] = clean_stat(stats.get("comment"))

    if stats.get("retweet"):
        data["retweets"] = clean_stat(stats.get("retweet"))

    if stats.get("heart"):
        data["likes"] = clean_stat(stats.get("heart"))

    # entries = {}
    data["hashtags"] = hashtag_parser(content.text)
    data["cashtags"] = cashtag_parser(content.text)
    # entries["urls"] = url_parser(content.links)

    # photos, videos = attachment_parser(body.find(".attachments", first=True))
    # entries["photos"] = photos
    # entries["videos"] = videos

    # data["entries"] = entries
    # quote = soup.find(".quote", first=True) #NOTE: Maybe useful later on
    return data
