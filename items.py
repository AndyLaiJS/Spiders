# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

import scrapy
import html
import re
from datetime import datetime, timedelta
from scrapy.loader.processors import TakeFirst
from scrapy.loader import ItemLoader


def out_list(l):
    if type(l) != list:
        return [l]
    else:
        if len(l) == 0:
            return [""]
        else:
            return l


def out_string(l):
    if type(l) == list:
        return '\n'.join(l)
    else:
        return str(l)


def out_others(l):
    if type(l) != list:
        return l
    else:
        if len(l) == 1:
            return l[0]
        else:
            return l


def unavailable_check(string):
    if not string:
        return None

    keywords = ["hidden", "not provided", "not specified", "n/a", "(n/a)"]
    if string.lower() in keywords:
        return None
    else:
        return string


def process_simple_field(value):
    clean_s = process_str(value)
    if type(clean_s) == list:
        return [s.lower() for s in clean_s if unavailable_check(s)]
    else:
        return unavailable_check(clean_s)


def process_str(strings):
    if not strings:
        return None
    elif type(strings) == list:
        result = []
        for s in strings:
            s = str(s)
            clean_s = html.unescape(s).strip()
            if re.search("[a-zA-z0-9]", clean_s):
                result.append(clean_s)
        return result
    else:
        return html.unescape(strings).strip()


def process_url(strings):
    if not strings:
        return None
    elif type(strings) == list:
        result = []
        for s in strings:
            if re.search("[a-zA-z0-9]", s):
                result.append(s)
        return result
    else:
        return strings.strip()


def process_number(number):
    if type(number) in [int, float]:
        return number
    elif type(number) == list:
        number = process_str(number)[0].replace(",", "")

    number = number.lower()
    multiplier = 1
    if 'k' in number:
        multiplier = 1000
    elif 'm' in number:
        multiplier = 1000000

    number = re.findall(r'[\d\.]+', number)
    try:
        if number:
            return float(number[0]) * multiplier
        else:
            return None
    except Exception:
        return None


def process_date(date):
    if not date:
        return None

    if type(date) == list:
        date = TakeFirst()(date)
    date = date.lower().strip()

    now = datetime.now()

    # Just posted
    # Today
    if "just posted" in date or "today" in date:
        return now

    # Parsing could go wrong, not going to die and waste the other data
    try:
        if "ago" in date:
            # 10 days ago
            if "day" in date:
                days = re.findall('\d+', date)[0]
                return now - timedelta(days=days)
            # 11 minutes ago
            elif "minute" in date:
                minutes = re.findall('\d+', date)[0]
                return now - timedelta(minutes=minutes)
            # about 1 hour ago
            elif "hour" in date:
                hours = re.findall('\d+', date)[0]
                return now - timedelta(hours=hours)
            else:
                return None

        if "-" in date:
            if "t" in date:
                # 2019-12-10T01:24:25.71Z
                if "." in date:
                    return datetime.strptime(date, "%Y-%m-%dt%H:%M:%S.%fz")
                # for adecco (the plus probably means utc+): 2020-06-18T15:56:00+10:00
                elif "+" in date:
                    actual_date, timezone = date.split("+")
                    return datetime.strptime(actual_date, "%Y-%m-%dt%H:%M:%S") - timedelta(hours=int(timezone.split(":")[0]) - 8)
                # 2019-12-27T03:51:29Z
                else:
                    return datetime.strptime(date, "%Y-%m-%dt%H:%M:%S")
            # 2019-06-17
            else:
                return datetime.strptime(date, "%Y-%m-%d")

        # 01 Jun 2020
        return datetime.strptime(date, "%d %b %Y")
    except Exception:
        return None


class SalaryItem(scrapy.Item):
    max = scrapy.Field(input_processor=process_number, output_processor=out_others)
    min = scrapy.Field(input_processor=process_number, output_processor=out_others)
    salary_type = scrapy.Field(input_processor=process_simple_field)
    extra_info = scrapy.Field(input_processor=process_simple_field)
    currency = scrapy.Field(input_processor=process_simple_field)
    salary_on_display = scrapy.Field(input_processor=process_simple_field)


class RequirementItem(scrapy.Item):
    career_level = scrapy.Field(input_processor=process_simple_field)
    years_of_experience = scrapy.Field(input_processor=process_simple_field)
    education_level = scrapy.Field(input_processor=process_simple_field)
    hard_skills = scrapy.Field(output_processor=out_list)
    soft_skills = scrapy.Field(input_processor=process_str, output_processor=out_list)


class CompanyItem(scrapy.Item):
    name = scrapy.Field(input_processor=process_simple_field)
    website_url = scrapy.Field(input_processor=process_url)
    overview = scrapy.Field(input_processor=process_simple_field)
    logo_url = scrapy.Field(input_processor=process_simple_field)
    other_jobs_url = scrapy.Field(input_processor=process_url, output_processor=out_list)


class LocationItem(scrapy.Item):
    raw_location = scrapy.Field(input_processor=process_simple_field)
    formatted_location = scrapy.Field(input_processor=process_simple_field)
    latitude = scrapy.Field(input_processor=process_number, output_processor=out_others)
    longitude = scrapy.Field(input_processor=process_number, output_processor=out_others)


class JobItem(scrapy.Item):
    job_id = scrapy.Field()
    title = scrapy.Field(input_processor=process_str)
    salary = scrapy.Field(output_processor=out_others)
    job_rating = scrapy.Field(input_processor=process_str)
    body = scrapy.Field(input_processor=process_str)
    summary = scrapy.Field(input_processor=process_str)
    duties = scrapy.Field(output_processor=out_list)
    requirement = scrapy.Field(output_processor=out_others)
    industry = scrapy.Field(input_processor=process_simple_field, output_processor=out_list)
    employment_type = scrapy.Field(input_processor=process_simple_field)
    function = scrapy.Field(input_processor=process_simple_field, output_processor=out_list)
    benefits = scrapy.Field(input_processor=process_simple_field, output_processor=out_list)
    location = scrapy.Field(output_processor=out_others)
    post_date = scrapy.Field(input_processor=process_date, output_processor=out_others)
    page_url = scrapy.Field(input_processor=process_url)
    company = scrapy.Field(output_processor=out_others)
    source = scrapy.Field()
    related_jobs = scrapy.Field(output_processor=out_list)
    head = scrapy.Field(output_processor=out_others)
    fetch_date = scrapy.Field(output_processor=out_others)


def get_loader(item, selector, default_input_processor=None, default_output_processor=out_string):
    loader = ItemLoader(item, selector=selector)
    loader.default_output_processor = default_output_processor
    if default_input_processor:
        loader.default_input_processor = default_input_processor

    return loader
