#######################################################################################################################
# NTP Time functions
#######################################################################################################################
import ntplib
import platform
import subprocess
from datetime import datetime
import pytz

def get_ntp_time():
    """Fetch the current time from an NTP server."""
    client = ntplib.NTPClient()
    response = client.request('pool.ntp.org')
    return response.tx_time

def set_system_time(new_time):
    """Set the system time (requires administrative privileges)."""
    formatted_time = new_time.strftime("%Y-%m-%d %H:%M:%S")
    
    if platform.system() == "Windows":
        # Windows command to set the system time
        date_cmd = new_time.strftime('Set-Date -Date "%m-%d-%Y %H:%M"')
        result = subprocess.run(["powershell", "-Command", date_cmd])
        if result.returncode != 0:
            raise OSError("Failed to set system time")
        else:
            print(f"System time set to {formatted_time}")
            return True
    elif platform.system() == "Linux":
        # Linux command to set the system time
        try:
            subprocess.run(['sudo', 'timedatectl', 'set-time', formatted_time], check=True)
        except subprocess.CalledProcessError as e:
            print(f"Error setting system time: {e}")
    else:
        raise OSError("Unsupported operating system")

def set_time(region_str:str):
    # Fetch current time from NTP server
    ntp_time = get_ntp_time()

    # Convert to UTC+7
    utc = pytz.utc
    local_tz = pytz.timezone(region_str)  # UTC+7 timezone
    utc_time = datetime.utcfromtimestamp(ntp_time).replace(tzinfo=utc)
    local_time = utc_time.astimezone(local_tz)

    # Print the local time for verification
    print(f"Current local time (UTC+7): {local_time.strftime('%Y-%m-%d %H:%M:%S')}")


    # Set the system time
    set_system_time(local_time)
    # Set the system time