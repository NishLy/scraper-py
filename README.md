---

# STMIK Widya Pratama Computer Lab Automation Script

This project provides a Python script, `scraper.py`, designed to automate the process of checking and installing applications in the computer labs at STMIK Widya Pratama. The script can be customized and accepts various command-line arguments to control its behavior, including login credentials, network configuration, and more.

## Prerequisites

- Python 3.7 or later
- Pyppeteer library
- Other dependencies as specified in `requirements.txt`

## Installation

Clone this repository and install the required Python packages:

```bash
git clone <repository-url>
cd <project-directory>
pip install -r requirements.txt
```

## Usage

The script can be run from the command line with various options:

```bash
python scraper.py [OPTIONS]
```

### Command-Line Arguments

- `--username`: The username for login (optional).
- `--password`: The password for login (optional).
- `--dangerously-say-yes`: Skip confirmation prompts (optional).
- `--skip-checked`: Skip applications that have already been checked (optional).
- `--skip-host-check`: Skip the retrieval of host information (optional).
- `--skip-installed`: Skip checking installed applications (optional).
- `--async`: Run application checks asynchronously (optional).
- `--no-report`: Skip sending the report (optional).
- `--pc-position`: Specify the position of the device in the lab (optional).
- `--pc-number`: Specify the number of the device in the lab (optional).
- `--set-network`: Enable network configuration settings (optional).
- `--custom-data`: Provide custom data to override the default scraping process (optional).

### Custom Data

The `--custom-data` parameter allows you to override the default scraping from the 'ceksoft' web app in the internal UPT. Instead, you can use a custom text file containing a list of applications and their requirements.

Example format for the custom data file:

```
flutter-sdk={"target":null,"minimum":"1.0.0"}
app2={"target":"2.0.0","minimum":"1.5.0"}
```

In this format:
- **target**: The specific version you want to ensure is installed (can be `null` if not specified).
- **minimum**: The minimum version required.

This custom data will be used to check and install applications according to the specified requirements.

### Example Usage

```bash
python scraper.py --username admin --password secret --skip-checked --async --pc-position "Lab 1" --pc-number 01 --set-network --custom-data /path/to/custom_data.txt
```

This command will log in with the given credentials, skip already checked applications, perform checks asynchronously, set the network configuration for device 01 in Lab 1, and use the custom data from the provided text file.

## Features

- **Automated Application Checks**: The script automates the process of checking and installing applications in the computer lab, saving time and effort.
- **Asynchronous Operation**: You can enable asynchronous checks for faster execution.
- **Custom Data**: Replace default scraping with your own custom instructions for specific applications.
- **Network Configuration**: Optionally configure network settings for each device.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Contact

For any inquiries or issues, please contact the project maintainer at [adhipamungkaswijayadi@gmail.com].

---
