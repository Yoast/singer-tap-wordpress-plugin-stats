"""Cleaner functions."""
# -*- coding: utf-8 -*-

from datetime import datetime, timezone
from types import MappingProxyType
from typing import Any, Optional

from tap_wordpress_plugin_stats.streams import STREAMS


class ConvertionError(ValueError):
    """Failed to convert value."""


def to_type_or_null(
    input_value: Any,
    data_type: Optional[Any] = None,
    nullable: bool = True,
) -> Optional[Any]:
    """Convert the input_value to the data_type.

    The input_value can be anything. This function attempts to convert the
    input_value to the data_type. The data_type can be a data type such as str,
    int or Decimal or it can be a function. If nullable is True, the value is
    converted to None in cases where the input_value == None. For example:
    a '' == None, {} == None and [] == None.

    Arguments:
        input_value {Any} -- Input value

    Keyword Arguments:
        data_type {Optional[Any]} -- Data type to convert to (default: {None})
        nullable {bool} -- Whether to convert empty to None (default: {True})

    Returns:
        Optional[Any] -- The converted value
    """
    # If the input_value is not equal to None and a data_type input exists
    if input_value and data_type:
        # Convert the input value to the data_type
        try:
            return data_type(input_value)
        except ValueError as err:
            raise ConvertionError(
                f'Could not convert {input_value} to {data_type}: {err}',
            )

    # If the input_value is equal to None and Nullable is True
    elif not input_value and nullable:
        # Convert '', {}, [] to None
        return None

    # If the input_value is equal to None, but nullable is False
    # Return the original value
    return input_value


def clean_row(row: dict, mapping: dict) -> dict:
    """Clean the row according to the mapping.

    The mapping is a dictionary with optional keys:
    - map: The name of the new key/column
    - type: A data type or function to apply to the value of the key
    - nullable: Whether to convert empty values, such as '', {} or [] to None

    Arguments:
        row {dict} -- Input row
        mapping {dict} -- Input mapping

    Returns:
        dict -- Cleaned row
    """
    cleaned: dict = {}

    key: str
    key_mapping: dict

    # For every key and value in the mapping
    for key, key_mapping in mapping.items():

        # Retrieve the new mapping or use the original
        new_mapping: str = key_mapping.get('map') or key

        # Convert the value
        cleaned[new_mapping] = to_type_or_null(
            row[key],
            key_mapping.get('type'),
            key_mapping.get('null', True),
        )

    return cleaned


def clean_active_versions(row: dict) -> dict:
    """Clean active versions.

    Arguments:
        row {dict} -- Input row

    Returns:
        dict -- Cleaned row
    """
    mapping: dict = STREAMS['active_versions'].get('mapping', {})

    # Add timestamp
    row['timestamp'] = datetime.now(
        tz=timezone.utc,
    ).replace(microsecond=0).isoformat()

    # Fix too long floats
    row['percentage'] = str(round(float(row['percentage']), 4))

    return clean_row(row, mapping)


def clean_active_installs(row: dict) -> dict:
    """Clean active installs.

    Arguments:
        row {dict} -- Input row

    Returns:
        dict -- Cleaned row
    """
    mapping: dict = STREAMS['active_installs'].get('mapping', {})

    row['percentage'] = row['percentage'].rstrip('-').rstrip('+')

    return clean_row(row, mapping)


def clean_downloads(row: dict) -> dict:
    """Clean downloads.

    Arguments:
        row {dict} -- Input row

    Returns:
        dict -- Cleaned row
    """
    mapping: dict = STREAMS['downloads'].get('mapping', {})

    return clean_row(row, mapping)


def clean_downloads_summary(row: dict) -> dict:
    """Clean download summary.

    Arguments:
        row {dict} -- Input row

    Returns:
        dict -- Cleaned row
    """
    mapping: dict = STREAMS['downloads_summary'].get('mapping', {})

    # Add timestamp
    row['timestamp'] = datetime.now(
        tz=timezone.utc,
    ).replace(microsecond=0).isoformat()

    return clean_row(row, mapping)


def clean_info(row: dict) -> dict:
    """Clean info.

    Arguments:
        row {dict} -- Input row

    Returns:
        dict -- Cleaned row
    """
    mapping: dict = STREAMS['info'].get('mapping', {})

    # Add timestamp
    row['timestamp'] = datetime.now(
        tz=timezone.utc,
    ).replace(microsecond=0).isoformat()

    plugin_data: dict = row['plugins'][0]

    # Add data
    row['active_installs'] = plugin_data.get('active_installs')
    row['downloaded'] = plugin_data.get('downloaded')
    row['last_updated'] = plugin_data.get('last_updated')
    row['num_ratings'] = plugin_data.get('num_ratings')
    row['rating'] = plugin_data.get('rating')
    row['ratings_0'] = plugin_data.get('ratings', {}).get('0')
    row['ratings_1'] = plugin_data.get('ratings', {}).get('1')
    row['ratings_2'] = plugin_data.get('ratings', {}).get('2')
    row['ratings_3'] = plugin_data.get('ratings', {}).get('3')
    row['ratings_4'] = plugin_data.get('ratings', {}).get('4')
    row['ratings_5'] = plugin_data.get('ratings', {}).get('5')
    row['support_threads'] = plugin_data.get('support_threads')
    row['support_threads_resolved'] = plugin_data.get(
        'support_threads_resolved',
    )
    row['version'] = plugin_data.get('version')

    return clean_row(row, mapping)


CLEANERS: MappingProxyType = MappingProxyType({
    'active_versions': clean_active_versions,
    'active_installs': clean_active_installs,
    'downloads': clean_downloads,
    'downloads_summary': clean_downloads_summary,
    'info': clean_info,
})
