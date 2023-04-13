###Useful functions###
import datetime as dt

class Utils:

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

    def round_coord(coord):
        try:
            value = str(round(float(coord),5))

        except ValueError:
            value = str(coord)

        return value

    def capitalize(s):
        return str(s).capitalize()

    def upper(s):
        return str(s).upper()

    def lower(s):
        return str(s).lower()

    def title(s):
        return str(s).title()

    def replace(find, rep, string):
        s = string.replace(find, rep)
        return s 

    def getYearMonth(date):
        try:
            result = dt.datetime.strptime(date, '%Y-%m-%dT%H:%M:%SZ')
        except ValueError:
            result = dt.datetime(1300,1,1)

        result = (format(result.year, '04d') + '-' + format(result.month, '02d'))

        return result