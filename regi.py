# test.py(csv)경로를 지정해서 데이터를 수집하고 지정해 둔 경로에 csv 파일을 저장하지만 사용자가 지정할 수 있게 변경하는 작업 

import os
import platform
import socket
import getpass
import psutil
import csv

def collect_system_info():
    system_info = {
        "System": platform.system(),
        "Node Name": platform.node(),
        "Release": platform.release(),
        "Version": platform.version(),
        "Machine": platform.machine(),
        "Processor": platform.processor(),
        "Architecture": platform.architecture(),
        "Python Version": platform.python_version()
    }
    return system_info

def collect_network_info():
    hostname = socket.gethostname()
    local_ip = socket.gethostbyname(hostname)
    username = getpass.getuser()

    network_info = {
        "Hostname": hostname,
        "Local IP Address": local_ip,
        "Username": username
    }
    return network_info

def collect_process_info():
    processes = []
    for process in psutil.process_iter(['pid', 'name']):
        process_data = {
            "PID": process.info['pid'],
            "Name": process.info['name']
        }
        processes.append(process_data)
    return processes

def list_files_in_directory(directory):
    try:
        files = os.listdir(directory)
        return files
    except Exception as e:
        return f"Error listing files: {e}"

def save_to_csv(data, filename, fieldnames):
    with open(filename, 'w', newline='') as csvfile:
        # Check if the file has write permission
        if not os.access(filename, os.W_OK):
            grant_permission_recursive(filename)

        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for row in data:
            writer.writerow(row)

def grant_permission_recursive(directory):
    for root, dirs, files in os.walk(directory):
        for d in dirs:
            path = os.path.join(root, d)
            os.chmod(path, 0o777)

if __name__ == "__main__":
    # 특정 디렉토리의 파일 목록 수집
    target_directory = input("Enter the target directory path: ")

    files_in_directory = list_files_in_directory(target_directory)
    print(f"Files in {target_directory}:")
    for file in files_in_directory:
        print(file)

    # 시스템 정보 수집
    system_info = collect_system_info()
    print("System Information:")
    for key, value in system_info.items():
        print(f"{key}: {value}")

    print("\n")

    # 네트워크 정보 수집
    network_info = collect_network_info()
    print("Network Information:")
    for key, value in network_info.items():
        print(f"{key}: {value}")

    print("\n")

    # 현재 실행 중인 프로세스 정보 수집
    process_info = collect_process_info()
    print("Process Information:")
    for process in process_info:
        print(process)

    print("\n")

    # CSV 파일 저장 경로 입력 받기
    csv_filename = input("Enter the CSV file path for saving data: ")

    # 필드 이름 정의
    fieldnames = ["System", "Node Name", "Release", "Version", "Machine", "Processor", 
                  "Architecture", "Python Version", "Hostname", "Local IP Address", 
                  "Username", "PID", "Name"]

    # Save data to CSV
    data_to_save = [system_info, network_info] + process_info
    save_to_csv(data_to_save, csv_filename, fieldnames)

    print(f"Data saved to {csv_filename}")
