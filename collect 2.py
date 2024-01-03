import subprocess
import os
import tkinter as tk
from tkinter import filedialog
from tkinter import messagebox

def export_registry_keys(key_paths, output_folder, root):
    try:
        root.destroy()

        for key_path in key_paths:
            # 마지막 경로 부분만 추출
            key_name = key_path.split("\\")[-1]

            output_file = os.path.join(output_folder, f'{key_name}')

            if os.path.exists(output_file):
                # 파일이 이미 존재하는 경우 덮어쓸지 여부 확인
                user_response = messagebox.askyesno("덮어쓰기", f"이미 지정된 폴더 '{output_file}'에 동일한 내용의 파일이 존재합니다. 덮어쓰시겠습니까?")
                if not user_response:
                    continue  # 덮어쓰기를 취소하면 다음 반복으로 건너뜁니다.

            # REG EXPORT 명령 생성
            command = f'reg export "{key_path}" "{output_file}"'

            # subprocess를 사용하여 명령 실행
            subprocess.run(command, shell=True, check=True)

            print(f'레지스트리 키 "{key_path}"가 성공적으로 {output_file}로 추출되었습니다.')

        root.destroy()  # Tkinter 창 닫기
    except subprocess.CalledProcessError as e:
        print(f'레지스트리 키 추출 오류: {e}')
        messagebox.showerror("오류", f"레지스트리 키 추출 오류: {e}")
    finally:
        root.destroy()

def choose_folder():
    # 폴더 선택 대화 상자 열기
    folder_path = filedialog.askdirectory()
    entry_var.set(folder_path)

# Tkinter 창 생성
root = tk.Tk()
root.title("레지스트리 파일 수집")

# 폴더 경로를 입력할 Entry 위젯
entry_var = tk.StringVar()
entry = tk.Entry(root, textvariable=entry_var, width=40)
entry.grid(row=0, column=0, padx=10, pady=10)

# 폴더 선택 버튼
choose_button = tk.Button(root, text="폴더 선택", command=choose_folder)
choose_button.grid(row=0, column=1, padx=10, pady=10)

# 레지스트리 키 경로 예제 (필요에 따라 추가 또는 제거)
key_paths = [
    r'HKEY_USERS\.DEFAULT',
    r'HKEY_LOCAL_MACHINE\SOFTWARE',
    r'HKEY_LOCAL_MACHINE\SAM',
    r'HKEY_LOCAL_MACHINE\SYSTEM',
    r'HKEY_LOCAL_MACHINE\HARDWARE',
    r'HKEY_LOCAL_MACHINE\BCD00000000',
    r'HKEY_LOCAL_MACHINE\SECURITY',
]

# 레지스트리 키 추출 버튼
export_button = tk.Button(root, text="레지스트리 파일 수집하기", command=lambda: export_registry_keys(key_paths, entry_var.get(), root))
export_button.grid(row=1, column=0, columnspan=2, pady=10)

# Tkinter 이벤트 루프 시작
root.mainloop()
