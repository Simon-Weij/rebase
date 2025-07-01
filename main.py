import os
import subprocess
import json
from config_save import move_files, import_from_appdir, rollback_files

def save_apps_to_json(filename, dnf_packages, flatpak_packages, copr_repos):
    output = {
        "dnf": dnf_packages,
        "flatpaks": flatpak_packages,
        "coprs": copr_repos
    }
    with open(filename, 'w') as f:
        json.dump(output, f, indent=2)
    print(f"Saved packages to JSON file: {filename} in directory {os.getcwd()}")


def create_config_json(filename, template):
    output = {
        "directories": template,
    }
    with open(filename, 'w') as f:
        json.dump(output, f, indent=2)
    print(f"Saved config to: {filename} in directory {os.getcwd()}")

def config_prompt():
    while True:
        print("\nDo you want to:")
        print("  1. Create a config file")
        print("  2. Import from application directory")
        print("  3. Export to application directory")
        print("  4. Rollback files")
        answer = input("Enter your choice [1/2/3/4]: ")
        if answer == "1":
            create_config_json("config_files.json", [])
            break
        elif answer == "2":
            import_from_appdir()
            break
        elif answer == "3":
            move_files()
            break
        elif answer == "4":
            rollback_files()
            break
        else:
            print("Invalid choice. Please enter 1, 2, 3, or 4.")


def main():
    config_prompt()


if __name__ == "__main__":
    main()
