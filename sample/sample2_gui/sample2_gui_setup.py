from src.main import Pykager

a = Pykager().build(
    app_name="sample2_gui"
    , path_python_file_include_main_func='sample2_gui_main.py'
    , app_hiddenimports=["tkinter"]  # tkinter is auto include by PyInstaller
    # , app_is_onefile=False
    # , _start_method="main"
)
