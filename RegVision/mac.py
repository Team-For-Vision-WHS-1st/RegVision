from __future__ import print_function
from __future__ import unicode_literals
from Registry import Registry
import sys

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

# MAC 주소 정보를 수집하고 출력
def mac_addresses(sys_reg):
    """
    MAC Addresses
    """
    registry = Registry.Registry(sys_reg)
    key_path = r"CurrentControlSet\Control\Class\{4D36E972-E325-11CE-BFC1-08002BE10318}"

    print(("=" * 51) + "\n[+] MAC Addresses\n" + ("=" * 51))

    try:
        with registry.open(key_path) as key:
            for subkey in key.subkeys():
                try:
                    network_address = subkey.value("NetworkAddress").value()
                    print("[-] Adapter InstanceID: %s" % subkey.name())
                    print("[-] MAC Address......: %s" % network_address)
                except Registry.RegistryValueNotFoundException:
                    print("[-] Adapter InstanceID: %s" % subkey.name())
                    print("[-] MAC Address......: N/A (Not found)")
                print("\n")
    except Registry.RegistryKeyNotFoundException:
        print("Error: Registry key not found.")

# SYSTEM hive의 경로를 받아 MAC 주소 정보를 출력
if __name__ == "__main__":
    sys_reg = sys.argv[1]
    print("[+] SYSTEM hive:   %s" % sys_reg)
    print("[+] The system's Control Set is :", control_set_check(sys_reg))
    mac_addresses(sys_reg)
