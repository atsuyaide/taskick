# Tama(仮)

TamaはPythonで実装されたイベント駆動のスクリプト自動実行ライブラリです.
利用者は実行するスクリプトの開発に集中し, 設定ファイル(YAML)を作成するだけで任意のタイミングでスクリプトを自動実行できます.

Tamaの主な機能は以下です.

- 実行したいスクリプトの起動タイミングは設定ファイル(YAML)で管理できます.
- タスクの起動タイミングとして日時, またはディレクトリ・ファイル操作を発火条件とすることが可能です.
- スケージュール実行の指定には[Crontab](https://www.tutorialspoint.com/unix_commands/crontab.htm)のフォーマットで利用できます.
- ディレクトリ・ファイル操作の検知には[Watchdog](https://github.com/gorakhargosh/watchdog)を利用しており, 任意の[event API](https://python-watchdog.readthedocs.io/en/stable/api.html#module-watchdog.events)を設定ファイルから指定して利用可能です.
## Usage

```shell
git clone https://github.com/kappa000/tama.git
cd ./tama
poetry install
poetry shell
python -m tama --debug
```
後は放置しておけば、指定された間隔・時間でjobが実行される.
