import shutil
import subprocess
from common.files import scratch_dir, SITE_POSTFIX
from common.date_string import get_current_timestemp

timestamp = get_current_timestemp()
directory = f"{scratch_dir}/{timestamp} {SITE_POSTFIX}"


def main():
    mirror_site()
    return directory


def mirror_site():
    shutil.rmtree(directory, ignore_errors=True)
    command = [
        "httrack",
        "https://www.vpngate.net/en/",
        "-O",
        directory,
    ]
    subprocess.run(command)


if __name__ == "__main__":
    main()
