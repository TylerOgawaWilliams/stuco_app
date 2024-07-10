import unicodedata
import logging

LOGGER = logging.getLogger(__name__)


def generate_username(email):
    # Using Python 3 and Django 1.11+, usernames can contain alphanumeric
    # (ascii and unicode), _, @, +, . and - characters. So we normalize
    # it and slice at 150 characters.
    first_part_of_email = email.split("@")[0]
    return unicodedata.normalize("NFKC", first_part_of_email)[:150]
