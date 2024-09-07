import os

app_dir = os.path.dirname(os.path.dirname(__file__))
scratch_dir = f"{app_dir}/temp"
download_dir = f"{scratch_dir}/raw_download"
processed_dir = f"{scratch_dir}/processed"

CONFIG_FILE_EXTENSION = '.ovpn'