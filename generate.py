"""Generate valid data for an ``inator_data.json`` file.

This module can be run as a library or as a program. It contains
variables and functions that can be used to generate a random
``inator_data.json``.

Note that this program **does not** write data to a file. Instead, it
prints the data to standard out. If you would like to save the
generated data to a file, consider using file redirection like so::

    python3.5 generate.py --inators=5 > data.json

The ``> data.json`` part tells your shell to redirect output from
the standard out pipe to a file instead.

"""
import argparse
import datetime
import json
import random
import re
import sys
import uuid

from condition import Condition
from utils import from_datetime


TIME_FORMAT = "%Y-%m-%dT%H:%M:%S"

INATORS = [
    'all-purpose-inator', 'amnesia-inator', 'babe-inator',
    'baby-cry-inator', 'back-story-inator', 'backstoryinator',
    'bad-inator', 'blow-inator', 'blow-itself-up-inator', 'boring-inator',
    'butler-inator', 'cobbler-inator', 'combine-inator',
    'confetti-inator', 'cool-inator', 'coolinator', 'cupcake-inator',
    'de-age-inator', 'de-handsome-inator', 'de-twist-inator',
    'decker-inator', 'derezz-inator', 'desert-inator', 'detwistinator',
    'disintegrator-inator', 'dodo-bird-incubator-inator',
    'dodo-bird-incubatorinator', 'double-inator', 'dough-blow-inator',
    'duplicate-inator', 'dynamic-inator', 'evil-inator', 'eye-inator',
    'faucet-inator', 'flat-a-platinator', 'forget-about-it-inator',
    'galaxy-inator', 'gimmelshtump-inator', 'gimmelshtumpinator',
    'hitch-a-ride-inator', 'home-inator', 'hug-inator',
    'if-a-tree-fell-in-the-forest-inator', 'incubator-inator',
    'inside-out-inator', 'juice-inator', 'julienn-inator',
    'key-find-inator', 'likely-inator', 'lock-inator', 'magnifinator',
    'magnify-inator', 'metal-unearth-inator', 'metal-unearthinator',
    'mind-transfer-inator', 'mindtransferinator',
    'music-video-clip-inator', 'mustache-inator', 'nice-inator',
    'non-inator', 'ohugconfetti-inator', 'other-dimension-inator',
    'outside-in-inator', 'overhang-inator', 'platyp-inator',
    'platypu-inator', 'pop-up-inator', 'purpose-inator', 'rain-inator',
    're-good-inator', 'replace-inator', 'retrieve-inator',
    'rotten-inator', 'rude-inator', 'rudeinator', 'schmaltz-inator',
    'sculpt-inator', 'slicer-inator', 'smells-like-hay-inator',
    'soup-inator', 'sphere-attract-inator', 'stain-inator', 'staininator',
    'stick-inator', 'suck-inator', 'taffy-inator',
    'tell-the-truth-inator', 'tellthetruthinator', 'transport-inator',
    'transportinator', 'turkey-inator', 'underwear-inator',
    'unearth-inator', 'up-inator', 'vaporizor-inator',
    'video-beam-hijack-non-inator'
]

LOREM_IPSUM = [
    "Lorem ipsum dolor sit amet, consectetur adipiscing elit.",
    "Curabitur finibus magna ut dui auctor, luctus tristique mi rhoncus.",
    "Donec consequat quam nec tortor tempor, non pellentesque pharetra.",
    "Mauris cursus feugiat lacinia.",
    "Donec in lectus augue.",
    "Pellentesque sit amet tempor quam.",
    "Sed a suscipit metus.",
    "Aliquam arcu nibh, finibus nec metus quis, commodo luctus justo.",
    "Morbi euismod feugiat hendrerit.",
    "Ut neque ante, scelerisque sit amet orci a, dictum ultricies lectus."
]

PLACES = ['airport', 'apartment building', 'bank', 'barber shop',
          'book store', 'bowling alley', 'bus stop', 'church',
          'convenience store', 'department store', 'fire department',
          'gas station', 'hospital', 'house', 'library', 'movie theater',
          'museum', 'office building', 'post office', 'restaurant', 'school',
          'mall', 'supermarket', 'train station']


def random_timeline():
    """Return a generator that yields ``datetime`` s.

    The generator yields randomly spaced ``datetime`` s in reverse
    chronological order. That is, every yielded ``datetime``
    represents a time that is further in the past than the one yielded
    before it. The difference between two successive ``datetime`` s is
    a random value between 24 to 72 hours.

    """
    prev = None
    while True:
        if prev is None:
            prev = datetime.datetime.now()
        delta = datetime.timedelta(hours=random.randint(25, 72))
        current = prev - delta
        yield current
        prev = current


def inator_record(name, added):
    """Return an inator record.

    Return a dictionary that represents data for an inator. Each
    record contains a randomly generated identifier, a random
    location, a random condition, and a random description. The name
    of the inator and the date/time it was added are requried as parameters.

    :param str name: The name of the inator
    :param datetime.datetime added: The date/time the inator record
        was added to the searchinator.

    :return: A dictionary representing an inator
    :rtype: dict

    """
    return {
        'ident': str(uuid.uuid4()),
        'name': name,
        'added': added,
        'location': random.choice(PLACES),
        'condition': Condition(random.randint(1, 5)),
        'description': ' '.join(random.sample(LOREM_IPSUM,
                                              random.randint(1, 5)))
    }


def random_inators(num):
    """Generate *num* random inators.

    :param int num: The number of inators to generate
    :return: A dict mapping an inator's identifier to its record
    :rtype: dict
    """
    chosen = random.sample(INATORS, num)
    records = (inator_record(i, t) for i, t in zip(chosen, random_timeline()))
    return {x['ident']: x for x in records}


def credentials(lst):
    """Return credential information.

    Format the credential data in *lst* so that it works with the
    searchinator. *lst* should contain strings of the format::

      username:password

    :param list lst: A list of colon-separated username/password pairs
    :return: A dict mapping usernames to their username/passwords
    :rtype: dict

    """
    pairs = (x.split(':') for x in lst)
    return {u: {"username": u, "password": p} for u, p in pairs}


def main():
    """Generate data suitable for use in the searchinator.

    For usage information, try running this module as a program like so::

      python3.5 generate.py --help
    """
    # Set up CLI argument parser
    parser = argparse.ArgumentParser(description='Generate -inator data')
    parser.add_argument('--inators', type=int, default=10,
                        help='The number of inators to create')
    parser.add_argument('--credentials',
                        type=str, nargs='+', default=['heinz:doof'],
                        help='Add additional credentials as username:password')
    args = parser.parse_args()

    # Check number of inators
    if args.inators < 0:
        sys.exit("Cannot generate a negative number of -inators.")

    # Check formatting of credentials. We expect only letters,
    # numbers, and underscore
    for c in args.credentials:
        if re.fullmatch(r'\w+:\w+', c) is None:
            msg = 'Credential "{}" is not formatted as "username:password".\n'
            msg += 'Be sure to only use letters, numbers, and underscores'
            msg += 'for the username and password. They must be separated'
            msg += 'by a single colon.'
            sys.exit(msg.format(c))

    # Generate data and assemble
    data = {
        "inators": random_inators(args.inators),
        "users": credentials(args.credentials)
    }

    # Print the data as a JSON object
    print(json.dumps(data, indent=4, default=from_datetime))


if __name__ == '__main__':
    # Run the program :)
    main()
