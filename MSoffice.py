# 미완성 코드입니다 
from __future__ import print_function
from __future__ import unicode_literals
from Registry import Registry
import re
import time
import os
import re
import sys
import pandas as pd 

recentDocs_dict = {}
results = []  

def parse_recent_files(value_data):
    try:
        file_list = re.findall(r'<(.+?)>', value_data)
        return file_list
    except UnicodeDecodeError:
        print("Error decoding value data.")
        return None

def recent_File(registry_path):
    registry = Registry.Registry(registry_path)
    key_path = 'SOFTWARE\\Microsoft\\Office\\16.0\\Common\\General'
    key = registry.open(key_path)

    for v in key.values():
        if v.name() == "RecentFiles":
            recent_files_list = parse_recent_files(v.value())
            for file_info in recent_files_list:
                file_info = file_info.split('|')
                file_name = file_info[0]
                file_path = file_info[1]
                last_access_time = int(file_info[2])
                last_access_time = time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime(last_access_time))
                results.append({
                    'File Name': file_name,
                    'File Path': file_path,
                    'Last Access Time': last_access_time
                })

if __name__ == "__main__":
    ntuser_reg = '.\\Registry_Folder\\User.NTUSER.DAT'  # NTUSER.DAT 경로 지정 
    print("[+] NTUSER Hive: %s" % ntuser_reg)
    recent_File(ntuser_reg)

    # Print results
    if results:
        df = pd.DataFrame(results)
        print(df)
    else:
        print("No recent files found.")
