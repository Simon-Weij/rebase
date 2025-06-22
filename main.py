import os
import subprocess
import json

from config_save import move_files, import_from_appdir, rollback_files


def get_user_installed_packages():
    result = subprocess.run(
        ["dnf", "repoquery", "--userinstalled", "--qf", "%{name}\\n"],
        capture_output=True,
        text=True,
        check=True
    )
    return result.stdout.splitlines()


def get_installed_flatpaks():
    result = subprocess.run(
        ["flatpak", "list", "--app", "--columns=application"],
        capture_output=True,
        text=True,
        check=True
    )
    return result.stdout.splitlines()


def save_apps_to_json(filename, dnf_packages, flatpak_packages):
    output = {
        "dnf": dnf_packages,
        "flatpaks": flatpak_packages
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
    print(f"Saved config structure to: {filename} in directory {os.getcwd()}")


def is_dnf_installed(package):
    result = subprocess.run(
        ["dnf", "list", "installed", package],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL
    )
    return result.returncode == 0


def is_flatpak_installed(package):
    result = subprocess.run(
        ["flatpak", "info", package],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL
    )
    return result.returncode == 0


def package_prompt():
    while True:
        print("\nDo you want to:")
        print("  1. Export packages to JSON")
        print("  2. Install packages from JSON")
        answer = input("Enter your choice [1/2]: ")

        if answer == "1":
            dnf_packages = get_user_installed_packages()
            flatpak_packages = get_installed_flatpaks()
            save_apps_to_json("packages.json", dnf_packages, flatpak_packages)
            break
        elif answer == "2":
            try:
                with open("packages.json", "r") as f:
                    data = json.load(f)
            except FileNotFoundError:
                print("Error: packages.json not found. Please export packages first.")
                return

            while True:
                print("\nDo you want to manually approve each package? [1=Yes/2=No]")
                answeryn = input("Enter your choice [1/2]: ")
                if answeryn in ("1", "2"):
                    break
                else:
                    print("Invalid choice. Please enter 1 or 2.")

            print("\n--- Installing DNF Packages ---")
            for package in data.get("dnf", []):
                if is_dnf_installed(package):
                    print(f"DNF package already installed: {package}")
                    continue

                print(f"Installing DNF package: {package}")
                if answeryn == "1":
                    input("Press Enter to install or Ctrl+C to skip...")
                    try:
                        subprocess.run(["sudo", "dnf", "install", package], check=True)
                    except subprocess.CalledProcessError as e:
                        print(f"Error installing DNF package {package}: {e}")
                else:
                    try:
                        subprocess.run(["sudo", "dnf", "install", package, "-y"], check=True)
                    except subprocess.CalledProcessError as e:
                        print(f"Error installing DNF package {package}: {e}")

            print("\n--- Installing Flatpak Applications ---")
            for package in data.get("flatpaks", []):
                if is_flatpak_installed(package):
                    print(f"Flatpak already installed: {package}")
                    continue

                print(f"Installing Flatpak: {package}")
                if answeryn == "1":
                    input("Press Enter to install or Ctrl+C to skip...")
                    try:
                        subprocess.run(f"flatpak install flathub {package}", shell=True, check=True)
                    except subprocess.CalledProcessError as e:
                        print(f"Error installing Flatpak {package}: {e}")
                else:
                    try:
                        subprocess.run(f"flatpak install flathub {package} -y", shell=True, check=True)
                    except subprocess.CalledProcessError as e:
                        print(f"Error installing Flatpak {package}: {e}")
            break
        else:
            print("Invalid choice. Please enter 1 or 2.")


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
    while True:
        print("\nWhat do you want to manage?")
        print("  1. Configuration files")
        print("  2. Packages")
        answerpc = input("Enter your choice [1/2]: ")
        if answerpc == "1":
            config_prompt()
            break
        elif answerpc == "2":
            package_prompt()
            break
        else:
            print("Invalid choice. Please enter 1 or 2.")


if __name__ == "__main__":
    main()