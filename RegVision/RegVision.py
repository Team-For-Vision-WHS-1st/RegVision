from __future__ import print_function
from __future__ import unicode_literals
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter

#태희님 코드 추가
from installed_application import get_installed_applications # 설치응용프로그램.py import 
from amcache_analyzer import analyze_amcache #amcache 모듈 import

#태희님 코드 추가
import wx.grid as girdlib
import sys
import os
import wx
from Registry import Registry
import csv
#영서님 코드 추가
import subprocess
from network import network_settings
from keyword_search import keyword

import pandas as pd #cms
import time #cms
import wx.grid #cms
import threading #cms
import codecs #cms
import struct #cms
import getpass
from datetime import datetime, timedelta#cms
from Registry import Registry#cms
from known_folders import folder_guids#cms



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

class WindowsInfoHandler:#cms code
    @staticmethod
    def os_settings(soft_reg):
        registry = Registry.Registry(soft_reg)
        os_dict = {}
        key = registry.open("Microsoft\\Windows NT\\CurrentVersion")
        for v in key.values():
            if v.name() == "ProductName":
                os_dict['Product Name'] = v.value()
            if v.name() == "ProductId":
                os_dict['Product ID'] = v.value()
            if v.name() == "CSDVersion":
                os_dict['CSD Version'] = v.value()
            if v.name() == "PathName":
                os_dict['Path Name'] = v.value()
            if v.name() == "InstallDate":
                os_dict['Install Date'] = time.strftime('%a %b %d %H:%M:%S %Y (UTC)', time.gmtime(v.value()))
            if v.name() == "RegisteredOrganization":
                os_dict['Registered Organization'] = v.value()
            if v.name() == "RegisteredOwner":
                os_dict['Registered Owner'] = v.value()

        os_series = pd.Series(os_dict, name="Operating System")
        return os_series

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
            font = wx.Font(8, wx.SWISS, wx.NORMAL, wx.NORMAL, False, u'Courier')
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
        self.SetColumnWidth(2, 300)
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

    def get_all_values(self):
        # 수정된 부분: 모든 값을 반환하는 함수 추가
        return list(self.values.values())

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


#영서님 코드 추가
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
        self.text3 = wx.StaticText(panel_2, label="기본도구", pos=(10, 40))
        keyword_button = wx.Button(panel_2, label="keyword_search", pos=(10, 60))
        timeline_button = wx.Button(panel_2, label="timeline_search", pos=(10, 90))

        self.text4 = wx.StaticText(panel_2, label="윈도우 설치 정보", pos=(10, 130))
        test_button = wx.Button(panel_2, label="Win info", pos=(10, 150))
        test_button.Bind(wx.EVT_BUTTON, self.WINF_button_click)
        

        self.text5 = wx.StaticText(panel_2, label="사용자 활동 정보", pos=(10, 180))
        test_button3 = wx.Button(panel_2, label="UserAssist", pos=(10, 200))
        test_button3.Bind(wx.EVT_BUTTON, self.UserAssist_button_click)

        self.text5 = wx.StaticText(panel_2, label="시스템 설정 정보", pos=(10, 230))
        test_button2 = wx.Button(panel_2, label="Suv list", pos=(10, 250))
        test_button2.Bind(wx.EVT_BUTTON, self.Suvlist_button_click)
        
        self.text6 = wx.StaticText(panel_2, label="응용프로그램 정보", pos=(10, 280))
        #태희님 코드 추가 350 - 376
        installed_apps_button = wx.Button(panel_2, label="설치된 응용프로그램", pos=(10,310))
        installed_apps_button.Bind(wx.EVT_BUTTON, self.OnInstalledAppsButtonClick)
        # amcache.hve 버튼 추가 
        amcache_analyzer_button = wx.Button(panel_2, label="Amcache.hve", pos=(10,340))
        amcache_analyzer_button.Bind(wx.EVT_BUTTON, self.OnAmcacheAnalyzerButtonClick)

        #test_button = wx.Button(panel_2, label="Test", pos=(10, 50))
        self.text7 = wx.StaticText(panel_2, label="네트워크 정보", pos=(10, 370))
        network_button = wx.Button(panel_2, label="TCP/IP", pos=(10, 390))

        self.text8 = wx.StaticText(panel_2, label="부가추출 정보", pos=(10, 420))
        mac_button = wx.Button(panel_2, label="맥 어드레스", pos=(10, 440)) 

        #test_button.Bind(wx.EVT_BUTTON, self.OnTestButtonClick)
        network_button.Bind(wx.EVT_BUTTON, self.OnNetworkButtonClick)
        keyword_button.Bind(wx.EVT_BUTTON, self.OnKeywordButtonClick)
        timeline_button.Bind(wx.EVT_BUTTON, self.OnTimelineButtonClick)
        mac_button.Bind(wx.EVT_BUTTON, self.OnMacAddressButtonClick)

        # 수평 분할창을 만듭니다.
        hsplitter = wx.SplitterWindow(v2splitter, -1)
        hsplitter.SetMinSize((300, -1))
        panel_top = wx.Panel(hsplitter, -1)
        panel_top.SetMinSize((-1, 300))
        panel_bottom = wx.Panel(hsplitter, -1)
        panel_bottom.SetMinSize((-1, 300))

        # 값 목록과 데이터를 표시하는 패널들을 만듭니다.
        self._value_list_view = ValuesListCtrl(panel_top, -1, style=wx.LC_REPORT)
        self._data_view = DataPanel(panel_bottom, -1)

        _expand_into(panel_top, self._value_list_view)
        _expand_into(panel_bottom, self._data_view)

        hsplitter.SplitHorizontally(panel_top, panel_bottom)
        v2splitter.SplitVertically(hsplitter, panel_2)
        vsplitter.SplitVertically(panel_left, v2splitter)

        vsplitter.SetSashPosition(325, True)
        _expand_into(self, vsplitter)
        self.Centre()

        self._value_list_view.Bind(wx.EVT_LIST_ITEM_SELECTED, self.OnValueSelected)
        self._tree.Bind(wx.EVT_TREE_SEL_CHANGED, self.OnKeySelected)

        self._tree.add_registry(registry)

    def OnInstalledAppsButtonClick(self, event):
        soft_reg = ".\\SOFTWARE"  # software path
        results = get_installed_applications(soft_reg)

        #팝업 창 생성하여 결과 표시 
        installed_apps_frame = InstalledApplicationsFrame(self, results)
        installed_apps_frame.Show()

    def OnAmcacheAnalyzerButtonClick(self, event):
        amcache_reg = ".\\Amcache.hve"  # amcache.hve path 
        results = analyze_amcache(amcache_reg)

        #pop-up reulsts
        amcache_analyze_frame = AmcacheAnalyzerFrame(self, results)
        amcache_analyze_frame.Show()

    def OnTestButtonClick(self, event):
        # 테스트 버튼 클릭 시 호출되는 함수
        test_frame = TestFrame(self)
        test_frame.Show()

    def WINF_button_click(self, event): #cms code
        # Create a new frame for the Windows information
        new_frame = WindowsInfoFrame(None, "Windows Information")
        new_frame.Show()

    def Suvlist_button_click(self, event): #cms code
        app = wx.App(False)
        frame = ServiceInfoFrame(None, title='Service Information', size=(800, 600))

        # Retrieve and load data into the wxPython GUI
        data = frame.retrieve_service_data()
        frame.load_data(data)

        frame.Show()
        app.MainLoop()

    def UserAssist_button_click(self, event): #cms code
        username = getpass.getuser()
        ntuser_path = username + '.NTUSER.DAT'  # Create a Path object

        app = wx.App(False)
        frame = UserAssistParser(ntuser_path, None, title='User Assist Information', size=(800, 600))

        frame.Show()
        app.MainLoop()

    def OnNetworkButtonClick(self, event):
        # 네트워크 버튼 클릭 시 호출되는 함수

        sys_reg = "SYSTEM"
        soft_reg = "SOFTWARE"

        results = network_settings(sys_reg,soft_reg)

        net_frame = NetworkFrame(self,results)
        net_frame.Show()
    
    def OnKeywordButtonClick(self, event):
        # 테스트 버튼 클릭 시 호출되는 함수


        registry_hive = wx.GetTextFromUser("Enter Registry Hive (e.g., SYSTEM):", "Registry Hive", default_value="")
        query = wx.GetTextFromUser("Enter Query:", "Query", default_value="")
        dialog_result = wx.MessageBox("Case Insensitive Search?", "Case Insensitive", wx.YES_NO | wx.CANCEL | wx.ICON_QUESTION)

        if dialog_result == wx.YES:
            case_insensitive = True
        elif dialog_result == wx.NO:
            case_insensitive = False
        else:
    # 사용자가 취소를 누르거나 대화 상자를 닫은 경우
            return

        if registry_hive and query:
        # 결과를 얻어옵니다.
            results = keyword(registry_hive, query, case_insensitive)

            if results:
            # 결과가 있으면 KeywordFrame을 생성하여 결과를 표시합니다.
                keyword_frame = KeywordFrame(self, results)
                keyword_frame.Show()
            else:
                wx.MessageBox("No results found.", "Info", wx.OK | wx.ICON_INFORMATION)
    


    def OnTimelineButtonClick(self, event):
        # 타임라인검색 버튼 클릭 시 호출되는 함수
        net_frame = TimelineFrame(self)
        net_frame.Show()

    def OnMacAddressButtonClick(self, event):
        # 맥어드레스 버튼 클릭 시 호출되는 함수
        net_frame = MacAddressFrame(self)
        net_frame.Show()

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

    def select_path(self, path):
        self._tree.select_path(path)

# installedApplication Frame class 태희님 코드 추가
class InstalledApplicationsFrame(wx.Frame):
    def __init__(self, parent, results):
        super(InstalledApplicationsFrame, self).__init__(parent, title = "설치된 응용프로그램", size = (800, 600))

        #Dataframe 생성 
        df = pd.DataFrame(results)

        #데이터 표시할 테이블 생성 
        grid = wx.grid.Grid(self)
        grid.CreateGrid(df.shape[0], df.shape[1])

        #열 이름 추가 
        for col, col_name in enumerate(df.columns):
            grid.SetColLabelValue(col, col_name)

        #데이터 추가 
        for row in range(df.shape[0]):
            for col in range(df.shape[1]):
                grid.SetCellValue(row, col, str(df.iloc[row,col]))
        # 열 너비 자동 조정 
        grid.AutoSizeColumns()
        
        # 레이아웃 설정 
        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(grid, 1, wx.EXPAND)
        self.SetSizer(sizer)
        self.Centre()

# AmcacheAnalyzerFrame class 태희님 코드 추가 
class AmcacheAnalyzerFrame(wx.Frame):
    def __init__(self, parent, results):
        super(AmcacheAnalyzerFrame, self).__init__(parent, title="Amcache 분석 결과", size=(800, 600))
        panel = wx.Panel(self)

        # 결과를 표시할 테이블 생성
        grid = wx.grid.Grid(panel)
        grid.CreateGrid(len(results), len(results[0]))

        # 열 이름 추가
        for col, col_name in enumerate(results[0].keys()):
            grid.SetColLabelValue(col, col_name)

        # 데이터 추가
        for row, result in enumerate(results):
            for col, value in enumerate(result.values()):
                grid.SetCellValue(row, col, str(value))
        
        # 열 너비 자동 조정 
        grid.AutoSizeColumns()

        # 레이아웃 설정
        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(grid, 1, wx.EXPAND)
        panel.SetSizer(sizer)
        self.Layout()

class TestFrame(wx.Frame):
    def __init__(self, parent):
        # 간단한 테스트 창을 표시하는 클래스
        super(TestFrame, self).__init__(parent, title="테스트 창", size=(300, 200))
        panel = wx.Panel(self)
        text = wx.StaticText(panel, label="이것은 테스트 창입니다!", pos=(10, 10))

class WindowsInfoFrame(wx.Frame):# cms 윈도우 정보창
    def __init__(self, parent, title):
        super(WindowsInfoFrame, self).__init__(parent, title=title, size=(600, 400))

        panel1 = wx.Panel(self)
        grid = wx.grid.Grid(panel1)
        data_series = WindowsInfoHandler.os_settings('software')
        grid.CreateGrid(data_series.shape[0], 2)

        # Add data to the grid
        for i, (index, value) in enumerate(data_series.items()):
            grid.SetCellValue(i, 0, str(index))
            grid.SetCellValue(i, 1, str(value))

        # Hide row and column labels
        grid.HideRowLabels()
        grid.HideColLabels()

        grid.EnableEditing(False)

        for i in range(data_series.shape[0]):
            grid.SetCellBackgroundColour(i, 0, wx.Colour(192, 192, 192))

        # Automatically adjust column sizes
        grid.AutoSizeColumns()

        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(grid, 1, wx.EXPAND)
        panel1.SetSizer(sizer)

        # Fit the frame to the content
        self.Fit()

class ServiceInfoFrame(wx.Frame): #cmd code
    def __init__(self, *args, **kw):
        super(ServiceInfoFrame, self).__init__(*args, **kw)

        self.path = "system"
        self.panel = wx.Panel(self)
        self.create_widgets()

    def create_widgets(self):
        vbox = wx.BoxSizer(wx.VERTICAL)

        # wx.ListCtrl 생성
        self.list_ctrl = wx.ListCtrl(self.panel, style=wx.LC_REPORT | wx.BORDER_SUNKEN)
        self.list_ctrl.InsertColumn(0, 'Service Name', width=150)
        self.list_ctrl.InsertColumn(1, 'Display Name', width=200)
        self.list_ctrl.InsertColumn(2, 'Image Path', width=300)
        self.list_ctrl.InsertColumn(3, 'DLL', width=300)
        self.list_ctrl.InsertColumn(4, 'Description', width=400)

        vbox.Add(self.list_ctrl, 1, flag=wx.EXPAND | wx.ALL, border=10)

        self.panel.SetSizer(vbox)

        # Bind events for header clicks
        for col in range(5):
            self.list_ctrl.Bind(wx.EVT_LIST_COL_CLICK, self.on_header_click, self.list_ctrl, col)

    def load_data(self, data):
        for index, row in data.iterrows():
            index = self.list_ctrl.InsertItem(index, row['service_name'])
            self.list_ctrl.SetItem(index, 1, row['display_name'])
            self.list_ctrl.SetItem(index, 2, row['image_path'])
            self.list_ctrl.SetItem(index, 3, row['dll'])
            self.list_ctrl.SetItem(index, 4, row['description'])

    def retrieve_service_data(self):
        registry = Registry.Registry(self.path)
        select = registry.open("Select")
        current = select.value("Current").value()
        services = registry.open("ControlSet00%d\\Services" % (current))

        data_list = []
        for service in services.subkeys():
            try:
                display_name = service.value("DisplayName").value()
            except:
                display_name = "Null"

            try:
                description = service.value("Description").value()
            except:
                description = "Null"

            try:
                image_path = service.value("ImagePath").value()
            except:
                image_path = "Null"

            try:
                dll = service.subkey("Parameters").value("ServiceDll").value()
            except:
                dll = "Null"

            data_list.append([service.name(), display_name, image_path, dll, description])

        # Create a DataFrame from the list
        data_columns = ['service_name', 'display_name', 'image_path', 'dll', 'description']
        df = pd.DataFrame(data_list, columns=data_columns)

        return df

    def on_header_click(self, event):
        col = event.GetColumn()
        data = self.list_ctrl.GetItemCount()

        items = [(self.list_ctrl.GetItemData(i), self.list_ctrl.GetItem(i, col).GetText()) for i in range(data)]
        items.sort(key=lambda x: x[1], reverse=event.GetSortOrder() == wx.SORT_DESCENDING)

        self.list_ctrl.DeleteAllItems()

        for i, (data, label) in enumerate(items):
            self.list_ctrl.InsertItem(i, label)
            self.list_ctrl.SetItemData(i, data)

class UserAssistParser(wx.Frame): #cms code
    def __init__(self, ntuser_path, *args, **kw):
        super(UserAssistParser, self).__init__(*args, **kw)

        self.ntuser_path = ntuser_path
        self.notebook = wx.Notebook(self)

        # Initialize threading lock
        self.lock = threading.Lock()

        # Create tabs immediately on frame creation
        self.create_tabs()

        # Create a sizer to organize the layout
        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(self.notebook, 1, wx.EXPAND | wx.ALL, 5)
        self.SetSizer(sizer)

    def create_tabs(self):
        ua_dict = self.get_key()
        output_list = self.get_output_list(ua_dict)

        panel = self.MyPanel(self.notebook, output_list)
        self.notebook.AddPage(panel, "User Assist Data")

    def get_key(self):
        pd_list = []
        try:
            reg_hive = Registry.Registry(str(self.ntuser_path))
        except Registry.RegistryParse.ParseException:
            sys.exit(f'\n[x] Wrong file type, regf Signature not found')

        if reg_hive.hive_type().value == 'ntuser.dat':
            try:
                ua_key = reg_hive.open('SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\Explorer\\UserAssist')
            except Registry.RegistryKeyNotFoundException:
                print(f'[x] UserAssist key not found')
            else:
                print(f'\n[+] Found {ua_key}')
                for guid in ua_key.subkeys():
                    if guid.subkey('Count').values():
                        print(f'[+] Found GUID with values: {guid.name()}')
                        print('[+] Parsing values...')
                        for value in guid.subkey('Count').values():
                            pd_dict = {}
                            program = self.resolve_guid(codecs.encode(value.name(), 'rot-13'))
                            parsed_data = self.raw_data_parser(value.value())
                            pd_dict[program] = parsed_data
                            pd_list.append(pd_dict)
            return pd_list
        else:
            print(f'\n{self.ntuser_path.name} is not a NTUSER.DAT file')

    def raw_data_parser(self, data):
        ua_data = []

        if len(data) == 16:  # WinXP
            run_count = struct.unpack("<I", data[4:8])[0]
            run_count -= 5
            focus_count = ''
            focus_time = ''
            ft = struct.unpack("<Q", data[8:])[0]
            last_executed = '' if not ft else self.convert_filetime(ft)
            ua_data.extend([run_count, focus_count, focus_time, last_executed])

        elif len(data) == 72:  # Win7+
            run_count = struct.unpack("<I", data[4:8])[0]
            focus_count = struct.unpack("<I", data[8:12])[0]
            focus_time = str(timedelta(milliseconds=struct.unpack("<I", data[12:16])[0])).split('.')[0]
            ft = struct.unpack("<Q", data[60:68])[0]
            last_executed = '' if not ft else self.convert_filetime(ft)
            ua_data.extend([run_count, focus_count, focus_time, last_executed])

        return ua_data

    def resolve_guid(self, program):
        for key, val in folder_guids.items():
            if key == program.split('\\')[0]:
                resolved = program.replace(key, val)
                return resolved
            else:
                continue
        return program

    def convert_filetime(self, ft):
        EPOCH_AS_FILETIME = 116444736000000000
        HUNDREDS_OF_NANOSECONDS = 10000000
        return datetime.utcfromtimestamp((ft - EPOCH_AS_FILETIME) / HUNDREDS_OF_NANOSECONDS).strftime(
            '%Y-%m-%d %H:%M:%S (UTC)')

    def get_output_list(self, ua_list):
        output_list = []
        for program in ua_list:
            for key, val in program.items():
                if not val:
                    pass
                else:
                    row = [key, val[0], val[1], val[2], val[3]]
                    output_list.append(row)
        return output_list

    class MyPanel(wx.Panel):
        def __init__(self, parent, data_series):
            super(UserAssistParser.MyPanel, self).__init__(parent)

            grid = wx.grid.Grid(self, -1)
            grid.CreateGrid(len(data_series), len(data_series[0]))

            for col, label in enumerate(['Program', 'Run Count', 'Focus Count', 'Focus Time', 'Last Executed']):
                grid.SetColLabelValue(col, label)

            for row, item in enumerate(data_series):
                for col, value in enumerate(item):
                    grid.SetCellValue(row, col, str(value))

            grid.EnableEditing(False)
            grid.EnableCellEditControl(False)

            sizer = wx.BoxSizer(wx.VERTICAL)
            sizer.Add(grid, 1, wx.EXPAND)
            self.SetSizer(sizer)

#영서님 코드 추가
class NetworkFrame(wx.Frame):
    def __init__(self, parent, results):
        super(NetworkFrame, self).__init__(parent, title="TCP/IP", size=(800, 600))
        panel = wx.Panel(self)

        # 결과를 표시할 테이블 생성
        grid = wx.grid.Grid(panel)
        grid.CreateGrid(len(results), len(results[0]))

        # 열 이름 추가
        for col, col_name in enumerate(results[0].keys()):
            grid.SetColLabelValue(col, str(col_name))

        # 데이터 추가
        for row, result in enumerate(results):
            for col, value in enumerate(result.values()):
                grid.SetCellValue(row, col, str(value))
        
        # 열 너비 자동 조정 
        grid.AutoSizeColumns()

        # 레이아웃 설정
        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(grid, 1, wx.EXPAND)
        panel.SetSizer(sizer)
        self.Layout()

class KeywordFrame(wx.Frame):
    def __init__(self, parent, results):
        super(KeywordFrame, self).__init__(parent, title="키워드 검색 결과", size=(800, 600))

        # DataFrame 생성
        df_paths = pd.DataFrame({"Paths": results["Paths"]})
        df_value_names = pd.DataFrame(results["ValueNames"], columns=["Path", "ValueName"])
        df_values = pd.DataFrame(results["Values"], columns=["Path", "ValueName"])

        # 레이아웃 설정
        sizer = wx.BoxSizer(wx.VERTICAL)

        # Paths 표시
        text_paths = wx.StaticText(self, label="Paths")
        sizer.Add(text_paths, 0, wx.ALL, 10)
        grid_paths = wx.grid.Grid(self)
        grid_paths.CreateGrid(df_paths.shape[0], 1)
        grid_paths.SetColLabelValue(0, "Path")
        for row in range(df_paths.shape[0]):
            grid_paths.SetCellValue(row, 0, str(df_paths.iloc[row, 0]))
        sizer.Add(grid_paths, 1, wx.EXPAND | wx.ALL, 10)

        # ValueNames 표시
        text_value_names = wx.StaticText(self, label="Value Names")
        sizer.Add(text_value_names, 0, wx.ALL, 10)
        grid_value_names = wx.grid.Grid(self)
        grid_value_names.CreateGrid(df_value_names.shape[0], df_value_names.shape[1])
        for col, col_name in enumerate(df_value_names.columns):
            grid_value_names.SetColLabelValue(col, col_name)
        for row in range(df_value_names.shape[0]):
            for col in range(df_value_names.shape[1]):
                grid_value_names.SetCellValue(row, col, str(df_value_names.iloc[row, col]))
        sizer.Add(grid_value_names, 1, wx.EXPAND | wx.ALL, 10)

        # Values 표시
        text_values = wx.StaticText(self, label="Values")
        sizer.Add(text_values, 0, wx.ALL, 10)
        grid_values = wx.grid.Grid(self)
        grid_values.CreateGrid(df_values.shape[0], df_values.shape[1])
        for col, col_name in enumerate(df_values.columns):
            grid_values.SetColLabelValue(col, col_name)
        for row in range(df_values.shape[0]):
            for col in range(df_values.shape[1]):
                grid_values.SetCellValue(row, col, str(df_values.iloc[row, col]))
        sizer.Add(grid_values, 1, wx.EXPAND | wx.ALL, 10)

        self.SetSizer(sizer)
        self.Centre()

    
#영서님 코드 추가    
class TimelineFrame(wx.Frame):
    def __init__(self, *args, **kw):
        super(TimelineFrame, self).__init__(*args, **kw, title = "시간 검색")

        self.panel = wx.Panel(self)
        self.create_widgets()

    def create_widgets(self):
        vbox = wx.BoxSizer(wx.VERTICAL)

        # 시간 검색
        hbox1 = wx.BoxSizer(wx.HORIZONTAL)
        after_time_label = wx.StaticText(self.panel, label="입력시간이후 검색(YYYY-MM-DD HH:MM:SS):")
        hbox1.Add(after_time_label, flag=wx.RIGHT, border=8)
        self.after_time_text = wx.TextCtrl(self.panel)
        hbox1.Add(self.after_time_text, proportion=1)
        vbox.Add(hbox1, flag=wx.EXPAND | wx.LEFT | wx.RIGHT | wx.TOP, border=10)

        # 레지스트리 하이브 이름
        hbox2 = wx.BoxSizer(wx.HORIZONTAL)
        registry_hives_label = wx.StaticText(self.panel, label="Registry Hive:")
        hbox2.Add(registry_hives_label, flag=wx.RIGHT, border=8)
        self.registry_hives_text = wx.TextCtrl(self.panel)
        hbox2.Add(self.registry_hives_text, proportion=1)
        vbox.Add(hbox2, flag=wx.EXPAND | wx.LEFT | wx.RIGHT | wx.TOP, border=10)

        # 검색 버튼
        search_button = wx.Button(self.panel, label="Search")
        search_button.Bind(wx.EVT_BUTTON, self.on_search)
        vbox.Add(search_button, flag=wx.EXPAND | wx.LEFT | wx.RIGHT | wx.TOP, border=10)

        self.result_text = wx.TextCtrl(self.panel, style=wx.TE_MULTILINE | wx.TE_READONLY)
        vbox.Add(self.result_text, proportion=1, flag=wx.EXPAND | wx.ALL, border=10)

        self.panel.SetSizer(vbox)

    def on_search(self, event):
        after_time = self.after_time_text.GetValue()
        registry_hives = self.registry_hives_text.GetValue()

        if not after_time or not registry_hives:
            wx.MessageBox("Please fill in all the required fields.", "Error", wx.OK | wx.ICON_ERROR)
            return

        script_path = os.path.join(os.path.dirname(__file__), "time_search.py")
        command = ["python", script_path, "--after", after_time] + registry_hives.split()

        try:
            result = subprocess.check_output(command, stderr=subprocess.STDOUT, text=True)
            self.result_text.SetValue(result)
        except subprocess.CalledProcessError as e:
            self.result_text.SetValue(e.output)

class MacAddressFrame(wx.Frame):
    def __init__(self, *args, **kw):
        super(MacAddressFrame, self).__init__(*args, **kw,title="Mac Address")

        self.panel = wx.Panel(self)
        self.text_ctrl = wx.TextCtrl(self.panel, style=wx.TE_MULTILINE | wx.TE_READONLY, size=(500, 300))

        self.display_mac_info()

        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(self.text_ctrl, 1, wx.EXPAND | wx.ALL, 10)

        self.panel.SetSizerAndFit(sizer)
        self.Show()

    def display_mac_info(self):
        sys_reg = "SYSTEM"  # SYSTEM파일 경로
        try:
            result = subprocess.run(["python", "mac.py", sys_reg], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            output = result.stdout.strip() if result.returncode == 0 else f"Error: {result.stderr.strip()}"
        except Exception as e:
            output = f"An error occurred: {e}"

        self.text_ctrl.SetValue(output)


class RegistryFileViewer(wx.Frame):
    def __init__(self, parent, files):
        # 레지스트리 파일을 표시하는 메인 프레임 클래스
        super(RegistryFileViewer, self).__init__(parent, -1, "RegVision", size=(800, 600))
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
            source_folders = ["C:\\Users\\Default", "C:\\Windows\\appcompat\\Programs",
                              "C:\\Windows\\System32\\config"]

            # 추출할 파일 이름 목록 지정
            file_names = ['NTUSER.DAT', 'COMPONENTS', 'Amcache.hve',
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

        wx.MessageBox(f"Data extracted and saved to '{csv_filename}'", "Extraction Complete")

    def menu_extract_pdf(self, evt):
        pdf_filename = 'extracted_data.pdf'
        for i in range(self._nb.GetPageCount()):
            page = self._nb.GetPage(i)
            if isinstance(page, RegistryFileView):
                data = page.extract_data()
                PDFExporter.export(pdf_filename, data)

        wx.MessageBox(f"Data extracted and saved to '{pdf_filename}'", "Extraction Complete")

    def menu_extract_md(self, evt):
        markdown_filename = 'extracted_data.md'
        for i in range(self._nb.GetPageCount()):
            page = self._nb.GetPage(i)
            if isinstance(page, RegistryFileView):
                page.export_to_markdown(markdown_filename)

        wx.MessageBox(f"Data extracted and saved to '{markdown_filename}'", "Extraction Complete")

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
        dialog = wx.FileDialog(self, "Open Registry File", wildcard=wildcard, style=wx.FD_OPEN | wx.FD_FILE_MUST_EXIST)

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
        about_info.SetWebSite("https://github.com/example/regviewer", "Registry Viewer GitHub Page")
        about_info.SetLicense("MIT License")
        wx.adv.AboutBox(about_info)

if __name__ == '__main__':
    app = wx.App(False)
    filenames = sys.argv[1:]
    frame = RegistryFileViewer(None, filenames)
    frame.Show()
    app.MainLoop()
