# import src
from src.main import Pykager

a = Pykager().build(
    app_name="sample3_kivy"
    , path_python_file_include_main_func='sample3_kivy_main.py'
    , name_start_method_of_main_python="main"
    # , app_hiddenimports=["tkinter"]  # tkinter is auto include by PyInstaller
    , app_is_onefile=False
    # , _start_method="main"
)
