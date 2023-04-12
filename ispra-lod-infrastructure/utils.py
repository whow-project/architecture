###Useful functions###

def chunks(lst, n):
    """Yield successive n-sized chunks from lst."""
    for i in range(0, len(lst), n):
        yield lst[i:i + n]


def label_it(dset):
    dset = str(dset)
    if (dset == "soilc"):
        return str("consumo del suolo")
        #return TermUtils.irify("consumo del suolo")
    elif (dset == "urban"):
        return str("aree urbane")
    elif (dset == "pest"):
        return str("pesticidi")
    else:
        return None

def label_en(dset):
    dset = str(dset)
    if (dset == "soilc"):
        return str("soil consumption")
    elif (dset == "urban"):
        return str("urban areas")
    elif (dset == "pest"):
        return str("pesticides")
    else:
        return None