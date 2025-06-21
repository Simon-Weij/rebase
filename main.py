import os
import subprocess
import json

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

def save_to_json(filename, dnf_packages, flatpak_packages):
    output = {
        "dnf": dnf_packages,
        "flatpaks": flatpak_packages
    }
    with open(filename, 'w') as f:
        json.dump(output, f, indent=2)
    print(f"Saved packages to JSON file: {filename} in directory {os.getcwd()}")

def main():
    answer = ''
    while answer.lower() not in ("e", "i"):
        print("Do you want to save your packages to export (e) or install (i) packages from the JSON file? [i/e]")
        answer = input().lower()

        if answer == "e":
            dnf_packages = get_user_installed_packages()
            flatpak_packages = get_installed_flatpaks()
            save_to_json("packages.json", dnf_packages, flatpak_packages)

        elif answer == "i":
            with open("packages.json", "r") as f:
                data = json.load(f)

            answeryn = ''
            while answeryn.lower() not in ("y", "n"):
                print("Do you want to manually approve each package? [y/n]")
                answeryn = input().lower()

            for package in data.get("dnf", []):
                print(f"Package: {package}")
                if answeryn == "y":
                    input("Press Enter to install or Ctrl+C to skip...")
                    subprocess.run(["sudo", "dnf", "install", package], check=True)
                else:
                    subprocess.run(["sudo", "dnf", "install", package, "-y"], check=True)

            for package in data.get("flatpaks", []):
                print(f"Flatpak: {package}")
                if answeryn == "y":
                    input("Press Enter to install or Ctrl+C to skip...")
                    subprocess.run(f"flatpak install flathub {package}", shell=True, check=True)
                else:
                    subprocess.run(f"flatpak install flathub {package} -y", shell=True, check=True)

if __name__ == "__main__":
    main()
