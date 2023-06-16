from requests import get
from bs4 import BeautifulSoup

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


def extract(source):
    """
    Returns a list of upcoming events

    Parameters
    ----------
    source : str
        The source-code of the webpage

    Returns
    -------
    list
        List of lists each containing event name, venue and timing
    """
    soup = BeautifulSoup(source, "html.parser")
    events = soup.find_all("strong")
    venues = soup.find_all("a", {"class": "venue-link"})
    dates = soup.find_all("time")
    dates = [date.text for date in dates if date.text != ""]
    return [[event.text, venue.text, date] for event, venue, date in zip(events, venues, dates)]


if __name__ == "__main__":
    scrapped = scrape(URL)
    print(extract(scrapped))
