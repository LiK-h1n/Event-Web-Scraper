from requests import get
from bs4 import BeautifulSoup
from smtplib import SMTP
from os import getenv
from email.message import EmailMessage
import sqlite3 as sql

URL = "https://www.songkick.com/metro-areas/29403-india-bangalore"

connection = sql.connect("data.db")


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
        List of lists each containing event name, venue, timing and link
    """
    soup = BeautifulSoup(source, "html.parser")
    names = soup.find_all("strong", {"class": None})
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
        Stores a provided row into the database

        Parameters
        ----------
        row : tuple
            The row that has to be stored
    """
    cursor = connection.cursor()
    cursor.execute("INSERT INTO Event VALUES(?,?,?,?)", row)
    connection.commit()


def read():
    """
        Reads the database and returns it's rows

        Returns
        -------
        rows : list
            List containing rows as tuples
    """
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM Event")
    rows = cursor.fetchall()
    return rows


def delete(row):
    """
        Deletes the provided row from the database

        Parameters
        ----------
        row : tuple
            The row that has to be deleted
    """
    cursor = connection.cursor()
    cursor.execute("DELETE FROM Event WHERE Name=? AND Venue=? AND Date=? AND Link=?", row)
    connection.commit()


if __name__ == "__main__":
    while True:
        scrapped = scrape(URL)
        upcoming_events = extract(scrapped)
        stored_events = read()

        for event in stored_events:
            if list(event) not in upcoming_events:
                delete(event)

        event_stored = False
        if len(upcoming_events) != 0:
            for event in upcoming_events:
                if tuple(event) not in stored_events:
                    store(event)
                    event_stored = True

            stored_events = read()
            if event_stored:
                message_content = ""
                for event in stored_events:
                    message_content += f"{event[0]}\n{event[1]}, {event[2]}\n{event[3]}\n\n"

                send_email(message_content)
