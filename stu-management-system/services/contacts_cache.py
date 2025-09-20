from django.core.cache import cache
from services.contacts import get_service, create_contact, get_numbers_in_group
CONTACTS_KEY = "google_contacts_numbers"

def load_contacts():
    service = get_service()
    numbers_list = get_numbers_in_group(service, group_name = "ShortCourses")
    cache.set(CONTACTS_KEY, set(numbers_list), timeout=None)

def get_contacts():
    return cache.get(CONTACTS_KEY, set())

def add_contact_cache(number):
    contacts = get_contacts()
    contacts.add(number)
    cache.set(CONTACTS_KEY, contacts, timeout=None)

def contact_exists(number):
    return number in get_contacts()

load_contacts()