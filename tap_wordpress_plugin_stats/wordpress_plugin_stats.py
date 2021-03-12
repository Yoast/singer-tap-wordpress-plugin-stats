"""WordPress.org stats fetcher."""

import logging
from types import MappingProxyType
from typing import Callable, Generator, List, Union

import httpx

from tap_wordpress_plugin_stats.cleaners import CLEANERS

API_SCHEME: str = 'https://'
API_BASE_URL: str = 'api.wordpress.org'
API_BASE_PATH: str = f'{API_SCHEME}{API_BASE_URL}'
ENDPOINT_ACTIVE_VERSIONS: str = '/stats/plugin/1.0/?slug=:plugin:'
ENDPOINT_ACTIVE_INSTALLS: str = (
    '/stats/plugin/1.0/active-installs.php?slug=:plugin:&limit=:limit:'
)
ENDPOINT_DOWNLOADS: str = (
    '/stats/plugin/1.0/downloads.php?slug=:plugin:&limit=:limit:'
)
ENDPOINT_DOWNLOADS_SUMMARY: str = (
    '/stats/plugin/1.0/downloads.php?slug=:plugin:&historical_summary=1'
)
ENDPOINT_INFO: str = (
    '/plugins/info/1.2/?action=query_plugins&request[per_page]'
    '=1&request[search]=:plugin:'
)

headers: MappingProxyType = MappingProxyType({
    'User-Agent': (
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
        'AppleWebKit/537.36 (KHTML, like Gecko) '
        'Chrome/74.0.3729.131 Safari/537.36'
    ),
})


class PluginNotFoundException(Exception):
    """Exception for when plugin is not found."""


class WordPressPluginStats(object):
    """WordPress PluginStats."""

    def __init__(self, plugins: Union[List[str], str]) -> None:
        """Initialize plugin stats api.

        Arguments:
            plugins {Union[List[str], str]} -- Name of the plugins
        """
        self.client: httpx.Client = httpx.Client(
            http2=True,
            headers=dict(headers),
        )

        # Set plugin or plugins
        if isinstance(plugins, str):
            self.plugins = [plugins]
        else:
            self.plugins = plugins

    def active_versions(self) -> Generator:  # noqa: WPS210
        """Active versions.

        Yields:
            Generator -- JSON
        """
        cleaner: Callable = CLEANERS.get('active_versions', {})

        # For every plugin
        for plugin in self.plugins:
            path: str = f'{ENDPOINT_ACTIVE_VERSIONS}' .replace(
                ':plugin:',
                plugin,
            )

            # Load the data
            response: dict = self._load(path)

            # Transform the records
            records: List[dict] = [
                {
                    'version': key,
                    'percentage': str(percentage),
                    'plugin': plugin,
                } for key, percentage in response.items()
            ]

            # Yield
            yield from (
                cleaner(record)
                for record in records
            )

    def active_installs(self, limit: int = 730) -> Generator:  # noqa: WPS210
        """Active installs.

        Keyword Arguments:
            limit {int} -- Number of historical data days (default: {730})

        Yields:
            Generator -- JSON
        """
        cleaner: Callable = CLEANERS.get('active_installs', {})

        # For every plugin
        for plugin in self.plugins:
            path: str = f'{ENDPOINT_ACTIVE_INSTALLS}' .replace(
                ':plugin:',
                plugin,
            ).replace(
                ':limit:',
                str(limit),
            )

            # Load the data
            response: dict = self._load(path)

            # Transform the records
            records: List[dict] = [
                {
                    'date': key,
                    'percentage': str(percentage),
                    'plugin': plugin,
                } for key, percentage in response.items()
            ]

            # Yield
            yield from (
                cleaner(record)
                for record in records
            )

    def downloads(self, limit: int = 730) -> Generator:  # noqa: WPS210
        """Plugin downloads.

        Keyword Arguments:
            limit {int} -- Number of historical data days (default: {730})

        Yields:
            Generator -- JSON
        """
        cleaner: Callable = CLEANERS.get('downloads', {})

        # For every plugin
        for plugin in self.plugins:
            path: str = f'{ENDPOINT_DOWNLOADS}' .replace(
                ':plugin:',
                plugin,
            ).replace(
                ':limit:',
                str(limit),
            )

            # Load the data
            response: dict = self._load(path)

            # Transform the records
            records: List[dict] = [
                {
                    'date': key,
                    'downloads': download,
                    'plugin': plugin,
                } for key, download in response.items()
            ]

            # Yield
            yield from (
                cleaner(record)
                for record in records
            )

    def downloads_summary(self) -> Generator:
        """Plugin downloads summary.

        Yields:
            Generator -- JSON
        """
        cleaner: Callable = CLEANERS.get('downloads_summary', {})

        # For every plugin
        for plugin in self.plugins:
            path: str = f'{ENDPOINT_DOWNLOADS_SUMMARY}' .replace(
                ':plugin:',
                plugin,
            )

            # Load the data
            response: dict = self._load(path)

            # add plugin
            response['plugin'] = plugin

            yield cleaner(response)

    def info(self) -> Generator:  # noqa: WPS110
        """Plugin info.

        Yields:
            Generator -- JSON
        """
        cleaner: Callable = CLEANERS.get('info', {})

        for plugin in self.plugins:
            path: str = f'{ENDPOINT_INFO}' .replace(
                ':plugin:',
                plugin,
            )
            response: dict = self._load(path)

            # add plugin
            response['plugin'] = plugin

            yield cleaner(response)

    def _load(self, path: str) -> dict:
        """Load an URL and return JSON.

        Arguments:
            path {str} -- Path to fetch from

        Returns:
            dict -- JSON as dict
        """
        url: str = f'{API_BASE_PATH}{path}'
        logging.info(f'Loading: {url}')
        response: httpx._models.Response = self.client.get(  # noqa: WPS437
            url,
        )
        response.raise_for_status()

        return response.json()
