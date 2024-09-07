import shutil
import subprocess
from common.files import site_dir, processed_site_dir

def main():
    mirror_site()


def mirror_site():
    shutil.rmtree(site_dir, ignore_errors=True)
    command = [
        "httrack",
        "https://www.vpngate.net/en/",
        "-O",
        site_dir,
    ]
    subprocess.run(command)

if __name__ == "__main__":
    main()