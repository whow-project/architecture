# ISPRA LOD Infrastructure

Dataset-specific processors for converting Italian environmental monitoring data into Linked Open Data (LOD). Each dataset module is a self-contained triplifier that maps CSV source data to RDF using RML mappings, with a shared framework handling configuration, incremental updates, and Virtuoso persistence.

## Usage

```bash
# Process a specific dataset
python rdfizer.py --soil          # Soil consumption
python rdfizer.py --urb           # Urban areas
python rdfizer.py --bathw         # Bathing water quality

# Process and upload to Virtuoso
python rdfizer.py --soil --upload --update

# Use a custom configuration
python rdfizer.py --config path/to/conf.json
```

### CLI Flags

| Flag | Dataset |
|------|---------|
| `-cmn` / `--common` | Common ontology entities |
| `-p` / `--pl` | Place / geographic data (ISTAT) |
| `-s` / `--soil` | Soil consumption |
| `-u` / `--urb` | Urban areas |
| `-e` / `--epe` | Bird ringing (Euring) |
| `-os` / `--ostreopsis` | Algal blooms |
| `-pe` / `--pest` | Pesticides |
| `-bw` / `--bathw` | Bathing water quality |
| `-mi` / `--marind` | Marine indicators |
| `-m` / `--mea` | Measures (RON / RMN / RMLV) |
| `-r` / `--rendis` | RENDIS water monitoring |
| `--upload` | Upload RDF files to remote server via SCP |
| `--update` | Update Virtuoso triplestore (incremental) |
| `--localisql` | Run iSQL commands locally |

## Architecture

```
rdfizer.py                  CLI entry point
  └─► Triplifier            Abstract base class (triplification.py)
       ├─► RONTriplifier     Dataset-specific subclass (ron/ron.py)
       ├─► RMNTriplifier     (rmn/rmn.py)
       ├─► UrbanTriplifier   (urban/urban.py)
       └─► ...
            └─► KnowledgeGraphLoader   RDF persistence (kg_loader.py)
```

### Processing Flow

1. **Initialisation** -- Load `conf.json`, preprocess raw data (UTF-8 conversion)
2. **Triplification** -- Apply RML mappings (Jinja2-templated) to CSV data via pyRML
3. **Diff** -- Compare new graph against previous version, compute added/deleted triples
4. **Persistence** -- Serialize to N-Triples (gzipped), optionally upload to Virtuoso

## Dataset Modules

Each dataset lives in its own directory with a versioned subfolder:

```
ron/
├── ron.py              # RONTriplifier class with custom functions
└── v2/
    ├── conf.json       # Dataset configuration
    ├── dirtydata/      # Raw input CSVs
    ├── data/           # Cleaned CSVs (UTF-8)
    └── rml/            # RML mapping files (.ttl)
```

## Configuration

Each dataset has a `conf.json`:

```json
{
  "dataset": "ron",
  "graph_iri": "https://w3id.org/italia/env/ld/ron/",
  "rdf_dump_file_name": "ron_data",
  "rdf_dump_file_serialisation": "ntriples",
  "data_folder": "data/ron/v2/data",
  "dirty_data_folder": "data/ron/v2/dirtydata",
  "rml_folder": "data/ron/v2/rml",
  "mappings": [
    {
      "rml": "stations_map.ttl",
      "data": [
        { "id": "csv_stations", "file": "stations.csv" }
      ]
    }
  ]
}
```

## Adding a New Dataset

1. Create a directory (e.g. `mydata/v2/`) with `rml/`, `data/`, and `dirtydata/` subdirectories
2. Write RML mappings in `rml/` (Jinja2 templates with `{{ variable }}` placeholders)
3. Create `conf.json` listing the mappings and their input CSV files
4. Subclass `Triplifier`:
   ```python
   from triplification import Triplifier

   class MyDataTriplifier(Triplifier):
       def __init__(self):
           super().__init__('mydata')

       def _dataset_initialisation(self, dirty_data_path, data_path):
           KnowledgeGraphLoader.convert_utf8(dirty_data_path, data_path)
   ```
5. Register the new flag in `rdfizer.py`

