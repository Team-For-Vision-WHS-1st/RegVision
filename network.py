from __future__ import print_function
from __future__ import unicode_literals
from Registry import Registry
import sys
import pandas as pd

# 시스템이 사용 중인 Control set 확인
def control_set_check(sys_reg):
    """
    Determine which Control Set the system was using
    """
    registry = Registry.Registry(sys_reg)
    key = registry.open("Select")
    for v in key.values():
        if v.name() == "Current":
            return v.value()

# 네트워크 설정 정보를 수집하고 출력
def network_settings(sys_reg, soft_reg):
    """
    Network Settings
    """
    registry = Registry.Registry(soft_reg)
    results = []
    key = registry.open("Microsoft\\Windows NT\\CurrentVersion\\NetworkCards")
    print(("=" * 51) + "\n[+] Network Adapters\n" + ("=" * 51))

    # Populate the subkeys containing the NICs information
    nic_list = []
    for v in key.subkeys():
        nic_list.append(v.name())

    for nic in nic_list:
        nics_dict = {}  # 함수 내에서 초기화
        nic_names = []  # 함수 내에서 초기화

        try:
            k = registry.open("Microsoft\\Windows NT\\CurrentVersion\\NetworkCards\\%s" % nic)
            for v in k.values():
                if v.name() == "Description":
                    desc = v.value()
                    nic_names.append(desc)
                if v.name() == "ServiceName":
                    guid = v.value()
            nics_dict['Description'] = nic_names[0] if nic_names else "Unknown"  # 수정된 부분
            nics_dict['ServiceName'] = guid
        except Registry.RegistryKeyNotFoundException:
            nics_dict['Description'] = "Unknown"
            nics_dict['ServiceName'] = "Unknown"

        reg = Registry.Registry(sys_reg)
        key2 = reg.open("ControlSet00%s\\services\\Tcpip\\Parameters\\Interfaces" % control_set_check(sys_reg))
        # Populate the subkeys containing the interfaces GUIDs
        int_list = []
        for v in key2.subkeys():
            int_list.append(v.name())

        # Grab the NICs info based on the above list
        for i in int_list:
            if i.startswith("{"):  # Filter out non-GUID entries
                key3 = reg.open("ControlSet00%s\\services\\Tcpip\\Parameters\\Interfaces\\%s" %
                                (control_set_check(sys_reg), i))
                for v in key3.values():
                    if v.name() == "Domain":
                        nics_dict['Domain'] = v.value()
                    if v.name() == "IPAddress":
                        # Sometimes the IP would end up in a list here so just doing a little check
                        ip = v.value()
                        nics_dict['IPAddress'] = ip[0]
                    if v.name() == "DhcpIPAddress":
                        nics_dict['DhcpIPAddress'] = v.value()
                    if v.name() == "DhcpServer":
                        nics_dict['DhcpServer'] = v.value()
                    if v.name() == "DhcpSubnetMask":
                        nics_dict['DhcpSubnetMask'] = v.value()

                # Just to avoid key errors and continue to do because not all will have these fields
                if not 'Domain' in nics_dict:
                    nics_dict['Domain'] = "N/A"
                if not 'IPAddress' in nics_dict:
                    nics_dict['IPAddress'] = "N/A"
                if not 'DhcpIPAddress' in nics_dict:
                    nics_dict['DhcpIPAddress'] = "N/A"
                if not 'DhcpServer' in nics_dict:
                    nics_dict['DhcpServer'] = "N/A"
                if not 'DhcpSubnetMask' in nics_dict:
                    nics_dict['DhcpSubnetMask'] = "N/A"

                results.append(nics_dict.copy())  # Copy the dictionary to avoid overwriting the same reference

    return results



            

# hive와 software hive의 경로를 받아 네트워크 정보만 출력
if __name__ == "__main__":
    sys_reg = sys.argv[1]
    soft_reg = sys.argv[2]
    
    results = network_settings(sys_reg, soft_reg)
    df = pd.DataFrame(results)
