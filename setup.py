from distutils.core import setup

from seija.manifest import VERSION

setup(
    name='seija',
    packages=[
        'seija',
        'seija.cogs',
        'seija.embeds',
        'seija.modules',
        'seija.reusables'
    ],
    version=VERSION,
    description='The heart of The Mapset Management Server on Discord.',
    author='Kyuunex',
    author_email='kyuunex@protonmail.ch',
    url='https://github.com/Kyuunex/Seija',
    install_requires=[
        'py-cord==2.0.0b4',
        'upsidedown',
        'pycountry',
        'Pillow',
        'aiosqlite',
        'bs4',
        'aiohttp',
        'beautifulsoup4',
        'psutil',
        'aioosuapi @ git+https://github.com/Kyuunex/aioosuapi.git@1.2.4',
        'aioosuwebapi @ git+https://github.com/Kyuunex/aioosuapi.git@2.0.0-dev6',
        'python-dateutil',
        'appdirs'
    ],
)
