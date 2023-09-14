import json
import os
import subprocess
import requests
from adbutils._utils import adb_path
from os.path import expanduser, exists
from adbutils import AdbDevice
import platform


platform = platform.system().lower()

if platform == 'windows':
    v = '\\'
else:
    v = '/'

platform_home_folder = expanduser('~')
print(platform_home_folder)
platform_downloads_folder = f'{platform_home_folder}{v}Downloads'
platform_ethos_folder = f'{platform_home_folder}{v}.ethos-group'
platform_main_folder = f'{platform_home_folder}{v}.ethos-groups{v}gabb-adb-gui'
platform_logs_folder = f'{platform_home_folder}{v}.ethos-group{v}gabb-adb-gui{v}logs'
platform_apk_folder = f'{platform_home_folder}{v}.ethos-group{v}gabb-adb-gui{v}apk'
platform_setedit_folder = f'{platform_home_folder}{v}.ethos-group{v}gabb-adb-gui{v}apk{v}setedit.apk'
platform_desktop_folder = f'{platform_home_folder}{v}Desktop'
platform_temporary_video_folder = f'{platform_home_folder}{v}Desktop{v}record.mp4'

platform_scrcpy_folder = f'{platform_home_folder}{v}.ethos-group{v}gabb-adb-gui{v}scrcpy'
platform_scrcpy_zip = f'{platform_scrcpy_folder}{v}{platform}64scrcpy.zip'
platform_scrcpy_extract = f'{platform_scrcpy_folder}{v}{platform}64scrcpy'

with open('AppStoreApkList.json', 'r', encoding='utf-8') as f:
    data = json.loads(f.read())


existing_apks = {
    'setedit': exists(platform_setedit_folder)

}

for entry in data:
    existing_apks[entry['apk_name']] = exists(f'{platform_apk_folder}{v}{entry["apk_name"]}.apk')

apks = {
    'setedit': 'https://f-droid.org/repo/io.github.muntashirakon.setedit_8.apk'
}

for entry in data:
    apks[entry['apk_name']] = entry['url']

print(existing_apks)
print(apks)


def insert_newlines(input_string, line_length=20):
    lines = []
    for i in range(0, len(input_string), line_length):
        lines.append(input_string[i:i + line_length])
    return '\n'.join(lines)


def check_scrcpy_install():
    return os.path.exists(platform_scrcpy_zip)


def path_fix(path: str, add_quotations: bool = False):
    v = ''
    if add_quotations:
        v = '"'
    if platform.system() == 'Windows':
        return v + path.replace('/', '\\') + v
    else:
        return v + path + v


def remove_html_tag(text, tag):
    return text[:text.find("<"+tag+">")] + text[text.find("</"+tag+">") + len(tag)+3:]
    

def download_apk(apk: str):

    if (apks[apk] is not None) and not existing_apks[apk]:  # if valid apk and not downloaded

        print(f"Downloading {apk}...")
        try:
            data = requests.get(apks[apk])

            if data.status_code != 200:
                raise
        except:
            print(f"An error has occurred while downloading {apk} from {apks[apk]}.")
            return None

        print(f"{apk} has been downloaded.")

        with open(f'{platform_apk_folder}{v}{apk}.apk', 'wb') as f:
            f.write(data.content)

    return f'{platform_apk_folder}{v}{apk}.apk'


def get_app_info(device: AdbDevice, app: str):
    return device.app_info(app)


def get_running_app(device: AdbDevice):
    return device.app_current()


def adb(command: str):
    # input something like 'install-multiple [path]'

    proc = subprocess.Popen(f'{adb_path()} {command}', stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
    (out, err) = proc.communicate()

    if out is None:
        out = b''

    if err is None:
        err = b''

    output = out.decode('utf-8') + err.decode('utf-8')

    return output


def get_device_dumpsys(device: AdbDevice, service: str):

    if service == 'battery':
        output = device.shell(f'dumpsys {service}').split('\n')

        return {'is_charging': bool(output[2].split(': ')[1]) or bool(output[2].split(': ')[2]),
                'percent': output[10].split(': ')[1] + '%',
                'voltage': output[12].split(': ')[1] + 'mV',
                }
    if service == 'cpuinfo':
        output = device.shell(f'dumpsys {service}')

        processes = []

        for process in output.split('\n')[2:-1]:

            processes.append({'usage': process.split('%')[0][2:] + '%',
                              'name': process.split('/')[1].split(':')[0]
                              })

        return {'total_percent': output.split('\n')[-1].split(' ')[0],
                'total_usage': {'user': output.split('\n')[-1].split(' ')[2], 'kernel': output.split('\n')[-1].split(' ')[5], 'io': output.split('\n')[-1].split(' ')[8]},
                'processes': processes,
                }

    if service == 'poweron':
        output1 = True if (device.shell(f'dumpsys deviceidle | grep mScreenLocked').split('=')[1]) == 'true' else False
        output2 = True if (device.shell(f'dumpsys deviceidle | grep mScreenOn').split('=')[1]) == 'true' else False

        return {
            'screen_locked': output1,
            'screen_on': output2,
        }

    if service == 'uptime':
        output = device.shell('cat /proc/uptime')

        return output.split(' ')[0]


def get_installed_apps(device: AdbDevice, third_party: bool = True, disabled_only=False, enabled_only=False):

    output = []
    arguments = ''

    if third_party:
        arguments += '-3 '
    if disabled_only:
        arguments += '-d '
    if enabled_only:
        arguments += '-e '

    for package in device.shell(f'pm list packages {arguments}').split('\n'):
        output.append(package[8:])

    return output


def in_setup_mode(device: AdbDevice):
    # in maintenance mode?
    print(device.shell('am get-current-user'))
    return not device.shell('am get-current-user') == '0'


def system_updates_disabled(device: AdbDevice):
    # are system updates disabled. True if disabled.

    packages = device.shell('pm list packages -d 2>/dev/null')

    return ('com.zte.zdm' in packages) and ('com.zte.zdmdaemon' in packages)


def gabb_updates_disabled(device: AdbDevice):
    # same as above with PackageUpdater

    packages = device.shell('pm list packages -d 2>/dev/null')

    return 'com.gabb.packageupdater' in packages


def setup_device(device: AdbDevice):
    # basic setup

    device.shell('pm disable-user com.zte.zdm')
    device.shell('pm disable-user com.gabb.packageupdater')
    device.shell('pm disable-user com.zte.zdmdaemon')
    device.shell('pm grant io.github.muntashirakon.setedit android.permission.WRITE_SECURE_SETTINGS')
    device.shell('settings put global development_settings_enabled 1')


def toggle_system_updates(device: AdbDevice, toggle: bool):
    if toggle:
        device.shell('pm enable com.zte.zdmdaemon')
        device.shell('pm enable com.zte.zdm')
    else:
        device.shell('pm disable-user com.zte.zdmdaemon')
        device.shell('pm disable-user com.zte.zdmn')


def toggle_gabb_updates(device: AdbDevice, toggle: bool):
    if toggle:
        device.shell('pm enable com.gabb.packageupdater')
    else:
        device.shell('pm disable-user com.gabb.packageupdater')


def is_installed(device: AdbDevice, package_name):

    if package_name == '':
        return False

    return f':{package_name}' in device.shell('pm list packages -3')


def install(device: AdbDevice, apk_path, package_name=None):
    adb(f'install-multiple --user 0 "{apk_path}"')
    if package_name is not None:
        device.shell(f'pm enable --user 0 {package_name}')
