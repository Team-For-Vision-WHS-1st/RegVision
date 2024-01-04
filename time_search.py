#실행 명령어: python time_search.py --after "2023-11-30 00:00:00" SAM 
#옵션으로 주어진 시각 이후에 수정된 키들을 출력 
from __future__ import print_function
from __future__ import unicode_literals

import os
import calendar
import argparse
from datetime import datetime
from Registry import Registry

#주어진 경로에서 가능한 레지스트리 하이브 이름을 추측하는 함수 
def guess_hive_name(path):
    for i in range(len(path)):
        rpath = path[-(i + 1):].lower()
        for guess in ["ntuser", "software", "system", "userdiff", "sam", "default"]:
            if guess in rpath:
                return guess.upper()
#타임라인 정보 생성 
def main():
    parser = argparse.ArgumentParser(
        description="Timeline Windows Registry key timestamps")
    parser.add_argument("--bodyfile", action="store_true",
                        help="Output in the Bodyfile 3 format")
    parser.add_argument("--after", type=str,
                        help="Show keys modified after the specified time (format: 'YYYY-MM-DD HH:MM:SS')")
    parser.add_argument("registry_hives", type=str, nargs="+",
                        help="Path to the Windows Registry hive to process")
    args = parser.parse_args()

    # 사용자가 지정한 시간을 datetime 객체로 변환
    after_time = None
    if args.after:
        after_time = datetime.strptime(args.after, '%Y-%m-%d %H:%M:%S')

    #재귀적으로 특정 키와 그 하위키들을 방문하면서 각 키의 타임스탬프 경로를 visitor함수에게 반환 
    def rec(key, visitor):
        try:
            timestamp = key.timestamp()
            if after_time is None or timestamp >= after_time:#타임스탬프와  사용자가 설정한 시각 비교 
                visitor(timestamp, key.path())
        except ValueError:
            pass
        for subkey in key.subkeys():
            rec(subkey, visitor)

    for filename in args.registry_hives:
        basename = os.path.basename(filename)
        reg = Registry.Registry(filename)  # 이 부분에서 reg 객체 정의 

        #Bodyfile3형식으로 출력할 때는 0으로 채워진 필드를 갖는 형식 
        if args.bodyfile:
            def visitor(timestamp, path):
                try:
                    print("0|[Registry %s] %s|0|0|0|0|0|%s|0|0|0" % \
                        (basename, path, int(calendar.timegm(timestamp.timetuple()))))
                except UnicodeDecodeError:
                    pass

            rec(reg.root(), visitor)
        else:
            items = []
            rec(reg.root(), lambda a, b: items.append((a, b)))
            for i in sorted(items, key=lambda x: x[0]):
                print("%s\t[Registry %s]%s" % (i[0], basename, i[1]))

if __name__ == "__main__":
    main()