from abc import ABC, abstractmethod
from typing import List

from .model import FeedEntry


class FeedEntryProcessor(ABC):
    @abstractmethod
    def process(entry: FeedEntry) -> None:
        raise NotImplemented()


class MultiFeedEntryProcessor(FeedEntryProcessor):
    def __init__(self, feed_entry_processors: List[FeedEntryProcessor]) -> None:
        self._feed_entry_processors = feed_entry_processors

    def process(self, entry: FeedEntry) -> None:
        for ep in self._feed_entry_processors:
            ep.process(entry)


class StatsFeedEntryProcessor(FeedEntryProcessor):
    def __init__(self) -> None:
        self._processed_ids = set()

    def process(self, entry: FeedEntry) -> None:
        self._processed_ids.add(entry.id)

    @property
    def procesed_entries_count(self) -> int:
        return len(self._processed_ids)


class PrintFeedEntryProcessor(FeedEntryProcessor):
    def __init__(self, text_width: int = 85) -> None:
        import re

        self._re = re.compile(r"<[^<]+?>")
        self._text_width = text_width

    def process(self, entry: FeedEntry) -> None:
        print(f"{entry.title:_^75}")
        print(entry.link)
        buffer = ""
        summary = self._re.sub("", entry.summary)
        for word in summary.split():
            if len(buffer) + len(word) + 1 > self._text_width:
                print(buffer)
                buffer = ""

            buffer += word + " "
        print(buffer[:-1])
        print("")
