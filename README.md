# Taskick

taskickはPythonで実装されたイベント駆動のスクリプト自動実行ライブラリです.
利用者は実行するスクリプトの開発に集中し, 設定ファイル(YAML)を作成するだけで任意のタイミングでスクリプトを自動実行できます.

[日本語版README](./README-ja.md)

Taskickの主な機能は以下です.

- 実行したいスクリプトの起動タイミングは設定ファイル(YAML)で管理できます.
- タスクの起動タイミングとして日時, またはディレクトリ・ファイル操作を発火条件とすることが可能です.
- スケージュール実行の指定には[Crontab](https://www.tutorialspoint.com/unix_commands/crontab.htm)のフォーマットで利用できます.
- ディレクトリ・ファイル操作の検知には[Watchdog](https://github.com/gorakhargosh/watchdog)を利用しており, 任意の[event API](https://python-watchdog.readthedocs.io/en/stable/api.html#module-watchdog.events)を設定ファイルから指定して利用可能です.

## Installation

```shell
$ pip install taskick
$ python -m taskick --version
Taskick 0.1.1
```

## Toy Example

PNG画像をPDFに変換するアプリケーションのtoy exampleを提示します.

まずexampleリポジトリをcloneしてください.

```shell
git clone https://github.com/kappa000/taskick-example.git
```

cloneしたディレクトリに移動し, 以下のTaskickを起動します.

```shell
$ cd taskick-example
$ python -m taskick -f jobconf.yaml -v info
INFO:taskick:Loading tasks...
INFO:taskick:Processing: example_task_1
INFO:taskick:Immediate execution option is selected.
INFO:taskick:Processing: example_time_trigger_task_1
INFO:taskick:Immediate execution option is selected.
INFO:taskick:Processing: example_file_trigger_task_1
INFO:taskick:Processing: example_file_trigger_task_2
INFO:taskick:Done.
INFO:taskick:Executing: example_task_1
INFO:taskick:Executing: example_time_trigger_task_1
Sat Mar 19 21:15:09 JST 2022 Hello Taskick! My HOME directory is /Users/kappa
2022-03-19 21:15:09.422750: hello Taskick! This task runs every 2 minutes.
```

inputフォルダに適当なPNG画像を保存すると, outputに変換されたPDFファイルが出力されます.
またinputフォルダにあるファイルは起動時, 毎分自動的に削除されます.

![convert png to pdf](./convert_png2pdf.gif)

これらのタスクは`jobconf.yaml`で制御され, Taskickが管理しています.
