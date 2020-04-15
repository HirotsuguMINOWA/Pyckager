# Pyckger

## Summary - 要約

A toolchain using Cython, PyInstaller. This can wrap you python code to native machine code. And packing to destribute by PyInstaller.
This code will make prevent leakage of code.

PythonソースコードをNativeCode化して，生成物をPythonソースコードの代わりにパッケージングして配布できるようにするモジュールです.

## Disclaimer-免責
- SUPPLIER DISCLAIMS ALL WARRANTIES NOT EXPRESSLY SET FORTH IN THIS AGREEMENT.
- サプライヤーは、本契約に明記された保証を除くほかは、すべての保証責任を排除する。

## State: DEVELOPPING
- This development is alpha version now. (my source code could be built only)
- This worked on windows(8.1) and mac(10.14.1) @ 2018/11/8.

## Requirement
- Python>3.4.
- Cannot use anaconda. Because the generated bin failed to run, maybe.

## Feature
- python codes are wrapped by native code
  - python files are converted to dynamic link library(.dylib/.so) by cython
  - that makes difficult to read your code (I think, but the fact is ...)

## Usage

1. Install python packages/modules which are requires in your building application
2. Make setup.py as shown below.
```python
from src.main import Pykager

Pykager().build(
    app_name="sample1_cli"
    , path_python_file_include_main_func='sample1_cli_main.py'
    , name_start_method_of_main_python="main"
)
```

## How to make setup.py

1. you muse set below
   1. timeline_headquarter python(=python file called first to run)
   2. [optional] header python file.
   3. entry point: the function to

### Example of setup.py

```mymain.py
def entry_point(): # called function which is 'entrypoint' to start_analysis your program.
    # description you want to do

if __name__=='__main__':
entry_point()
```

## flow to process
Please refer 'doc/design.md' by mermaid viewer. mermaid is javascript. It can see some editor Haroopad.

## short explanation
- tmp_cython.py: script to build your python code convert to dll.



## MEMO

#### vs other solution

##### minifiy
My code after converted occurred error.

##### opy
My code after converted occurred error.

##### Encrpyt



## Troubleshooting


Please test below order.
1. Did all Python packages required from your application were installed into your current used python interpreter?
   2. use one group package either of pypi or of anaconda. In the Python interpreter, pykager may fail.
2. Make PyInstaller packing your app. If cannot, pykager will fail.

# Detail:Disclaimer-免責

## 保証の否認
本Webサイトの使用は、お客様ご自身の責任でなされるものとします。すべての資料、情報、製品、ソフトウェア、プログラムおよびサービスは現状のまま提供され、いかなる保証も適用されません。開発は、適用される法律の許す限りにおいて、法律上の瑕疵担保責任、商品性の保証、特定目的への適合性の保証、権利の不侵害の保証を含むいかなる明示もしくは黙示の保証責任も一切負いません。また 開発者は、本Webサイトが中断しないこと、時事性、安全性、もしくは誤りがないことを保証しません。

お客様は、資料、情報、製品、ソフトウェア、プログラム、またはサービスをダウンロードもしくはその他の手段で取得する場合は、お客様ご自身の判断および責任において行っていただくこと、また、その結果として発生するデータの損失またはお客様のコンピューター・システムへの損傷などのいかなる損害もすべてお客様の責任となることを理解し、同意するものとします。

お客様が本Webサイトの情報を使用すること、または、他のハイパー・リンクされているWebサイトを使用することに起因して発生する直接的損害、間接的損害、偶発的損害、通常の損害、特別の損害あるいはその他の拡大損害 (逸失利益、ビジネスの中断、情報システム上のプログラムおよびデータの損失、情報システムの損失およびその他の損失を含むがこれに限られない) に対するいかなる責任も負いません。



## DISCLAIMER OF WARRANTY
USE OF THIS SITE IS AT YOUR SOLE RISK. ALL MATERIALS, INFORMATION, PRODUCTS, SOFTWARE, PROGRAMS, AND SERVICES ARE PROVIDED "AS IS," WITH NO WARRANTIES OR GUARANTEES WHATSOEVER. DEVELOPER EXPRESSLY DISCLAIMS TO THE FULLEST EXTENT PERMITTED BY LAW ALL EXPRESS, IMPLIED, STATUTORY, AND OTHER WARRANTIES, GUARANTEES, OR REPRESENTATIONS, INCLUDING, WITHOUT LIMITATION, THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE, AND NON-INFRINGEMENT OF PROPRIETARY AND INTELLECTUAL PROPERTY RIGHTS. WITHOUT LIMITATION, DEVELOPER MAKES NO WARRANTY OR GUARANTEE THAT THIS WEB SITE WILL BE UNINTERRUPTED, TIMELY, SECURE, OR ERROR-FREE.

YOU UNDERSTAND AND AGREE THAT IF YOU DOWNLOAD OR OTHERWISE OBTAIN MATERIALS, INFORMATION, PRODUCTS, SOFTWARE, PROGRAMS, OR SERVICES, YOU DO SO AT YOUR OWN DISCRETION AND RISK AND THAT YOU WILL BE SOLELY RESPONSIBLE FOR ANY DAMAGES THAT MAY RESULT, INCLUDING LOSS OF DATA OR DAMAGE TO YOUR COMPUTER SYSTEM.

IN NO EVENT WILL DEVELOPER BE RELIABLE TO ANY PARTY FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY OR CONSEQUENTIAL DAMAGES OF ANY TYPE WHATSOEVER RELATED TO OR ARISING FROM THIS WEB SITE OR ANY USE OF THIS WEB SITE, OR OF ANY SITE OR RESOURCE LINKED TO, REFERENCED, OR ACCESSED THROUGH THIS WEB SITE, OR FOR THE USE OR DOWNLOADING OF, OR ACCESS TO, ANY MATERIALS, INFORMATION, PRODUCTS, OR SERVICES, INCLUDING, WITHOUT LIMITATION, ANY LOST PROFITS, BUSINESS INTERRUPTION, LOST SAVINGS OR LOSS OF PROGRAMS OR OTHER DATA, EVEN IF DEVELOPER ARE EXPRESSLY ADVISED OF THE POSSIBILITY OF SUCH DAMAGES.




