import os
import json
import shutil

CONFIG_FILE = "config_files.json"
TARGET_DIR = os.path.join(os.getcwd(), "appdir")


def move_files():
    if not os.path.exists(CONFIG_FILE):
        print(f"Config file {CONFIG_FILE} not found.")
        return

    with open(CONFIG_FILE, "r") as f:
        config = json.load(f)

    paths = config.get("directories", [])
    if not paths:
        print("No paths listed in the config file.")
        return

    os.makedirs(TARGET_DIR, exist_ok=True)
    rollback_data = {}

    for path in paths:
        path = os.path.expanduser(path)
        if not os.path.exists(path):
            print(f"Path not found: {path}")
            continue

        name = os.path.basename(path.rstrip("/"))
        new_path = os.path.join(TARGET_DIR, name)

        if os.path.islink(path):
            print(f"Skipping symlink: {path}")
            continue

        shutil.move(path, new_path)
        os.symlink(new_path, path)
        print(f"Moved {path} -> {new_path} and created symlink")

        rollback_data[path] = new_path

    with open("rollback.json", "w") as f:
        json.dump(rollback_data, f, indent=2)


def import_from_appdir():
    if not os.path.exists(CONFIG_FILE):
        print(f"Config file {CONFIG_FILE} not found.")
        return

    with open(CONFIG_FILE, "r") as f:
        config = json.load(f)

    paths = config.get("directories", [])
    if not paths:
        print("No paths listed in the config file.")
        return

    for original_path in paths:
        original_path = os.path.expanduser(original_path)
        name = os.path.basename(original_path.rstrip("/"))
        new_path = os.path.join(TARGET_DIR, name)

        if not os.path.exists(new_path):
            print(f"No saved file/dir at {new_path}, skipping.")
            continue

        if os.path.islink(original_path):
            os.unlink(original_path)
        elif os.path.isdir(original_path):
            shutil.rmtree(original_path)
        elif os.path.isfile(original_path):
            os.remove(original_path)

        os.symlink(new_path, original_path)
        print(f"Linked {original_path} -> {new_path}")


def rollback_files():
    if not os.path.exists("rollback.json"):
        print("No rollback data found.")
        return

    with open("rollback.json", "r") as f:
        rollback_data = json.load(f)

    for link_path, moved_path in rollback_data.items():
        link_path = os.path.expanduser(link_path)

        if os.path.islink(link_path):
            os.unlink(link_path)
            print(f"Removed symlink: {link_path}")

        shutil.move(moved_path, link_path)
        print(f"Restored {link_path} from {moved_path}")

    os.remove("rollback.json")
    print("Rollback complete. Cleaned up rollback.json.")

