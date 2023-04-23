import re
from datetime import datetime
from typing import Dict


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
        if ic.text == "":
            value = 0
        value = ic.text

        stats[key] = value
    return stats


def attachment_parser(attachments):
    photos, videos = [], []
    if attachments:
        if attachments.find("img"):
            photos = ["https://nitter.net" + i.get("src") for i in attachments.find_all("img")]
        else:
            photos = []
        if attachments.find("source"):
            videos = ["https://nitter.net" + i.get("src") for i in attachments.find_all("source")]
        else:
            videos = []

    return photos, videos


def url_parser(text):
    content_split = text.split(" ")
    return [i for i in content_split if "http://" in i or "https://" in i]


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
    data["nitter_url"] = url
    data["tweet_url"] = url.replace("nitter.net", "twitter.com")
    data["username"] = username

    retweet = soup.find("div", class_="retweet-header")
    data["is_retweet"] = True if retweet else False

    body = soup.find("div", class_="tweet-body")

    pinned = body.find("div", class_="pinned")
    data["is_pinned"] = True if pinned else False

    data["date"] = date_parser(body.find("span", class_="tweet-date").find("a").get("title"))

    content = body.find("div", class_="tweet-content")
    data["raw_content"] = content.text
    data["rendered_content"] = content.text.replace("\n", " ")

    stats = stats_parser(soup.find("div", class_="tweet-stats"))

    if stats.get("comment"):
        data["replies_count"] = clean_stat(stats.get("comment"))
    else:
        data["replies_count"] = 0

    if stats.get("retweet"):
        data["retweet_count"] = clean_stat(stats.get("retweet"))
    else:
        data["retweet_count"] = 0

    if stats.get("heart"):
        data["like_count"] = clean_stat(stats.get("heart"))
    else:
        data["like_count"] = 0

    # entries = {}
    data["hashtags"] = hashtag_parser(content.text)
    data["cashtags"] = cashtag_parser(content.text)
    data["urls"] = url_parser(content.text)

    photos, videos = attachment_parser(body.find("div", class_="attachments"))
    data["photos"] = photos
    data["videos"] = videos

    return data
