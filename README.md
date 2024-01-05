RegVision (English)
===============

<br>
<br>

Introduction
------------
RegVision is a pure Python library that extracts and analyzes Windows registry files. This includes NTUSER.DAT, userdiff, and SOFTWARE. This tool consists of a registry tree interface, a toolbox interface for user convenience, and a Value interface. RegVision still has many shortcomings. Therefore, some errors remain. We plan to fix this, and bug reports and feedback are always welcome. You may change or upgrade the code and functionality of this library.

<br>
<br>

Setup
-----

To use RegVision, the following preliminary work is required.

<br>
<br>

**First**, install the Python module.
### Install reportlab, wxPython, pandas:
`pip install reportlab wxPython pandas`
### Install Registry module
`pip install Registry`

<br>
<br>

**Second**, in the same folder as `RegVision.py`
Extracted registry files such as `Amcache.hve`, `HARDWARE`, `SYSTEM`, `NTUSER.DAT`, `SOFTWARE`
`installed_application.py`, `amcache_analyzer.py`, `time_search.py`, `network.py`, `mac.py`, `keyword_search.py`, and `known_folders.py` must also be in the same folder as `RegVision.py`.

<br>
<br>

Wanted
------
  - Fix
  - Bug reports.
  - Feedback.

RegVision was created for your free Windows registry analysis. Although it is still lacking, I hope you can modify and use it as you wish.

<br>
<br>

License
-------
RegVision is released under the MIT License.

<br>
<br>

Sources
-------
RegVision was created by referring to williballenthin's python-registry. 
Therefore, the source also follows python-registry.

We also inform you that the internal functions are created in-house by our team.

<br>

#### williballenthin's python-registry Sources

Nearly all structure definitions used in python-registry
came from one of two sources:
1) WinReg.txt, by B.H., which may be accessed at:
   http://pogostick.net/~pnh/ntpasswd/WinReg.txt
2) The Windows NT Registry File Format version 0.4, by
   Timothy D. Morgan, which may be accessed at:
   https://docs.google.com/viewer?url=http%3A%2F%2Fsentinelchicken.com%2Fdata%2FTheWindowsNTRegistryFileFormat.pdf
Copies of these resources are included in the
`documentation/` directory of the python-registry source.


The source directory for python-registry contains a `sample/`
subdirectory that contains small programs that use python-registry.
For example, `regview.py` is a read-only clone of Microsoft Window's
Regedit, implemented in a few hundred lines.

<br>
<br>

-----------------------------------------------------

<br>
<br>

RegVision(한국어)
===============

<br>
<br>

소개
------------
RegVision은 Windows 레지스트리 파일을 추출하고 분석하는 순수 Python 라이브러리입니다. 여기에는 NTUSER.DAT, userdiff 및 소프트웨어가 포함됩니다. 이 도구는 레지스트리 트리 인터페이스, 사용자 편의를 위한 도구 상자 인터페이스, 값 인터페이스로 구성됩니다. RegVision에는 여전히 많은 단점이 있습니다. 따라서 일부 오류가 남아 있습니다. 우리는 이 문제를 수정할 계획이며, 버그 보고서와 피드백은 언제나 환영합니다. 이 라이브러리의 코드와 기능을 변경하거나 업그레이드할 수 있습니다.

<br>
<br>

설정
-----

RegVision을 사용하기 위해서는 다음과 같은 사전 작업이 필요합니다.

<br>
<br>

**첫 번째**, Python 모듈을 설치합니다.
### Reportlab, wxPython, Pandas를 설치합니다.
`pip install reportlab wxPython pandas`
### 레지스트리 모듈 설치
`pip 설치 레지스트리`

<br>
<br>

**두 번째**, `RegVision.py`와 동일한 폴더에 있음
`Amcache.hve`, `HARDWARE`, `SYSTEM`, `NTUSER.DAT`, `SOFTWARE`와 같은 추출된 레지스트리 파일
`installed_application.py`, `amcache_analyzer.py`, `time_search.py`, `network.py`, `mac.py`, `keyword_search.py` 및 `known_folders.py`도 같은 폴더에 있어야 합니다. 'RegVision.py'.

<br>
<br>

구함
------
  - 수정.
  - 버그 보고서.
  - 피드백.

RegVision은 무료 Windows 레지스트리 분석을 위해 만들어졌습니다. 아직은 부족하지만 원하시는 대로 수정해서 사용하시길 바라겠습니다.

<br>
<br>

특허
-------
RegVision은 MIT 라이센스에 따라 출시됩니다.

<br>
<br>

출처
-------
RegVision은 williballenthin의 python-registry를 참조하여 만들어졌습니다.
따라서 소스도 python-registry를 따릅니다.

또한 내부 기능은 당사 팀에서 자체적으로 제작함을 알려드립니다.

<br>

#### williballenthin의 python-registry 소스

python-registry에서 사용되는 거의 모든 구조 정의
다음 두 소스 중 하나에서 나왔습니다.
1) B.H.의 WinReg.txt. 다음 위치에서 액세스할 수 있습니다.
   http://pogostick.net/~pnh/ntpasswd/WinReg.txt
2) Windows NT 레지스트리 파일 형식 버전 0.4
   Timothy D. Morgan은 다음 주소에서 액세스할 수 있습니다.
   https://docs.google.com/viewer?url=http%3A%2F%2Fsentinelchicken.com%2Fdata%2FTheWindowsNTRegistryFileFormat.pdf
이러한 리소스의 사본은
python-registry 소스의 `documentation/` 디렉토리.


python-registry의 소스 디렉터리에는 `sample/`이 포함되어 있습니다.
python-registry를 사용하는 작은 프로그램이 포함된 하위 디렉터리입니다.
예를 들어 `regview.py`는 Microsoft Window의 읽기 전용 복제본입니다.
Regedit는 수백 줄로 구현됩니다.
