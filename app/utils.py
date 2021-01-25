import random
import string

import requests


def random_string_generator(size=5, chars=string.ascii_lowercase + string.ascii_uppercase):
    """
    Function to create a random string, used for
    """
    return "".join(random.choice(chars) for _ in range(size))


def download_file(url, path):
    """
    :param url:
    :param path:
    :return:
    """
    try:
        r = requests.get(url, allow_redirects=True)
        open(path, 'wb').write(r.content)
        return True
    except:
        return False
