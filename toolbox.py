#혁람님 GUI 바탕으로 제가 구현한 module import + class 및 함수 몇개 추가해서 붙였습니다 

from __future__ import print_function
from __future__ import unicode_literals
import sys
import os
import wx
from Registry import Registry
# 추가된 module
import pandas as pd
import wx.grid as girdlib
from installed_application import get_installed_applications # 설치응용프로그램.py import 
from amcache_analyzer import analyze_amcache #amcache 모듈 import

# 각 메뉴 및 탭에 대한 ID 정의
ID_FILE_OPEN = wx.NewIdRef()
ID_FILE_SESSION_SAVE = wx.NewIdRef()
ID_FILE_SESSION_OPEN = wx.NewIdRef()
ID_TAB_CLOSE = wx.NewIdRef()
ID_FILE_EXIT = wx.NewIdRef()
ID_HELP_ABOUT = wx.NewIdRef()


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
            self.SetItemData(subkey_item, {"key": subkey, "has_expanded": False})

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

        # 설치된 응용프로그램 버튼 추가 
        installed_apps_button = wx.Button(panel_2, label="설치된 응용프로그램", pos=(10,80))
        installed_apps_button.Bind(wx.EVT_BUTTON, self.OnInstalledAppsButtonClick)

        # amcache.hve 버튼 추가 
        amcache_analyzer_button = wx.Button(panel_2, label="Amcache.hve", pos=(10,120))
        amcache_analyzer_button.Bind(wx.EVT_BUTTON, self.OnAmcacheAnalyzerButtonClick)

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

    #설치된 응용프로그램 버튼 클릭시 호출되는 함수 
    def OnInstalledAppsButtonClick(self, event):
        soft_reg = ".\\Registry_folder\\SOFTWARE"
        results = get_installed_applications(soft_reg)

        #팝업 창 생성하여 결과 표시 
        installed_apps_frame = InstalledApplicationsFrame(self, results)
        installed_apps_frame.Show()

    def OnAmcacheAnalyzerButtonClick(self, event):
        amcache_reg = ".\\Registry_folder\\Amcache.hve"
        results = analyze_amcache(amcache_reg)

        #pop-up reulsts
        amcache_analyze_frame = AmcacheAnalyzerFrame(self, results)
        amcache_analyze_frame.Show()

class TestFrame(wx.Frame):
    def __init__(self, parent):
        # 간단한 테스트 창을 표시하는 클래스
        super(TestFrame, self).__init__(parent, title="테스트 창", size=(300, 200))
        panel = wx.Panel(self)
        text = wx.StaticText(panel, label="이것은 테스트 창입니다!", pos=(10, 10))


class RegistryFileViewer(wx.Frame):
    def __init__(self, parent, files):
        # 레지스트리 파일을 표시하는 메인 프레임 클래스
        super(RegistryFileViewer, self).__init__(parent, -1, "RegView", size=(800, 600))
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

    def _open_registry_file(self, filename):
        # 주어진 파일에 대한 레지스트리 파일 뷰를 생성하는 함수
        with open(filename, "rb") as f:
            registry = Registry.Registry(f)
            view = RegistryFileView(self._nb, registry=registry, filename=filename)
            self._nb.AddPage(view, basename(filename))
            return view

    def menu_file_open(self, evt):
        # "Open File" 메뉴 항목에 대한 이벤트 핸들러
        dialog = wx.FileDialog(None, "Choose Registry File", "", "", "*", wx.FD_OPEN)
        if dialog.ShowModal() != wx.ID_OK:
            return
        filename = os.path.join(dialog.GetDirectory(), dialog.GetFilename())
        self._open_registry_file(filename)

    def menu_file_exit(self, evt):
        # "Exit Program" 메뉴 항목에 대한 이벤트 핸들러
        sys.exit(0)

    def menu_file_session_open(self, evt):
        # "Open Session" 메뉴 항목에 대한 이벤트 핸들러
        self._nb.DeleteAllPages()

        dialog = wx.FileDialog(None, "Open Session File", "", "", "*", wx.FD_OPEN)
        if dialog.ShowModal() != wx.ID_OK:
            return
        filename = os.path.join(dialog.GetDirectory(), dialog.GetFilename())
        with open(filename, "rb") as f:
            t = f.read()

            lines = t.split("\n")

            if len(lines) % 2 != 1:
                self.SetStatusText("Malformed session file!")
                return

            while len(lines) > 1:
                filename = lines.pop(0)
                path = lines.pop(0)

                view = self._open_registry_file(filename)
                view.select_path(path.partition("\\")[2])

            self.SetStatusText("Opened session")

    def menu_file_session_save(self, evt):
        # "Save Session" 메뉴 항목에 대한 이벤트 핸들러
        dialog = wx.FileDialog(None, "Save Session File", "", "", "*", wx.FD_SAVE)
        if dialog.ShowModal() != wx.ID_OK:
            return
        filename = os.path.join(dialog.GetDirectory(), dialog.GetFilename())
        with open(filename, "wb") as f:
            for i in range(0, self._nb.GetPageCount()):
                page = self._nb.GetPage(i)
                f.write(page.filename() + "\n")

                path = page.selected_path()
                if path:
                    f.write(path)
                f.write("\n")
            self.SetStatusText("Saved session")

    def menu_tab_close(self, evt):
        # "Close" 탭 메뉴 항목에 대한 이벤트 핸들러
        self._nb.RemovePage(self._nb.GetSelection())

    def menu_help_about(self, evt):
        # "About" 도움말 메뉴 항목에 대한 이벤트 핸들러
        wx.MessageBox("regview.py, a part of `python-registry`\n\nhttp://www.williballenthin.com/registry/", "info")

    # def menu_installed_applications(self, evt):
    #     # 설치된 응용프로그램 버튼 클릭 시 실행되는 함수 
    #     soft_reg = ".\\Registry_Folder\\SOFTWARE" # software reg path 
    #     results = get_installed_applications(soft_reg)

    #     #팝업 창 생성하여 결과 표시 
    #     installed_apps_frame = InstalledApplicationsFrame(self, results)
    #     installed_apps_frame.Show()

    # def menu_amcache_analyzer(slef,evt):
    #     # amcache.hve 버튼 클릭 시 실행되는 함수 
    #     amcache_reg = ".\\Registry_folder"


# installedApplication Frame class 
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

        # 레이아웃 설정 
        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(grid, 1, wx.EXPAND)
        self.SetSizer(sizer)
        self.Centre()

# AmcacheAnalyzerFrame class 
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

        # 레이아웃 설정
        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(grid, 1, wx.EXPAND)
        panel.SetSizer(sizer)
        self.Layout()
            
if __name__ == '__main__':
    app = wx.App(False)

    filenames = sys.argv[1:]

    frame = RegistryFileViewer(None, filenames)
    frame.Show()
    app.MainLoop()
