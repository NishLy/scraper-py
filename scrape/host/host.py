#######################################################################################################################
# MAIN FUNCTION HOST INFO
#######################################################################################################################
import wmi
import GPUtil

def get_cpu_info():
    w = wmi.WMI()
    cpu_list = []
    for processor in w.Win32_Processor():
        cpu_info = {
            "Name": processor.Name.strip(),
            "Cores": processor.NumberOfCores,
            "Threads": processor.ThreadCount,
            "ClockSpeed": f"{processor.MaxClockSpeed / 1500:.2f} GHz",
            "Manufacturer": processor.Manufacturer.strip(),
            "TDP": "N/A",  # TDP information is not available from WMI
            "Generation": "N/A"  # Generation information is not available from WMI
        }
        cpu_list.append(cpu_info)
    return cpu_list

def get_ram_info():
    w = wmi.WMI()
    ram_list = []
    for memory in w.Win32_PhysicalMemory():
        ram_info = {
            "Manufacturer": memory.Manufacturer.strip(),
            "Capacity (GB)": f"{int(memory.Capacity) / (1024 ** 3):.2f}",
            "Type": memory.MemoryType,
            "Speed (MHz)": f"{memory.Speed} MHz"
        }
        ram_list.append(ram_info)
    return ram_list

def get_gpus_info():
    # Initialize WMI and GPUtil
    w = wmi.WMI()
    gpus = GPUtil.getGPUs()
    
    gpu_info_list = []
    
    # Collect GPU info from WMI
    video_cards = w.Win32_VideoController()
    for card in video_cards:
        gpu_info = {
            "Name": card.Name.strip(),
            "Manufacturer": card.AdapterCompatibility.strip(),
            "VRAM (GB)": int(card.AdapterRAM) / (1024 ** 3),
            "Core Clock Speed (MHz)": "Not Available via WMI",
            "Architecture": "Integrated" if "Intel" in card.Name or "AMD" in card.Name else "Discrete"
        }
        gpu_info_list.append(gpu_info)
    
    # Collect additional GPU info from GPUtil
    for gpu in gpus:
        gpu_info = {
            "Name": gpu.name.strip(),
            "Manufacturer": gpu.vendor.strip(),
            "VRAM (GB)": gpu.memoryTotal / 1024,
            "Core Clock Speed (MHz)": gpu.clockSpeed,
            "Architecture": gpu.name.split()[0]  # Rough estimation of architecture
        }
        gpu_info_list.append(gpu_info)
    
    return gpu_info_list

def get_disk_info():
    w = wmi.WMI()
    disk_list = []
    for disk in w.Win32_DiskDrive():
        disk_info = {
            "DeviceID": disk.DeviceID.strip(),
            "Size (GB)": f"{int(disk.Size) / (1024 ** 3):.2f}",
            "Manufacturer": disk.Manufacturer.strip(),
            "InterfaceType": disk.InterfaceType
        }
        disk_list.append(disk_info)
    return disk_list

def get_network_info():
    w = wmi.WMI()
    adapters = w.Win32_NetworkAdapterConfiguration(IPEnabled=True)
    network_list = []
    
    for adapter in adapters:
        hardware_info = []
        if adapter.Description:
            hardware_info = w.Win32_NetworkAdapter(Description=adapter.Description)
        
        if hardware_info:
            hardware_info = hardware_info[0]
            manufacturer = hardware_info.Manufacturer.strip() if hardware_info.Manufacturer else "Unknown"
        else:
            manufacturer = "Unknown"

        adapter_info = {
            "Description": adapter.Description.strip(),
            "Manufacturer": manufacturer,
            "MACAddress": adapter.MACAddress,
            "IPAddresses": adapter.IPAddress[0] if adapter.IPAddress else "No IP Address",
            "IPSubnet": adapter.IPSubnet[0] if adapter.IPSubnet else "No Subnet",
            "DefaultIPGateway": adapter.DefaultIPGateway[0] if adapter.DefaultIPGateway else "No Gateway",
            "Type": "Wi-Fi" if 'Wi-Fi' in adapter.Description or 'Wireless' in adapter.Description else "LAN"
        }
        
        network_list.append(adapter_info)
    
    return network_list