import cpuinfo

def get_cpu_info():
    """
    Return info regarding CPU model installed

    :return: Info regarding CPU model installed.
    :rtype: list
    """

    try:
        cpu_info = cpuinfo.get_cpu_info()["brand_raw"]
    except:
        cpu_info= "CPU Info not available"
        
    return [cpu_info]