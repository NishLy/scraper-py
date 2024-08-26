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
            "Generation": "N/A",  # Generation information is not available from WMI
            "Socket": processor.SocketDesignation.strip(),
            "Architecture": processor.Architecture,
            "L2 Cache Size (KB)": processor.L2CacheSize,
            "L3 Cache Size (KB)": processor.L3CacheSize,
            "Virtualization": "Enabled" if processor.VirtualizationFirmwareEnabled else "Disabled",
            "Hyper-Threading": "Enabled" if processor.SecondLevelAddressTranslationExtensions else "Disabled",
            "VT-x": "Enabled" if processor.VtxSupport else "Disabled",
            "VT-d": "Enabled" if processor.VtdSupport else "Disabled",
            "AES": "Enabled" if processor.AESEnabled else "Disabled",
            "NX": "Enabled" if processor.ExecuteDisableBitAvailable else "Disabled",
            "SSE": "Enabled" if processor.DataExecutionPrevention_Available else "Disabled",
            "SSE2": "Enabled" if processor.DataExecutionPrevention_SupportPolicy else "Disabled",
            "SSE3": "Enabled" if processor.DataExecutionPrevention_32BitApplications else "Disabled",
            "SSSE3": "Enabled" if processor.DataExecutionPrevention_Drivers else "Disabled",
            "SSE4_1": "Enabled" if processor.DataExecutionPrevention_SecuritySupport else "Disabled",
            "SSE4_2": "Enabled" if processor.DataExecutionPrevention_Permanent else "Disabled",
            "AVX": "Enabled" if processor.DataExecutionPrevention_Enforcement else "Disabled",
        }
        cpu_list.append(cpu_info)
    return cpu_list

MEMORY_TYPES = {
        0: "Unknown",
        1: "Other",
        2: "DRAM",
        3: "Synchronous DRAM",
        4: "Cache DRAM",
        5: "EDO",
        6: "EDRAM",
        7: "VRAM",
        8: "SRAM",
        9: "RAM",
        10: "ROM",
        11: "Flash",
        12: "EEPROM",
        13: "FEPROM",
        14: "EPROM",
        15: "CDRAM",
        16: "3DRAM",
        17: "SDRAM",
        18: "SGRAM",
        19: "RDRAM",
        20: "DDR",
        21: "DDR2",
        22: "DDR2 FB-DIMM",
        24: "DDR3",
        25: "FBD2",
        26: "DDR4",
        27: "LPDDR",
        28: "LPDDR2",
        29: "LPDDR3",
        30: "LPDDR4",
        31: "Logical non-volatile device",
        32: "HBM",
        33: "HBM2",
        34: "DDRII",
        35: "DDRIII",
        36: "DDRIV",
        37: "LPDDR5",
    }

def get_ram_info():
    w = wmi.WMI()
    ram_list = []
    
    for memory in w.Win32_PhysicalMemory():
        ram_info = {
            "Manufacturer": memory.Manufacturer.strip(),
            "Size (GB)": f"{int(memory.Capacity) / (1024 ** 3):.2f}",
            "Type": MEMORY_TYPES[memory.MemoryType] if memory.MemoryType in MEMORY_TYPES else "Unknown",
            "Speed (MHz)": f"{memory.Speed} MHz",
            "Serial Number": memory.SerialNumber.strip(),
            "Part Number": memory.PartNumber.strip(),
            "Form Factor": memory.FormFactor,
            "Device Locator": memory.DeviceLocator.strip(),
            "Bank Label": memory.BankLabel.strip(),
            "Configured Clock Speed (MHz)": f"{memory.ConfiguredClockSpeed} MHz",
            "Voltage": f"{memory.ConfiguredVoltage} V",
            "Data Width": memory.DataWidth,
            "Total Width": memory.TotalWidth,
            "Position in Row": memory.PositionInRow,
            "Interleave Data Depth": memory.InterleaveDataDepth,
            "Interleave Position": memory.InterleavePosition,
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
            "Architecture": "Integrated" if "Intel" in card.Name or "AMD" in card.Name else "Discrete",
        }
        gpu_info_list.append(gpu_info)
    
    # Collect additional GPU info from GPUtil
    for gpu in gpus:
        gpu_info = {
            "Name": gpu.name.strip(),
            "Manufacturer": gpu.vendor.strip(),
            "VRAM (GB)": gpu.memoryTotal / 1024,
            "Core Clock Speed (MHz)": gpu.clockSpeed,
            "Architecture": gpu.name.split()[0],  # Rough estimation of architecture
            
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
            "InterfaceType": disk.InterfaceType,
            "Type": disk.MediaType.strip(),
            "Model": disk.Model.strip(),
            "Serial Number": disk.SerialNumber.strip()
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

def get_motherboard_info():
    c = wmi.WMI()
    motherboard_info = []
    
    for board in c.Win32_BaseBoard():
        info = {
            "Manufacturer": board.Manufacturer,
            "Model": board.Product,
            "Serial Number": board.SerialNumber,
            "Version": board.Version,
            "Asset Tag": board.AssetTag,
        }
        motherboard_info.append(info)
    
    return motherboard_info
