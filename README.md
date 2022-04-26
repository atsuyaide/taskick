# Taskick

[![pypi-taskick](https://img.shields.io/pypi/v/taskick)](https://pypi.org/project/taskick/)

Taskick is an event-driven Python library that automatically executes scripts or any commands.
It not only automates tedious routine tasks and operations, but also makes it easy to develop [applications](https://github.com/atsuyaide/taskick#toy-example).

[日本語版 README](https://github.com/atsuyaide/taskick/blob/main/README-ja.md)

The main features of Taskick are as follows

- Automatically execute commands and scripts.
- Script execution timing can be managed in a configuration file (YAML).
- You can specify datetime and directory/file operations as task triggers.

And,

- Execution schedules can be specified in Crontab format.
- [Watchdog](https://github.com/gorakhargosh/watchdog) is used to detect directory and file operations.  Any [events API](https://python-watchdog.readthedocs.io/en/stable/api.html#module-watchdog.events) provided by Watchdog can be specified in the configuration file.

## Installation

```shell
$ pip install taskick==0.1.6b0
$ python -m taskick
Taskick 0.1.6b0
usage: python -m taskick [-h] [--verbose] [--version] [--batch-load BATCH_LOAD]
                         [--file FILE [FILE ...]] [--log-config LOG_CONFIG]

optional arguments:
  -h, --help            show this help message and exit
  --verbose, -v         increase the verbosity of messages: '-v' for normal output, '-vv' for more
                        verbose output and '-vvv' for debug
  --version, -V         display this application version and exit
  --batch-load BATCH_LOAD, -b BATCH_LOAD
                        configuration files can be load in batches
  --file FILE [FILE ...], -f FILE [FILE ...]
                        specify configuration files (YAML) for the task to be executed
  --log-config LOG_CONFIG, -l LOG_CONFIG
                        specify a logging configuration file
$ python -m taskick -V
Taskick 0.1.6b0
```

## Toy Example

Here is a toy-eample that converts a PNG image to PDF.
In this sample, the conversion script is automatically invoked when it detects that a PNG image has been saved to a specific folder.
The script converts the PNG to PDF and saves it in another folder.

First, clone [taskick-example](https://github.com/atsuyaide/taskick-example).

```shell
git clone https://github.com/atsuyaide/taskick-example.git
```

Then, execute the following command.

```shell
$ cd taskick-example
$ pip install -r requirements.txt
$ python -m taskick -b batch.yaml -vv
INFO:taskick:Loading: ./config/welcome.yaml
INFO:taskick:Processing: Welcome_taskick
INFO:taskick:Startup option is selected.
INFO:taskick:Registered
INFO:taskick:Loading: ./config/main.yaml
INFO:taskick:Processing: remove_files_in_input_folder
INFO:taskick:Startup option is selected.
INFO:taskick:Await option is selected.
INFO:taskick:Registered
INFO:taskick:Processing: png2pdf
INFO:taskick:Registered
INFO:taskick:Executing: Welcome_taskick
INFO:taskick:"remove_files_in_input_folder" is waiting for "Welcome_taskick" to finish.
Sun Apr 24 23:25:43 JST 2022 Welcome to Taskick!
waiting 5 seconds...
INFO:taskick:Executing: remove_files_in_input_folder
```

You can now launch an application that converts PNG images to PDF.

When a PNG image is saved in the `input` folder, a converted PDF file is output in the `output` folder.
Files in the input folder are automatically deleted at startup or every minute.


![png2gif](https://github.com/atsuyaide/taskick/raw/main/toy-example.gif)

The application consists of `welcome.yaml` and `main.yaml`, and Taskick reads the two files indirectly by loading `batch.yaml`.
For details of the configuration files, see the [project page](https://github.com/atsuyaide/taskick-example).
