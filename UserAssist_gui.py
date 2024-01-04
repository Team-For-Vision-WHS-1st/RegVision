import codecs
import struct
import sys
import wx
import wx.grid
import threading
from datetime import datetime, timedelta
from Registry import Registry
from pathlib import Path
from known_folders import folder_guids


class UserAssistParser:
    def __init__(self, ntuser_path):
        self.ntuser_path = ntuser_path

    def convert_filetime(self, ft):
        EPOCH_AS_FILETIME = 116444736000000000
        HUNDREDS_OF_NANOSECONDS = 10000000
        return datetime.utcfromtimestamp((ft - EPOCH_AS_FILETIME) / HUNDREDS_OF_NANOSECONDS).strftime(
            '%Y-%m-%d %H:%M:%S (UTC)')

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

    def main(self):
        if self.ntuser_path.is_file():
            ua_dict = self.get_key()
            output_list = self.get_output_list(ua_dict)
            return output_list
        else:
            print(f'\nInvalid file path: {self.ntuser_path}')

class MyPanel(wx.Panel):
    def __init__(self, parent, data_series):
        super(MyPanel, self).__init__(parent)

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
        ntuser_path = self.path  # Update path based on your needs
        user_assist_parser = UserAssistParser(ntuser_path)
        series_data = user_assist_parser.main()

        panel = MyPanel(self.notebook, series_data)
        self.notebook.AddPage(panel, "User Assist Data")

    def on_add_tab(self, event):
        # Create a new tab when the button is clicked
        self.create_tabs()

def main():
    path = 'minse.NTUSER.DAT'  # Set the path externally
    ntuser_path = Path(path)  # Create a Path object

    app = wx.App(False)
    frame = ServiceInfoFrame(ntuser_path, None, title='User Assist Information', size=(800, 600))

    frame.Show()
    app.MainLoop()

if __name__ == '__main__':
    main()