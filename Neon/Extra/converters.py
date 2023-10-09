import time
def time(time):
    hours, remainder = divmod(time, 3600)
    minutes, seconds = divmod(remainder, 60)
    days, hours = divmod(hours, 24)

    text = ''
    if days > 0:
        text += f"{hours} day{'s' if hours != 1 else ''}, "
    if hours > 0:
        text += f"{hours} hour{'s' if hours != 1 else ''}, "
    if minutes > 0:
        text += f"{minutes} minute{'s' if minutes != 1 else ''} and "
    text += f"{seconds} second{'s' if seconds != 1 else ''}"

    return text


def TimeConvert(time):
    pos = ["s","m","h","d"]
    time_dict = {"s" : 1, "m" : 60, "h" : 3600 , "d" : 3600*24}

    unit = time[-1]

    if unit not in pos:
        return -1
    try:
        val = int(time[:-1])
    except:
        return -2

    return val * time_dict[unit]