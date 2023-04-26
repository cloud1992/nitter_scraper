from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import BaseModel as Base


class Tweet(Base):
    """Represents a status update from a twitter user.

    This object is a subclass of the pydantic BaseModel which makes it easy to serialize
    the object with the .dict() and json() methods.

    Attributes:
        tweet_id: Twitter assigned id associated with the tweet.
        tweet_url: Twitter assigned url that links to the tweet.
        is_retweet: Represents if the tweet is a retweet.
        is_pinned: Represents if the user has pinned the tweet.
        time: Time the user sent the tweet.
        text: Text contents of the tweet.
        replies: A count of the replies to the tweet.
        retweets: A count of the times the tweet was retweeted.
        likes: A count of the times the tweet was liked.
        entries: Contains the entries object which holds metadata
            on the tweets text contents.

    """

    tweet_id: int
    tweet_url: str
    nitter_url: str
    username: str
    is_verified: bool
    fullname: Optional[str]
    is_retweet: bool
    is_pinned: bool
    date: datetime
    raw_content: str
    rendered_content: str
    replies_count: int
    retweet_count: int
    like_count: int
    hashtags: List[str]
    cashtags: List[str]
    urls: List[str]
    photos: List[str]
    videos: List[str]

    @classmethod
    def from_dict(cls, elements: Dict[str, Any]) -> "Tweet":
        """Creates Tweet object from a dictionary of processed text elements.

        Args:
            elements: Preprocessed attributes of a tweet object.

        Returns:
            Tweet object.

        """
        return cls(**elements)


class Profile(Base):
    """The profile object contains Twitter User account metadata.

    This object is a subclass of the pydantic BaseModel which makes it easy to serialize
    the object with the .dict() and json() methods.

    Attributes:
        username: The users screen_name, handle or alias. '@elonmusck'
        name: The users name as they've defined it.
        profile_photo: URL reference to the profiles photo.
        biography: The users autobiography.
        joined: The date the user joined Twitter.
        tweets_count: The number of Tweets (including retweets) issued by the user.
        following_count: The number of accounts the user is following.
        followers_count: The number of followers this account has.
        likes_count: Number of likes the follower has received.
        is_verified: Indicates if the user has been verified.
        banner_photo: URL reference to the profiles banner.
        location: A user defined location.
        website: A user defined website.

    """

    username: str
    name: str
    profile_photo: str
    biography: str
    joined: datetime
    location: str
    tweets_count: int
    following_count: int
    followers_count: int
    likes_count: int
    website: Optional[str] = None
    banner_photo: str
    is_verified: bool

    @classmethod
    def from_dict(cls, elements: Dict[str, Any]) -> "Profile":
        """Creates Profile object from a dictionary of processed text elements.

        Args:
            elements: Preprocessed attributes of a profile object.

        Returns:
            Profile object.

        """
        return cls(**elements)
