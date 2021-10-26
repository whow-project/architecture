from argparse import ArgumentParser, Namespace

from kg_loader import KnowledgeGraphLoader
from rmn.rmn import RMNTriplifier
from ron.ron import RONTriplifier
from places.place_shp2csv import place_maker
from places.places import placesRDF
from rendis.rendisV2 import RendisTriplifier
from soilc.soilc import SoilcTriplifier
from triplification import TriplificationManager
from urban.urban import UrbanTriplifier


def process(arg_parser: Namespace):
    if args.places:
        #place_maker("places/input/data_istat/")
        print("Preprocessing Complete")
        placesRDF()
        print("Places Complete")
    if args.measures:
        print("Processing measures...")
        
        if args.dataset:
            print("Found specific dataset: %s"%(args.dataset))
            datasets = [args.dataset]
        else:
            datasets = ['ron', 'rmn']
        
        for dataset in datasets:
            if dataset == 'rmn':
                triplifier = RMNTriplifier()
            elif dataset == 'ron':
                triplifier = RONTriplifier()
            else:
                triplifier = None
                
            if triplifier:
                triplification_manager = TriplificationManager(triplifier, KnowledgeGraphLoader())
                triplification_manager.do_triplification()
        
        '''
        if args.test:
            #f = measuresRDFV2
            triplification_manager = TriplificationManager(RMNTriplifier(), KnowledgeGraphLoader())
            f = triplification_manager.do_triplification
        else:
            f = measuresRDF
        for dataset in datasets:
            print("\t from %s"%(dataset))
            if args.test:
                f()
            else:
                f(dataset=dataset)
            print("%s Complete"%(dataset))
        '''
            
    if args.rendis:
        triplification_manager = TriplificationManager(RendisTriplifier(), KnowledgeGraphLoader())
        triplification_manager.do_triplification()
               
    if args.indicators:
        indicatorsRDF("soilc",  separator=";")
        print("Soilc Complete (Indicators)")
        indicatorsRDF("urban", separator=";")
        print("Indicators Complete")
    else:
        if args.soil:
            for year in args.soil:
                print(year)
                triplification_manager = TriplificationManager(SoilcTriplifier(year), KnowledgeGraphLoader())
                triplification_manager.do_triplification()
        if args.urban:
            #indicatorsRDF("urban", separator=";")
            #print("Urban Area Complete")
            year = args.urban[0]
            triplification_manager = TriplificationManager(UrbanTriplifier(year), KnowledgeGraphLoader())
            triplification_manager.do_triplification()





if __name__ == "__main__":
    arg_parser = ArgumentParser("annual_run.py", description="This script runs ISPRA Data Conversion (annual)")

    arg_parser.add_argument("-p", "--pl", dest="places", nargs='?',
                            const=True, default=False,
                            help="Places Conversion")

    arg_parser.add_argument("-i", "--ind", dest="indicators", nargs='?',
                            const=True, default=False,
                            help="Indicators Conversion")
                            
    arg_parser.add_argument("-s", "--soil", dest="soil", nargs='+',
                            default=False,
                            help="Soil consumption Conversion")
                            
    arg_parser.add_argument("-u", "--urb", dest="urban", nargs=1,
                            default=False,
                            help="Urban area Conversion")

    arg_parser.add_argument("-m", "--mea", dest="measures", nargs='?',
                            const=True, default=False,
                            help="Measures Conversion")
    
    arg_parser.add_argument("-r", "--rendis", dest="rendis", nargs='?',
                            const=True, default=False,
                            help="Rendis Conversion")
                            
    arg_parser.add_argument("-t", "--tes", dest="test", nargs='?',
                            const=True, default=False,
                            help="Testing mode")
                            
    arg_parser.add_argument("-d", "--dat", dest="dataset", required=False, help="Dataset")


    args = arg_parser.parse_args()

    process(args)
