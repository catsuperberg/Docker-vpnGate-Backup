import os

app_dir = os.path.dirname(os.path.dirname(__file__))
ram_dir = f"{app_dir}/ram"
scratch_dir = f"{ram_dir}/scratch"
buffer_dir = f"{ram_dir}/buffer"
buffer_config_dir = f"{buffer_dir}/configs"
buffer_site_dir = f"{buffer_dir}/site"

CONFIG_FILE_EXTENSION = '.ovpn'
IMAGE_EXTENSIONS = ['.jpg', '.png']

ERROR_POSTFIX = "ERROR"
SITE_POSTFIX = "(SITE)"