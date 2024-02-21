from abc import ABC, abstractmethod
import calendar
import feedparser
import json
import logging

from .feedparser_date_format_handlers import pap_mediaroom_date_format_handler
from .model import Feed, FeedEntry
from .processor import FeedEntryProcessor
from .provider import FeedsListProvider

log = logging.getLogger(__name__)


class FeedsLastCheckProvider(ABC):
    @abstractmethod
    def get_last_checked(self, feed_url: str) -> int:
        raise NotImplemented()

    @abstractmethod
    def update_last_checked(self, feed_url: str) -> None:
        raise NotImplemented()


class JsonFileFeedsLastCheckProvider(FeedsLastCheckProvider):
    def __init__(self, feeds_last_check_info_file_path: str) -> None:
        self._feeds_last_check_info_file_path = feeds_last_check_info_file_path
        self._feeds_last_check = {}
        try:
            with open(
                self._feeds_last_check_info_file_path, "r"
            ) as feeds_last_check_file:
                self._feeds_last_check = json.load(feeds_last_check_file)
            log.info("Feeds last check file succesfuly loaded.")
        except Exception:
            log.warning("No feeds last check file. Using empty dict.")

    def get_last_checked(self, feed_url: str) -> int | None:
        return self._feeds_last_check.get(feed_url, None)

    def update_last_checked(self, feed_url: str, last_check_timestamp: int) -> None:
        if self._feeds_last_check.get(feed_url, None) != last_check_timestamp:
            self._feeds_last_check[feed_url] = last_check_timestamp
            with open(
                self._feeds_last_check_info_file_path, "w+"
            ) as feeds_last_check_file:
                json.dump(self._feeds_last_check, feeds_last_check_file, indent=2)
            log.info("Feeds last check file succesfuly loaded.")


class FeedParser(ABC):
    @abstractmethod
    def parse(self, feed_url: str) -> Feed:
        raise NotImplemented()


class FeedparserFeedParser(FeedParser):
    def __init__(self) -> None:
        feedparser.registerDateHandler(pap_mediaroom_date_format_handler)
        self.feedparser = feedparser

    def parse(self, feed_url: str) -> Feed:
        # dict_keys(['title', 'title_detail', 'summary', 'summary_detail', 'links', 'link', 'id', 'guidislink', 'published', 'published_parsed', 'tags'])
        # dict_keys(['bozo', 'entries', 'feed', 'headers', 'etag', 'updated', 'updated_parsed', 'href', 'status', 'encoding', 'version', 'namespaces'])
        feed = self.feedparser.parse(feed_url)
        feed_entries = []
        for fe in feed.entries:
            try:
                entry_time = calendar.timegm(fe.published_parsed)
            except Exception as e:
                log.error(
                    f'Converting date {fe.published}/{fe.published_parsed} failed with error: "{e}".'
                )
                continue

            feed_entries.append(
                FeedEntry(
                    id=fe.id,
                    title=fe.title,
                    summary=fe.summary,
                    link=fe.link,
                    published=entry_time,
                    published_parsed=fe.published_parsed,
                )
            )
        return Feed(url=feed_url, entries=feed_entries)


class FeedsReader:
    def __init__(
        self,
        feeds_list_provider: FeedsListProvider,
        feeds_last_check_provider: FeedsLastCheckProvider,
        feed_parser: FeedParser,
        *,
        feed_entry_processor: FeedEntryProcessor | None,
    ) -> None:
        self._feeds_list_provider = feeds_list_provider
        self._feeds_last_check_provider = feeds_last_check_provider
        self._feed_parser = feed_parser
        self._feed_entry_processor = feed_entry_processor

    def read(self) -> None:
        for feed_url in self._feeds_list_provider.feeds_list:
            last_check_timestamp = self._process_feed(
                feed_url,
                self._feeds_last_check_provider.get_last_checked(feed_url),
            )
            self._feeds_last_check_provider.update_last_checked(
                feed_url, last_check_timestamp
            )

    def _process_feed_entry(self, entry: FeedEntry):

        log.info(f'Processing [{entry.id}] "{entry.title}" from  {entry.published}')
        if self._feed_entry_processor:
            self._feed_entry_processor.process(entry)

    def _process_feed(
        self, feed_url: str, last_check_timestamp: float | None = None
    ) -> float:
        log.info(f"Processing feed `{feed_url}`.")

        feed = self._feed_parser.parse(feed_url)

        this_check_timestamp = last_check_timestamp

        for entry in feed.entries:
            if (
                last_check_timestamp is not None
                and entry.published <= last_check_timestamp
            ):
                log.debug(
                    f"Skipping outdated entry [{entry.id}] from feed `{feed.url}`."
                )
                continue

            self._process_feed_entry(entry)

            if this_check_timestamp is None or this_check_timestamp < entry.published:
                this_check_timestamp = entry.published

        log.info(f"`{feed_url}` last checked at {this_check_timestamp}.")
        return this_check_timestamp
