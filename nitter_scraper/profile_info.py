from typing import Optional

import requests
from bs4 import BeautifulSoup

from nitter_scraper.schema import Profile
from nitter_scraper.utils import profile_parser


def get_profile(username: str) -> Optional[Profile]:
    """Scrapes nitter for the target users profile information.

    Args:
        username: The target profiles username.


    Returns:
        Profile object if successfully scraped, otherwise None.

    Raises:
        ValueError: If the target profile does not exist or is private.

    """

    url = f"https://nitter.net/{username}"
    response = requests.get(url)

    if response.status_code == 200:
        html = response.content
        soup = BeautifulSoup(html, "html.parser")
        profile = profile_parser(soup)

        if profile is None:
            return None

        profile_info = profile_parser(soup)
        profile = Profile.from_dict(profile_info)

        return profile

    elif response.status_code == 404:
        raise ValueError("The target profile does not exist.")

    elif response.status_code == 403:
        raise ValueError("The target profile is private.")

    else:
        raise ValueError("Unknown error.")
