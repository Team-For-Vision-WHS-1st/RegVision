#초기 작성 코드

import os
import platform
import socket
import getpass
import psutil

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
        processes.append(process.info)
    return processes

def list_files_in_directory(directory):
    try:
        files = os.listdir(directory)
        return files
    except Exception as e:
        return f"Error listing files: {e}"

if __name__ == "__main__":
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

    # 특정 디렉토리의 파일 목록 수집
    target_directory = "C:\\Users\\"  # 대상 디렉토리 경로를 변경하세요.
    files_in_directory = list_files_in_directory(target_directory)
    print(f"Files in {target_directory}:")
    for file in files_in_directory:
        print(file)
