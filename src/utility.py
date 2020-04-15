import sys


def check_pyver(compared, base_or_current=None):
    """
    Check to satisfy python ver. if return True, satisfied.
    :param compared:
    :type compared: tuple
    :param base_or_current:
    :type base_or_current: tuple
    :return: true: is eq_grater, false is lesser
    """
    if not base_or_current:
        base_or_current = sys.version_info[0:3]
    cnt = len(compared) if len(compared) < len(base_or_current) else len(base_or_current)
    for i in range(cnt):
        if compared[i] < base_or_current[i]:
            return False
    return True
