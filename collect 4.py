import subprocess
import os
import shutil
import tkinter as tk
from tkinter import filedialog
from tkinter import messagebox

def export_registry_keys(key_paths, output_folder):
    try:
        for key_path in key_paths:
            # 경로의 마지막 부분만 추출
            key_name = key_path.split("\\")[-1]

            output_file = os.path.join(output_folder, f'{key_name}')

            if os.path.exists(output_file):
                # 파일이 이미 존재하는 경우 덮어쓸지 여부 확인
                user_response = messagebox.askyesno("덮어쓰기", f"지정된 폴더 '{output_file}'에 동일한 내용의 파일이 이미 있습니다. 덮어쓰시겠습니까?")
                if not user_response:
                    continue # 덮어쓰기를 취소하고 다음 반복으로 이동.

            # REG EXPORT 명령어 생성
            command = f'reg export "{key_path}" "{output_file}"'

            # 서브프로세스를 사용하여 명령어 실행
            subprocess.run(command, shell=True, check=True)

            print(f'레지스트리 키 "{key_path}"이(가) {output_file}로 성공적으로 추출되었습니다.')

    except subprocess.CalledProcessError as e:
        print(f'레지스트리 키 추출 오류: {e}')
        messagebox.showerror("오류", f"레지스트리 키 추출 중 오류 발생: {e}")

def extract_files(source_folders, destination_folder, file_names):
    """
    특정 파일 이름을 가진 파일을 원본 폴더에서 추출하여 대상 폴더에 저장합니다.

    매개변수:
    - source_folders (list): 파일을 추출할 원본 폴더 목록입니다.
    - destination_folder (str): 추출된 파일을 저장할 대상 폴더입니다.
    - file_names (list): 추출할 파일 이름 목록입니다.

    반환값:
    None
    """
    # 대상 폴더가 존재하지 않으면 생성합니다.
    if not os.path.exists(destination_folder):
        os.makedirs(destination_folder)

    for source_folder in source_folders:
        # 원본 폴더가 존재하는지 확인합니다.
        if not os.path.exists(source_folder):
            print(f"원본 폴더 '{source_folder}'이(가) 존재하지 않습니다.")
            continue

        # 원본 폴더의 모든 파일 목록을 가져옵니다.
        files = os.listdir(source_folder)

        # 지정된 파일 이름을 가진 파일만 추출합니다.
        for file_name in files:
            if file_name in file_names:
                source_path = os.path.join(source_folder, file_name)
                destination_path = os.path.join(destination_folder, file_name)

                # 파일을 대상 폴더로 복사합니다.
                shutil.copy2(source_path, destination_path)
                print(f"파일 '{file_name}'이(가) '{destination_folder}'로 추출되었습니다.")

# 출력 폴더를 선택하는 함수
def select_folder():
    folder_path = filedialog.askdirectory()
    return folder_path

# Tkinter 창 생성
root = tk.Tk()
root.withdraw() # 주 창 숨기기

# 레지스트리 키 추출을 위한 폴더 선택
output_folder = select_folder()

# 폴더 선택이 취소되면 종료
if not output_folder:
    print("추출이 취소되었습니다.")
else:
    # 레지스트리 키 경로 예시 (필요에 따라 추가 또는 제거)
    key_paths = [
        r'HKEY_USERS\.DEFAULT',
        r'HKEY_LOCAL_MACHINE\SOFTWARE',
        r'HKEY_LOCAL_MACHINE\SAM',
        r'HKEY_LOCAL_MACHINE\SYSTEM',
        r'HKEY_LOCAL_MACHINE\HARDWARE',
        r'HKEY_LOCAL_MACHINE\BCD00000000',
        r'HKEY_LOCAL_MACHINE\SECURITY',
    ]

    # 레지스트리 키 추출 함수 호출
    export_registry_keys(key_paths, output_folder)

    # 파일 추출을 위한 원본 및 대상 폴더 지정
    source_folders = ["C:\\Users\\Default", "C:\\Windows\\System32\\config"]

    # 추출할 파일 이름 목록 지정
    file_names = ['NTUSER.DAT', 'COMPONENTS', 'SECURITY', 'DEFAULT'] # 원하는 파일 이름으로 변경
    
    # 선택된 폴더로 extract_files 함수 호출
    extract_files(source_folders, output_folder, file_names)
