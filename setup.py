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
    'version': '0.1.0',
    'description': '',
    'long_description': '# Taskick(仮)\n\nイベント駆動のスクリプト自動実行ライブラリ.\n\n- 設定ファイル(```jobcong.yaml```)をライブラリが読み込み, タスクの実行スケジュール自動管理する.\n- 実行スケージュールは[Crontab](https://www.tutorialspoint.com/unix_commands/crontab.htm)のフォーマットで読み込み可能にする.\n- 今後[Watchdog](https://github.com/gorakhargosh/watchdog)を利用し, ディレクトリ操作とスクリプト実行を連携させる予定.\n## Usage\n\n```shell\ngit clone https://github.com/kappa000/taskick.git\ncd ./taskick\npoetry install\npoetry shell\npython -m taskick --debug\n```\n後は放置しておけば、指定された間隔・時間でjobが実行される.\n',
    'author': 'Atsuya Ide',
    'author_email': 'atsuya.ide528@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/kappa000/taskick',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
