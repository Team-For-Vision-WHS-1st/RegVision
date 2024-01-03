import os
import shutil
import tkinter as tk
from tkinter import filedialog

def extract_files(source_folders, destination_folder, file_names):
    # 대상 폴더가 존재하지 않으면 생성
    if not os.path.exists(destination_folder):
        os.makedirs(destination_folder)

    for source_folder in source_folders:
        # 소스 폴더가 존재하는지 확인
        if not os.path.exists(source_folder):
            print(f"소스 폴더 '{source_folder}'가 존재하지 않습니다.")
            continue

        # 소스 폴더의 모든 파일 목록 가져오기
        files = os.listdir(source_folder)

        # 지정된 파일명을 가진 파일만 추출
        for file_name in files:
            if file_name in file_names:
                source_path = os.path.join(source_folder, file_name)
                destination_path = os.path.join(destination_folder, file_name)

                # 파일을 대상 폴더로 복사
                shutil.copy2(source_path, destination_path)
                print(f"파일 '{file_name}'이(가) '{destination_folder}'로 추출되었습니다.")

# 사용자가 직접 소스 폴더 및 대상 폴더 지정
source_folders = ["C:\\Windows\\System32\\config", "C:\\Users\\Default"]
root = tk.Tk()
root.withdraw()  # 주 창 숨기기
destination_folder = filedialog.askdirectory(title="저장할 폴더 선택")

# 사용자가 대화 상자를 취소하면 종료
if not destination_folder:
    print("추출 취소됨.")
else:
    # 추출할 파일명 리스트 지정
    file_names = ['NTUSER.DAT', 'SAM', 'SOFTWARE', 'SECURITY', 'SYSTEM', 'COMPONENTS', 'DEFAULT']  # 원하는 파일명으로 변경
    
    # 선택한 폴더로 extract_files 함수 호출
    extract_files(source_folders, destination_folder, file_names)