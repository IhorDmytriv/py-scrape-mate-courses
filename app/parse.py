import csv
import logging
import re
import sys
from dataclasses import dataclass, fields, astuple
from typing import List
from urllib.parse import urljoin

from bs4 import BeautifulSoup, Tag
from requests import Session


@dataclass
class Course:
    name: str = ""
    short_description: str = ""
    duration: str = ""
    link: str = ""


BASE_URL = "https://mate.academy/"
session = Session()

COURSE_FIELDS = [field.name for field in fields(Course)]

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout)
    ],
)


def get_page_soup(url: str) -> BeautifulSoup:
    response = session.get(url)
    return BeautifulSoup(response.text, "html.parser")


def delete_duplicates_tags(tags: List[Tag]) -> List[Tag]:
    unique_tags = []
    for tag in tags:
        if tag not in unique_tags:
            unique_tags.append(tag)

    return unique_tags


def get_courses_from_page(page_soup: BeautifulSoup) -> List[Course]:
    logging.info("Get courses from page")

    courses = []
    courses_tag_a = page_soup.find_all("a", href=re.compile(r"^/courses/"))
    # Delete duplicates
    courses_tag_a = delete_duplicates_tags(courses_tag_a)

    for tag_a in courses_tag_a:

        link = tag_a.get("href")
        if "source" in link:
            continue

        li = tag_a.find("li")
        if not li:
            continue

        course_link = (urljoin(BASE_URL, link))
        course_name = (li.text.strip())

        courses.append(Course(name=course_name, link=course_link))

    return courses


def parse_course_page(course: Course) -> Course:
    logging.info(f"Parse course {course.name}")

    page_soup = get_page_soup(course.link)

    desc_tag = page_soup.find("p", class_=re.compile(r"Profession"))
    if desc_tag:
        course.short_description = desc_tag.text.strip()

    duration_tag = page_soup.find("div", string=re.compile(r"місяці"))
    if duration_tag:
        course.duration = duration_tag.text.strip()

    return course


def write_courses_to_csv(courses: List[Course]) -> None:
    with open("courses.csv", "w", newline="") as file:
        writer = csv.writer(file)
        writer.writerow(COURSE_FIELDS)
        writer.writerows([astuple(course) for course in courses])
    logging.info("Courses written to csv...!")


def get_all_courses() -> list[Course]:
    page_soup = get_page_soup(BASE_URL)
    courses = get_courses_from_page(page_soup)
    list_parsed_courses = [parse_course_page(course) for course in courses]
    logging.info("Done!")
    write_courses_to_csv(list_parsed_courses)
    return list_parsed_courses


if __name__ == "__main__":
    get_all_courses()
