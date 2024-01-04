import wx
import pandas as pd
from Registry import Registry

class ServiceInfoFrame(wx.Frame):
    def __init__(self, *args, **kw):
        super(ServiceInfoFrame, self).__init__(*args, **kw)

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

    def load_data(self, data):
        for index, row in data.iterrows():
            index = self.list_ctrl.InsertItem(index, row['service_name'])
            self.list_ctrl.SetItem(index, 1, row['display_name'])
            self.list_ctrl.SetItem(index, 2, row['image_path'])
            self.list_ctrl.SetItem(index, 3, row['dll'])
            self.list_ctrl.SetItem(index, 4, row['description'])


def main():
    app = wx.App(False)
    frame = ServiceInfoFrame(None, title='Service Information', size=(800, 600))
    
    # Your existing code for retrieving data
    path = 'system'
    registry = Registry.Registry(path)
    select = registry.open("Select")
    current = select.value("Current").value()
    services = registry.open("ControlSet00%d\\Services" % (current))

    data_list = []
    for service in services.subkeys():
        try:
            display_name = service.value("DisplayName").value()
        except:
            display_name = "???"

        try:
            description = service.value("Description").value()
        except:
            description = "???"

        try:
            image_path = service.value("ImagePath").value()
        except:
            image_path = "???"

        try:
            dll = service.subkey("Parameters").value("ServiceDll").value()
        except:
            dll = "???"

        data_list.append([service.name(), display_name, image_path, dll, description])

    # Create a DataFrame from the list
    data_columns = ['service_name', 'display_name', 'image_path', 'dll', 'description']
    df = pd.DataFrame(data_list, columns=data_columns)

    # Load data into the wxPython GUI
    frame.load_data(df)

    frame.Show()
    app.MainLoop()

if __name__ == '__main__':
    main()