import os

app_dir = os.path.dirname(os.path.dirname(__file__))
ram_dir = f"{app_dir}/ram"
scratch_dir = f"{ram_dir}/scratch"
buffer_dir = f"{ram_dir}/buffer"
buffer_config_dir = f"{buffer_dir}/config"
buffer_site_dir = f"{buffer_dir}/site"
buffer_config_dir = f"{buffer_dir}/configs"
buffer_site_dir = f"{buffer_dir}/site"

backup_dir = f"{app_dir}/backup"
backup_local_dir = f"{backup_dir}/local"
backup_remote_dir = f"{backup_dir}/remote"

CONFIG_FILE_EXTENSION = ".ovpn"
IMAGE_EXTENSIONS = [".jpg", ".png"]

ERROR_POSTFIX = "ERROR"
SITE_POSTFIX = "(SITE)"
