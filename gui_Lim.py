#민서님 코드에서 제가 추가한 부분이 있는 class들만 가져왔습니다! 
import subprocess
class RegistryFileView(wx.Panel):
    def __init__(self, parent, registry, filename):
        # 추가적인 수직 분할창을 만듭니다.
        self.text2 = wx.StaticText(panel_2, label="ToolBox", pos=(10, 10))
        #test_button = wx.Button(panel_2, label="Test", pos=(10, 50))
        self.text3 = wx.StaticText(panel_2, label="기본도구", pos=(10, 50))
        keyword_button = wx.Button(panel_2, label="keyword_search", pos=(10, 70))
        timeline_button = wx.Button(panel_2, label="timeline_search", pos=(10, 100))
        self.text4 = wx.StaticText(panel_2, label="네트워크 정보", pos=(10, 140))
        network_button = wx.Button(panel_2, label="TCP/IP", pos=(10, 160))
        self.text4 = wx.StaticText(panel_2, label="부가추출 정보", pos=(10, 200))
        mac_button = wx.Button(panel_2, label="맥 어드레스", pos=(10, 220))

        #test_button.Bind(wx.EVT_BUTTON, self.OnTestButtonClick)
        network_button.Bind(wx.EVT_BUTTON, self.OnNetworkButtonClick)
        keyword_button.Bind(wx.EVT_BUTTON, self.OnKeywordButtonClick)
        timeline_button.Bind(wx.EVT_BUTTON, self.OnTimelineButtonClick)
        mac_button.Bind(wx.EVT_BUTTON, self.OnMacAddressButtonClick)

        def OnNetworkButtonClick(self, event):
        # 네트워크 버튼 클릭 시 호출되는 함수
            net_frame = NetworkFrame(self)
            net_frame.Show()
    
        def OnKeywordButtonClick(self, event):
        # 키워드검색 버튼 클릭 시 호출되는 함수
            net_frame = KeywordFrame(self)
            net_frame.Show()

        def OnTimelineButtonClick(self, event):
        # 타임라인검색 버튼 클릭 시 호출되는 함수
            net_frame = TimelineFrame(self)
            net_frame.Show()

        def OnMacAddressButtonClick(self, event):
        # 맥어드레스 버튼 클릭 시 호출되는 함수
            net_frame = MacAddressFrame(self)
            net_frame.Show()

class NetworkFrame(wx.Frame):
    def __init__(self, *args, **kw):
        super(NetworkFrame, self).__init__(*args, **kw, title="네트워크 정보")

        self.panel = wx.Panel(self)
        self.result_text = wx.TextCtrl(self.panel, style=wx.TE_MULTILINE | wx.TE_READONLY, size=(300, 150))

        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(self.result_text, 1, wx.EXPAND | wx.ALL, 30)
        self.panel.SetSizerAndFit(sizer)
        self.Bind(wx.EVT_CLOSE, self.on_close)

        # 아래 두 줄을 추가하여 객체 생성 시 run_network2 함수를 호출.
        self.run_network()
        self.Show()
    

    def run_network(self):
        try:
            result = subprocess.check_output(['python', 'network.py', 'SYSTEM', 'SOFTWARE'], text=True, stderr=subprocess.STDOUT)
            self.result_text.SetValue(result)
        except subprocess.CalledProcessError as e:
            self.result_text.SetValue(f"Error: {e.output}")

    def on_close(self, event):
        self.Destroy()

class KeywordFrame(wx.Frame):
    def __init__(self, *args, **kw):
        super(KeywordFrame, self).__init__(*args, **kw,title="키워드 검색")

        self.InitUI()

    def InitUI(self):
        pnl = wx.Panel(self)

        vbox = wx.BoxSizer(wx.VERTICAL)

        hbox1 = wx.BoxSizer(wx.HORIZONTAL)
        hbox2 = wx.BoxSizer(wx.HORIZONTAL)

        self.registry_label = wx.StaticText(pnl, label='Registry Hive:')
        self.query_label = wx.StaticText(pnl, label='Keyword:')
        self.result_text = wx.TextCtrl(pnl, style=wx.TE_MULTILINE | wx.TE_READONLY, size=(400, 200))

        self.registry_text = wx.TextCtrl(pnl)
        self.query_text = wx.TextCtrl(pnl)
        self.case_insensitive_checkbox = wx.CheckBox(pnl, label='Case Insensitive')

        hbox1.Add(self.registry_label, flag=wx.RIGHT, border=8)
        hbox1.Add(self.registry_text, proportion=1)
        hbox1.Add(self.query_label, flag=wx.LEFT | wx.RIGHT, border=8)
        hbox1.Add(self.query_text, proportion=1)
        hbox1.Add(self.case_insensitive_checkbox, flag=wx.LEFT, border=8)

        vbox.Add(hbox1, flag=wx.EXPAND | wx.LEFT | wx.RIGHT | wx.TOP, border=10)
        vbox.Add((-1, 10))

        hbox2.Add(self.result_text, proportion=1, flag=wx.EXPAND)

        vbox.Add(hbox2, proportion=1, flag=wx.LEFT | wx.RIGHT | wx.EXPAND, border=10)
        vbox.Add((-1, 10))

        search_button = wx.Button(pnl, label='Search', size=(100, 30))
        search_button.Bind(wx.EVT_BUTTON, self.OnSearch)

        vbox.Add(search_button, flag=wx.ALIGN_RIGHT | wx.RIGHT, border=10)

        pnl.SetSizer(vbox)

        self.SetSize((600, 400))
        self.Centre()

    def OnSearch(self, event):
        registry_hive = self.registry_text.GetValue()
        query = self.query_text.GetValue()
        case_insensitive = self.case_insensitive_checkbox.GetValue()

        result = self.run_search(registry_hive, query, case_insensitive)
        self.result_text.SetValue(result)

    def run_search(self, registry_hive, query, case_insensitive):
        command = ['python', 'keyword_search.py', registry_hive, query]
        if case_insensitive:
            command.append('-i')

        process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        output, error = process.communicate()

        if error:
            return f"Error: {error}"

        return output
    
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





