# Taskick(仮)

イベント駆動のスクリプト自動実行ライブラリ.

- 設定ファイル(```jobcong.yaml```)をライブラリが読み込み, タスクの実行スケジュール自動管理する.
- 実行スケージュールは[Crontab](https://www.tutorialspoint.com/unix_commands/crontab.htm)のフォーマットで読み込み可能にする.
- 今後[Watchdog](https://github.com/gorakhargosh/watchdog)を利用し, ディレクトリ操作とスクリプト実行を連携させる予定.
## Usage

```shell
git clone https://github.com/kappa000/taskick.git
cd ./taskick
poetry install
poetry shell
python -m taskick --debug
```
後は放置しておけば、指定された間隔・時間でjobが実行される.
