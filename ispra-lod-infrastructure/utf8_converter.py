#!/usr/bin/python
# -*- coding: utf-8 -*-

#pip install chardet
#linux iconv -l
import glob
from chardet.universaldetector import UniversalDetector
from pathlib import Path
import os.path

class UTF8Converter():
    
    def __init__(self, input_dir, output_dir):
    	self.__input_dir = input_dir
    	self.__output_dir = output_dir

    def convert(self):
        #fileext = "csv" #estensione del file da processare e codificare in UTF-8
        fileext = "*" # * ==> tutto quello che trova in input-toclean ... estensione del file da processare e codificare in UTF-8
        
        

        detector = UniversalDetector()
        for filename in glob.glob(str(self.__input_dir)+'/*.'+fileext):
            #IDENTIFICA L'ENCODING DEL FILE DI PARTENZA .... encodingfrom=ASCII, encodingfrom=ISO-8859-1, encodingfrom=WINDOWS-1252, ....

            print (filename.ljust(100))
                
            posnomefile=filename.rfind("/") #LINUX ...
            justnomefile=filename[posnomefile+1:]
                
            filenameclean=str(self.__output_dir)+'/'+justnomefile
            detector.reset()
            
            #if not os.path.isfile(filenameclean):
                
                
            with open(filename, 'rb') as infile:
                for line in infile:
                    detector.feed(line)
                    if detector.done: 
                        break
                detector.close()
                #print (detector.result)
                encodingfrom = detector.result['encoding']
                print(encodingfrom)
            # ... CREA I FILE DI ARRIVO APRENDOLI CON L'ENCODING DI PARTENZA encodingfrom (IN MODO DA NON PERDERE INFORMAZIONI)
            #... E CODIFICANDO I NUOVI FILES CON ENCODING PARI A UTF-8

            #posnomefile=filename.rfind("\\") #WINDOWS ...
            
            BLOCKSIZE = 1024*1024
            with open(filename, 'rb') as inf:
                with open(filenameclean, 'wb') as ouf:
                    while True:
                        data = inf.read(BLOCKSIZE)
                        if not data: break
                        converted = data.decode(encodingfrom).encode('utf-8')
                        ouf.write(converted)
            
            
            #with open(filename, mode="r", encoding=encodingfrom) as fr:
            #    data = fr.read()
                
            #with open(filenameclean, mode="w",encoding='UTF-8') as fw:
            #    fw.write(data)
            
            #with open(filenameclean, mode="w",encoding='UTF-8') as fw, open(filename, mode="r", encoding=encodingfrom) as fr:
            #    fw.writelines(l for l in fr)
#            else:
 #               print("File %s already exists in UTF-8 encoding."%(justnomefile))


    def convert_single_file(self, file_to_convert):
    #as convert, but takes only one file

        detector = UniversalDetector()
        filename = os.path.join(self.__input_dir,file_to_convert)

        print (filename.ljust(100))

        posnomefile=filename.rfind("/") #LINUX ...
        justnomefile=filename[posnomefile+1:]
            
        filenameclean=str(self.__output_dir)+'/'+justnomefile
        detector.reset()

        BLOCKSIZE = 1024*1024
        with open(filename, 'rb') as inf:
            with open(filenameclean, 'wb') as ouf:
                while True:
                    data = inf.read(BLOCKSIZE)
                    if not data: break
                    converted = data.decode(encodingfrom).encode('utf-8')
                    ouf.write(converted)
                    
            #print (detector.result)
            encodingfrom = detector.result['encoding']
            print(encodingfrom)
        
        with open(filename, mode="r", encoding=encodingfrom) as fr:
            data = fr.read()
            
        with open(filenameclean, mode="w",encoding='UTF-8') as fw:
            fw.write(data)
    

