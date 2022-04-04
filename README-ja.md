# Taskick

Taskick は, スクリプトやコマンドを自動的に実行するイベント駆動型のPythonライブラリです.
面倒な定型作業や操作を自動化するだけでなく, [アプリケーション](https://github.com/atsuyaide/taskick#toy-example)の開発も容易にします.

[English ver. README](https://github.com/atsuyaide/taskick)

Taskickの主な機能は以下の通りです.

- コマンドやスクリプトを自動実行できます.
- スクリプトの実行タイミングや振る舞いを設定ファイル（YAML）で管理できます.
- タスクのトリガーとして, 日付やディレクトリ・ファイル操作などを指定できます.

また,

- 実行スケジュールはCrontabフォーマットで指定可能です.
- ディレクトリやファイルの操作の検出には[Watchdog](https://github.com/gorakhargosh/watchdog)を使用します. Watchdogが提供する任意の[イベントAPI](https://python-watchdog.readthedocs.io/en/stable/api.html#module-watchdog.events)は設定ファイルから指定することができます.

## インストール

```shell
$ pip install taskick
$ python -m taskick
Taskick 0.1.5a4
usage: __main__.py [-h] [--verbose] [--version] [--file FILE [FILE ...]]
                   [--log_config LOG_CONFIG]

optional arguments:
  -h, --help            show this help message and exit
  --verbose, -v         increase the verbosity of messages: '-v' for normal
                        output, '-vv' for more verbose output and '-vvv' for
                        debug
  --version, -V         display this application version and exit
  --file FILE [FILE ...], -f FILE [FILE ...]
                        select task configuration files (YAML)
  --log-config LOG_CONFIG, -l LOG_CONFIG
                        select a logging configuration file (YAML or other)
$ python -m taskick -V
Taskick 0.1.5a4
```

## Toy Example

PNG画像をPDFに変換するtoy-exampleを紹介します.
このサンプルでは, PNG画像が特定のフォルダに保存されたことを検出すると, Taskickがスクリプトを起動します.
スクリプトは, PNGをPDFに変換し, 別のフォルダに保存します.
詳しくは, [プロジェクトページ](https://github.com/atsuyaide/taskick-example)をご覧ください.

まず[taskick-example](https://github.com/atsuyaide/taskick-example)のコードをクローンします.

```shell
git clone https://github.com/atsuyaide/taskick-example.git
```

クローンしたtaskick-exempleフォルダに移動し, 以下のコマンドを実行します.

```shell
$ cd taskick-example
$ pip install -r requirements.txt
$ python -m taskick -f welcome.yaml main.yaml -vv
INFO:taskick:Loading: welcome.yaml
INFO:taskick:Processing: Welcome_taskick
INFO:taskick:Startup execution option is selected.
INFO:taskick:Registered: Welcome_taskick
INFO:taskick:Loading: main.yaml
INFO:taskick:Processing: remove_files_in_input_folder
INFO:taskick:Startup execution option is selected.
INFO:taskick:Registered: remove_files_in_input_folder
INFO:taskick:Processing: png2pdf
INFO:taskick:Registered: png2pdf
INFO:taskick:Executing: Welcome_taskick
INFO:taskick:"remove_files_in_input_folder" is waiting for "Welcome_taskick" to finish.
Sun Mar 27 00:10:45 JST 2022 Welcome to Taskick!
waiting 5 seconds...
INFO:taskick:Executing: remove_files_in_input_folder
```

これでPNG画像をPDFに変換するアプリケーションを起動できました.

入力フォルダにPNG画像を保存すると出力フォルダに変換後のPDFファイルが出力されます.
また入力フォルダー内のファイルは, 起動時または1分ごとに自動的に削除されます.

![png2gif](https://github.com/atsuyaide/taskick/raw/main/png_to_pdf.gif)

このアプリケーションは`welcome.yaml`と`main.yaml`で構成され, Taskickがそれらタスクの実行を管理しています.
