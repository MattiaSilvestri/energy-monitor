import platform

def get_cpu_info():
    """
    Return info regarding CPU model installed

    :return: Info regarding CPU model installed.
    :rtype: str
    """

    try:
        cpu_info = platform.processor()
    except:
        cpu_info = "CPU Info not available"
        
    return cpu_info