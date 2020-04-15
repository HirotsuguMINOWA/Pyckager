#!/usr/bin/env python
# coding: utf8

skip_throw_cython = False

if skip_throw_cython:
    print("[WARNING] Cythonのビルドがスキップに設定されており，合わせてtmpフォルダのcleanもされません")
# 注意: WINEでno left spaceやらエラーでる．
# 原因の１つは,日本語をprintするのはうまくいかない

import logging
from utility import check_pyver

if not check_pyver((3, 5) or not (check_pyver((2, 7) and not check_pyver(3, 0)))):
    logging.warning("This program requires Python version 2.7 or >=3.5")
# from enum import auto
# import enum
# from strenum import StrEnum
from pathlib import Path

import argparse

import os
import shlex
import shutil
import subprocess
import sys

# logging.basicConfig(filename='MOCSupporter.log', level=logging.DEBUG)
logging.basicConfig(level=logging.DEBUG)

# TODO: entry_point.pyを手動で修正する仕組みを作る
# FIXME: timeline_headquater.pyが.pyxの場合，entry_point.pyはcimportを使う必要があると思われる
# TODO: entry_point.pyで無駄な空行を消す
# FIXME: "from.... #日本語コメント" -> error occured on codec(UTF8)となった．つまり#以下は削除するように要修正
# TODO: Cythonでは複数Pythonを1つのlibへまとめられるので，フォルダ階層を考慮してなくて良いかもしれません
# TODO: cythonの中間ファイル(.c,.def)を削除するように調整
# TODO: Src Projectにrequirement.txtが含まれる場合，とりこむ用改良
# FIXME: cythonでdll化するpythonコードをtmp_pythonにコピーしてビルドすること，srcフォルダにごみが残るため
# TODO: timeline_headquater()の代わりのエントリーポイントを変更できる引数をもうける事

import enum

if check_pyver((3, 5)):
    class StrEnumL(str, enum.Enum):
        def __str__(self):
            return self.value

        # pylint: disable=no-self-argument
        # The first argument to this function is documented to be the name of the
        # enum member, not `self`:
        # https://docs.python.org/3.6/library/enum.html#using-automatic-values
        # def _generate_next_value_(name, *_):
        #     return name
else:
    class StrEnumL(str, enum.Enum):
        def __str__(self):
            return self.value

        # pylint: disable=no-self-argument
        # The first argument to this function is documented to be the name of the
        # enum member, not `self`:
        # https://docs.python.org/3.6/library/enum.html#using-automatic-values
        def _generate_next_value_(name, *_):
            return name


class OSCategory1(StrEnumL):
    """
    Classification Major on OS
    """
    windows = "windows"
    unix = "unix"  # posix系,macos ,linux
    unknown = "unknown"


class OSCategory2(StrEnumL):
    """
    Classification Minor on OS
    pythonのsys.platformに従う事．
    class化して詳細を得た方がよさそう
    """
    wine = "wine"
    win32 = "win32"
    win64 = "win64"  # Use?
    windows = "windows"  # Use?
    osx_linux = "osx_linux"
    linux = "linux"
    cygwin = "cygwin"
    darwin = "darwin"
    unknown = "unknown"


class Pykager:

    @property
    def enc_on_os(self):
        """
        setup.pyを作る用にOSに応じたencodingを返す
        :return:
        """

        if self.os_cat2 in [OSCategory2.win32, OSCategory2.win64]:
            return 'cp932'
        else:
            return 'utf8'

    @staticmethod
    def _get_filepath_list(
            path
            , ext
            , excludes=[]
            , debug_mode=False
    ):
        """
        Retrieve file list of indicated path
        :param path:
        :param ext:
        :param excludes:
        :param debug_mode:
        :return:
        """
        if debug_mode:
            print("[Debug] Searching PATH:", path)
        file_list = []
        for (root, dirs, files) in os.walk(path):
            for file in files:
                # パスセパレータは\\より/の方が好きなので置換
                root2, ext_tmp = os.path.splitext(file)
                if not (file in excludes) and ext_tmp == "." + ext:
                    file_list.append(os.path.join(root, file))
                    # file_list.append(file.replace("\\", "/"))
        if debug_mode:
            print("[Debug] Found Path")
            print(file_list)
        return file_list

    @property
    def _ext_lib(self):
        if self.os_cat2 in (OSCategory2.wine, OSCategory2.win32, OSCategory2.win64, OSCategory2.windows):
            return "pyd"
        else:
            return "so"

    def _detect_os(self, is_wine):
        """

        :param is_wine: wine or not
        :type is_wine: bool
        :return:
        """
        # self.os_cat2 = None
        if is_wine:
            self.os_cat2 = OSCategory2.wine
            # self._os_type = 'windows'
        else:
            for cat2 in OSCategory2:
                if cat2 == sys.platform:
                    self.os_cat2 = cat2
                    # return
            # self.os_cat2 = sys.platform  # 'win32', 'linux', 'cygwin', or 'darwin'(mac)
        print("[Debug] OSType:", self.os_cat2)

    @property
    def _newline_for_output(self):
        """ Return newline char according to OS type """
        if self.os_cat1 == OSCategory1.windows:
            return '\r\n'
        elif self.os_cat1 == OSCategory1.unix:
            return '\r'
        else:
            raise SystemError("Failed to detect OS of your system")

    @property
    def _sep4data_bin(self):
        """ generate separator to data and binary """
        if self.os_cat1 == OSCategory1.windows:  # FIXME: 要修正
            return ";"
        elif self.os_cat1 == OSCategory1.unix:
            return ":"
        else:
            raise SystemError("Failed to detect OS of your system")

    def __init__(self):

        # Get initial path
        self._pl_first_wd = Path.cwd()
        self.setup_file_name = "tmp_cython_script.py"  # cythonでのbuild用setup.py
        # pyinstallerで取り込むべきファイルを置くfolder
        self.dir_gen_shared_libs_obsolute = "gen_libs"
        self.dirname_packing_data = "packing_data"
        # FIXME: 元フォルダを汚さないためにnativedll化するpython filesはコピーする事
        # TODO: 生成されたpy->dllはフラットフォルダ構成内にいる事に要注意
        self.cython_dir_copied_python_files = "tmp_copied_python_files"
        # packingにおいてbasedirを初期化するか否か
        self.packing_init_basedir = False
        self._dirname_wcd = "tmp_pykager"

    def build(
            self
            , app_name
            # , target_src_abs_path_obsolute
            , path_python_file_include_main_func
            , name_start_method_of_main_python=""
            , app_hiddenimports=[]
            , app_hiddenimports_to_avoid_trouble=["pkg_resources.py2_warn"]
            , path_header_python_file=""
            , additional_paths_of_python_files=[]  # type:list[str]
            , app_datas=[]
            , app_exclude=[]
            , app_do_clean=True  # FIXME: Trueに固定した方がよい．tmpdirは，処理時に削除，debugのため，異常を含む終了は残しておく
            , is_wine=False
            , app_is_onefile=True
            , do_run_app=True
            , mode_debug=False
            # , is_build_so_lib=True
            # , dir_dist_in_cython="dist_cython"
            , pack_as_app_at_osx_only=False
            , app_upx_enable=False
            , python_ver=3
            , app_is_gui=False
            , app_debug=False
            , cython_one_liblize=False
            , wcd_whole="_pykager"
            , cython_clean_intermidiate=True
            , app_rpath_attach_experimental="."  # important set as "."
    ):
        """
         :param wcd_whole:
         :param cython_clean_intermidiate:
         :param app_rpath_attach_experimental:
         :param app_do_clean:
         :param app_name:
         :param path_python_file_include_main_func: timeline_headquater()を含むappの主となるpythonファイルのpath
         :type path_python_file_include_main_func: str
         :param path_header_python_file: ヘッダーファイル，メインファイルはso化され,from句から始まるファイルも抽出されるがそれでも足りない命令を追記するための仕組み
         :type path_header_python_file: str
         :param target_src_abs_path_obsolute:
         :param app_datas: packageへ含めるデータファイル. list[(inc_dat_path1,place_in_app1),...]
         :type app_datas: list[(str,str)]
         :param is_app_onefile: アプリをonefile化するか否か
         :param mode_debug:
         :param additional_paths_of_python_files: library(dll/so)化したいpython fileのpath. path_python_file_include_main_funcで指定した以外のpython file path.
         :param pack_as_app_at_osx_only: application用にpacking
         :param cython_one_liblize: SharedLib(s)を１つにまとめる. 将来，DefaultをTrueへ
         :return:
         """
        app_hiddenimports.extend(app_hiddenimports_to_avoid_trouble)
        # Run App
        # self.do_run_app = True

        """ timeline_headquater working dir is a path to start_analysis this script"""
        # self.__wcd_default = os.getcwd()

        # self.cython_wcd_dir_obsolute = self._dirname_wcd
        # self.pyinstaller_wcd_dir_obsolute = self._dirname_wcd

        # self.path_wcd = os.path.join(self.__wcd_default, self._dirname_wcd)
        self._ppath_wcd = self._pl_first_wd.joinpath(self._dirname_wcd)
        # self.cython_wcd_path_obsolute = self._ppath_wcd.as_posix() # 下記行へ置換
        self._cython_pwcd = self._ppath_wcd
        # self.pyinstaller_wcd_path_obsolute = self._ppath_wcd.as_posix() # 下記行へ置換
        # self._pyinstaller_pwcd = self._ppath_wcd

        # common
        # self.mode_debug = mode_debug  # FIXME: loggerを使え．
        if path_header_python_file:
            # self.path_header_python_file = self._pl_first_wd.joinpath(path_header_python_file).as_posix()
            self._pl_header_file = self._pl_first_wd.joinpath(path_header_python_file)
        else:
            # self.path_header_python_file = ""
            self._pl_header_file = None

        self._start_method = name_start_method_of_main_python
        self._app_name = app_name
        ## for build_native

        """ app化. Mac OSXのみ """
        # FIXME: generate .app wont work well
        self._pack_as_app_at_osx_only = pack_as_app_at_osx_only
        if self._pack_as_app_at_osx_only:  # if True, run the app by "open -a" cmd
            app_is_gui = app_is_onefile = True

        # """ set path of timeline_headquater python file """
        # self.pathdir_include_main_python_file = target_src_abs_path_obsolute
        # logging.debug("pathdir_include_main_python_file:%s" % self.pathdir_include_main_python_file)

        """ timeline_headquater python file, pyinstallerで必要となる"""
        # TODO: add check the path which indicates python file
        self._ppath_main_python = self._pl_first_wd.joinpath(
            path_python_file_include_main_func)

        """ set pathdir has timeline_headquater python file """
        # self.pathdir_include_main_python_file = os.path.abspath(os.path.dirname(path_python_file_include_main_func))
        logging.debug("path has timeline_headquater python file:%s" % self._ppath_main_python)

        # """ 拡張子なしmain関数を含むPythonファイル名（拡張子を除く）"""
        # self.main_python_filename_without_ext, ext = os.path.splitext(
        #     os.path.basename(self._ppath_main_python))

        """ built .so TrueがDefault """
        # self.is_build_so_lib = is_build_so_lib

        # self.python_version = "3"
        # self.tmp_dir_c_source = "tmp"

        self._pl_packing_data = self._ppath_wcd.joinpath(self.dirname_packing_data)
        # self.path_store_gen_libs = self._ppath_wcd.joinpath(self.dir_gen_shared_libs_obsolute).as_posix()

        ## for src

        # self.working_dir = "tmp_packing"

        # self.filename_app_main = "main_generated.py"
        # self.filename_main_spec = "main_generated.spec"
        ###################################################

        """ proc. skip cython """
        if skip_throw_cython:
            app_do_clean = False

        """ script dir """
        # self.base_script_abs_path = os.path.abspath(os.path.dirname(__file__))

        """ Detect OS """
        self._detect_os(is_wine=is_wine)

        # self.path_sep = os.sep
        # if self.os_cat1== OSType.windows:
        #     self.path_sep = "¥"
        # elif self.os_cat1== OSType.unix:
        #     self.path_sep = "/"
        # else:
        #     raise SystemError("Failed detect OS of your system")

        # """ generate separator to data and binary """
        # _sep4data_bin = ""
        # if self.os_cat1== OSCategory1.windows:
        #     _sep4data_bin = ";"
        # elif self.os_cat1== OSCategory1.unix:
        #     _sep4data_bin = ":"
        # else:
        #     raise Exception("未対応のOS")

        """ Procedures """
        self._gen_shared_lib(
            python_ver=python_ver
            , cython_one_liblize=cython_one_liblize
            , clean_c_files=cython_clean_intermidiate
            , rpath_for_attach=app_rpath_attach_experimental
        )
        self._packaging(
            name=app_name
            , datas=app_datas
            , exclude_modules=app_exclude
            , hiddenimports=app_hiddenimports
            , upx_enable=app_upx_enable
            , python_ver=python_ver
            , do_clean=app_do_clean
            , is_onefile=app_is_onefile
            , is_gui_app=app_is_gui
            , app_debug=app_debug
        )
        # self._copy_gen2wcd(
        #
        # )
        """ copy gen dir to wcd """
        new_path = self._pl_first_wd / self.app_dist
        if new_path.exists():
            shutil.rmtree(new_path.as_posix())

        # if app_is_onefile:
        p_src_dist = self._ppath_wcd / self.app_dist  # / self._app_name

        # shutil.copy(self.p_app.as_posix(), self._pl_first_wd.as_posix())
        # self.p_app = self._ppath_wcd
        # p_src_dist.rename(self.p_app)
        # print("src:%s\ndst:%s" % (p_src_dist.as_posix(), self._pl_first_wd.as_posix()))
        new_path = shutil.move(p_src_dist.as_posix(), self._pl_first_wd.as_posix())

        # temp/dir1/dir_new/
        # self.p_app =Path(new_path
        """ """
        if do_run_app:
            self._app_run(p_app=Path(new_path), is_one_file=app_is_onefile)

    @staticmethod
    def check_encoding(file_path):
        """
        Return encoding of file
        :return: detected encoding name
        """
        from chardet.universaldetector import UniversalDetector
        detector = UniversalDetector()
        with open(file_path, mode='rb') as f:
            logging.info("Detecting codec")
            for binary in f:
                detector.feed(binary)
                if detector.done:
                    break
        detector.close()
        # logging.debug(detector.result, end='')
        # logging.debug(detector.result['encoding'], end='')
        return detector.result['encoding']

    # _os_cat1 = OSCategory1.unknown

    @property
    def os_cat1(self):
        """
        Return os category largely = win?unix?unknown?
        :return:
        :rtype: OSCategory1
        """
        # if self._os_cat1 is None or self._os_cat1 == OSCategory2.unknown:
        if self.os_cat2 in (
                OSCategory2.wine, OSCategory2.win32, OSCategory2.win64, OSCategory2.windows, OSCategory2.cygwin):
            return OSCategory1.windows
        elif self.os_cat2 in (OSCategory2.darwin, OSCategory2.linux):
            return OSCategory1.unix
        else:
            # If detected as unknown, parameters can not be decided.
            raise SystemError("Failed detect OS of your system:%s" % os.name)
            # return OSCategory1.unknown
        # return self._os_cat1

    def _gen_shared_lib(
            self
            # , is_build_so_lib
            , working_dir="tmp_cython"  # FIXME: obsolute and to self.
            , python_ver=3
            , clean_c_files=False
            , build_dir="build_lib"
            , cython_one_liblize=False
            , rpath_for_attach=""
    ):
        """
        CythonでSharedLibsを作る
        :param do_clean: SharedLibs生成フォルダ，ファイルを全て消去
        :param build_dir: ShareLibsを生成するフォルダ
        :param cython_one_liblize: SharedLibを１つにまとめる. 将来，DefaultをTrueへ
        :param rpath_for_attach: The relative path to store lib, data, files
        :return:
        """

        # if is_build_so_lib:

        # ターゲットのpathへ遷移

        # self.cython_wcd_path = os.path.join(self.pathdir_include_main_python_file, working_dir)
        # self.cython_working_path = self.pathdir_include_main_python_file

        if not self._cython_pwcd.exists():
            self._cython_pwcd.mkdir()
        # if do_clean:
        #     shutil.rmtree(self._cython_pwcd.as_posix())
        os.chdir(self._cython_pwcd.as_posix())

        print("[Debug] chdir to :", self._cython_pwcd.as_posix())
        py_src_paths = self._get_filepath_list(self._ppath_main_python.parent.as_posix(),
                                               ext="py")  # FIXME: pyxも含められる用に
        # os.chdir(self.base_script_abs_path)

        """ Remove header python """
        if self._pl_header_file and self._pl_header_file.name in py_src_paths:
            py_src_paths.remove(self._pl_header_file.name)

        for file in py_src_paths:
            if os.path.exists(file):
                print("[Debug] File is exists:", file)
            else:
                print("[Debug] File is not exists:", file)

        if cython_one_liblize:
            # １つの.soへ集約できる．Extentionsクラスを使うから
            setup_py = '''
#cython: language_level={python_ver}, boundscheck=False
from distutils.core import setup
from Cython.Build import cythonize
from distutils.extension import Extension

extensions = [Extension("{app_name}", {py_src_paths})]

setup(
    name="{app_name}",
    ext_modules=cythonize(
        extensions
        # build according to python3
        ,compiler_directives={compiler_directives}
        #, working="{dir_dist_in_cython}"
     )
)
                            '''.strip().format(
                python_ver=python_ver
                , app_name=self._app_name
                , py_src_paths=py_src_paths
                , compiler_directives='{"language_level":%s}' % python_ver
                , dir_dist_in_cython=self.dir_dist_in_cython
            )

        else:

            setup_py = '''
#cython: language_level={python_ver}, boundscheck=False
from distutils.core import setup,Extension
from Cython.Build import cythonize

setup(
    name="{app_name}",
    ext_modules=cythonize(
        {py_src_paths}
        # build according to python3
        , compiler_directives={compiler_directives}
        #, working="{dir_dist_in_cython}"
     )

)
                        '''.strip().format(
                python_ver=python_ver
                , app_name=self._app_name
                , py_src_paths=py_src_paths
                # , compiler_directives="{\"language_level\":%s}" % python_ver
                , compiler_directives='{"language_level":%s}' % python_ver
                , dir_dist_in_cython=self.dir_gen_shared_libs_obsolute
            )

        # print("[Debug] setup_test_code2.py---------------------------")
        # print(setup_py)

        with open(self.setup_file_name, 'w') as f:  # 書き込みモードで開く
            f.write(setup_py)  # 引数の文字列をファイルに書き込む

        """ Detect OS and Build """
        # --inplace: ビルド対象の相対フォルダ(例:src以下)の構造を再現する．本プログラムでは，--inplaceパラはON/OFF両方対応
        # cmd_build_base = "python {0} build_ext --build-lib {1}".format(self.setup_file_name, self.dir_dist_in_cython)
        cmd_build = "python {setup_file_name} build_ext --build-lib {build_lib}".format(
            setup_file_name=self.setup_file_name
            , build_lib=self.dir_gen_shared_libs_obsolute  # cannot abs path.
        )

        if self.os_cat1 == OSCategory1.windows:
            cmd_build = cmd_build + " --compiler=mingw32"

        if not skip_throw_cython:
            print("Building Libraries with Command:", cmd_build)
            args = shlex.split(cmd_build)
            # print("分割コマンド:", args)
            p = subprocess.Popen(args, shell=False)  # Success!
            p.wait()

        """ Clean C files """
        if clean_c_files:
            for pysrc_path in py_src_paths:
                tmp = Path(pysrc_path).with_suffix(".c")
                if tmp.exists():
                    tmp.unlink()
        """
        生成したLibのPATHからPyinstaller用binaries_includeリストを作る
        """
        # if self.os_cat1()==OSType.windows:
        #     common_prefix = os.path.commonprefix(self.path_store_gen_libs) # 前のver.ではこちらを適用
        # elif self.os_cat1()==OSType.unix:
        #     common_prefix = self.path_store_gen_libs
        # else:
        #     raise Exception("PATH落ち")
        # common_prefix = self.path_store_gen_libs  # TODO: common_prefix削除
        # １つ上位のPATHを取得
        # common_prefix = os.path.abspath(os.path.join(common_prefix, os.pardir))
        # common_prefix += "/"

        # common_prefix = common_prefix_childdir

        self.paths_each_gen_libs = self._get_filepath_list(path=self._cython_pwcd.as_posix(), ext=self._ext_lib)
        # gen_lib_filename = [os.path.basename(x) for x in self.paths_each_gen_libs]  # type: list[str]

        # app_dirs_place_libs = [libdir.replace(filename, "") for (libdir, filename) in
        #                        zip(self.paths_each_gen_libs, gen_lib_filename)]

        # 書式： binaries = [("取り込みたいlibPATH","配置したいlibのdir"),...]
        # self.binaries_inc = [
        #     (os.path.join(self.base_script_abs_path, x), os.path.join(".", y.replace(common_prefix, ""))) for (x, y) in
        #     zip(self.path_each_gen_libs, app_dirs_place_libs)]

        # def get_dir_to_set_libs(dir):
        #     """
        #     下記でhiddenimportするライブラリへのPATHを返す
        #     :param dir:
        #     :return:
        #     """
        #     if dir == "":
        #         return "."
        #     else:
        #         return "." + dir

        """ write out parameters '--add-binary'command to plyinstaller """
        # self.binaries_inc_param = ["--add-binary '%s:%s'%s" % (
        #     (os.path.join(self.base_script_abs_path, x)
        #      , get_dir_to_set_libs(y.replace(common_prefix, ""))
        #      ,self._newline_for_output)
        # ) for (x, y) in zip(self.paths_each_gen_libs, app_dirs_place_libs)]
        self.binaries_inc_param = []
        """ write out parameters '--add-binary'command to plyinstaller """
        for a_path_gen_lib in self.paths_each_gen_libs:
            self.binaries_inc_param.append("--add-binary \'%s%s%s\'" % (
                a_path_gen_lib
                , self._sep4data_bin
                , rpath_for_attach))
            # , a_path_gen_lib.replace(common_prefix + self.path_sep, "")))

        logging.debug("parameter:%s" % self.binaries_inc_param)

    def _packaging(
            self
            , name
            , binaries=[]
            , datas=[]
            , hiddenimports=[]
            , exclude_modules=[]
            , upx_enable=False
            # , working_dir="tmp_pyinstaller"
            , mode_debug=True
            , python_ver=3
            , is_onefile=True
            , do_clean=True
            , is_gui_app=False
            , app_debug=False
            , app_dist="dist"
    ):
        """
        １つのファイル/ディレクトリにパッケージング
        :type hiddenimports: list
        :param do_clean: Clean intermediate product or not
        :return: なし
        """

        """ 頻出参照変数生成 """
        self.app_dist = app_dist  # TODO: 任意に変更できるように要修正

        # obsolute_working_path = self._ppath_wcd.as_posix()

        # 空フォルダ生成
        # os.makedirs(obsolute_working_path)
        # os.chdir(obsolute_working_path)
        # self.copy_dest = obsolute_working_path
        # self.copy_dest = self._ppath_wcd.as_posix()

        # フォルダTreeの削除
        # if os.path.exists(obsolute_working_path) and do_clean:
        #     shutil.rmtree(obsolute_working_path)

        self.filename_entry_point = "entry_point.py"
        # self._ppath_entry_point = os.path.join(self._pl_packing_data, self.filename_entry_point)
        self._ppath_entry_point = Path(self._pl_packing_data).joinpath(self.filename_entry_point)

        """ making package dir """
        if not self._pl_packing_data.exists():
            os.mkdir(self._pl_packing_data.as_posix())

        """ making entry_point.py """
        self._codec_main_python_file = self.check_encoding(
            file_path=self._ppath_main_python.as_posix())
        with open(self._ppath_main_python.as_posix(), 'r', encoding=self._codec_main_python_file) as f: # Caution) as_posix() func. requires for python3.5,3.6 or later?
            lines = f.readlines()
            lines_strip = [line.strip() for line in lines]
            dat_from = [line for line in lines_strip if
                        line.startswith('from ') or line.startswith('import ')]  # or '_MEIPASS' in line
            # TODO: コード抽出は行単位であるため，スコープを考慮した抽出に変える必要を要検討
            # TODO: 行冒頭の空白が除去されて書き出されている
            with open(self._ppath_entry_point.as_posix(), mode='w') as to_f: # Caution) as_posix() func. requires for python3.5,3.6 or later?
                if self._pl_header_file and self._pl_header_file.name != "":
                    if not self._pl_header_file.exists():
                        raise Exception("Not found header file")
                    with open(self._pl_header_file, "r") as f_header:
                        lines = f_header.readlines()
                        if lines is not None and lines != "":
                            to_f.write(self._newline_for_output.join(lines) + self._newline_for_output)
                to_f.write(self._newline_for_output.join(dat_from) + self._newline_for_output)
                """ add entry point """
                # to_f.write("if hasattr(sys, \"_MEIPASS\"):")
                # to_f.write("    sys._MEIPASS")
                if self._start_method:
                    to_f.write("from %s import %s%s" % (
                        self._ppath_main_python.stem, self._start_method, self._newline_for_output))
                    to_f.write("%s()%s" % (self._start_method, self._newline_for_output))
                else:
                    # No indicate entry_point
                    to_f.write("import %s%s" %
                               (self._ppath_main_python.stem, self._newline_for_output)
                               )

        #         main_py = """
        # from {main_python_filename_without_ext} import timeline_headquater
        # timeline_headquater()
        #         """.strip().format(
        #             # encoding=self.enc_on_os()
        #             main_python_filename_without_ext=self.main_python_filename_without_ext
        #         )
        #
        #         f = open(self.filename_app_main, 'w', encoding=self.enc_on_os())  # 書き込みモードで開く
        #         # f = open(filename_app_main, 'w')  # 書き込みモードで開く
        #         f.write(main_py)  # 引数の文字列をファイルに書き込む
        #         f.close()  # ファイルを閉じる

        """
        Make parameter for cui command of PyInstaller
        """
        cmd_build = "pyinstaller"

        """ Add binaries """
        for x in self.binaries_inc_param:
            cmd_build += " " + x

        # """ add binaries """
        # if binaries is None:
        #     binaries = []
        #
        # """ add generated libs """
        # paths_gen_lib = self._get_filepath_list(self.path_store_gen_libs, ext=self._ext_lib())
        # FIXME: 下記フラット構造しか対応してない

        #
        # for a_path in paths_gen_lib:
        #     binaries.append([a_path, "."])

        # for x in binaries:  # TODO: functionize
        #     cmd_build += "  --add-binary '{path_include}{data_separator}{dir_place}'".format(path_include=x[0],
        #                                                                                      data_separator=_sep4data_bin,
        #                                                                                      dir_place=x[1])

        for x in hiddenimports:
            # cmd_build += " --hidden-import=%s%s" % (x, self._newline_for_output)
            cmd_build += " --hidden-import=%s" % x

        for x in exclude_modules:
            cmd_build += " --exclude-module %s" % x

        def get_operator_data_or_binary(cmd_building, ope, binaries_or_datas):
            """
            parameter of data and binary for CUI of pyInstaller
            :param ope:
            :type ope:str
            :param binaries_or_datas:[[path of lib,dir_to_set_lib],[...]]
            :type binaries_or_datas:[[]]
            :return:
            """
            # res = ""
            if binaries_or_datas is None or len(binaries_or_datas) == 0:
                return cmd_building
            for x in binaries_or_datas:
                cmd_building += " {operator} '{path_include}{data_separator}{dir_place}' ".format(
                    operator=ope,
                    path_include=x[0],
                    data_separator=self._sep4data_bin,
                    dir_place=x[1])
            return cmd_building

        """ add 'data's and 'binaries' from indicated parameter """
        cmd_build = get_operator_data_or_binary(cmd_build, "--add-data", datas)
        cmd_build = get_operator_data_or_binary(cmd_build, "--add-binary", binaries)

        if is_onefile:
            cmd_build += " --onefile"

        if is_gui_app:
            cmd_build += " --windowed"  # -w, --windowed, --noconsoleは同義．別途，コマンドプロンプトが現れない、エラーを除く。

        if app_debug:
            cmd_build += " --debug"

        if upx_enable:
            cmd_build += " --upx"
        else:
            cmd_build += " --noupx"
        # if do_clean:
        #    cmd_build += " --clean -y"  # -y: outputフォルダ削除確認にyesを引き渡す？

        cmd_build += " -n %s" % name

        # if self.os_cat1== OSType.windows:
        #     cmd_build += " '%s'" % self._ppath_entry_point
        # elif self.os_cat1== OSType.unix:
        #     cmd_build += " '%s'" % self._ppath_entry_point
        # else:
        #     raise Exception("Out of expected OSType")
        cmd_build += " '%s'" % self._ppath_entry_point  # ''でくくった方が安定してpyinstallerが起動する

        print("src CMD:", cmd_build)
        """ write out log to confirm """
        with open("pyinstaller_parameter.log", "w", encoding=self.enc_on_os) as f:
            f.write(cmd_build)

        args = shlex.split(cmd_build)
        # print(":", args)
        p = subprocess.Popen(args, shell=False)  # Success!
        p.wait()

    def _app_run(self
                 , p_app
                 , is_one_file):
        """
        run the generated app
        :param p_app: Path of the generated application
        :type p_app: Path
        :param is_one_file: the app is summarized into one file or not.
        :type is_one_file:bool
        """
        logging.info("Running generated app-----------------------------------------------------------")

        # FIXME: binaryが生成されているか確認するコードを書こう

        if is_one_file:
            cmd = (p_app / self._app_name).as_posix()
        else:
            cmd = (p_app / self._app_name / self._app_name).as_posix()

        if self._pack_as_app_at_osx_only:
            # .specにapp化したときの実行
            cmd = "open -a %s" % cmd

        if self.os_cat2 == "wine":
            cmd = "wine %s" % cmd

        logging.debug("Running Command: %s" % cmd)
        args = shlex.split(cmd)
        p_app = subprocess.Popen(args, shell=True)  # Success!
        p_app.wait()


def entry_point_cli():
    """
    this is call from CLI command
    :return:
    """
    raise NotImplementedError("Called timeline_headquater entry. Un-implemeneted")
    # FIXME: ここで引数の解析を実施．./pykagerでコマンドを実行できる
