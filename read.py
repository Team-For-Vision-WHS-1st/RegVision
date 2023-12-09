import os
import sys
import winreg
import ctypes
import tkinter as tk
from tkinter import filedialog


def save_registry_key_to_file(hive, subkey, save_directory):
    try:
        # Convert hive to corresponding registry constant
        if hive == "HKLM":
            hive_key = winreg.HKEY_LOCAL_MACHINE
        elif hive == "HKU":
            hive_key = winreg.HKEY_USERS
        elif hive == "HKCR":
            hive_key = winreg.HKEY_CLASSES_ROOT
        elif hive == "HKCC":
            hive_key = winreg.HKEY_CURRENT_CONFIG
        elif hive == "HKCU":
            hive_key = winreg.HKEY_CURRENT_USER
        else:
            print(f"Invalid hive: {hive}")
            return

        # Combine hive and subkey to create the full key path
        full_key_path = os.path.join(hive, subkey)

        # Open the registry key
        key = winreg.OpenKey(hive_key, subkey, 0, winreg.KEY_READ | winreg.KEY_WOW64_64KEY)

        # Read all values in the registry key
        values = []
        index = 0
        while True:
            try:
                name, value, data_type = winreg.EnumValue(key, index)
                values.append((name, value, data_type))
                index += 1
            except OSError:
                break

        # Close the registry key
        winreg.CloseKey(key)

        # Save values to a text file
        file_name = f"{subkey}_registry_file"
        file_path = os.path.join(save_directory, file_name)

        with open(file_path, 'w', encoding='utf-8') as file:
            file.write(f"Registry Key: {full_key_path}\n\n")
            for name, value, data_type in values:
                file.write(f"{name}: {value} ({data_type})\n")

        print(f"Registry key '{full_key_path}' saved to file: {file_path}")
    except PermissionError as e:
        print(f"Error: Access denied - {e}")
    except FileNotFoundError as e:
        print(f"Error: Specified file not found - {e}")
    except Exception as e:
        print(f"Error: {e}")

def get_save_directory():
    root = tk.Tk()
    root.withdraw()
    folder_selected = filedialog.askdirectory()
    return folder_selected

def main():

    # 레지스트리 키 경로 직접 지정
    key_paths = [
        ("HKLM", "SYSTEM"),
        ("HKLM", "SOFTWARE"),
        ("HKLM", "SAM"),
        #("HKLM", "SECURITY"),
        #("HKU", "DEFAULT"),
        # Add more key paths as needed
    ]

    # 사용자로부터 저장할 경로 입력 받기 (Tkinter를 사용)
    save_directory = get_save_directory()

    # 입력 받은 경로가 존재하지 않으면 생성
    os.makedirs(save_directory, exist_ok=True)

    for hive, subkey in key_paths:
        # Save the registry key to the file
        save_registry_key_to_file(hive, subkey, save_directory)

if __name__ == "__main__":
    main()