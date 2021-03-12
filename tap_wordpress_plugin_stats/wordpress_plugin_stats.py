"""WordPress.org stats fetcher."""
import logging
import httpx


API_SCHEME: str = 'https://'
API_BASE_URL: str = 'api.wordpress.org'
ENDPOINT_ACTIVE_VERSIONS: str = '/stats/plugin/1.0/?slug=:plugin'
ENDPOINT_ACTIVE_INSTALLS: str = \
    '/stats/plugin/1.0/active-installs.php?slug=:plugin&limit=:limit'
ENDPOINT_DOWNLOADS: str = \
    '/stats/plugin/1.0/downloads.php?slug=:plugin&limit=:limit'
ENDPOINT_DOWNLOADS_SUMMARY: str = \
    '/stats/plugin/1.0/downloads.php?slug=:plugin&historical_summary=1'
ENDPOINT_INFO: str = \
    '/plugins/info/1.2/?action=query_plugins&request[per_page]' \
    '=1&request[search]=:plugin'


class PluginNotFoundException(Exception):
    """Exception for when plugin is not found."""


class WordPressPluginStats:
    """WordPress Stats."""

    headers: dict = \
        {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
                       'AppleWebKit/537.36 (KHTML, like Gecko) '
                       'Chrome/74.0.3729.131 Safari/537.36'}

    def __init__(self, plugin: str) -> None:
        """Initialize plugin stats api.

        Arguments:
            plugin {str} -- Name of the plugins
        """
        self.plugin = plugin

    def _load(self, url: str) -> dict:
        """Load an URL and return JSON.

        Arguments:
            url {str} -- URL to fetch from

        Returns:
            dict -- JSON as dict
        """
        logging.info(f'Loading: {url}')
        client: httpx.Client = httpx.Client(http2=False)
        response: httpx._models.Response = client.get(
            url, headers=self.__class__.headers)

        return response.json()

    def active_versions(self) -> dict:
        """Active versions.

        Returns:
            dict -- JSON
        """
        url: str = f'{SCHEME}://{BASE_URL}{ENDPOINT_ACTIVE_VERSIONS}' \
                   .replace(':plugin', self.plugin)
        return self._load(url)

    def active_installs(self, limit: int = 730) -> dict:        
        """Active installs.

        Keyword Arguments:
            limit {int} -- Number of historical data days (default: {730})

        Returns:
            dict -- JSON
        """
        url: str = f'{SCHEME}://{BASE_URL}{ENDPOINT_ACTIVE_INSTALLS}' \
                   .replace(':plugin', self.plugin) \
                   .replace(':limit', str(limit))
        return self._load(url)

    def downloads(self, limit: int = 730) -> dict:
        """Plugin downloads.

        Keyword Arguments:
            limit {int} -- Number of historical data days (default: {730})

        Returns:
            dict -- JSON
        """
        url: str = f'{SCHEME}://{BASE_URL}{ENDPOINT_DOWNLOADS}' \
                   .replace(':plugin', self.plugin) \
                   .replace(':limit', str(limit))
        return self._load(url)

    def downloads_summary(self) -> dict:
        """Plugin downloads summary.

        Returns:
            dict -- JSON
        """
        url: str = f'{SCHEME}://{BASE_URL}{ENDPOINT_DOWNLOADS_SUMMARY}' \
                   .replace(':plugin', self.plugin)
        return self._load(url)
    
    def info(self) -> dict:
        """Plugin info.

        Returns:
            dict -- JSON
        """
        url: str = f'{SCHEME}://{BASE_URL}{ENDPOINT_INFO}' \
                   .replace(':plugin', self.plugin)
        
        result: dict = self._load(url)
        if 'plugins' not in result:
            raise RuntimeError('Unexpected result. Field plugin was not found')
        if len(result['plugins']) < 1:
            raise PluginNotFoundException(f'{self.plugin} not found')

        return result['plugins'][0]