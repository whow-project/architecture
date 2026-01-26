# Architecture and Toolkit

The general goal of the WHOW Toolkit is to enable the creation of a knowledge graph that represents data about water quality and health parameters coming from heterogeneous sources and open data formats that are currently a knowledge soup that can be hardly accessed, queried, interpreted and managed homogeneously. Accordingly, we envision a modular set of tools that can be customised and configured in a decentralised fashion. Originally developed for water quality and health monitoring data under the Connecting European Facility (CEF) Programme (Grant Agreement 2019-EU-IA-0089), the toolkit provides reusable software components for transforming raw data into structured, queryable linked data.

![Alt text](/whow-toolkit/img/modules.png?raw=true "Modules")
![Alt text](/whow-toolkit/img/module-composition.png?raw=true "Module composition")

## Repository Structure

```
architecture/
├── whow-toolkit/              # Core Python toolkit (modules, API, web UI)
├── whow-toolkit-docker/       # Docker Compose orchestration and deployment
└── ispra-lod-infrastructure/  # ISPRA environmental dataset processors
```

| Component | Description |
|-----------|-------------|
| [whow-toolkit](whow-toolkit/) | Core toolkit with modular processing pipeline, REST/WebSocket APIs, and web interface |
| [whow-toolkit-docker](whow-toolkit-docker/) | Containerised deployment with Airflow, Virtuoso, PostgreSQL, and Redis |
| [ispra-lod-infrastructure](ispra-lod-infrastructure/) | Dataset-specific triplifiers for Italian environmental monitoring data (RON, RMN, RENDIS, etc.) |

## Quick Start

### Docker Deployment (recommended)

```bash
cd whow-toolkit-docker
docker compose build
docker compose up -d
```

This starts the following services:

| Service | Port | Description |
|---------|------|-------------|
| WHOW Toolkit | 5000 | Web UI and REST API |
| WebSocket | 8765 | Async component communication |
| Airflow | 8080 | Workflow orchestration UI |
| Virtuoso | 8890 | SPARQL endpoint and RDF store |
| Flower | 5555 | Celery task monitoring |

Default Airflow credentials: `airflow` / `airflow`

### Local Development

```bash
cd whow-toolkit
pip install -e .
cd WHOWToolkit
python whow-tk.py
```

The toolkit runs on `http://localhost:5000` with the WebSocket server on port `8765`.

## Technology Stack

| Category | Technologies |
|----------|-------------|
| Framework | Pelix/iPOPO (OSGi), Flask |
| RDF/Semantic Web | rdflib, pyRML, Owlready2, owlrl, pyshacl |
| Database | Virtuoso 7 (triplestore), PostgreSQL (Airflow metadata) |
| Orchestration | Apache Airflow with CeleryExecutor |
| Infrastructure | Docker, Redis (task broker) |
| Data Processing | chardet, Jinja2, pandas |

## Standards and Vocabularies

The toolkit produces data conforming to:

- **DCAT-AP** - Data Catalog Application Profile for metadata
- **RML** - RDF Mapping Language for data transformation
- **SHACL** - Shapes Constraint Language for validation
- **OWL 2** - Web Ontology Language for reasoning
- **W3C TIME**, **GeoSPARQL**, **WGS84** - Temporal and spatial representation
- **INSPIRE** - Monitoring facilities vocabulary

## Data Quality Assessment

The validator module computes Metadata Quality Assessment (MQA) scores across five dimensions:

- **Findability** - Keywords, themes, categories, spatial/temporal coverage
- **Accessibility** - Download URLs, access services, media types
- **Interoperability** - Controlled vocabularies, standard formats, linked schemas
- **Reusability** - Licensing, provenance, documentation, contact information
- **Contextuality** - Temporal resolution, spatial resolution, file size

## ISPRA Datasets

The `ispra-lod-infrastructure` component provides triplifiers for Italian environmental monitoring datasets:

| Dataset | Description |
|---------|-------------|
| RON | National Wave Network (Rete Ondametrica Nazionale) |
| RMN | National Meteorological Network |
| RENDIS | Water Framework Directive monitoring |
| Urban | Urban environmental and land cover monitoring |
| SoilC | Soil carbon measurements |
| Bathw | Water body bathymetry |
| Pest | Pesticide residue monitoring |
| Land | Land cover and land use |
| Euring | European avian ringing data |
| Ostreopsis | Harmful algal bloom monitoring |
| MarInd | Marine environment indicators |
| Place | Geographic place ontology (ISTAT integration) |

## License

The WHOW Toolkit is licensed under the [Apache License 2.0](https://www.apache.org/licenses/LICENSE-2.0).

## Acknowledgements

This project has been funded under the Connecting European Facility (CEF) Programme of the European Union (Grant Agreement 2019-EU-IA-0089).
