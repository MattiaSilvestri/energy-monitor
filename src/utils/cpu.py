import cpuinfo
import psutil

def get_cpu_info():
    """
    Return info regarding CPU model installed.

    :return: Info regarding CPU model installed
    :rtype: str
    """

    try:
        cpu_info = cpuinfo.get_cpu_info()["brand_raw"]
    except:
        cpu_info= "CPU Info not available"
        
    return cpu_info


def get_cpu_usage(seconds):
    """
    Return the average CPU usage over a time interval period.

    :param seconds: Time interval period considered
    :type seconds: float
    :return: CPU usage percentage
    :rtype: float or None
    """

    try:
        cpu_percentage = psutil.cpu_percent(seconds)
    except:
        cpu_percentage= None
        
    return cpu_percentage

def get_cpu_tdp():
    """
    Mock function to be replaced soon.

    :return: CPU Thermal Design Power (TDP) in watts
    :rtype: int
    """
        
    return 15