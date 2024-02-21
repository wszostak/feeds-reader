from abc import ABC

import logging

log = logging.getLogger(__name__)


class FeedsListProvider(ABC):
    @property
    def get_list(self) -> list[str]:
        raise NotImplemented()


class FileFeedsListProvider(FeedsListProvider):
    def __init__(self, file_name: str) -> None:
        with open(file_name, "r") as feeds_file:
            feeds = feeds_file.readlines()
        log.info("Feeds list successfully loaded.")
        self._feeds_list = [
            feed.strip()
            for feed in feeds
            if len(feed.strip()) > 0 and feed.strip()[0] != "#"
        ]

    @property
    def feeds_list(self) -> list[str]:
        return self._feeds_list


class ListFeedsListProvider(FeedsListProvider):
    def __init__(self, feeds_list: list[str]) -> None:
        self._feeds_list = feeds_list

    @property
    def feeds_list(self) -> list[str]:
        return self._feeds_list
