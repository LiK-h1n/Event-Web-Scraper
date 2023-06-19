from requests import get
from bs4 import BeautifulSoup
from csv import writer
from pandas import read_csv

URL = "https://www.songkick.com/metro-areas/29403-india-bangalore"


def scrape(url):
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
    names = soup.find_all("strong")
    venues = soup.find_all("a", {"class": "venue-link"})
    dates = soup.find_all("time")
    dates = [date.text for date in dates if date.text != ""]
    return [[name.text, venue.text, date] for name, venue, date in zip(names, venues, dates)]


def send_email():
    print("Email was sent!")


def store(row):
    """
        Stores a provided row into the csv file

        Parameters
        ----------
        row : list
            The row that has to be stored
    """
    with open("data.csv", "a", encoding="utf-8") as file:
        wrt = writer(file, lineterminator="\n")
        wrt.writerow(row)


def read():
    """
        Reads the csv file and returns it as a DataFrame

        Returns
        -------
        DataFrame
            DataFrame containing event details
    """
    return read_csv("data.csv")


if __name__ == "__main__":
    scrapped = scrape(URL)
    events = extract(scrapped)
    content = read()

    if len(events) != 0:
        for event in events:
            if event not in content.values.tolist():
                store(event)
