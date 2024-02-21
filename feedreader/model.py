from dataclasses import dataclass
from typing import List


@dataclass
class FeedEntry:
    id: str
    title: str
    summary: str
    link: str
    published: int
    published_parsed: str


@dataclass
class Feed:
    url: str
    entries: List[FeedEntry]
