from setuptools import setup, find_packages

install_reqs = [
    l for l in
    open('reqs/install.in').readlines()
    if l and l[0] != '-'
]


setup(
    name='steam-matchup',
    version='0.0.0',
    packages=find_packages(),

    install_requires=install_reqs,
    extras_require={
        'windows': ['pywin32'],
    },

    entry_points={
        'paste.app_factory': {
            'main=steam_matchup:main',
        },
    },
)
