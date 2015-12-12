from setuptools import setup, find_packages

setup(
    name='steam-matchup',
    version='0.0.0',
    packages=find_packages(),

    install_requires=[
        'dogpile.cache',
        'pyramid',
        'pyramid_openid',
        'scrapy',
        'waitress',
    ],

    entry_points={
        'paste.app_factory': {
            'main=steam_matchup:main',
        },
    },
)
