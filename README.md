# Anthropic API Token Usage Checker

## Overview
A Python script to check token usage and limits across different Claude 3 models from Anthropic.

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

## Compilation Compatibility
- Works with compiled executables
- Searches for config file in same directories as the script or executable
- Supports runtime API key input

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
```bash
python anthropic_usage_checker.py
```

## Features
- Retrieve token limits for all Claude 3 models
- Show total and remaining tokens
- Display time remaining until reset
- Automatically detect system timezone

## Dependencies
- requests
- tabulate
- pytz

## License
MIT License
