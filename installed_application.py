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
    print(registry.root().subkeys())
    results = []  # 응용프로그램 정보를 담을 리스트

    temp_list = []
    key = registry.open("Microsoft\\Windows\\CurrentVersion\\Uninstall")
    for v in key.subkeys():
        temp_list.append(v.name())

    for temp in temp_list:
        k = registry.open("Microsoft\\Windows\\CurrentVersion\\Uninstall\\%s" % temp)
        application_dict = {}
        print(k.name())
        for v in k.values():
            if v.name() == "DisplayName" or v.name() == "displayname":
                application_dict['Name'] = v.value()
            if v.name() == "DisplayVersion":
                application_dict['Version'] = v.value()
            if v.name() == "Publisher":
                application_dict['Publisher'] = v.value()
            if v.name() == "InstallLocation":
                application_dict['InstallationPath'] = v.value()
            if v.name() == "InstallDate":
                application_dict['InstallationDate'] = v.value()
            if v.name() == "InstallSource":
                application_dict['SourcePath'] = v.value()
            if v.name() == "UninstallString":
                application_dict['RemoveCommand'] = v.value()
        if not application_dict:
            application_dict['Name'] = k.name()
        results.append(application_dict)

    # 딕셔너리의 리스트를 pandas DataFrame으로 변환
    df = pd.DataFrame(results)

    # DataFrame을 CSV 파일로 저장
    df.to_csv('installedApplication_output.csv', index=False)

    print("[+] 결과가 installedApplication_output.csv로 저장되었습니다.")

if __name__ == "__main__":
    soft_reg = '.\\Registry_Folder\\SOFTWARE' # SOFTWARE 경로 지정 
    print("[+] SOFTWARE Hive : %s" % soft_reg)
    installed_applications(soft_reg)
