#configuration_file

#virtuoso
triplestore_host = "127.0.0.1"
triplestore_host_username = "andrea"
triplestore_host_password = "t01:S06:d11_"
triplestore_upload_folder = "/Users/andrea/Documents/CNR/ISPRA/virtuoso_test/upload"
triplestore_delete_folder = "/Users/andrea/Documents/CNR/ISPRA/virtuoso_test/delete"
triplestore_url = "http://localhost:8891/sparql"
triplestore_isql_path = "/Applications/Virtuoso Open Source Edition v7.2.app/Contents/virtuoso-opensource/bin"
odbc_driver = "/Applications/Virtuoso Open Source Edition v7.2.app/Contents/virtuoso-opensource/lib/virtodbc.so"
triplestore_connection_retry_sleep = 60
triplestore_connection_retry_attempts = 5
triplestore_triples_upload_limit=1000


# indicators
indicators_field = {"soilc": "Campo_ID", "urban": "Campo"}

# dataset mappings
dataset_mappings = {
    'indicators/soilc' : 'https://dati.isprambiente.it/ld/soilc',
    'indicators/urban' : 'https://dati.isprambiente.it/ld/urban'
}

# multiprocessing
number_of_processes = 8

