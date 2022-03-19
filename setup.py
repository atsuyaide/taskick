# -*- coding: utf-8 -*-
from setuptools import setup

packages = ["taskick"]

package_data = {"": ["*"]}

install_requires = ["PyYAML>=6.0,<7.0", "schedule>=1.1.0,<2.0.0", "watchdog>=2.1.6,<3.0.0"]

setup_kwargs = {
    "name": "taskick",
    "version": "0.1.2",
    "description": "",
    "long_description": "# Taskick\n\ntaskickはPythonで実装されたイベント駆動のスクリプト自動実行ライブラリです.\n利用者は実行するスクリプトの開発に集中し, 設定ファイル(YAML)を作成するだけで任意のタイミングでスクリプトを自動実行できます.\n\n[日本語版README](./README-ja.md)\n\nTaskickの主な機能は以下です.\n\n- 実行したいスクリプトの起動タイミングは設定ファイル(YAML)で管理できます.\n- タスクの起動タイミングとして日時, またはディレクトリ・ファイル操作を発火条件とすることが可能です.\n- スケージュール実行の指定には[Crontab](https://www.tutorialspoint.com/unix_commands/crontab.htm)のフォーマットで利用できます.\n- ディレクトリ・ファイル操作の検知には[Watchdog](https://github.com/gorakhargosh/watchdog)を利用しており, 任意の[event API](https://python-watchdog.readthedocs.io/en/stable/api.html#module-watchdog.events)を設定ファイルから指定して利用可能です.\n\n## Installation\n\n```shell\n$ pip install taskick\n$ python -m taskick --version\nTaskick 0.1.2\n```\n\n## Toy Example\n\nPNG画像をPDFに変換するアプリケーションのtoy exampleを提示します.\n\nまずexampleリポジトリをcloneしてください.\n\n```shell\ngit clone https://github.com/kappa000/taskick-example.git\n```\n\ncloneしたディレクトリに移動し, 以下のTaskickを起動します.\n\n```shell\n$ cd taskick-example\n$ python -m taskick -f jobconf.yaml -v info\nINFO:taskick:Loading tasks...\nINFO:taskick:Processing: example_task_1\nINFO:taskick:Immediate execution option is selected.\nINFO:taskick:Processing: example_time_trigger_task_1\nINFO:taskick:Immediate execution option is selected.\nINFO:taskick:Processing: example_file_trigger_task_1\nINFO:taskick:Processing: example_file_trigger_task_2\nINFO:taskick:Done.\nINFO:taskick:Executing: example_task_1\nINFO:taskick:Executing: example_time_trigger_task_1\nSat Mar 19 21:15:09 JST 2022 Hello Taskick! My HOME directory is /Users/kappa\n2022-03-19 21:15:09.422750: hello Taskick! This task runs every 2 minutes.\n```\n\ninputフォルダに適当なPNG画像を保存すると, outputに変換されたPDFファイルが出力されます.\nまたinputフォルダにあるファイルは起動時, 毎分自動的に削除されます.\n\n![convert png to pdf](./convert_png2pdf.gif)\n\nこれらのタスクは`jobconf.yaml`で制御され, Taskickが管理しています.\n",
    "author": "Atsuya Ide",
    "author_email": "atsuya.ide528@gmail.com",
    "maintainer": None,
    "maintainer_email": None,
    "url": "https://github.com/kappa000/taskick",
    "packages": packages,
    "package_data": package_data,
    "install_requires": install_requires,
    "python_requires": ">=3.8,<4.0",
}


setup(**setup_kwargs)
