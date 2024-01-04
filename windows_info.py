import wx
import wx.grid
import pandas as pd
import time
from Registry import Registry

def os_settings(soft_reg):
    registry = Registry.Registry(soft_reg)
    os_dict = {}
    key = registry.open("Microsoft\\Windows NT\\CurrentVersion")
    for v in key.values():
        if v.name() == "ProductName":
            os_dict['ProductName'] = v.value()
        if v.name() == "ProductId":
            os_dict['ProductId'] = v.value()
        if v.name() == "CSDVersion":
            os_dict['CSDVersion'] = v.value()
        if v.name() == "PathName":
            os_dict['PathName'] = v.value()
        if v.name() == "InstallDate":
            os_dict['InstallDate'] = time.strftime('%a %b %d %H:%M:%S %Y (UTC)', time.gmtime(v.value()))
        if v.name() == "RegisteredOrganization":
            os_dict['RegisteredOrganization'] = v.value()
        if v.name() == "RegisteredOwner":
            os_dict['RegisteredOwner'] = v.value()

    os_series = pd.Series(os_dict, name="OperatingSystem")
    return os_series


class MyFrame(wx.Frame):
    def __init__(self, parent, title, data_series):
        super(MyFrame, self).__init__(parent, title=title, size=(400, 300))

        panel = wx.Panel(self)
        grid = wx.grid.Grid(panel)
        grid.CreateGrid(data_series.shape[0], 2)
        
        # 데이터 추가
        for i, (index, value) in enumerate(data_series.items()):
            grid.SetCellValue(i, 0, str(index))
            grid.SetCellValue(i, 1, str(value))

        # 헤더 및 라벨 숨김
        grid.HideRowLabels()
        grid.HideColLabels()

        grid.EnableEditing(False)

        for i in range(data_series.shape[0]):
            grid.SetCellBackgroundColour(i, 0, wx.Colour(192, 192, 192))

        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(grid, 1, wx.EXPAND)
        panel.SetSizer(sizer)

        self.Show(True)



if __name__ == '__main__':
    # 예제 데이터 생성
    soft_reg = 'software' #sys.argv[2] # software
    series_data = os_settings(soft_reg)


    app = wx.App(False)
    frame = MyFrame(None, "윈도우 정보", series_data)
    app.MainLoop()
