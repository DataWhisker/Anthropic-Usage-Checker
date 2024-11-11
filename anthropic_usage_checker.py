import os
import sys
import configparser
import requests
import json
from datetime import datetime, timezone, timedelta
import pytz
from tabulate import tabulate

class AnthropicUsageTracker:
    def __init__(self, config_path=None):
        """
        Initialize the Anthropic Usage Tracker
        Attempts to find configuration in multiple locations
        """
        self.api_key = self._load_api_key(config_path)
        self.base_url = 'https://api.anthropic.com/v1'
        
        # Get system timezone
        self.local_tz = datetime.now().astimezone().tzinfo
        print(f"System Timezone: {self.local_tz}")
        
        # Updated Claude 3 models with exact names
        self.claude_models = [
            "claude-3-5-sonnet-20241022",
            "claude-3-5-haiku-20241022",
            "claude-3-opus-20240229", 
            "claude-3-sonnet-20240229", 
            "claude-3-haiku-20240307"
        ]

    def _find_config_file(self, config_path=None):
        """
        Find configuration file in multiple potential locations
        """
        # List of potential config file locations
        potential_paths = [
            config_path,  # User-specified path
            'config.ini',  # Current directory
            os.path.join(os.path.dirname(sys.executable), 'config.ini'),  # Executable directory
            os.path.expanduser('~/.anthropic_usage/config.ini'),  # User home directory
            os.path.join(os.path.dirname(__file__), 'config.ini')  # Script directory
        ]

        # Check if running as a compiled executable
        if getattr(sys, 'frozen', False):
            potential_paths.append(os.path.join(sys._MEIPASS, 'config.ini'))

        # Remove None values and check each path
        for path in [p for p in potential_paths if p]:
            if os.path.exists(path):
                return path
        
        return None

    def _load_api_key(self, config_path=None):
        """
        Load API key from configuration file or environment
        """
        # First, check environment variable
        env_api_key = os.environ.get('ANTHROPIC_API_KEY')
        if env_api_key:
            return env_api_key

        # Find and load config file
        found_config_path = self._find_config_file(config_path)
        
        if found_config_path:
            try:
                config = configparser.ConfigParser()
                config.read(found_config_path)
                
                # Try to get API key from config
                if config.has_section('ANTHROPIC') and config.has_option('ANTHROPIC', 'API_KEY'):
                    return config.get('ANTHROPIC', 'API_KEY')
            except Exception as e:
                print(f"Error reading configuration file: {e}")
        
        # If no config found, prompt for manual input or raise error
        raise ValueError("""
        No API key found. Please:
        1. Create a config.ini file with ANTHROPIC_API_KEY
        2. Set ANTHROPIC_API_KEY environment variable
        3. Manually input API key when prompted
        """)

    def _format_reset_time(self, reset_time_str):
        """
        Convert UTC reset time to local time with timezone name
        """
        try:
            # Parse the UTC time
            reset_time = datetime.strptime(reset_time_str, "%Y-%m-%dT%H:%M:%SZ")
            reset_time = reset_time.replace(tzinfo=timezone.utc)
            
            # Convert to local time
            local_time = reset_time.astimezone()
            
            # Calculate time difference
            now = datetime.now(timezone.utc).astimezone()
            time_diff = reset_time.astimezone() - now
            
            # Format the time difference
            if time_diff.total_seconds() < 0:
                time_remaining = "Reset time passed"
            else:
                hours = int(time_diff.total_seconds() // 3600)
                minutes = int((time_diff.total_seconds() % 3600) // 60)
                time_remaining = f"Resets in {hours}h {minutes}m"
            
            # Format the local time with timezone name
            formatted_time = local_time.strftime("%Y-%m-%d %I:%M:%S %p %Z")
            return f"{formatted_time} ({time_remaining})"
            
        except (ValueError, AttributeError):
            return "Unknown"

    def _format_number(self, value):
        """
        Format number with commas for better readability
        """
        try:
            return f"{int(value):,}"
        except (ValueError, TypeError):
            return str(value)

    def check_token_usage(self):
        """
        Check current rate limits and token usage for Claude models
        Returns a dictionary with usage information for each model
        """
        usage_data = {}
        
        # Headers for API request
        headers = {
            'anthropic-version': '2023-06-01',
            'content-type': 'application/json',
            'x-api-key': self.api_key
        }
        
        try:
            # Make API calls for each model to get their specific limits
            for model in self.claude_models:
                payload = {
                    "model": model,
                    "max_tokens": 1,
                    "messages": [{"role": "user", "content": "Check limits"}]
                }
                
                response = requests.post(
                    f"{self.base_url}/messages", 
                    headers=headers, 
                    json=payload
                )
                
                # Format the reset time
                reset_time = response.headers.get('anthropic-ratelimit-tokens-reset', 'Unknown')
                formatted_reset_time = self._format_reset_time(reset_time) if reset_time != 'Unknown' else 'Unknown'
                
                # Extract and format rate limit information from headers
                usage_data[model] = {
                    'requests_limit': self._format_number(response.headers.get('anthropic-ratelimit-requests-limit', 'Unknown')),
                    'requests_remaining': self._format_number(response.headers.get('anthropic-ratelimit-requests-remaining', 'Unknown')),
                    'tokens_limit': self._format_number(response.headers.get('anthropic-ratelimit-tokens-limit', 'Unknown')),
                    'tokens_remaining': self._format_number(response.headers.get('anthropic-ratelimit-tokens-remaining', 'Unknown')),
                    'reset_time': formatted_reset_time
                }
            
            return usage_data
        
        except requests.RequestException as e:
            print(f"Error checking token usage: {e}")
            return {}

def main():
    try:
        # Allow manual API key input if not found in config
        try:
            tracker = AnthropicUsageTracker()
        except ValueError as e:
            print(str(e))
            api_key = input("Please enter your Anthropic API key: ")
            os.environ['ANTHROPIC_API_KEY'] = api_key
            tracker = AnthropicUsageTracker()
        
        print("\nNote: The rate limits shown below represent the most restrictive limits currently in effect.")
        print("These are typically per-minute limits unless a more restrictive limit (like daily) has been reached.")
        
        usage = tracker.check_token_usage()
        
        # Prepare data for tabulate
        table_data = []
        for model, usage_info in usage.items():
            table_data.append([
                model,
                usage_info['requests_limit'],
                usage_info['requests_remaining'],
                usage_info['tokens_limit'],
                usage_info['tokens_remaining'],
                usage_info['reset_time']
            ])
        
        # Create and print table with right-aligned numbers
        headers = ["Model", "Req Limit", "Req Remaining", "Token Limit", "Tokens Remaining", "Reset Time"]
        print("\nCurrent Rate Limits and Usage:")
        print(tabulate(table_data, headers=headers, tablefmt="grid", colalign=("left", "right", "right", "right", "right", "left")))

        # Optional: Write to file
        with open('anthropic_token_usage.txt', 'w') as f:
            f.write(f"System Timezone: {tracker.local_tz}\n\n")
            f.write("Note: The rate limits shown below represent the most restrictive limits currently in effect.\n")
            f.write("These are typically per-minute limits unless a more restrictive limit (like daily) has been reached.\n\n")
            f.write("Current Rate Limits and Usage:\n")
            f.write(tabulate(table_data, headers=headers, tablefmt="grid", colalign=("left", "right", "right", "right", "right", "left")))

    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    main()
