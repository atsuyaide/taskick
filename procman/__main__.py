import os
import sys
import yaml
from logging import getLogger

logger = getLogger('procamn')

EXAMPLE_JOBCONF = {
    'example_process_1': {
        'execute': {
            'immediate': True,
            'when': '0 * * * *',
            'script': './sandbox/example.py'
        },
        'options': {
            'message': '"procman. Run by time event trigger."'
        }
    },
    'example_process_2': {
        'execute': {
            'immediate': True,
            'when': 'create ./sandbox/example*',
            'script': './sandbox/example.py'
        },
        'options': {
            'message': '"procman. Run by file event trigger."'
        }
    }
}

EXAMPLE_SCRIPT = '''
import argparse
parser = argparse.ArgumentParser(
    description="This is example procman script.")
parser.add_argument("--message", default="world", type=str)
args = parser.parse_args()

print(f"hello {args.message}!")
'''


def _init(args: list) -> None:
    def yes_or_no() -> bool:
        while True:
            ans = input('y/n>> ').upper()
            if ans in ['Y', 'YES']:
                return True
            elif ans in ['N', 'NO']:
                return False
            else:
                print('Retype "Yes" or "No"')

    if len(args) == 2:
        folder_path = ''
    elif len(args) == 3:
        folder_path = args[2]
    else:
        print('Too many arguments.')
        return 1

    INIT_FILES = {
        os.path.join(os.getcwd(), folder_path, 'jobconf.yaml'): EXAMPLE_JOBCONF,
        os.path.join(os.getcwd(), folder_path, 'example.py'): EXAMPLE_SCRIPT
    }

    for file_path, script in INIT_FILES.items():
        if os.path.isfile(file_path):
            print(f'"{file_path}" is already exist. Overwrite?')
            if yes_or_no():
                pass
            else:
                continue

        with open(file_path, 'w') as f:
            if '.yaml' in file_path:
                yaml.dump(script, f, encoding='utf-8', allow_unicode=True)
            else:
                f.write(script)
            print(f'=> Saved: {file_path}')

    return 0


def _main(job_config: str) -> None:
    with open(job_config, 'r') as f:
        config = yaml.safe_load(f)

    print(config)


def main() -> None:
    args = sys.argv

    if len(args) == 1:
        return _main('./jobconf.yaml')
    elif args[1] == 'init':
        _init(args)
    elif os.path.isfile(args[1]):
        return _main(args[1])
    else:
        print('Invalid arguments.')


if __name__ == '__main__':
    sys.exit(main())
