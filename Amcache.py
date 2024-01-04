from __future__ import print_function
from __future__ import unicode_literals
from Registry import Registry

import time
import os
import re
import sys
import pandas as pd

def installed_applications(soft_reg):
    registry = Registry.Registry(soft_reg)
    results = []  # 응용프로그램 정보를 담을 리스트

    temp_list = []
    key = registry.open("Root\\InventoryApplicationFile")
    for v in key.subkeys():
        temp_list.append(v.name())

    for temp in temp_list:
        k = registry.open("Root\\InventoryApplicationFile\\%s" % temp)
        application_dict = {}

        for v in k.values():
            if v.name() == "LowerCaseLongPath":
                application_dict['FolderPath'] = v.value()
            if v.name() == "Name":
                application_dict['File Name'] = v.value()
            if v.name() == "Size":
                application_dict['Size'] = v.value()
            if v.name() == "LinkDate":
                application_dict['CreatedTime'] = v.value()
            if v.name() == "LongPathHash":
                application_dict['File Reference Key'] = v.value()
            # if v.name() == "InstallSource":
            #     application_dict['SourcePath'] = v.value()
            # if v.name() == "UninstallString":
            #     application_dict['RemoveCommand'] = v.value()

        results.append(application_dict)

    # 딕셔너리의 리스트를 pandas DataFrame으로 변환
    df = pd.DataFrame(results)

    df.index = df.index + 1

    # DataFrame을 CSV 파일로 저장
    df.to_csv('amcache_output.csv', index=True)

    print("[+] 결과가 amcache_output.csv로 저장되었습니다.")

if __name__ == "__main__":
    amcache = '.\\Registry_Folder\\Amcache.hve' # SOFTWARE 경로 지정 
    print("[+] Amcache Hive : %s" % amcache)
    installed_applications(amcache)
