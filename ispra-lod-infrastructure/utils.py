###Useful functions###
import datetime as dt

class Utils:

    def identity(s):
        '''
        Returns same string through urification    
        '''
        return s
    
    def chunks(lst, n):
        """Yield successive n-sized chunks from lst."""
        for i in range(0, len(lst), n):
            yield lst[i:i + n]


    def label_it(dset):
        dset = str(dset.lower())
        if (dset == "soilc"):
            return str("consumo del suolo")
            #return TermUtils.irify("consumo del suolo")
        elif (dset == "urban"):
            return str("aree urbane")
        elif (dset == "bathw"):
            return str("acque di balneazione")
        elif (dset == "pest"):
            return str("pesticidi")
        elif (dset == "marind"):
            return str("IndicatoriMarini")
        elif (dset=="rmn"):
            return str("Rete Mareografica Nazionale")
        elif (dset=="ron"):
            return str("Rete Ondametrica Nazionale")
        else:
            return None

    def label_en(dset):
        dset = str(dset.lower())
        if (dset == "soilc"):
            return str("soil consumption")
        elif (dset == "urban"):
            return str("urban areas")
        elif (dset == "bathw"):
            return str("bathing waters")
        elif (dset == "pest"):
            return str("pesticides")
        elif (dset == "marind"):
            return str("MarineIndicators")
        elif (dset=="rmn"):
            return str("National Tide Gauge Network")
        elif (dset=="ron"):
            return str("National Wave Buoy Network")
        else:
            return None

    def round_coord(coord):
        try:
            value = str(round(float(coord),5))
        except (ValueError, TypeError) as e:
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
    
    def get_xsd_type(s):
        if str(s) == "Number":
            return "xsd:integer"
        else:
            return "xsd:float"