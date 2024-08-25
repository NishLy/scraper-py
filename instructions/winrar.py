from scrape.instruction import Response,run_as_admin
from scrape.utils import download_and_save_file
from scrape.pywinauto import wait_for_element,run_app,wait_for_window,attach_to_existing_window

import subprocess
import os
import time
import logging

logging.basicConfig(level=logging.DEBUG)

RESOURE_SOURCE_URL = "https://www.win-rar.com/fileadmin/winrar-versions/winrar/winrar-x64-701.exe"
DOWNLOAD_SAVE_PATH = os.path.join(os.getcwd(), "instructions\\downloads")
FILE_NAME = "winrar-x64-701.exe"


def install_software(installer_path):
    try:
        # proccess = subprocess.Popen([installer_path], shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        
        # if not proccess:
        #     return False
        
        app = run_app(installer_path,backend='uia')

        # Continue with automation after the installer starts
        installer_window = wait_for_window(app, "WinRAR 7.01", timeout=30)
        
        if not installer_window:
            return False

        # Wait for and click the "Next" button
        install_button = wait_for_element(installer_window, "Install", "Button")
        
        if install_button:
            install_button.click()
        
        # Changing window title to "WinRAR Setup", Need to wait for the window to appear
        time.sleep(5)
                
        if app.windows() == []:
            app = attach_to_existing_window("WinRAR Setup")
            if not app:
                return False
            
        winrar_setup = wait_for_window(app, "WinRAR Setup", timeout=10)

        if not winrar_setup:
            return False
        
        # Wait for and click the "OK" button
        
        ok_button = wait_for_element(winrar_setup, "OK", "Button")
        
        if not ok_button:
            return False
        
        ok_button.click()
        
        # Wait for and click the "Done" button
        
        done_button = wait_for_element(winrar_setup, "Done", "Button")
        
        if not done_button:
            return False
        
        done_button.click()
        
        app.kill()
        return True
    except Exception as e:
        print(f"Error on install_software : {e}")
        return False


def main(requirement: dict[str,str])-> Response:
   
    try:
        os.makedirs(os.path.dirname(DOWNLOAD_SAVE_PATH), exist_ok=True)
        
        if not os.path.exists(os.path.join(DOWNLOAD_SAVE_PATH, FILE_NAME)):
            if not download_and_save_file(RESOURE_SOURCE_URL, os.path.join(DOWNLOAD_SAVE_PATH, FILE_NAME)):
                return Response(
                    status=False,
                    message="Failed to download WinRar",
                    data={}
                )
            
        if not os.path.exists(os.path.join(DOWNLOAD_SAVE_PATH, FILE_NAME)):
            return Response(
                status=False,
                message="WinRar installer not found",
                data={}
            )
        
        
        if not install_software(os.path.join(DOWNLOAD_SAVE_PATH, FILE_NAME)):
            return Response(
                status=False,
                message="Failed to install WinRar",
                data={}
            )
            
        return Response(
            status=True,
            message="WinRar installed successfully",
            data={}
        )
            
            
    except Exception as e:
        return Response(
            status=False,
            message="An error occurred while installing WinRar -> {}".format(str(e)),
            data={}
        )
        
    
if __name__ == "__main__":
    print(main({})) 
    input("Press Enter to continue...")
     