from setuptools import setup, find_packages


def get_version():
    import re
    for line in open('imds/__init__.py'):
        match = re.match("__version__ *= *'(.*)'", line)
        if match:
            return match.groups()[0]
    raise RuntimeError('__version__ is not found')


requirements = [
    'requests',
    'Pillow'
]

setup(
    name='imds',
    version=get_version(),
    author='devforfu',
    url='https://github.com/devforfu/imds',
    packages=find_packages(),
    install_requires=requirements
)
