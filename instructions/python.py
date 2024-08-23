import urllib.request
import os
import sys


def download_file(url, destination):
    try:
        # Send a GET request to the URL and open the response
        with urllib.request.urlopen(url) as response:
            # Get the total file size (from Content-Length header)
            total_size = int(response.headers.get('Content-Length', 0))
            
            # Open the destination file to write the content
            with open(destination, 'wb') as file:
                downloaded_size = 0
                chunk_size = 8192  # 8KB chunks
                
                # Download the file in chunks
                while True:
                    chunk = response.read(chunk_size)
                    if not chunk:
                        break
                    file.write(chunk)
                    downloaded_size += len(chunk)
                    
                    # Calculate and print the progress
                    percent_complete = (downloaded_size / total_size) * 100
                    sys.stdout.write(f"\rDownload progress: {percent_complete:.2f}%")
                    sys.stdout.flush()
                
                sys.stdout.write("\nDownload complete!\n")
                return True
        
    except Exception as e:
        print(f"An error occurred: {e}")
        return False

def main():
    # URL of the file to download (replace with actual URL)
    file_url = 'https://www.python.org/ftp/python/3.9.0/python-3.9.0-amd64.exe'  # Replace with a valid URL
    destination_file = 'python_installer.exe'
    
    success = download_file(file_url, destination_file)
    
    if success:
        print("File downloaded successfully.")
        
    else:
        print("Failed to download the file.")
    
    return success

if __name__ == "__main__":
    main()