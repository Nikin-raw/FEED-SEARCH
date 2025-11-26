# XML Feed Analyzer

[🇪🇸 Español](#español) | [🇬🇧 English](#english)

---

## Español

### Herramienta para analizar feeds XML y buscar información sobre jobs y teams.

### 📋 Características

- ✅ Analiza todos los archivos XML en la carpeta `XMLFEEDS` en bulk
- ✅ Busca todos los jobs de un team específico (y los cuenta)
- ✅ Busca un job específico de un team específico
- ✅ Maneja diferentes identificadores para teams (company ID, company name, team identifier)
- ✅ Maneja diferentes identificadores para jobs (job ID, reference ID, job name)
- ✅ Búsqueda flexible (case-insensitive y por coincidencia parcial)
- ✅ Resumen de jobs agrupados por team

### 🚀 Uso

#### 1. Buscar todos los jobs de un team

```bash
python feed_analyzer.py team "nombre_del_team"
```

**Ejemplo:**
```bash
python feed_analyzer.py team "Acme Corp"
```

Esto buscará en todos los XMLs y mostrará todos los jobs que pertenezcan a ese team, ya sea por company name, company ID, o cualquier otro identificador.

#### 2. Buscar un job específico de un team específico

```bash
python feed_analyzer.py job "nombre_del_team" "nombre_o_id_del_job"
```

**Ejemplo:**
```bash
python feed_analyzer.py job "Acme Corp" "Senior Developer"
```

Esto buscará jobs que coincidan tanto con el team como con el job especificado.

#### 3. Ver resumen por teams

```bash
python feed_analyzer.py summary
```

Muestra un resumen con la cantidad de jobs por cada team.

#### 4. Listar todos los jobs

```bash
python feed_analyzer.py all
```

Muestra todos los jobs encontrados en todos los XMLs.

### 📁 Estructura

```
FEED SEARCH/
├── XMLFEEDS/           # Coloca aquí tus archivos XML
│   ├── feed1.xml
│   ├── feed2.xml
│   └── ...
├── feed_analyzer.py    # Script principal
└── README.md          # Este archivo
```

### 🔍 Campos que busca

La herramienta es flexible y busca información en múltiples campos posibles:

#### Para Teams/Companies:
- `companyId`, `company-id`, `clientId`, `teamId`
- `company`, `companyName`, `client`, `clientName`, `teamName`
- `team`, `department`, `division`, `businessUnit`

#### Para Jobs:
- `jobId`, `job-id`, `id`, `requisitionId`
- `referenceId`, `reference-id`, `refNumber`, `requisitionNumber`
- `title`, `jobTitle`, `jobName`, `position`, `positionTitle`

### 💡 Uso en Python

También puedes usar la clase `FeedAnalyzer` directamente en tu código:

```python
from feed_analyzer import FeedAnalyzer, print_jobs_table

# Crear el analyzer
analyzer = FeedAnalyzer("XMLFEEDS")

# Buscar todos los jobs de un team
jobs = analyzer.search_jobs_by_team("Acme Corp")
print(f"Encontrados: {len(jobs)} jobs")
print_jobs_table(jobs)

# Buscar un job específico
jobs = analyzer.search_specific_job("Acme Corp", "Senior Developer")
print_jobs_table(jobs)

# Obtener resumen
summary = analyzer.get_summary_by_team()
for team, count in summary.items():
    print(f"{team}: {count} jobs")
```

### 📊 Formato de salida

La herramienta muestra información detallada de cada job encontrado:

```
🔹 Job #1
   File:         feed1.xml
   Job ID:       12345
   Reference ID: REF-2025-001
   Job Name:     Senior Software Developer
   Company Name: Acme Corp
   Company ID:   ACME123
   Team:         Engineering
```

### ⚙️ Requisitos

- Python 3.6 o superior
- Librería estándar de Python (no requiere instalaciones adicionales)

### 🎯 Notas

- La búsqueda es **case-insensitive** (no distingue mayúsculas/minúsculas)
- Se hace búsqueda por **coincidencia parcial** (si buscas "Acme" encontrará "Acme Corp")
- Maneja diferentes formatos de XML y namespaces automáticamente
- Si un XML no tiene un tag específico de job, intentará usar el elemento raíz

---

## English

### Tool to analyze XML feeds and search for information about jobs and teams.

### 📋 Features

- ✅ Analyzes all XML files in the `XMLFEEDS` folder in bulk
- ✅ Searches all jobs from a specific team (and counts them)
- ✅ Searches for a specific job from a specific team
- ✅ Handles different identifiers for teams (company ID, company name, team identifier)
- ✅ Handles different identifiers for jobs (job ID, reference ID, job name)
- ✅ Flexible search (case-insensitive and partial matching)
- ✅ Summary of jobs grouped by team

### 🚀 Usage

#### 1. Search all jobs from a team

```bash
python feed_analyzer.py team "team_name"
```

**Example:**
```bash
python feed_analyzer.py team "Acme Corp"
```

This will search through all XMLs and display all jobs belonging to that team, whether by company name, company ID, or any other identifier.

#### 2. Search for a specific job from a specific team

```bash
python feed_analyzer.py job "team_name" "job_name_or_id"
```

**Example:**
```bash
python feed_analyzer.py job "Acme Corp" "Senior Developer"
```

This will search for jobs matching both the team and the specified job.

#### 3. View summary by teams

```bash
python feed_analyzer.py summary
```

Shows a summary with the number of jobs per team.

#### 4. List all jobs

```bash
python feed_analyzer.py all
```

Shows all jobs found in all XMLs.

### 📁 Structure

```
FEED SEARCH/
├── XMLFEEDS/           # Place your XML files here
│   ├── feed1.xml
│   ├── feed2.xml
│   └── ...
├── feed_analyzer.py    # Main script
└── README.md          # This file
```

### 🔍 Searched Fields

The tool is flexible and searches for information in multiple possible fields:

#### For Teams/Companies:
- `companyId`, `company-id`, `clientId`, `teamId`
- `company`, `companyName`, `client`, `clientName`, `teamName`
- `team`, `department`, `division`, `businessUnit`

#### For Jobs:
- `jobId`, `job-id`, `id`, `requisitionId`
- `referenceId`, `reference-id`, `refNumber`, `requisitionNumber`
- `title`, `jobTitle`, `jobName`, `position`, `positionTitle`

### 💡 Using in Python

You can also use the `FeedAnalyzer` class directly in your code:

```python
from feed_analyzer import FeedAnalyzer, print_jobs_table

# Create the analyzer
analyzer = FeedAnalyzer("XMLFEEDS")

# Search all jobs from a team
jobs = analyzer.search_jobs_by_team("Acme Corp")
print(f"Found: {len(jobs)} jobs")
print_jobs_table(jobs)

# Search for a specific job
jobs = analyzer.search_specific_job("Acme Corp", "Senior Developer")
print_jobs_table(jobs)

# Get summary
summary = analyzer.get_summary_by_team()
for team, count in summary.items():
    print(f"{team}: {count} jobs")
```

### 📊 Output Format

The tool displays detailed information for each job found:

```
🔹 Job #1
   File:         feed1.xml
   Job ID:       12345
   Reference ID: REF-2025-001
   Job Name:     Senior Software Developer
   Company Name: Acme Corp
   Company ID:   ACME123
   Team:         Engineering
```

### ⚙️ Requirements

- Python 3.6 or higher
- Python standard library (no additional installations required)

### 🎯 Notes

- Search is **case-insensitive** (doesn't distinguish uppercase/lowercase)
- **Partial matching** is performed (if you search "Acme" it will find "Acme Corp")
- Handles different XML formats and namespaces automatically
- If an XML doesn't have a specific job tag, it will try to use the root element
