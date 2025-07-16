import csv
import logging
import re
import sys
from dataclasses import dataclass, fields, astuple
from typing import List

from bs4 import BeautifulSoup
from requests import Session


@dataclass
class Course:
    name: str
    short_description: str = ""
    duration: str = ""


BASE_URL = "https://mate.academy/"
session = Session()

COURSE_FIELDS = [field.name for field in fields(Course)]

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("app.log", encoding="utf-8"),
        logging.StreamHandler(sys.stdout)
    ],
)


def get_page_soup(url: str) -> BeautifulSoup:
    response = session.get(url)
    return BeautifulSoup(response.text, "html.parser")


def get_courses_from_page(page_soup: BeautifulSoup) -> List[Course]:
    courses = []
    courses_a = page_soup.find_all("a", href=re.compile(r"^/courses/"))
    for tag_a in courses_a:
        li = tag_a.find("li")
        if li:
            courses.append(li.text.strip())
    # Delete duplicates
    courses = list(set(courses))
    return [Course(name=course_name) for course_name in courses]


def write_courses_to_csv(courses: list[Course]) -> None:
    with open("courses.csv", "w", newline="") as file:
        writer = csv.writer(file)
        writer.writerow(COURSE_FIELDS)
        writer.writerows([astuple(course) for course in courses])
    logging.info("Courses written to csv...!")


def get_all_courses() -> list[Course]:
    page_soup = get_page_soup(BASE_URL)
    return get_courses_from_page(page_soup)
    # write_courses_to_csv(courses=courses)


if __name__ == "__main__":
    get_all_courses()
