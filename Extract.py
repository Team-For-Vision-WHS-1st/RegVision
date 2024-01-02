#pdf 수정중인 파일입니다.

from __future__ import print_function
from __future__ import unicode_literals
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter

import sys
import os
import wx
from Registry import Registry
import csv

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
            fieldnames = ['Filename', 'Selected Path', 'Value Name', 'Value Type', 'Value Data']
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
            c.drawString(72, y_position, f"Selected Path: {item['Selected Path']}")
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
                md_file.write(f"**Selected Path:** {item['Selected Path']}\n\n")
                md_file.write(f"**Value Name:** {item['Value Name']}\n\n")
                md_file.write(f"**Value Type:** {item['Value Type']}\n\n")
                md_file.write(f"**Value Data:** {item['Value Data']}\n\n")
                md_file.write("---\n\n")

class ValuesListCtrl(wx.ListCtrl):
    def __init__(self, *args, **kwargs):
        super(ValuesListCtrl, self).__init__(*args, **kwargs)
        self.InsertColumn(0, "Value name")
        self.InsertColumn(1, "Value type")
        self.SetColumnWidth(0, 300)
        self.SetColumnWidth(1, 300)
        self.values = {}

    def clear_values(self):
        self.DeleteAllItems()
        self.values = {}

    def add_value(self, value):
        n = self.GetItemCount()
        self.InsertItem(n, value.name())
        self.SetItem(n, 1, value.value_type_str())
        self.values[value.name()] = value

    def get_value(self, valuename):
        return self.values[valuename]

    def get_all_values(self):
        # 수정된 부분: 모든 값을 반환하는 함수 추가
        return list(self.values.values())


class RegistryTreeCtrl(wx.TreeCtrl):
    def __init__(self, *args, **kwargs):
        super(RegistryTreeCtrl, self).__init__(*args, **kwargs)
        self.Bind(wx.EVT_TREE_ITEM_EXPANDING, self.OnExpandKey)

    def add_registry(self, registry):
        root_key = registry.root()
        root_item = self.AddRoot(root_key.name())
        self.SetItemData(root_item, {"key": root_key,
                                     "has_expanded": False})

        if len(root_key.subkeys()) > 0:
            self.SetItemHasChildren(root_item)

    def delete_registry(self):
        self.DeleteAllItems()

    def select_path(self, path):
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
        if self.GetItemData(item)["has_expanded"]:
            return

        key = self.GetItemData(item)["key"]

        for subkey in key.subkeys():
            subkey_item = self.AppendItem(item, subkey.name())
            self.SetItemData(subkey_item, {"key": subkey,
                                           "has_expanded": False})

            if len(subkey.subkeys()) > 0:
                self.SetItemHasChildren(subkey_item)

        self.GetItemData(item)["has_expanded"] = True

    def OnExpandKey(self, event):
        item = event.GetItem()
        if not item.IsOk():
            item = self.GetSelection()

        if not self.GetItemData(item)["has_expanded"]:
            self._extend(item)


class DataPanel(wx.Panel):
    def __init__(self, *args, **kwargs):
        super(DataPanel, self).__init__(*args, **kwargs)
        self._sizer = wx.BoxSizer(wx.VERTICAL)
        self.SetSizer(self._sizer)

    def extract_data(self, value):
        data = {
            'Filename': self.GetParent().filename(),
            'Selected Path': self.GetParent().selected_path(),
            'Value Name': value.name(),
            'Value Type': value.value_type_str(),
            'Value Data': str(value.value())
        }
        return data

    def display_value(self, value):
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
                view.InsertItem(view.GetItemCount(), string)

        elif data_type == Registry.RegBin or \
                data_type == Registry.RegNone:
            view = wx.TextCtrl(self, style=wx.TE_MULTILINE | wx.HSCROLL)  # wx.HSCROLL 추가
            font = wx.Font(8, wx.SWISS, wx.NORMAL, wx.NORMAL, False, u'Courier')
            view.SetFont(font)
            view.SetValue(_format_hex(value.value()))

        else:
            view = wx.TextCtrl(self, style=wx.TE_MULTILINE)
            view.SetValue(str(value.value()))

        self._sizer.Add(view, 1, wx.EXPAND)
        self._sizer.Layout()

    def clear_value(self):
        self._sizer.Clear()
        self._sizer.Add(wx.Panel(self, -1), 1, wx.EXPAND)
        self._sizer.Layout()

class RegistryFileView(wx.Panel):
    def __init__(self, parent, registry, filename):
        super(RegistryFileView, self).__init__(parent, -1, size=(800, 600))
        self._filename = filename

        vsplitter = wx.SplitterWindow(self, -1)
        panel_left = wx.Panel(vsplitter, -1)
        self._tree = RegistryTreeCtrl(panel_left, -1)
        _expand_into(panel_left, self._tree)

        hsplitter = wx.SplitterWindow(vsplitter, -1)
        panel_top = wx.Panel(hsplitter, -1)
        panel_bottom = wx.Panel(hsplitter, -1)

        self._value_list_view = ValuesListCtrl(panel_top, -1, style=wx.LC_REPORT)
        self._data_view = DataPanel(panel_bottom, -1)

        _expand_into(panel_top, self._value_list_view)
        _expand_into(panel_bottom, self._data_view)

        hsplitter.SplitHorizontally(panel_top, panel_bottom)
        vsplitter.SplitVertically(panel_left, hsplitter)

        vsplitter.SetSashPosition(325, True)
        _expand_into(self, vsplitter)
        self.Centre()

        self._value_list_view.Bind(wx.EVT_LIST_ITEM_SELECTED, self.OnValueSelected)
        self._tree.Bind(wx.EVT_TREE_SEL_CHANGED, self.OnKeySelected)
        # 뷰에 대한 노트북 참조 추가
        self._nb = parent

        self._tree.add_registry(registry)

    def OnKeySelected(self, event):
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

    def export_to_markdown(self, markdown_filename='extracted_data.md'):
        data = self.extract_data()  # 데이터 추출
        Extractor.export_to_markdown(markdown_filename, data)
        wx.MessageBox(f"Data extracted and saved to '{markdown_filename}'", "Extraction Complete")

        data = self.extract_data()  # 데이터를 다시 추출
        with open('extracted_data.csv', 'w', newline='', encoding='utf-8') as csvfile:
            fieldnames = ['Filename', 'Selected Path', 'Value Name', 'Value Type', 'Value Data']
            csv_writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            csv_writer.writeheader()
            csv_writer.writerows(data)

        with open('extracted_data.csv', 'w', newline='', encoding='utf-8') as csvfile:
            fieldnames = ['Filename', 'Selected Path', 'Value Name', 'Value Type', 'Value Data']
            csv_writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            csv_writer.writeheader()
            csv_writer.writerows(data)

    def filename(self):
        return self._filename

    def selected_path(self):
        item = self._tree.GetSelection()
        if item:
            return self._tree.GetItemData(item)["key"].path()
        return False

    # RegistryFileView 클래스에서 extract_data 수정
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

    def OnValueSelected(self, event):
        item = event.GetItem()
        value = self._value_list_view.get_value(item.GetText())
        self._data_view.display_value(value)


class RegistryFileViewer(wx.Frame):
    def __init__(self, parent, files):
        super(RegistryFileViewer, self).__init__(parent, -1, "Registry Viewer", size=(800, 600))
        self.CreateStatusBar()

        menu_bar = wx.MenuBar()
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

        help_menu = wx.Menu()
        _about = help_menu.Append(ID_HELP_ABOUT, '&About')
        self.Bind(wx.EVT_MENU, self.menu_help_about, _about)
        menu_bar.Append(help_menu, "&Help")
        self.SetMenuBar(menu_bar)

        extract_menu = wx.Menu()
        _extract = extract_menu.Append(wx.ID_ANY, '&Extract')
        self.Bind(wx.EVT_MENU, self.menu_extract, _extract)
        menu_bar.Append(extract_menu, "&Extract")

        self.SetMenuBar(menu_bar)

        p = wx.Panel(self)
        self._nb = wx.Notebook(p)

        for filename in files:
            self._open_registry_file(filename)

        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(self._nb, 1, wx.EXPAND)
        p.SetSizer(sizer)
        self.Layout()

    def menu_extract(self, evt):
        # PDF에 데이터 추출 및 저장
        data = self.export_to_pdf()
        wx.MessageBox("Data extracted and saved to 'extracted_data.pdf'", "Extraction Complete")

        # Markdown에 데이터 추출 및 저장
        markdown_filename = 'extracted_data.md'
        for i in range(self._nb.GetPageCount()):
            page = self._nb.GetPage(i)
            if isinstance(page, RegistryFileView):
                page.export_to_markdown(markdown_filename)

        # CSV에 데이터 추출 및 저장
        with open('extracted_data.csv', 'w', newline='', encoding='utf-8') as csvfile:
            fieldnames = ['Filename', 'Selected Path', 'Value Name', 'Value Type', 'Value Data']
            csv_writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            csv_writer.writeheader()

            for item in data:
                csv_writer.writerow({
                    'Filename': item['Filename'],
                    'Selected Path': item['Selected Path'],
                    'Value Name': item['Value Name'],
                    'Value Type': item['Value Type'],
                    'Value Data': item['Value Data']
                })

        wx.MessageBox(f"Data extracted and saved to 'extracted_data.csv', '{markdown_filename}', and 'extracted_data.pdf'", "Extraction Complete")

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
                    c.drawString(72, y_position, f"선택된 경로: {item['Selected Path']}")
                    y_position -= line_height
                    c.drawString(72, y_position, f"값 이름: {item['Value Name']}")
                    y_position -= line_height
                    c.drawString(72, y_position, f"값 유형: {item['Value Type']}")
                    y_position -= line_height
                    c.drawString(72, y_position, f"값 데이터: {item['Value Data']}")
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
        with open(filename, "rb") as f:
            registry = Registry.Registry(f)
            view = RegistryFileView(self._nb, registry=registry, filename=filename)
            self._nb.AddPage(view, os.path.basename(filename))
            return view

    def menu_file_open(self, evt):
        dialog = wx.FileDialog(None, "Choose Registry File", "", "", "*", wx.FD_OPEN)
        if dialog.ShowModal() != wx.ID_OK:
            return
        filename = os.path.join(dialog.GetDirectory(), dialog.GetFilename())
        self._open_registry_file(filename)

    def menu_file_exit(self, evt):
        sys.exit(0)

    def menu_file_session_open(self, evt):
        self._nb.DeleteAllPages()

        dialog = wx.FileDialog(None, "Open Session File", "", "", "*.csv", wx.OPEN)
        if dialog.ShowModal() != wx.ID_OK:
            return
        filename = os.path.join(dialog.GetDirectory(), dialog.GetFilename())
        with open(filename, "r") as csvfile:
            csv_reader = csv.reader(csvfile)
            next(csv_reader)  # Skip header row

            for row in csv_reader:
                filename, path = row
                view = self._open_registry_file(filename)
                view.select_path(path)

            self.SetStatusText("Opened session")

    def menu_file_session_save(self, evt):
        dialog = wx.FileDialog(None, "Save Session File", "", "", "*.csv", wx.SAVE | wx.FD_OVERWRITE_PROMPT)
        if dialog.ShowModal() != wx.ID_OK:
            return
        filename = os.path.join(dialog.GetDirectory(), dialog.GetFilename())
        with open(filename, "w", newline='') as f:
            csv_writer = csv.writer(f)
            csv_writer.writerow(['Filename', 'Selected Path'])

            for i in range(0, self._nb.GetPageCount()):
                page = self._nb.GetPage(i)
                filename = page.filename()
                path = page.selected_path() or ""
                csv_writer.writerow([filename, path])

            self.SetStatusText("Saved session to CSV")

    def menu_tab_close(self, evt):
        self._nb.RemovePage(self._nb.GetSelection())

    def menu_help_about(self, evt):
        wx.MessageBox("Registry Viewer\n\nhttp://www.williballenthin.com/registry/", "About")


if __name__ == '__main__':
    app = wx.App(False)
    filenames = sys.argv[1:]
    frame = RegistryFileViewer(None, filenames)
    frame.Show()
    app.MainLoop()
