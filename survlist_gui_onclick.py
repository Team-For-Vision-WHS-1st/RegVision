import wx
from Registry import Registry
import threading

class ServiceInfo:
    def __init__(self, service_name, display_name, image_path, dll, description):
        self.service_name = service_name
        self.display_name = display_name
        self.image_path = image_path
        self.dll = dll
        self.description = description

class ServiceInfoFrame(wx.Frame):
    def __init__(self, path, *args, **kw):
        super(ServiceInfoFrame, self).__init__(*args, **kw)

        self.path = path
        self.notebook = wx.Notebook(self)

        # Create a button to add new tabs
        self.addButton = wx.Button(self, wx.ID_ANY, "Add Tab")
        self.Bind(wx.EVT_BUTTON, self.on_add_tab, self.addButton)

        # Create a sizer to organize the layout
        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(self.addButton, 0, wx.ALL | wx.EXPAND, 5)
        sizer.Add(self.notebook, 1, wx.EXPAND | wx.ALL, 5)
        self.SetSizer(sizer)

        # Initialize threading lock
        self.lock = threading.Lock()

    def create_tabs(self):
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

            service_info = ServiceInfo(service.name(), display_name, image_path, dll, description)
            data_list.append(service_info)

        list_ctrl = wx.ListCtrl(self.notebook, style=wx.LC_REPORT | wx.BORDER_SUNKEN)
        list_ctrl.InsertColumn(0, 'Service Name', width=150)
        list_ctrl.InsertColumn(1, 'Display Name', width=200)
        list_ctrl.InsertColumn(2, 'Image Path', width=300)
        list_ctrl.InsertColumn(3, 'DLL', width=300)
        list_ctrl.InsertColumn(4, 'Description', width=400)

        self.load_data(list_ctrl, data_list)
        self.notebook.AddPage(list_ctrl, "All Services")

        # Bind event for header clicks
        list_ctrl.Bind(wx.EVT_LIST_COL_CLICK, self.on_header_click)

    def load_data(self, list_ctrl, data):
        list_ctrl.DeleteAllItems()
        for i, service_info in enumerate(data):
            index = list_ctrl.InsertItem(i, service_info.service_name)
            list_ctrl.SetItem(index, 1, service_info.display_name)
            list_ctrl.SetItem(index, 2, service_info.image_path)
            list_ctrl.SetItem(index, 3, service_info.dll)
            list_ctrl.SetItem(index, 4, service_info.description)

    def on_header_click(self, event):
        col = event.GetColumn()
        # Start a new thread to handle the sorting operation
        threading.Thread(target=self.sort_data, args=(col,), daemon=True).start()

    def sort_data(self, col):
        with self.lock:
            # Lock to prevent race conditions
            data = self.get_data()

            # Sort the data based on the specified column
            data.sort(key=lambda x: getattr(x, self.get_attribute_name(col)))

            # Update the list control with the sorted data
            wx.CallAfter(self.load_data, self.notebook.GetCurrentPage(), data)

    def get_attribute_name(self, col):
        # Map column index to corresponding attribute name
        attribute_names = ['service_name', 'display_name', 'image_path', 'dll', 'description']
        return attribute_names[col]

    def get_data(self):
        # Retrieve the data from the list control
        data = []
        list_ctrl = self.notebook.GetCurrentPage()
        for i in range(list_ctrl.GetItemCount()):
            service_name = list_ctrl.GetItemText(i)
            display_name = list_ctrl.GetItem(i, 1).GetText()
            image_path = list_ctrl.GetItem(i, 2).GetText()
            dll = list_ctrl.GetItem(i, 3).GetText()
            description = list_ctrl.GetItem(i, 4).GetText()

            service_info = ServiceInfo(service_name, display_name, image_path, dll, description)
            data.append(service_info)

        return data

    def on_add_tab(self, event):
        # Create a new tab when the button is clicked
        self.create_tabs()

def main():
    path = 'system'  # Set the path externally
    app = wx.App(False)
    frame = ServiceInfoFrame(path, None, title='Service Information', size=(800, 600))

    frame.Show()
    app.MainLoop()

if __name__ == '__main__':
    main()