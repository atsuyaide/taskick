# Taskick(仮)

taskickはPythonで実装されたイベント駆動のスクリプト自動実行ライブラリです.
利用者は実行するスクリプトの開発に集中し, 設定ファイル(YAML)を作成するだけで任意のタイミングでスクリプトを自動実行できます.

Taskickの主な機能は以下です.

- 実行したいスクリプトの起動タイミングは設定ファイル(YAML)で管理できます.
- タスクの起動タイミングとして日時, またはディレクトリ・ファイル操作を発火条件とすることが可能です.
- スケージュール実行の指定には[Crontab](https://www.tutorialspoint.com/unix_commands/crontab.htm)のフォーマットで利用できます.
- ディレクトリ・ファイル操作の検知には[Watchdog](https://github.com/gorakhargosh/watchdog)を利用しており, 任意の[event API](https://python-watchdog.readthedocs.io/en/stable/api.html#module-watchdog.events)を設定ファイルから指定して利用可能です.

## Installation

```shell
$ pip install taskick
$ python -m taskick --version
Taskick 0.1.0
```

## Toy Examples

まず, 空の設定ファイル(YAML)を用意します.

```shell
$ touch jobconf.yaml
```

### Taskick起動時にTaskを起動する

ファイルに下記を記載します.

```yaml
example_task:
  status: 1 # 0 -> This task is inactive. 1 -> This task is active.
  commands:
    - echo
    - Hello Taskick!
  execution:
    event_type: null
```

TaskickはStatusがActiveなtaskのみ読み込みます.

Taskickを起動すると以下の出力が得られます.

```shell
$ python -m taskick -f ./jobconf.yaml
Hello Taskick!
```

### Taskをスケジュール実効する

ファイルに下記を記載します.

```yaml
example_time_trigger_task:
  status: 1
  commands:
    - echo
    - Hello Taskick! This task runs every one minute.
  execution:
    immediate: false
    event_type: time
    detail:
      when: "*/1 * * * *"
```

Taskickを起動すると以下の出力が得られます.

```shell
$ python -m taskick -f ./jobconf.yaml
Hello Taskick!
```
