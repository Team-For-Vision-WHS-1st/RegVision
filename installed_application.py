# installed_applications.py

from Registry import Registry
import pandas as pd

def get_installed_applications(soft_reg):
    registry = Registry.Registry(soft_reg)
    results = []  # 응용프로그램 정보를 담을 리스트

    temp_list = []
    key = registry.open("Microsoft\\Windows\\CurrentVersion\\Uninstall")
    for v in key.subkeys():
        temp_list.append(v.name())

    for temp in temp_list:
        k = registry.open("Microsoft\\Windows\\CurrentVersion\\Uninstall\\%s" % temp)
        application_dict = {}
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

    return results

if __name__ == "__main__":
    soft_reg = '.\\Registry_Folder\\SOFTWARE'
    results = get_installed_applications(soft_reg)
    for app_dict in results:
        if not app_dict:
            app_dict['Name'] = 'Unknown'
            app_dict.setdefault('Name', 'Unknown')
            app_dict.setdefault('Version', 'Unknown')
            app_dict.setdefault('Publisher', 'Unknown')
            app_dict.setdefault('InstallationPath', 'Unknown')
            app_dict.setdefault('InstallationDate', 'Unknown')
            app_dict.setdefault('SourcePath', 'Unknown')
            app_dict.setdefault('RemoveCommand', 'Unknown')        
        else:
            app_dict.setdefault('Name', 'Unknown')
            app_dict.setdefault('Version', 'Unknown')
            app_dict.setdefault('Publisher', 'Unknown')
            app_dict.setdefault('InstallationPath', 'Unknown')
            app_dict.setdefault('InstallationDate', 'Unknown')
            app_dict.setdefault('SourcePath', 'Unknown')
            app_dict.setdefault('RemoveCommand', 'Unknown')
    df = pd.DataFrame(results)
    df.to_csv('installedApplication_output.csv', index=False)
    print("[+] 결과가 installedApplication_output.csv로 저장되었습니다.")
