from argparse import ArgumentParser, Namespace

from kg_loader import KnowledgeGraphLoader
from rmn.rmn import RMNTriplifier
from ron.ron import RONTriplifier
from place.place_shp2csv import place_maker
from place.place import placeRDF
from rendis.rendisV2 import RendisTriplifier
from soilc.soilc import SoilcTriplifier
from triplification import TriplificationManager
from urban.urban import UrbanTriplifier


def process(arg_parser: Namespace):
    
    
    triplifiers = []
    
    if args.place:
        #place_maker("data/istat/Limiti01012015.zip")
        print("Preprocessing Complete")
        placeRDF()
        print("Place Complete")
    elif args.measures:
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
                triplifiers.append(triplifier)
            
    elif args.rendis:
        triplifiers.append(RendisTriplifier())
               
    elif args.soil:
        for year in args.soil:
            print(year)
            triplifiers.append(SoilcTriplifier(year))
    elif args.urban:
        for year in args.urban:
            print(year)
            triplifiers.append(UrbanTriplifier(year))

    for triplifier in triplifiers:
        
        '''
        Here we create the TriplificationManager and we optionally set the custom path to the JSON configuration file.
        Such a path is passed by means of the argument -c via command line.
        The path value is stored inside the object args.json_config 
        In case no argument is passed then the default path (e.g. ./soilc/conf.json) is used.
        '''
        triplification_manager = TriplificationManager(triplifier, KnowledgeGraphLoader(), args.json_config)
        #triplification_manager.do_triplification()
        triplification_manager.do_triplification(args.upload)


if __name__ == "__main__":
    arg_parser = ArgumentParser("annual_run.py", description="This script runs ISPRA Data Conversion (annual)")

    arg_parser.add_argument("-p", "--pl", dest="place", nargs='?',
                            const=True, default=False,
                            help="place Conversion")

    arg_parser.add_argument("-i", "--ind", dest="indicators", nargs='?',
                            const=True, default=False,
                            help="Indicators Conversion")
                            
    arg_parser.add_argument("-s", "--soil", dest="soil", nargs='+',
                            default=False,
                            help="Soil consumption Conversion")
                            
    arg_parser.add_argument("-u", "--urb", dest="urban", nargs='+',
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
    
    arg_parser.add_argument("-c", "--config", dest="json_config", required=False, help="Path to JSON configuration file.")

    arg_parser.add_argument("--upload", help="upload the output files on the test server", action="store_true")


    args = arg_parser.parse_args()
    
    process(args)
