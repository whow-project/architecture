# WHOW Toolkit

The core Python package providing modular, reusable software components for knowledge graph creation and management. Built on the Pelix/iPOPO component framework, the toolkit uses dynamic service discovery to assemble a processing pipeline that transforms raw data into validated, enriched RDF knowledge graphs.

## Architecture

The toolkit follows a service-oriented architecture where each module is a self-contained Pelix bundle. Modules communicate through two interface patterns:

- **REST API** (HTTP, port 5000) - Synchronous, stateless request/response over standard HTTP methods
- **WebSocket API** (port 8765) - Asynchronous, bidirectional messaging for event-driven workflows

```
WHOWToolkit/
├── api/                  # Core interfaces and data models
├── ingestion/            # Data download and DCAT cataloguing
├── data_cleansing/       # Character encoding detection and normalisation
├── triplifier/           # RML-based RDF mapping
├── metadata/             # DCAT-AP metadata generation
├── validator/            # SHACL validation and MQA scoring
├── reasoners/            # OWL reasoning with Pellet
├── triplestores/         # Virtuoso triplestore management
├── dagfactory/           # Apache Airflow DAG generation
├── web/                  # Flask web application and UI
├── whow-tk.py            # Main entry point
├── flowhow.py            # Airflow DAG definition
└── setup.py              # Package configuration
```

## Entry Point

The toolkit is launched via `whow-tk.py`, which creates a Pelix framework and dynamically discovers and loads all module bundles:

```bash
cd WHOWToolkit
python whow-tk.py
```

The startup sequence:
1. Creates the Pelix/iPOPO framework with shell support
2. Scans each module directory for `*_core.py`, `*_rest.py`, and `*_ws.py` files
3. Installs and starts each bundle in dependency order (core, then REST, then WebSocket)
4. Launches the Flask HTTP server on port 5000 and WebSocket server on port 8765

## Modules

### API (`api/api.py`)

Defines the abstract interfaces and shared data models used by all modules.

**Core Interfaces:**

| Interface | Purpose | Dependencies |
|-----------|---------|-------------|
| `Ingester` | Downloads and catalogues data sources | None |
| `DataPreprocessor` | Cleans and normalises raw data | `Ingester` |
| `Mapper` | Converts data to RDF using RML mappings | `DataPreprocessor` |
| `MetadataCreator` | Generates DCAT-AP metadata | `Mapper` |
| `Validator` | Validates RDF against SHACL shapes | `MetadataCreator` |
| `Reasoner` | Performs OWL reasoning over ontologies | None |
| `TriplestoreManager` | Manages RDF persistence in Virtuoso | `Mapper` |
| `DAGFactory` | Generates Airflow DAGs programmatically | None |

**Data Models:**

| Class | Description |
|-------|-------------|
| `DataSource` | A single data source with ID, filename, and URI reference |
| `DataCollection` | Collection of `DataSource` objects |
| `MapperInput` | Data sources paired with RML mapping configurations |
| `MetadataInput` / `MetadataConf` | DCAT metadata configuration (graph ID, dataset ID, distribution ID) |
| `ValidatorInput` / `ValidatorConfiguration` | SHACL validation targets |
| `DCATCatalog`, `DCATDataset`, `DCATDistribution` | DCAT object model with RDF serialisation |

**Utility Classes:**

| Class | Description |
|-------|-------------|
| `RDFTermFactory` | Parses prefixed URIs (e.g. `dct:title`) and typed literals into rdflib objects |
| `MultiOrderedDict` | OrderedDict supporting duplicate keys (for INI config parsing) |
| `MediaTypeRegistry` | Maps WHOW media type URIs to file extensions |
| `WHOWFlow` | RDF namespace for the WHOW workflow ontology (`https://w3id.org/whow/onto/flow/`) |
| `Configuration` | JSON configuration file loader |

---

### Ingestion (`ingestion/`)

Downloads data distributions from remote URLs and creates a DCAT catalog of ingested data.

**Implementation:** `SimpleIngester` (Pelix component providing `ingester` service)

**Behaviour:**
1. Accepts a DCAT graph describing a catalog with datasets and distributions
2. Downloads each distribution's `accessURL` to the local data folder
3. Assigns UUID-based filenames to avoid conflicts
4. Updates the DCAT catalog TTL file with local references

**Configuration** (`conf/props.json`):
```json
{
  "data.folder": "./ingestion/data/",
  "meta.folder": "./ingestion/meta/",
  "data.catalogue.graph_path": "./ingestion/meta/catalog.ttl",
  "http.endpoint": "http://localhost:5000/data/"
}
```

**API Endpoints:**
- REST: Data management via HTTP
- WebSocket: Async ingestion events

---

### Data Cleansing (`data_cleansing/`)

Detects character encoding of input files and converts them to UTF-8.

**Implementation:** `Cleanser` (Pelix component providing `preprocessor` service)

**Behaviour:**
1. Reads raw bytes from each data source
2. Uses `chardet` to detect the original encoding
3. Decodes and re-encodes as UTF-8
4. Writes cleaned files to the output directory with standardised naming

**Configuration** (`conf/props.json`):
```json
{
  "dirtydata.folder": "./data_cleansing/dirty/",
  "cleandata.folder": "./data_cleansing/clean/"
}
```

---

### Triplifier (`triplifier/`)

Converts structured data (CSV) to RDF graphs using RML (RDF Mapping Language) specifications.

**Implementation:** `PYRMLMapper` (Pelix component providing `mapper` service)

**Behaviour:**
1. Loads RML mapping files (Turtle with Jinja2 template variables)
2. Substitutes template variables (e.g. CSV file paths, dataset identifiers)
3. Applies RML mappings to CSV data using the `pyRML` library
4. Serialises the resulting RDF graph to N-Triples format

**Configuration** (`conf/props.json`):
```json
{
  "rml.folder": "./mappers/rml",
  "graphs.folder": "./mappers/graphs",
  "http.endpoint": "http://localhost:5000/mapper/"
}
```

**RML Template Example:**
```turtle
@prefix rml: <http://semlab.be/ns/rml#> .
@prefix rr: <http://www.w3.org/ns/r2rml#> .

:CSV_SOURCE
  rml:source "{{ csv_file }}" ;
  rml:referenceFormulation ql:CSV ;
  crml:separator ";" .

:StationMapping
  rml:logicalSource :CSV_SOURCE ;
  rr:subjectMap [
    rr:template "https://w3id.org/whow/resource/station/{CODE}"
  ] .
```

---

### Metadata (`metadata/`)

Generates DCAT-AP compliant metadata from INI configuration files.

**Implementation:** `DCATMetadataCreator` (Pelix component providing `metadata_creator` service)

**Behaviour:**
1. Reads an INI configuration file describing dataset and distribution properties
2. Parses prefixed URIs (`dct:title`, `dcat:keyword`) and typed literals
3. Creates an RDF graph with DCAT-AP metadata
4. Outputs metadata in Turtle or N-Triples format

**INI Configuration Example:**
```ini
[dataset]
dct:title = 'Water Quality Monitoring'@en
dct:description = 'Monitoring data for water quality parameters'@en
dcat:keyword = 'water'@en

[distribution]
dcat:accessURL = <https://example.org/data/water-quality.csv>
dct:format = <http://publications.europa.eu/resource/authority/file-type/CSV>
```

---

### Validator (`validator/`)

Validates RDF metadata against SHACL shapes and computes data quality metrics.

**Implementation:** `SHACLValidator` (Pelix component providing `validator` service)

**Behaviour:**
1. Loads DCAT-AP SHACL shape graphs
2. Validates input RDF graphs using `pyshacl`
3. Checks controlled vocabulary compliance against reference vocabularies
4. Computes MQA (Metadata Quality Assessment) scores across five dimensions:
   - **Findability** - Keywords, themes, categories, spatial/temporal metadata
   - **Accessibility** - Download URLs, access services, media types, formats
   - **Interoperability** - Standard vocabularies, linked schemas, controlled lists
   - **Reusability** - License, provenance, documentation, contact info
   - **Contextuality** - Temporal resolution, spatial resolution, file size

**Configuration** (`conf/props.json`):
```json
{
  "shacl.file": "./validator/shacl/dcat-ap-SHACL.ttl",
  "vocabularies.folder": "./validator/vocs",
  "http.endpoint": "http://localhost:5000/validator/"
}
```

---

### Reasoners (`reasoners/`)

Performs OWL reasoning and inference over ontology networks.

**Implementation:** `PelletReasoner` (Pelix component providing `reasoner` service)

**Behaviour:**
1. Loads OWL ontologies using `Owlready2`
2. Runs the Pellet reasoner to derive inferred triples
3. Exports the resulting enriched graph in RDF format

---

### Triplestores (`triplestores/`)

Manages RDF graph persistence in OpenLink Virtuoso.

**Implementation:** `VirtuosoTriplestoreManager` (Pelix component providing `triplestore` service)

**Behaviour:**
1. Connects to Virtuoso via ODBC (`pyodbc`)
2. Loads N-Triples files using Virtuoso's bulk loader (`ld_dir_all`, `rdf_loader_run`)
3. Issues `CHECKPOINT` after loading for durability

**Configuration** (`conf/props.json`):
```json
{
  "graphs.folder": "./mappers/graphs"
}
```

---

### DAG Factory (`dagfactory/`)

Generates Apache Airflow DAGs programmatically from workflow specifications.

**Implementation:** `AirflowDAGFactory` (Pelix component providing `dagfactory` service)

**Behaviour:**
1. Reads a JSON or RDF workflow specification
2. Renders Jinja2 templates to produce Python DAG files
3. Deploys DAGs to Airflow's DAG directory
4. Manages DAG lifecycle via the Airflow REST API

**Configuration** (`conf/props.json`):
```json
{
  "dags.folder": "./dagfactory/dags/",
  "http.endpoint": "http://localhost:5000",
  "website.airflow.endpoint": "http://localhost:8080",
  "airflow.endpoint": "http://host.docker.internal:8080",
  "airflow.user": "airflow",
  "airflow.pwd": "airflow"
}
```

**Workflow Specification Example** (`input.json`):
```json
{
  "id": "my-pipeline",
  "data": [
    {"id": "csv_stations", "filename": "stations.csv", "uri": "https://example.org/stations.csv"}
  ],
  "graphs": [
    {"id": "stations-graph", "rmls": [{"uri": "stations_map.ttl"}]}
  ]
}
```

---

### Web (`web/`)

Flask-based web application providing the user interface and service entry points.

**Implementation:** `webapp.py` with Pelix integration

**Components:**
- `_WebSocketServer` - WebSocket server on port 8765 that routes messages to registered `WebSocketComponent` instances
- `HTTPServer` - HTTP REST server on port 5000 with Blueprint-based routing
- `HomeWeb` - Home page rendering the toolkit description

**Templates:**
- `index.html` - Base template (Bootstrap 4, jQuery, Font Awesome)
- `home.html` - Home page with project description and architecture diagram

## Dependencies

```
rdflib==6.3.2
owlrl==6.0.2
pyrml @ git+https://github.com/anuzzolese/pyrml
iPOPO==1.0.1
shortuuid==1.0.9
Jinja2==3.1.2
Werkzeug==2.2.2
Flask==2.2.2
apache-airflow==2.4.2
pyodbc==5.0.1
owlready2==0.43
oxrdflib==0.3.4
chardet==5.1.0
Cython==0.29.35
requests==2.31.0
pyshacl==0.23.0
```

## Adding a New Module

To create a new module that plugs into the toolkit pipeline:

1. Create a directory under `WHOWToolkit/` (e.g. `mymodule/`)
2. Implement the core logic in `mymodule_core.py` as a Pelix component:
   ```python
   from pelix.ipopo.decorators import ComponentFactory, Provides, Instantiate

   @ComponentFactory("my-module-factory")
   @Provides("my_service")
   @Instantiate("my-module-instance")
   class MyModule:
       def do_job(self, input_data):
           # Processing logic here
           pass
   ```
3. Optionally add `mymodule_rest.py` for REST endpoints and `mymodule_ws.py` for WebSocket handlers
4. Add a `conf/props.json` for module-specific configuration
5. Add the module name to the `modules` list in `whow-tk.py`

The framework will automatically discover and load the new bundle at startup.

## License

Apache License 2.0
