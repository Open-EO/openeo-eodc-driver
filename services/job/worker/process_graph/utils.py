from random import choice
from string import ascii_lowercase, digits

def generate_random_id(size=5):
    return "".join(choice(ascii_lowercase + digits) for _ in range(size))