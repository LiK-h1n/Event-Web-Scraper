from requests import get
from bs4 import BeautifulSoup
from csv import writer
from pandas import read_csv
from smtplib import SMTP
from os import getenv
from email.message import EmailMessage

URL = "https://www.songkick.com/metro-areas/29403-india-bangalore"
CSV_PATH = "data.csv"


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
    links = soup.find_all("a", {"class": "event-link chevron-wrapper"})
    return [[name.text, venue.text, date, f"https://www.songkick.com{link['href']}"] for name, venue, date, link in zip(names, venues, dates, links)]


def send_email(content):
    """
        Sends an email consisting of upcoming events

        Parameters
        ----------
        content : str
            The message content that the email contains
    """
    message = EmailMessage()
    message["Subject"] = "Upcoming Events"
    message.set_content(content)

    sender = getenv("EMAIL")
    password = getenv("PASSWORD")

    gmail = SMTP("smtp.gmail.com", 587)
    gmail.ehlo()
    gmail.starttls()
    gmail.login(sender, password)
    gmail.sendmail(sender, sender, message.as_string())
    gmail.quit()
    print("Email was sent")


def store(row):
    """
        Stores a provided row into the csv file

        Parameters
        ----------
        row : list
            The row that has to be stored
    """
    with open(CSV_PATH, "a", encoding="utf-8") as file:
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
    return read_csv(CSV_PATH)


if __name__ == "__main__":
    while True:
        scrapped = scrape(URL)
        upcoming_events = extract(scrapped)
        stored_events = read()

        for index, event in enumerate(stored_events.values.tolist()):
            if event not in upcoming_events:
                stored_events.drop(index, inplace=True)
        stored_events.to_csv(CSV_PATH, index=False)

        event_stored = False
        if len(upcoming_events) != 0:
            for event in upcoming_events:
                if event not in stored_events.values.tolist():
                    store(event)
                    event_stored = True

            stored_events = read()
            if event_stored:
                message_content = ""
                for index, row in stored_events.iterrows():
                    message_content += f"{row['Name']}\n{row['Venue']}, {row['Date']}\n{row['Link']}\n\n"

                send_email(message_content)
