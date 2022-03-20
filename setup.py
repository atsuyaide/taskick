# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['taskick']

package_data = \
{'': ['*']}

install_requires = \
['PyYAML>=6.0,<7.0', 'schedule>=1.1.0,<2.0.0', 'watchdog>=2.1.6,<3.0.0']

setup_kwargs = {
    'name': 'taskick',
    'version': '0.1.3',
    'description': '',
    'long_description': None,
    'author': 'Atsuya Ide',
    'author_email': 'atsuya.ide528@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
