from src.main import Pykager

a = Pykager().build(
    app_name="sample1_cli"
    , path_python_file_include_main_func='sample1_cli_main.py'
    , name_start_method_of_main_python="main"
)
