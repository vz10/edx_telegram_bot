# -*- coding: utf-8 -*-
from distutils.core import setup

def is_requirement(line):
    """
    Return True if the requirement line is a package requirement;
    that is, it is not blank, a comment, or editable.
    """
    # Remove whitespace at the start/end of the line
    line = line.strip()

    # Skip blank lines, comments, and editable installs
    return not (
        line == '' or
        line.startswith('-r') or
        line.startswith('#') or
        line.startswith('-e') or
        line.startswith('git+')
    )

def load_requirements(*requirements_paths):
    """
    Load all requirements from the specified requirements files.
    Returns a list of requirement strings.
    """
    requirements = set()
    for path in requirements_paths:
        requirements.update(
            line.strip() for line in open(path).readlines()
            if is_requirement(line)
        )
    return list(requirements)

setup(
    name='edx-telegram-bot',
    version='0.1',
    equires=['python-telegram-bot', 'requests'],
    author='RaccoonGang',
    author_email='info@raccoongang.com',
    packages=['edx-telegram-bot'],
    url='https://github.com/vz10/raccoonBot',
    license='BSD licence, see LICENCE.txt',
    description='Telegram bot which assistants edx users',
    long_description=open('README.txt').read(),
    zip_safe=False,
    install_requires=load_requirements('requirements.txt'),
)