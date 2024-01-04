import wx
import wx.grid
import pandas as pd
import time
from Registry import Registry


class WindowsInfo(wx.Frame):
    def __init__(self, parent, title):
        super(WindowsInfo, self).__init__(parent, title=title, size=(400, 300))

        self.notebook = wx.Notebook(self)

        # Add a button to trigger the creation of the tab
        button_panel = wx.Panel(self)
        button = wx.Button(button_panel, label="Show Windows Information", size=(200, 30))
        button.Bind(wx.EVT_BUTTON, self.on_button_click)

        button_sizer = wx.BoxSizer(wx.VERTICAL)
        button_sizer.AddStretchSpacer()
        button_sizer.Add(button, 0, wx.ALIGN_CENTER | wx.ALL, 10)
        button_sizer.AddStretchSpacer()

        button_panel.SetSizer(button_sizer)

        self.sizer = wx.BoxSizer(wx.VERTICAL)
        self.sizer.Add(button_panel, 0, wx.EXPAND)
        self.sizer.Add(self.notebook, 1, wx.EXPAND)

        self.SetSizer(self.sizer)

        self.Center()
        self.Show(True)

    def on_button_click(self, event):
        # Create a panel for the Windows information tab
        panel1 = wx.Panel(self.notebook)
        grid = wx.grid.Grid(panel1)
        data_series = WindowsInfo.os_settings('software')
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

        # Add the panel to the notebook with a label
        self.notebook.AddPage(panel1, "Windows Information")

        # Fit the frame to the content
        self.Fit()

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


if __name__ == '__main__':
    app = wx.App(False)
    frame = WindowsInfo(None, "Window Information")
    app.MainLoop()