#configuration_file

#virtuoso
triplestore_host = "127.0.0.1"
triplestore_host_username = "username"
triplestore_host_password = ""
triplestore_upload_folder = "./upload"
triplestore_delete_folder = "./delete"
triplestore_url = "http://localhost:8891/sparql"
triplestore_isql_path = "/virtuoso-opensource/bin"
odbc_driver = "/virtuoso-opensource/lib/virtodbc.so"
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

