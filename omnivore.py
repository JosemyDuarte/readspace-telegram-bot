from omnivoreql import OmnivoreQL


class OmnivoreQLClient:
    """
    OmnivoreQLClient Class
    ======================

    A wrapper around the OmnivoreQL client to make it easier to use.

    Attributes
    ----------

    - ``client``: An instance of the OmnivoreQL client responsible for making API requests.

    Methods
    -------

    ``__init__(self, token)``
        Initializes the OmnivoreQLClient with the provided API token.

        :param token: The Omnivore API token for authentication.

    ``get_profile(self)``
        Retrieves the user profile information from the OmnivoreQL API.

        :returns: A dictionary containing the user profile information.

    ``get_articles(self, query, cursor=None)``
        Retrieves a list of articles based on the specified query and cursor.

        :param query: The query string to filter articles.
        :param cursor: The cursor for paginating through the results. Defaults to None.

        :returns: A dictionary containing information about the articles matching the query.

    Usage
    -----

    1. Initialize OmnivoreQLClient:

        .. code-block:: python

            omnivore_client = OmnivoreQLClient("your_api_token")

    2. Get user profile:

        .. code-block:: python

            profile = omnivore_client.get_profile()

    3. Get articles with a query:

        .. code-block:: python

            articles = omnivore_client.get_articles(query="in:archive", cursor="10")
    """

    def __init__(self, token: str):
        self.client = OmnivoreQL(token)

    def get_profile(self) -> dict:
        try:
            return self.client.get_profile()
        except Exception as e:
            print(e)
            return {}

    def get_articles(self, query: str, cursor: str = None) -> dict:
        return self.client.get_articles(query=query, cursor=cursor)


class ArticleDownloader:
    """
    ArticleDownloader Class
    =======================

    This class facilitates the downloading of articles based on specific criteria, such as the presence of a given label.

    Attributes
    ----------

    - ``client``: An instance of the OmnivoreQLClient class responsible for making API requests.

    Methods
    -------

    ``__init__(self, client: OmnivoreQLClient)``
        Initializes the ArticleDownloader with the provided OmnivoreQLClient instance.

        :param client: An instance of the OmnivoreQLClient class.

    ``download_articles(self, label_name: str) -> list``
        Downloads articles based on the specified label.

        :param label_name: The label name used for filtering articles.

        :returns: A list of articles matching the specified criteria.

    ``should_include_article(article, label_name: str) -> bool``
        Determines whether an article should be included based on the presence of a given label.

        :param article: The article to be checked.
        :param label_name: The label name to check for.

        :returns: True if the article should be included, False otherwise.

    ``get_next_page_params(articles: dict) -> str or None``
        Retrieves the cursor for paginating to the next page of articles.

        :param articles: A dictionary containing information about the current page of articles.

        :returns: The cursor for the next page if it exists, None otherwise.

    Usage
    -----

    1. Initialize the ArticleDownloader:

        .. code-block:: python

            article_downloader = ArticleDownloader(omnivore_client)

    2. Download articles with a specified label:

        .. code-block:: python

            downloaded_articles = article_downloader.download_articles(label_name="readspace")
    """

    def __init__(self, client: OmnivoreQLClient):
        self.client = client

    def download_articles(self, label_name: str) -> list:
        profile = self.client.get_profile()
        if profile is None:
            raise Exception("Could not get profile")

        articles_query = "in:archive"
        all_articles = []
        end_cursor = None

        while True:
            articles = self.client.get_articles(query=articles_query, cursor=end_cursor)
            if not articles["search"]["pageInfo"]["hasNextPage"]:
                break

            for article in articles["search"]["edges"]:
                if self.should_include_article(article, label_name):
                    all_articles.append(article)

            end_cursor = self.get_next_page_params(articles)
            if end_cursor is None:
                break

        return all_articles

    @staticmethod
    def should_include_article(article, label_name: str) -> bool:
        highlights = article["node"]["highlights"]
        if highlights is None or not highlights:
            return False

        for highlight in highlights:
            labels = highlight["labels"]
            if labels and any(label["name"] == label_name for label in labels):
                return True

        return False

    @staticmethod
    def get_next_page_params(articles: dict) -> str or None:
        page_info = articles["search"]["pageInfo"]
        return page_info["endCursor"] if page_info["hasNextPage"] else None
