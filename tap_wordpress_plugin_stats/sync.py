"""Sync data."""
# -*- coding: utf-8 -*-
import logging
from datetime import datetime, timezone
from typing import Callable

import singer
from singer.catalog import Catalog

from tap_wordpress_plugin_stats.wordpress_stats import WordPressPluginStats

LOGGER: logging.RootLogger = singer.get_logger()


def sync(  # noqa: WPS210, WPS213
    wp: WordPressPluginStats,
    catalog: Catalog,
) -> None:
    """Sync data from tap source.

    Arguments:
        wp {WordPressPluginStats} -- WordPressPluginStats client
        catalog {Catalog} -- Stream catalog
    """
    # For every stream in the catalog
    LOGGER.info('Sync')

    # Only selected streams are synced, whether a stream is selected is
    # determined by whether the key-value: "selected": true is in the schema
    # file.
    for stream in catalog.get_selected_streams({}):
        LOGGER.info(f'Syncing stream: {stream.tap_stream_id}')

        # Write the schema
        singer.write_schema(
            stream_name=stream.tap_stream_id,
            schema=stream.schema.to_dict(),
            key_properties=stream.key_properties,
        )

        # Every stream has a corresponding method in the WordPress Stats object
        # The stream: mysql will call: wp.mysql
        tap_data: Callable = getattr(wp, stream.tap_stream_id)

        # The tap_data method yields rows of data from the API
        for row in tap_data():

            # Write a row to the stream
            singer.write_record(
                stream.tap_stream_id,
                row,
                time_extracted=datetime.now(timezone.utc),
            )
