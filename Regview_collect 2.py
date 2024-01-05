from __future__ import print_function
from __future__ import unicode_literals
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

import sys
import os
import wx
from Registry import Registry
import csv

import subprocess
import shutil
import tkinter as tk
from tkinter import filedialog
from tkinter import messagebox


def _expand_into(dest, src):
    vbox = wx.BoxSizer(wx.VERTICAL)
    vbox.Add(src, 1, wx.EXPAND | wx.ALL)
    dest.SetSizer(vbox)


ID_FILE_OPEN = wx.NewIdRef()
ID_FILE_SESSION_SAVE = wx.NewIdRef()
ID_FILE_SESSION_OPEN = wx.NewIdRef()
ID_TAB_CLOSE = wx.NewIdRef()
ID_FILE_EXIT = wx.NewIdRef()
ID_HELP_ABOUT = wx.NewIdRef()


# CSVExporter 클래스 정의
class CSVExporter:
    @staticmethod
    def export(filename, data):
        with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
            fieldnames = ['Filename', 'Selected Path',
                          'Value Name', 'Value Type', 'Value Data']
            csv_writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            csv_writer.writeheader()
            csv_writer.writerows(data)


# PDFExporter 클래스 정의
class PDFExporter:
    @staticmethod
    def export(filename, data):
        c = canvas.Canvas(filename, pagesize=letter)
        y_position = 750
        line_height = 14

        for item in data:
            c.drawString(72, y_position, f"Filename: {item['Filename']}")
            y_position -= line_height
            c.drawString(72, y_position,
                         f"Selected Path: {item['Selected Path']}")
            y_position -= line_height
            c.drawString(72, y_position, f"Value Name: {item['Value Name']}")
            y_position -= line_height
            c.drawString(72, y_position, f"Value Type: {item['Value Type']}")
            y_position -= line_height
            c.drawString(72, y_position, f"Value Data: {item['Value Data']}")
            y_position -= line_height * 2

            if y_position < 72:
                c.showPage()
                y_position = 750

        c.save()
        print(f"PDF file has been created: {filename}")

        # 데이터 반환
        return data


class Extractor:
    @staticmethod
    def export_to_markdown(filename, data):
        with open(filename, 'w', encoding='utf-8') as md_file:
            md_file.write("# Extracted Registry Data\n\n")

            for item in data:
                md_file.write(f"## {item['Filename']}\n\n")
                md_file.write(
                    f"**Selected Path:** {item['Selected Path']}\n\n")
                md_file.write(f"**Value Name:** {item['Value Name']}\n\n")
                md_file.write(f"**Value Type:** {item['Value Type']}\n\n")
                md_file.write(f"**Value Data:** {item['Value Data']}\n\n")
                md_file.write("---\n\n")


def nop(*args, **kwargs):
    # 아무 동작도 하지 않는 함수
    pass


def basename(path):
    # 경로에서 파일의 기본 이름을 추출하는 함수
    if "/" in path:
        path = path.split("/")[-1]
    if "\\" in path:
        path = path.split("\\")[-1]
    return path


def _expand_into(dest, src):
    # wxPython 패널을 다른 패널에 추가하는 함수
    vbox = wx.BoxSizer(wx.VERTICAL)
    vbox.Add(src, 1, wx.EXPAND | wx.ALL)
    dest.SetSizer(vbox)


def _format_hex(data):
    # 데이터를 16진수 형식으로 포맷팅하는 함수
    byte_format = {}
    for c in range(256):
        if c > 126:
            byte_format[c] = '.'
        elif len(repr(chr(c))) == 3 and chr(c):
            byte_format[c] = chr(c)
        else:
            byte_format[c] = '.'

    def format_bytes(s):
        return "".join([byte_format[ord(c)] for c in s])

    def dump(src, length=16):
        N = 0
        result = ''
        while src:
            s, src = src[:length], src[length:]
            hexa = ' '.join(["%02X" % ord(x) for x in s])
            s = format_bytes(s)
            result += "%04X   %-*s   %s\n" % (N, length * 3, hexa, s)
            N += length
        return result
    return dump(data)


class DataPanel(wx.Panel):
    def __init__(self, *args, **kwargs):
        # 데이터를 표시하는 wxPython 패널 클래스
        super(DataPanel, self).__init__(*args, **kwargs)
        self._sizer = wx.BoxSizer(wx.VERTICAL)
        self.SetSizer(self._sizer)
        self.SetMinSize((300, 100))

    def display_value(self, value):
        # 데이터 값을 표시하는 함수
        self._sizer.Clear()
        data_type = value.value_type()

        if data_type == Registry.RegSZ or \
                data_type == Registry.RegExpandSZ or \
                data_type == Registry.RegDWord or \
                data_type == Registry.RegQWord:
            view = wx.TextCtrl(self, style=wx.TE_MULTILINE)
            view.SetValue(str(value.value()))

        elif data_type == Registry.RegMultiSZ:
            view = wx.ListCtrl(self, style=wx.LC_LIST)
            for string in value.value():
                view.InsertStringItem(view.GetItemCount(), string)

        elif data_type == Registry.RegBin or \
                data_type == Registry.RegNone:
            view = wx.TextCtrl(self, style=wx.TE_MULTILINE)
            font = wx.Font(8, wx.SWISS, wx.NORMAL,
                           wx.NORMAL, False, u'Courier')
            view.SetFont(font)
            view.SetValue(_format_hex(value.value()))

        else:
            view = wx.TextCtrl(self, style=wx.TE_MULTILINE)
            view.SetValue(str(value.value()))

        self._sizer.Add(view, 1, wx.EXPAND)
        self._sizer.Layout()

    def clear_value(self):
        # 데이터 값을 지우는 함수
        self._sizer.Clear()
        self._sizer.Add(wx.Panel(self, -1), 1, wx.EXPAND)
        self._sizer.Layout()


class ValuesListCtrl(wx.ListCtrl):
    def __init__(self, *args, **kwargs):
        # 레지스트리 값 목록을 표시하는 wxPython 리스트 컨트롤 클래스
        super(ValuesListCtrl, self).__init__(*args, **kwargs)
        self.InsertColumn(0, "Value name")
        self.InsertColumn(1, "Value type")
        self.SetColumnWidth(0, 300)
        self.SetColumnWidth(1, 300)
        self.values = {}

    def clear_values(self):
        # 모든 값 목록을 지우는 함수
        self.DeleteAllItems()
        self.values = {}

    def add_value(self, value):
        # 값 추가 함수
        n = self.GetItemCount()
        self.InsertItem(n, value.name())
        self.SetItem(n, 1, value.value_type_str())
        self.values[value.name()] = value

    def get_value(self, valuename):
        # 특정 이름의 값을 가져오는 함수
        return self.values[valuename]


class RegistryTreeCtrl(wx.TreeCtrl):
    def __init__(self, *args, **kwargs):
        # 레지스트리 트리를 표시하는 wxPython 트리 컨트롤 클래스
        super(RegistryTreeCtrl, self).__init__(*args, **kwargs)
        self.Bind(wx.EVT_TREE_ITEM_EXPANDING, self.OnExpandKey)

    def add_registry(self, registry):
        # 레지스트리를 트리에 추가하는 함수
        root_key = registry.root()
        root_item = self.AddRoot(root_key.name())
        self.SetItemData(root_item, {"key": root_key, "has_expanded": False})

        if len(root_key.subkeys()) > 0:
            self.SetItemHasChildren(root_item)

    def delete_registry(self):
        # 트리의 모든 항목을 지우는 함수
        self.DeleteAllItems()

    def select_path(self, path):
        # 특정 경로를 선택하는 함수
        parts = path.split("\\")
        node = self.GetRootItem()

        for part in parts:
            self._extend(node)
            (node, cookie) = self.GetFirstChild(node)

            cont = True
            while node and cont:
                key = self.GetItemData(node)["key"]
                if key.name() == part:
                    self.SelectItem(node)
                    cont = False
                else:
                    node = self.GetNextSibling(node)

    def _extend(self, item):
        # 아이템을 확장하는 함수
        if self.GetItemData(item)["has_expanded"]:
            return

        key = self.GetItemData(item)["key"]

        for subkey in key.subkeys():
            subkey_item = self.AppendItem(item, subkey.name())
            self.SetItemData(
                subkey_item, {"key": subkey, "has_expanded": False})

            if len(subkey.subkeys()) > 0:
                self.SetItemHasChildren(subkey_item)

        self.GetItemData(item)["has_expanded"] = True

    def OnExpandKey(self, event):
        # 아이템이 확장되면 호출되는 함수
        item = event.GetItem()
        if not item.IsOk():
            item = self.GetSelection()

        if not self.GetItemData(item)["has_expanded"]:
            self._extend(item)


class RegistryFileView(wx.Panel):
    def __init__(self, parent, registry, filename):
        # 레지스트리 파일을 표시하는 메인 패널 클래스
        super(RegistryFileView, self).__init__(parent, -1, size=(800, 600))
        self._filename = filename

        # 수직 분할창을 만듭니다.
        vsplitter = wx.SplitterWindow(self, -1)
        panel_left = wx.Panel(vsplitter, -1)
        panel_left.SetMinSize((200, 200))
        self._tree = RegistryTreeCtrl(panel_left, -1)
        _expand_into(panel_left, self._tree)

        # 추가적인 수직 분할창을 만듭니다.
        v2splitter = wx.SplitterWindow(vsplitter, -1)
        v2splitter.SetMinSize((300, -1))
        panel_2 = wx.Panel(v2splitter, -1)
        self.text2 = wx.StaticText(panel_2, label="ToolBox", pos=(10, 10))
        test_button = wx.Button(panel_2, label="Test", pos=(10, 40))
        test_button.Bind(wx.EVT_BUTTON, self.OnTestButtonClick)

        # 수평 분할창을 만듭니다.
        hsplitter = wx.SplitterWindow(v2splitter, -1)
        hsplitter.SetMinSize((300, -1))
        panel_top = wx.Panel(hsplitter, -1)
        panel_top.SetMinSize((-1, 300))
        panel_bottom = wx.Panel(hsplitter, -1)
        panel_bottom.SetMinSize((-1, 300))

        # 값 목록과 데이터를 표시하는 패널들을 만듭니다.
        self._value_list_view = ValuesListCtrl(
            panel_top, -1, style=wx.LC_REPORT)
        self._data_view = DataPanel(panel_bottom, -1)

        _expand_into(panel_top, self._value_list_view)
        _expand_into(panel_bottom, self._data_view)

        hsplitter.SplitHorizontally(panel_top, panel_bottom)
        v2splitter.SplitVertically(hsplitter, panel_2)
        vsplitter.SplitVertically(panel_left, v2splitter)

        vsplitter.SetSashPosition(325, True)
        _expand_into(self, vsplitter)
        self.Centre()

        self._value_list_view.Bind(
            wx.EVT_LIST_ITEM_SELECTED, self.OnValueSelected)
        self._tree.Bind(wx.EVT_TREE_SEL_CHANGED, self.OnKeySelected)

        self._tree.add_registry(registry)

    def extract_data(self):
        data = []
        for i in range(self._value_list_view.GetItemCount()):
            value_name = self._value_list_view.GetItemText(i)
            value = self._value_list_view.get_value(value_name)
            data.append({
                'Filename': self._filename,
                'Selected Path': self.selected_path(),
                'Value Name': value_name,
                'Value Type': value.value_type_str(),
                'Value Data': str(value.value())
            })
        return data

    def OnTestButtonClick(self, event):
        # 테스트 버튼 클릭 시 호출되는 함수
        test_frame = TestFrame(self)
        test_frame.Show()

    def OnKeySelected(self, event):
        # 레지스트리 트리에서 아이템 선택 시 호출되는 함수
        item = event.GetItem()
        if not item.IsOk():
            item = self._tree.GetSelection()

        key = self._tree.GetItemData(item)["key"]

        parent = self.GetParent()
        while parent:
            try:
                parent.SetStatusText(key.path())
            except AttributeError:
                pass
            parent = parent.GetParent()

        self._data_view.clear_value()
        self._value_list_view.clear_values()
        for value in key.values():
            self._value_list_view.add_value(value)

    def OnValueSelected(self, event):
        # 값 목록에서 아이템 선택 시 호출되는 함수
        item = event.GetItem()
        value = self._value_list_view.get_value(item.GetText())
        self._data_view.display_value(value)

    def filename(self):
        return self._filename

    def selected_path(self):
        item = self._tree.GetSelection()
        if item:
            return self._tree.GetItemData(item)["key"].path()
        return False

    def select_path(self, path):
        self._tree.select_path(path)

    def export_to_markdown(self, markdown_filename='extracted_data.md'):
        data = self.extract_data()  # 데이터 추출
        Extractor.export_to_markdown(markdown_filename, data)
        wx.MessageBox(
            f"Data extracted and saved to '{markdown_filename}'", "Extraction Complete")


class TestFrame(wx.Frame):
    def __init__(self, parent):
        # 간단한 테스트 창을 표시하는 클래스
        super(TestFrame, self).__init__(parent, title="테스트 창", size=(300, 200))
        panel = wx.Panel(self)
        text = wx.StaticText(panel, label="이것은 테스트 창입니다!", pos=(10, 10))


class RegistryFileViewer(wx.Frame):
    def __init__(self, parent, files):
        # 레지스트리 파일을 표시하는 메인 프레임 클래스
        super(RegistryFileViewer, self).__init__(
            parent, -1, "RegView", size=(800, 600))
        self.CreateStatusBar()

        menu_bar = wx.MenuBar()
        # 파일 메뉴 및 탭 메뉴에 대한 정의
        file_menu = wx.Menu()
        _open = file_menu.Append(ID_FILE_OPEN, '&Open File')
        self.Bind(wx.EVT_MENU, self.menu_file_open, _open)
        file_menu.AppendSeparator()
        _session_save = file_menu.Append(ID_FILE_SESSION_SAVE, '&Save Session')
        self.Bind(wx.EVT_MENU, self.menu_file_session_save, _session_save)
        _session_open = file_menu.Append(ID_FILE_SESSION_OPEN, '&Open Session')
        self.Bind(wx.EVT_MENU, self.menu_file_session_open, _session_open)
        file_menu.AppendSeparator()
        _exit = file_menu.Append(ID_FILE_EXIT, 'E&xit Program')
        self.Bind(wx.EVT_MENU, self.menu_file_exit, _exit)
        menu_bar.Append(file_menu, "&File")

        tab_menu = wx.Menu()
        _close = tab_menu.Append(ID_TAB_CLOSE, '&Close')
        self.Bind(wx.EVT_MENU, self.menu_tab_close, _close)
        menu_bar.Append(tab_menu, "&Tab")

        # Collect 메뉴에 대한 정의
        collect_menu = wx.Menu()
        _registry_collect = collect_menu.Append(wx.ID_ANY, 'Registry Collect')
        self.Bind(wx.EVT_MENU, self.menu_registry_collect, _registry_collect)
        menu_bar.Append(collect_menu, "&Collect")
        self.SetMenuBar(menu_bar)

        # Extract 메뉴에 대한 정의
        extract_menu = wx.Menu()
        _extract_csv = extract_menu.Append(wx.ID_ANY, 'Extract as CSV')
        self.Bind(wx.EVT_MENU, self.menu_extract_csv, _extract_csv)
        _extract_pdf = extract_menu.Append(wx.ID_ANY, 'Extract as PDF')
        self.Bind(wx.EVT_MENU, self.menu_extract_pdf, _extract_pdf)
        _extract_md = extract_menu.Append(wx.ID_ANY, 'Extract as Markdown')
        self.Bind(wx.EVT_MENU, self.menu_extract_md, _extract_md)

        # Extract 메뉴에 하위 메뉴 추가
        menu_bar.Append(extract_menu, "&Extract")
        self.SetMenuBar(menu_bar)  # 전역 메뉴바로 설정

        # 도움말 메뉴에 대한 정의
        help_menu = wx.Menu()
        _about = help_menu.Append(ID_HELP_ABOUT, '&About')
        self.Bind(wx.EVT_MENU, self.menu_help_about, _about)
        menu_bar.Append(help_menu, "&Help")
        self.SetMenuBar(menu_bar)

        p = wx.Panel(self)
        self._nb = wx.Notebook(p)

        # 파일 목록에 대해 루프를 돌며 각 파일에 대한 레지스트리 파일 뷰를 생성
        for filename in files:
            self._open_registry_file(filename)

        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(self._nb, 1, wx.EXPAND)
        p.SetSizer(sizer)
        self.Layout()

    def export_registry_keys(self, key_paths, output_folder):
        try:
            for key_path in key_paths:
                # 경로의 마지막 부분만 추출
                key_name = key_path.split("\\")[-1]

                output_file = os.path.join(output_folder, f'{key_name}')

                if os.path.exists(output_file):
                    # 파일이 이미 존재하는 경우 덮어쓸지 여부 확인
                    user_response = messagebox.askyesno(
                        "덮어쓰기", f"지정된 폴더 '{output_file}'에 동일한 내용의 파일이 이미 있습니다. 덮어쓰시겠습니까?")
                    if not user_response:
                        continue  # 덮어쓰기를 취소하고 다음 반복으로 이동.

                # REG EXPORT 명령어 생성
                command = f'reg export "{key_path}" "{output_file}"'

                # 서브프로세스를 사용하여 명령어 실행
                subprocess.run(command, shell=True, check=True)

                print(
                    f'레지스트리 키 "{key_path}"이(가) {output_file}로 성공적으로 추출되었습니다.')

        except subprocess.CalledProcessError as e:
            print(f'레지스트리 키 추출 오류: {e}')
            messagebox.showerror("오류", f"레지스트리 키 추출 중 오류 발생: {e}")

    def extract_files(self, source_folders, destination_folder, file_names):
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
                    destination_path = os.path.join(
                        destination_folder, file_name)

                    # 파일을 대상 폴더로 복사합니다.
                    shutil.copy2(source_path, destination_path)
                    print(
                        f"파일 '{file_name}'이(가) '{destination_folder}'로 추출되었습니다.")

    # 출력 폴더를 선택하는 함수

    def select_folder(self):
        folder_path = filedialog.askdirectory()
        return folder_path

    # Tkinter 창 생성
    root = tk.Tk()
    root.withdraw()  # 주 창 숨기기

    def menu_registry_collect(self, event):
        # "Registry Collect" 메뉴 항목을 선택했을 때 호출되는 함수
        output_folder = self.select_folder()

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
            self.export_registry_keys(key_paths, output_folder)

            # 파일 추출을 위한 원본 및 대상 폴더 지정
            source_folders = ["C:\\Users\\Default",
                              "C:\\Windows\\System32\\config"]

            # 추출할 파일 이름 목록 지정
            file_names = ['NTUSER.DAT', 'COMPONENTS',
                          'SECURITY', 'DEFAULT']  # 원하는 파일 이름으로 변경

            # 선택된 폴더로 extract_files 함수 호출
            self.extract_files(source_folders, output_folder, file_names)

    def menu_extract_csv(self, evt):
        csv_filename = 'extracted_data.csv'
        for i in range(self._nb.GetPageCount()):
            page = self._nb.GetPage(i)
            if isinstance(page, RegistryFileView):
                data = page.extract_data()
                CSVExporter.export(csv_filename, data)

        wx.MessageBox(
            f"Data extracted and saved to '{csv_filename}'", "Extraction Complete")

    def menu_extract_pdf(self, evt):
        pdf_filename = 'extracted_data.pdf'
        for i in range(self._nb.GetPageCount()):
            page = self._nb.GetPage(i)
            if isinstance(page, RegistryFileView):
                data = page.extract_data()
                PDFExporter.export(pdf_filename, data)

        wx.MessageBox(
            f"Data extracted and saved to '{pdf_filename}'", "Extraction Complete")

    def menu_extract_md(self, evt):
        markdown_filename = 'extracted_data.md'
        for i in range(self._nb.GetPageCount()):
            page = self._nb.GetPage(i)
            if isinstance(page, RegistryFileView):
                page.export_to_markdown(markdown_filename)

        wx.MessageBox(
            f"Data extracted and saved to '{markdown_filename}'", "Extraction Complete")

    def menu_extract(self, evt):
        # PDF에 데이터 추출 및 저장
        pdf_filename = 'extracted_data.pdf'
        for i in range(self._nb.GetPageCount()):
            page = self._nb.GetPage(i)
            if isinstance(page, RegistryFileView):
                data = page.extract_data()
                PDFExporter.export(pdf_filename, data)

        # Markdown에 데이터 추출 및 저장
        markdown_filename = 'extracted_data.md'
        for i in range(self._nb.GetPageCount()):
            page = self._nb.GetPage(i)
            if isinstance(page, RegistryFileView):
                page.export_to_markdown(markdown_filename)

        # CSV에 데이터 추출 및 저장
        csv_filename = 'extracted_data.csv'
        for i in range(self._nb.GetPageCount()):
            page = self._nb.GetPage(i)
            if isinstance(page, RegistryFileView):
                data = page.extract_data()
                CSVExporter.export(csv_filename, data)

        wx.MessageBox(
            f"Data extracted and saved to '{pdf_filename}', '{markdown_filename}', and '{csv_filename}'", "Extraction Complete")

    def export_to_pdf(self, pdf_filename='extracted_data.pdf'):
        # PDF 생성을 위한 캔버스 생성
        c = canvas.Canvas(pdf_filename, pagesize=letter)

        # 첫 번째 줄을 위한 시작 Y 위치 정의
        y_position = 750  # 페이지 상단부터 시작

        # 텍스트 줄의 높이 정의
        line_height = 14

        # 노트북에서 현재 선택된 페이지를 가져옴
        selected_page_index = self._nb.GetSelection()

        # 선택된 페이지가 RegistryFileView의 인스턴스인지 확인
        if selected_page_index != wx.NOT_FOUND:
            selected_page = self._nb.GetPage(selected_page_index)

            if isinstance(selected_page, RegistryFileView):
                # PDF에 포함될 데이터 추출
                data = selected_page.extract_data()

                for item in data:
                    # 각 데이터 항목에 대한 텍스트 줄 그리기
                    c.drawString(72, y_position, f"파일명: {item['Filename']}")
                    y_position -= line_height
                    c.drawString(72, y_position,
                                 f"선택된 경로: {item['Selected Path']}")
                    y_position -= line_height
                    c.drawString(72, y_position, f"값 이름: {item['Value Name']}")
                    y_position -= line_height
                    c.drawString(72, y_position, f"값 유형: {item['Value Type']}")
                    y_position -= line_height
                    c.drawString(72, y_position,
                                 f"값 데이터: {item['Value Data']}")
                    y_position -= line_height * 2  # 항목 간에 추가 여백 추가

                    # 페이지 하단에 도달하면 새로운 페이지 생성
                    if y_position < 72:
                        c.showPage()
                        y_position = 750  # Y 위치를 다시 페이지 상단으로 설정

                # PDF 파일 저장
                c.save()
                print(f"PDF 파일이 생성되었습니다: {pdf_filename}")
            else:
                wx.MessageBox("레지스트리 데이터가 있는 유효한 페이지를 선택해주세요.", "오류")
        else:
            wx.MessageBox("레지스트리 데이터가 있는 유효한 페이지를 선택해주세요.", "오류")

        # 수정된 부분: 데이터 반환
        return data

    def _open_registry_file(self, filename):
        # 주어진 파일에 대한 레지스트리 파일 뷰를 생성하는 함수
        try:
            registry = Registry.Registry(filename)
        except Registry.RegistryParseError as e:
            wx.LogError("Error parsing registry file: %s" % e)
            return

        registry_view = RegistryFileView(self._nb, registry, filename)
        self._nb.AddPage(registry_view, basename(filename), select=True)

    def menu_file_open(self, event):
        # "Open File" 메뉴 항목을 선택했을 때 호출되는 함수
        wildcard = "Registry files (*.dat;*.ntuser.dat;*.log;*.hive)|*.dat;*.ntuser.dat;*.log;*.hive|" \
                   "All files (*.*)|*.*"
        dialog = wx.FileDialog(self, "Open Registry File",
                               wildcard=wildcard, style=wx.FD_OPEN | wx.FD_FILE_MUST_EXIST)

        if dialog.ShowModal() == wx.ID_CANCEL:
            return

        filepath = dialog.GetPath()
        self._open_registry_file(filepath)

    def menu_file_session_save(self, event):
        # "Save Session" 메뉴 항목을 선택했을 때 호출되는 함수
        pass  # 여기에 세션 저장 코드를 추가하세요.

    def menu_file_session_open(self, event):
        # "Open Session" 메뉴 항목을 선택했을 때 호출되는 함수
        pass  # 여기에 세션 열기 코드를 추가하세요.

    def menu_file_exit(self, event):
        # "Exit Program" 메뉴 항목을 선택했을 때 호출되는 함수
        self.Close()

    def menu_tab_close(self, event):
        # "Close" 탭 메뉴 항목을 선택했을 때 호출되는 함수
        idx = self._nb.GetSelection()
        if idx != -1:
            self._nb.DeletePage(idx)

    def menu_help_about(self, event):
        # "About" 메뉴 항목을 선택했을 때 호출되는 함수
        about_info = wx.adv.AboutDialogInfo()
        about_info.SetName("Registry Viewer")
        about_info.SetVersion("1.0")
        about_info.SetDescription("A simple registry file viewer")
        about_info.SetWebSite(
            "https://github.com/example/regviewer", "Registry Viewer GitHub Page")
        about_info.SetLicense("MIT License")
        wx.adv.AboutBox(about_info)


if __name__ == '__main__':
    app = wx.App(False)
    filenames = sys.argv[1:]
    frame = RegistryFileViewer(None, filenames)
    frame.Show()
    app.MainLoop()