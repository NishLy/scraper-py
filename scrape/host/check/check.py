#######################################################################################################################
# Check Virtualization function
#######################################################################################################################

import wmi
import pythoncom

def check_virtualization():
    pythoncom.CoInitialize()
    c = wmi.WMI()
    for processor in c.Win32_Processor():
        if hasattr(processor, 'VirtualizationFirmwareEnabled'):
            if processor.VirtualizationFirmwareEnabled:
                print("#"*150)
                print("This Computer CPU Virtualization is enabled")
                print("#"*150)
                pythoncom.CoUninitialize()
                return True
            else:
                print("#"*150)
                print("This Computer CPU Virtualization is not enabled")
                print("#"*150)
                pythoncom.CoUninitialize()
                return False
        else:
            print("#"*150)
            print("This Computer CPU Virtualization is not enabled")
            print("#"*150)
            pythoncom.CoUninitialize()
            return False
    pythoncom.CoUninitialize()
    return None
