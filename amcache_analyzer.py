# amcache_analyzer.py

from Registry import Registry
import pandas as pd

def analyze_amcache(amcache_path):
    # Amcache 데이터를 분석하여 결과를 반환하는 함수
    registry = Registry.Registry(amcache_path)
    results = []

    key = registry.open("Root\\InventoryApplicationFile")
    for subkey in key.subkeys():
        application_dict = {}
        for value in subkey.values():
            if value.name() == "LowerCaseLongPath":
                application_dict['FolderPath'] = value.value()
            elif value.name() == "Name":
                application_dict['File Name'] = value.value()
            elif value.name() == "Size":
                application_dict['Size'] = value.value()
            elif value.name() == "LinkDate":
                application_dict['CreatedTime'] = value.value()
            elif value.name() == "LongPathHash":
                application_dict['File Reference Key'] = value.value()
        results.append(application_dict)

    return results

if __name__ == "__main__":
    amcache_path = '.\\Registry_Folder\\Amcache.hve'  # 실제 Amcache 경로로 수정해야 합니다.
    results = analyze_amcache(amcache_path)

    # 결과를 CSV 파일로 저장
    df = pd.DataFrame(results)
    df.index = df.index + 1
    df.to_csv('amcache_output.csv', index=True)
    print("[+] 결과가 amcache_output.csv로 저장되었습니다.")
