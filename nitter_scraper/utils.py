import re
from datetime import datetime
from typing import Dict

from bs4 import Tag


def timeline_parser(soup: Tag):
    return soup.find("div", class_="timeline")


def pagination_parser(timeline, extension: str, username: str, search_kind: str) -> str:
    show_more_tag = timeline.find("div", class_="show-more")
    next_page = ""
    if show_more_tag is not None:
        if "timeline-item" in show_more_tag["class"]:
            show_more_div = show_more_tag.find_next_sibling("div", class_="show-more")
            if show_more_div is not None:
                next_page_tag = show_more_div.find("a")
                if next_page_tag is not None:
                    next_page = next_page_tag.get("href")
            else:
                return "search ended"

        else:
            next_page_tag = show_more_tag.find("a")
            if next_page_tag is not None:
                next_page = next_page_tag.get("href")
    if search_kind == "user":
        return f"https://nitter.{extension}/{username}{next_page}"
    else:
        return f"https://nitter.{extension}/search{next_page}"


def clean_stat(stat):
    return int(stat.replace(",", ""))


def link_parser(tweet_link, extension: str):
    link = tweet_link.get("href")
    tweet_url = link
    parts = tweet_url.split("/")

    tweet_id = parts[-1].replace("#m", "")
    username = parts[1]
    tweet_url = f"https://nitter.{extension}{tweet_url}"
    return tweet_id, username, tweet_url


def date_parser(tweet_date):
    date_format = "%b %d, %Y · %I:%M %p %Z"
    # date_format_2 = "%b %d, %Y B· %I:%M %p %Z"
    if "В·" in tweet_date:
        tweet_date = tweet_date.replace("В·", "·")
    #     date = datetime.strptime(tweet_date, date_format)
    # else:
    #     date = datetime.strptime(tweet_date, date_format)
    date = datetime.strptime(tweet_date, date_format)
    return date


def stats_parser(tweet_stats):
    stats = {}
    for ic in tweet_stats.find_all("div", class_="icon-container"):
        key = ic.find("span").get("class")[0].replace("icon", "").replace("-", "")
        if ic.text == "":
            value = 0
        value = ic.text

        stats[key] = value
    return stats


def attachment_parser(attachments, extension: str):
    photos, videos = [], []
    if attachments:
        if attachments.find("img"):
            photos = [f"https://nitter.{extension}" + i.get("src") for i in attachments.find_all("img")]
        else:
            photos = []
        if attachments.find("source"):
            videos = [f"https://nitter.{extension}" + i.get("src") for i in attachments.find_all("source")]
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


def fullname_and_verified_parser(soup: Tag) -> tuple:
    fullname = soup.find("a", class_="fullname")
    verified = soup.find("span", class_="icon-ok verified-icon")
    return fullname.text if fullname else None, True if verified else False


def parse_tweet(soup: Tag, extension: str) -> Dict:
    data = {}
    id, username, url = link_parser(soup.find("a", class_="tweet-link"), extension)
    data["tweet_id"] = id
    data["nitter_url"] = url
    data["tweet_url"] = url.replace(f"nitter.{extension}", "twitter.com")
    data["username"] = username
    data["fullname"], data["is_verified"] = fullname_and_verified_parser(soup)

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

    photos, videos = attachment_parser(body.find("div", class_="attachments"), extension)
    data["photos"] = photos
    data["videos"] = videos

    return data


# profile parser#
def profile_full_name_parser(soup: Tag) -> str:
    profile_full_name = soup.find("a", class_="profile-card-fullname")
    if profile_full_name:
        profile_full_name = profile_full_name.text
    return profile_full_name


def profile_username_parser(soup: Tag) -> str:
    profile_username = soup.find("a", class_="profile-card-username")
    if profile_username:
        profile_username = profile_username.text
    return profile_username.replace("@", "")


def profile_photo_parser(soup: Tag, extension: str) -> str:
    profile_photo_tag = soup.find("a", class_="profile-card-avatar")
    if profile_photo_tag is None:
        return None
    profile_photo = profile_photo_tag.find("img").get("src")
    profile_photo_url = f"https://nitter.{extension}" + profile_photo
    return profile_photo_url


def profile_biography_parser(soup: Tag) -> str:
    profile_biography = soup.find("div", class_="profile-bio")
    if profile_biography:
        profile_biography = profile_biography.text
    else:
        return None

    return profile_biography


def profile_location_parser(soup: Tag) -> str:
    profile_location = soup.find("div", class_="profile-location")
    if profile_location is None:
        return None
    return profile_location.text.replace("\n", "")


def profile_joined_parser(soup: Tag) -> str:
    profile_joined = soup.find("div", class_="profile-joindate")
    if profile_joined is None:
        return None
    joined_date_string = profile_joined.find("span").get("title")

    date_format = "%I:%M %p - %d %b %Y"
    joined_date = datetime.strptime(joined_date_string, date_format)
    return joined_date


def profile_tweets_count_parser(soup: Tag) -> int:
    profile_tweets_count = soup.find("li", class_="posts")
    if profile_tweets_count is None:
        return 0
    profile_tweets_count = profile_tweets_count.find("span", class_="profile-stat-num")
    if profile_tweets_count is None:
        return 0
    return int(profile_tweets_count.text.replace(",", ""))


def profile_followers_count_parser(soup: Tag) -> int:
    profile_followers_count = soup.find("li", class_="followers")
    if profile_followers_count is None:
        return 0
    profile_followers_count = profile_followers_count.find("span", class_="profile-stat-num")
    if profile_followers_count is None:
        return 0
    return int(profile_followers_count.text.replace(",", ""))


def profile_following_count_parser(soup: Tag) -> int:
    profile_following_count = soup.find("li", class_="following")
    if profile_following_count is None:
        return 0
    profile_following_count = profile_following_count.find("span", class_="profile-stat-num")
    if profile_following_count is None:
        return 0
    return int(profile_following_count.text.replace(",", ""))


def profile_likes_count_parser(soup: Tag) -> int:
    profile_likes_count = soup.find("li", class_="likes")
    if profile_likes_count is None:
        return 0
    profile_likes_count = profile_likes_count.find("span", class_="profile-stat-num")
    if profile_likes_count is None:
        return 0
    return int(profile_likes_count.text.replace(",", ""))


def profile_website_parser(soup: Tag) -> str:
    profile_website = soup.find("div", class_="profile-website")
    if profile_website:
        profile_website = profile_website.find("a").get("href")
        return profile_website


def profile_banner_photo_parser(soup: Tag, extension: str) -> str:
    profile_banner_photo_tag = soup.find("div", class_="profile-banner")
    if profile_banner_photo_tag is None:
        return None
    profile_banner_photo = profile_banner_photo_tag.find("img")
    if profile_banner_photo is None:
        return None
    profile_banner_photo_url = f"https://nitter.{extension}" + profile_banner_photo.get("src")
    return profile_banner_photo_url


def profile_is_verified_parser(soup: Tag) -> bool:
    profile_is_verified = soup.find("span", class_="icon-ok verified-icon")
    if profile_is_verified:
        return True
    else:
        return False


def profile_parser(soup: Tag, extension: str) -> Dict:
    profile = {}
    profile["name"] = profile_full_name_parser(soup)
    profile["username"] = profile_username_parser(soup)
    profile["profile_photo"] = profile_photo_parser(soup, extension)
    profile["biography"] = profile_biography_parser(soup)
    profile["location"] = profile_location_parser(soup)
    profile["joined"] = profile_joined_parser(soup)
    profile["tweets_count"] = profile_tweets_count_parser(soup)
    profile["followers_count"] = profile_followers_count_parser(soup)
    profile["following_count"] = profile_following_count_parser(soup)
    profile["likes_count"] = profile_likes_count_parser(soup)
    profile["website"] = profile_website_parser(soup)
    profile["banner_photo"] = profile_banner_photo_parser(soup, extension)
    profile["is_verified"] = profile_is_verified_parser(soup)
    return profile
