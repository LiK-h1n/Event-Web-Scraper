from requests import get
import selectorlib

URL = "https://www.songkick.com/metro-areas/29403-india-bangalore"


def scrape(url=URL):
    """
    Scrapes the website's view-source from the URL

    Parameters
    ----------
    url : str
        The website's url to scrape from

    Returns
    -------
    source: str
        The website's view-source
    """

    response = get(url)
    source = response.text
    return source


if __name__ == "__main__":
    help(scrape)
