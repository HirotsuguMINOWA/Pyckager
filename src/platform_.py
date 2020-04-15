from src import OSCategory1, OSCategory2

#TODO: In the future, the below class will be implemented into main class Pykager.

class MyPlatform:
    """
    - sys.platformを使う事ができればよいがwineが認識できないため．
    - すべてEnumで返す．strがほしければstr()を使う．これによりdetectedOSの漏れがなくなるのではないか
    """
    __os_cat2 = OSCategory2.unknown

    @property
    def os_cat1(self):
        """
        :rtype: OSCategory1
        """
        if self.__os_cat2 in (OSCategory2.win32, OSCategory2.wine, OSCategory2.cygwin):
            return OSCategory1.windows
        else:
            return OSCategory1.unix

    @property
    def os_cat2(self):
        return self.__os_cat2
        # for item in OSCategory2:  # type: OSCategory2
        #     if item == self.__os_cat2:
        #         return item
        #     else:
        #         raise Exception("Not matched")

    @os_cat2.setter
    def os_cat2(self, os_name):
        if isinstance(os_name, OSCategory2):
            self.__os_cat2 = os_name
        elif isinstance(os_name, str):
            for item in OSCategory2:
                if str(item) == os_name:
                    self.__os_cat2 = item
        else:
            raise Exception("os_cat2 did not recognized")

    # def get_os_name_str(self):
    #     return self.__os_cat2

    def detect_platform(self, set_as_wine=False):
        """

        :return:
        """
        if set_as_wine:
            self.__os_cat2 = OSCategory2.wine  # FIXME: mainへのargsを見れば自動検出できないだろうか
        else:
            self.os_cat2 = sys.platform
            return self.os_cat2
