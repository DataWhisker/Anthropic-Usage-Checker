# Anthropic API Token Usage Checker

## Overview
A Python script to check token usage and limits across different Claude 3 models from Anthropic.

## Project Structure
```
.
├── anthropic_usage_checker.py    # Main script file
├── config.ini.sample            # Sample configuration file
├── requirements.txt             # Python dependencies
├── LICENSE                      # MIT License
├── README.md                    # This documentation
└── output/                      # Build output directory
    └── anthropic_usage_checker.exe  # Compiled executable
```

## Configuration Methods
The script supports multiple ways to provide your API key:

1. **Configuration File**
   - Create `config.ini` in:
     - Current directory
     - Executable directory
     - `~/.anthropic_usage/config.ini`
     - Script directory

2. **Environment Variable**
   - Set `ANTHROPIC_API_KEY` environment variable

3. **Manual Input**
   - If no key is found, you'll be prompted to enter it manually

## Output Location
- The program saves results to `anthropic_token_usage.txt` in the same directory as the script/executable
- Output location is displayed in the console after saving
- Ensures output is always alongside the application for easy access

## Compilation Compatibility
- Works with compiled executables
- Searches for config file in same directories as the script or executable
- Supports runtime API key input
- When running as executable:
  - Terminal window stays open until user presses Enter
  - Allows time to review results before closing
  - Clear "Press Enter to exit..." prompt

## Prerequisites
- Python 3.7+
- Anthropic API Key

## Setup
1. Clone the repository
2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Configure API Key:
   - Copy `config.ini.sample` to `config.ini`
   - Replace `your_api_key_here` with your actual Anthropic API key

## Usage
### Running as Script
```bash
python anthropic_usage_checker.py
```

### Running as Executable
1. Launch the executable
2. Review the results
3. Press Enter when ready to close

## Features
- Retrieve token limits for all Claude 3 models
- Show total and remaining tokens
- Display time remaining until reset
- Automatically detect system timezone
- Save results to file in application directory
- User-friendly terminal behavior for executable

## Dependencies
- requests
- tabulate
- pytz

## License
MIT License
