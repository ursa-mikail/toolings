import json
import yaml
import time, os

def ask_question(prompt, default=None):
    """Ask a question and return user input, with an optional default value."""
    user_input = input(f"{prompt} ({default if default else 'press enter for default'}): ").strip()
    return user_input if user_input else default

def generate_config():
    """Generate a basic JSON/YAML configuration based on user input."""
    timestamp = time.strftime("%Y_%m_%d_%H%M_%S")
    config = {
        "tool_name": ask_question("Enter the tool name", "my_tool"),
        "version": ask_question("Enter version", timestamp),
        "api_key": ask_question("Enter API key (leave empty if not required)", ""),
        "enable_logging": ask_question("Enable logging? (yes/no)", "yes").lower() == "yes",
        "output_format": ask_question("Preferred output format (json/yaml)", "json"),
        "settings": {
            "retry_attempts": int(ask_question("Number of retry attempts", "3")),
            "timeout": int(ask_question("Timeout duration in seconds", "30")),
        }
    }
    return config, timestamp

def save_config(config, filename="./out/config.json", format="json", config_timestamp=time.strftime("%Y_%m_%d_%H%M_%S")):
    """Save configuration to a JSON or YAML file."""
    os.makedirs(os.path.dirname(filename), exist_ok=True)
    
    if format == "yaml":
        filename = "./out/config_" + config_timestamp + ".yaml"
        with open(filename, "w") as f:
            yaml.dump(config, f, default_flow_style=False)
    else:
        filename = "./out/config_" + config_timestamp + ".json"
        with open(filename, "w") as f:
            json.dump(config, f, indent=4)
    print(f"Configuration saved to {filename}")

def main():
    print("\n=== Configuration Setup Utility ===\n")
    config, timestamp = generate_config()
    print("\nGenerated Configuration:")
    print(json.dumps(config, indent=4) if config["output_format"] == "json" else yaml.dump(config, default_flow_style=False))
    save_config(config, format=config["output_format"], config_timestamp=timestamp)
    print("\nSetup complete. You can modify the configuration file if needed.")

if __name__ == "__main__":
    main()

"""

=== Configuration Setup Utility ===

Enter the tool name (my_tool): 
Enter version (2025_02_14_2249_01): 
Enter API key (leave empty if not required) (press enter for default): 
Enable logging? (yes/no) (yes): 
Preferred output format (json/yaml) (json): 
Number of retry attempts (3): 
Timeout duration in seconds (30): 

Generated Configuration:
{
    "tool_name": "my_tool",
    "version": "2025_02_14_2249_01",
    "api_key": "",
    "enable_logging": true,
    "output_format": "json",
    "settings": {
        "retry_attempts": 3,
        "timeout": 30
    }
}
Configuration saved to ./out/config_2025_02_14_2249_01.json

Setup complete. You can modify the configuration file if needed.
"""