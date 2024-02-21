import logging
from feedreader import FeedparserFeedParser, FeedsReader, JsonFileFeedsLastCheckProvider
from feedreader.processor import MultiFeedEntryProcessor, PrintFeedEntryProcessor, StatsFeedEntryProcessor

from feedreader.provider import FileFeedsListProvider

FEEDS_LAST_CHECK_INFO_FILE = "./feeds_last_check.json"
FEEDS_LIST_FILE = "./feeds.txt"

if __name__ == "__main__":
    logging.basicConfig(level=logging.ERROR)

    feeds_list_provider = FileFeedsListProvider(FEEDS_LIST_FILE)
    # feeds_list_provider = ListFeedsListProvider(["https://example.com/rss"])

    feeds_last_check_provider = JsonFileFeedsLastCheckProvider(FEEDS_LAST_CHECK_INFO_FILE)
    feed_parser = FeedparserFeedParser()

    stats_processor = StatsFeedEntryProcessor()
    print_processor = PrintFeedEntryProcessor()

    FeedsReader(feeds_list_provider, feeds_last_check_provider, feed_parser,
                feed_entry_processor=MultiFeedEntryProcessor([
                    stats_processor,
                    print_processor
                ])
    ).read()

    print(f"Processed `{stats_processor.procesed_entries_count}` unique feeds.")