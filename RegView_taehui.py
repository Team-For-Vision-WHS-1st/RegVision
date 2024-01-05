# RegView.py에 제가 추가했던 코드만 보기 편하게 빼놨습니다


# 추가된 module
import pandas as pd
import wx.grid as girdlib
from installed_application import get_installed_applications # 설치응용프로그램.py import 
from amcache_analyzer import analyze_amcache #amcache 모듈 import


# class RegistryFileView(wx.Panel): 에 추가
#    def __init__(self, parent, registry, filename):함수 이하 내용
        # 설치된 응용프로그램 버튼 추가 
        installed_apps_button = wx.Button(panel_2, label="설치된 응용프로그램", pos=(10,80))
        installed_apps_button.Bind(wx.EVT_BUTTON, self.OnInstalledAppsButtonClick)
        # amcache.hve 버튼 추가 
        amcache_analyzer_button = wx.Button(panel_2, label="Amcache.hve", pos=(10,120))
        amcache_analyzer_button.Bind(wx.EVT_BUTTON, self.OnAmcacheAnalyzerButtonClick)

    def OnInstalledAppsButtonClick(self, event):
        soft_reg = ".\\Registry_folder\\SOFTWARE"  \\ software path
        results = get_installed_applications(soft_reg)

        #팝업 창 생성하여 결과 표시 
        installed_apps_frame = InstalledApplicationsFrame(self, results)
        installed_apps_frame.Show()

    def OnAmcacheAnalyzerButtonClick(self, event):
        amcache_reg = ".\\Registry_folder\\Amcache.hve"  \\ amcache.hve path 
        results = analyze_amcache(amcache_reg)

        #pop-up reulsts
        amcache_analyze_frame = AmcacheAnalyzerFrame(self, results)
        amcache_analyze_frame.Show()



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
        # 열 너비 자동 조정 
        grid.AutoSizeColumns()
        
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
        
        # 열 너비 자동 조정 
        grid.AutoSizeColumns()

        # 레이아웃 설정
        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(grid, 1, wx.EXPAND)
        panel.SetSizer(sizer)
        self.Layout()
