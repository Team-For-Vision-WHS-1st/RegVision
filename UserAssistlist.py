import codecs
import struct
import sys
import wx
import wx.grid
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

class MyFrame(wx.Frame):
    def __init__(self, parent, title, data_series):
        super(MyFrame, self).__init__(parent, title=title, size=(400, 300))

        panel = wx.Panel(self)
        grid = wx.grid.Grid(panel, -1)
        
        # Assuming each item in data_series is a list
        grid.CreateGrid(len(data_series), len(data_series[0]))
        
        # Setting column labels Program,Run Count,Focus Count,Focus Time,Last Executed
        for col, label in enumerate(['Program', 'Run Count', 'Focus Count' ,'Focus Time', 'Last Executed']):
            grid.SetColLabelValue(col, label)
        
        # Populating grid with data
        for row, item in enumerate(data_series):
            for col, value in enumerate(item):
                grid.SetCellValue(row, col, str(value))

        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(grid, 1, wx.EXPAND)
        panel.SetSizer(sizer)

        self.Show(True)

if __name__ == '__main__':
    file = input('파일 설정 :')
    #file = 'minse.NTUSER.DAT'
    ntuser_path = Path(file)

    user_assist_parser = UserAssistParser(ntuser_path)
    series_data = user_assist_parser.main()
    
    app = wx.App(False)
    frame = MyFrame(None, "classuserassist정보", series_data)
    app.MainLoop()