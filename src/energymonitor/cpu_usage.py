import cpuinfo
import psutil

def get_cpu_info():
    """
    Return info regarding CPU model installed.

    :return: Info regarding CPU model installed
    :rtype: list
    """

    try:
        cpu_info = cpuinfo.get_cpu_info()["brand_raw"]
    except:
        cpu_info= "CPU Info not available"
        
    return [cpu_info]


def get_cpu_usage(seconds):
    """
    Return the average CPU usage over a time interval period.

    :param seconds: Time interval period considered
    :type seconds: float
    :return: CPU usage percentage
    :rtype: float
    """

    try:
        cpu_percentage = psutil.cpu_percent(seconds)
    except:
        cpu_percentage= "CPU usage not available"
        
    return cpu_percentage