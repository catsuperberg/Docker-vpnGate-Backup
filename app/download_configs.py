import requests
import asyncio
import asyncping3
import base64
import shutil
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from util.timing_decorator import timing_decorator, async_timing_decorator
from util.row_as_dict import row_as_dict
from common.files import download_dir, CONFIG_FILE_EXTENSION

EXPECTED_FIRST_LINE = '*vpn_servers'
UNSUPPORTED_FORMAT_FILE = 'ERROR_FORMAT_UNSUPPORTED_FALLBACK_TO_RAW_FILE_FROM_URL'
VPN_LIST_CSV_FILE = 'VpnList.csv'
CONFIG_DIRECTORY_NAME = 'OpenVPN'
CONFIG_DIRECTORY_PATH = f"{download_dir}/{CONFIG_DIRECTORY_NAME}"

IP_KEY = 'IP'
IS_REACHABLE_KEY = 'Reachable'
BASE64_KEY = 'OpenVPN_ConfigData_Base64'
TEXT_KEY = 'OpenVPN_Config_File'

INVALID_ROWS = ['*', '']

HEADERS = {
    "Accept": "text/plain",
    "Accept-Encoding": "br, zstd, gzip, compress, deflate",
    "User-Agent": "Chrome/122.0.0.0",
}

PRIMARY_URL = "http://www.vpngate.net/api/iphone/"
SECONDARY_URL = "https://www.vpngate.net/api/iphone/"


executor = ThreadPoolExecutor(99)


@timing_decorator
def main():
    try:
        clear_temp()
        response, csv_stream, csv_header = open_csv_stream()
    except:
        print("Failed to get parsable data")
        return

    vpns = asyncio.run(csv_with_reachability_tested(csv_stream, csv_header))
    if(len(vpns) <= 0):
        print("No vpns found")
        return

    decode_configs(vpns)
    reachable_vpns = [vpn for vpn in vpns if vpn[IS_REACHABLE_KEY]]
    extract_configs(reachable_vpns)
    save_csv(vpns)
    print_result_info(vpns, reachable_vpns)

    response.close()

# needed for better compression
def decode_configs(vpns):
    for vpn in vpns:
        vpn[TEXT_KEY] = base64.b64decode(vpn.pop(BASE64_KEY))

def clear_temp():
    dir = Path(download_dir)
    shutil.rmtree(dir, ignore_errors=True)
    dir.mkdir(parents=True, exist_ok=True)


@timing_decorator
def open_csv_stream():
    response = requests.get(PRIMARY_URL, headers=HEADERS, stream=True)
    if response.status_code != 200:
        response = requests.get(SECONDARY_URL, stream=True)
    if response.status_code != 200:
        raise Exception("Failed to connect to API")

    csv_body_stream = response.iter_lines(decode_unicode=True)
    first_line = next(csv_body_stream)
    if first_line != EXPECTED_FIRST_LINE:
        save_fallback('\n'.join([first_line] + list(csv_body_stream)))
        raise Exception("Unexpected file structure")

    csv_header = next(csv_body_stream).split(',')
    return response, csv_body_stream, csv_header


@async_timing_decorator
async def csv_with_reachability_tested(stream, header):
    awaitables = [mark_is_reachable(row, header) for row in stream if row not in INVALID_ROWS]
    return await asyncio.gather(*awaitables)

async def mark_is_reachable(row, header):
    data = row_as_dict(row, header)
    data[IS_REACHABLE_KEY] = await ping(data[IP_KEY])
    return data

async def ping(ip):
    return isinstance(await asyncping3.ping(ip, timeout=0.5), float)


@timing_decorator
def extract_configs(reachable_vpns):
    Path(CONFIG_DIRECTORY_PATH).mkdir(parents=True, exist_ok=True)
    executor.map(write_config_content, reachable_vpns)

def write_config_content(vpn):
    with open(f"{CONFIG_DIRECTORY_PATH}/{vpn['CountryShort']}-{vpn['IP']}({vpn['#HostName']}){CONFIG_FILE_EXTENSION}", "wb") as file:
        file.write(vpn[TEXT_KEY])


def save_csv(vpns):
    header_line = ','.join(vpns[0].keys())
    data_lines = [','.join([str(value) for value in vpn.values()]) for vpn in vpns]
    content = '\n'.join([header_line] + data_lines)
    with open(f"{download_dir}/{VPN_LIST_CSV_FILE}", "w") as file:
        file.write(content)

def save_fallback(content):
    with open(f"{download_dir}/{UNSUPPORTED_FORMAT_FILE}", "w") as file:
        file.write(content)


def print_result_info(vpns, reachable_vpns):
    full_config_count = len(vpns)
    reachable_count = len(reachable_vpns)
    print(f"Downloaded and extracted {reachable_count} out of {full_config_count} vpns in config.\nRest were filtered by pinging IPs.")


if __name__ == "__main__":
    main()
