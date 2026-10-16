# German Habilitations 1904–1922

The list of all habilitations at German-speaking universities between the summer semester 1904
and the winter semester 1921/22 + summer semester 1922, as reported in the *Deutscher
Universitätskalender*, with GND identifiers for the persons.

[TODO: one or two sentences on why this list was compiled / the related project or paper]

## Source: the *Deutscher Universitätskalender*

The *Deutscher Universitätskalender* (German University Calendar) was a directory published every semester (once per year after 1914). It listed the teaching staff of the universities in the German Empire as well as all of Switzlerand and the German-speaking universities of the Austro-Hungarian Empire.
The Kalender was published by the *Deutscher Universitätsverein* (German University Association) in Berlin, and later in Leipzig. It was edited by a committee of university professors.

Between summer semester 1904 and winter semester 1921/22 + summer semester 1922, the Kalender reported habilitations at each university (outside Germany: until 1918).
These include the field (though not the titles) and sometimes the birth date or birth year of the habilitand. The Kalender also reported moves of habilitated persons between universities (Umhabilitierung).

The scans were obtained via Google Books and the Bayerische Staatsbibliothek (signature: H.lit.p. 396 o).

### What a habilitation is

The habilitation is the second academic qualification after the doctorate. A habilitand writes a habilitation thesis (*Habilitationsschrift*) and gives a trial lecture. The faculty then grants the *venia legendi*, the right to teach a subject at that university. The habilitated person becomes a *Privatdozent*: an unsalaried lecturer who is eligible for a professorship.
The habilitation was therefore the entry point into an academic career.

A habilitation applies to one university only. Someone who moved as a Privatdozent had to transfer their venia legendi to the new university. This is called an *Umhabilitierung* (re-habilitation). The Kalender reports such moves alongside the habilitations.

## Files

| File | Content                                                                   |
|------|---------------------------------------------------------------------------|
| `habilitations.csv` | One row per reported habilitation (3,480 rows)                            |
| `migrations.csv` | One row per move of a habilitated person to another university (310 rows) |

Both CSV files are UTF-8 encoded (with a byte order mark, so that Excel opens them correctly) and comma-separated.

### `habilitations.csv`

| Column | Content |
|--------|---------|
| `Name` | Name as printed, usually with abbreviated forenames (`Gg.` = Georg, `Heinr.` = Heinrich, `Frz.` = Franz) |
| `Namenszusatz` | Title, position or profession printed before the name, as printed: `Pf.` (Professor), `P.-D.` (Privatdozent), `Dr.`, `Lektor`, `Frau`, … Empty for most rows |
| `Hochschule` | University, normalized (e.g. `Freiburg i. B.` → `Freiburg`, `Freiburg (Schweiz)` → `Fribourg`). 38 universities |
| `Fakultät` | Faculty, as printed. Empty for about a third of the rows, and spelled inconsistently |
| `Abteilung` | Section of the philosophical faculty, as printed (`II Sektion`, `1 Abteilung`, `mathemat-naturwiss. Abt.`). Only at universities whose philosophical faculty was split, usually into humanities and mathematics/sciences: Basel, Bern, München, Würzburg, Zürich. For 8 entries the Kalender omits the faculty heading and prints only the section; their `Fakultät` is empty, although the section belongs to the philosophical faculty. An empty `Abteilung` does not mean the faculty was undivided: the Kalender often omits the section heading |
| `Semester` | `1904 SS` (summer semester), `1904/1905 WS` (winter semester), and from 1916/17 on combined: `1916/1917 WS u. 1917 SS` |
| `Gebiet` | Field of the venia legendi, written out in full from the printed abbreviation (`Ophthalmol.` → `Augenheilkunde`). Latin clinical names are given in German |
| `Geburtstag` | Date of birth, as printed. Filled for about a fifth of the rows; the format varies (`29.3.83`, `1876`) |
| `GND` | ID of the person in the Gemeinsame Normdatei (GND) of the German National Library, if one was found: `https://d-nb.info/gnd/<GND>` |

Rules:

- **A person is identified by their GND.** A person with a GND appears only once in this file,
  at their first entry in the Kalender.
- **Entries without a GND stand alone.** The same person can then appear twice: in this file
  and in `migrations.csv`, or twice in this file.
- **An entry is a move, not a habilitation,** if the Kalender names a university the person
  came from, or if the person already appears at an earlier date at another university. Such
  entries are in `migrations.csv`.
- **Repeated entries are dropped.** The Kalender sometimes reports the same person at the same
  university twice, e.g. in two consecutive issues. Only the earliest entry is kept. This
  removes 110 of the 3,900 entries.

### `migrations.csv`

The same columns as `habilitations.csv`, plus:

| Column | Content |
|--------|---------|
| `Umhabilitierung` | The university the person moved from. Normalized like `Hochschule` where possible, otherwise as printed (for institutions outside the list). Either taken from the Kalender's note or, if there is none, the university of the person's previous entry |

`Hochschule` and `Semester` are the university the person moved to and the semester the
Kalender reports the move.

## Coverage

- 2,819 of the 3,480 habilitations (81%) have a GND.
- An empty `GND` means that no GND record exists for the person, or that the person could not be identified unambiguously.
- Names, faculties and fields are given as printed in the Kalender, including its misprints. The GND record gives the correct name.

## Usage

Read the files directly from GitHub in Python:

```python
import pandas as pd

URL = "https://raw.githubusercontent.com/Michael-E-Rose/German_Habilitations_1904-1922/main/"

habilitations = pd.read_csv(URL + "habilitations.csv", dtype=str, keep_default_na=False)
migrations = pd.read_csv(URL + "migrations.csv", dtype=str, keep_default_na=False)

# Habilitations per semester and university
habilitations.groupby(["Semester", "Hochschule"]).size()

# The career of a person: their habilitation and all later moves
gnd = "1045186562"  # W. Brünings: Zürich 1904, Freiburg 1908/09, Jena 1909/10
pd.concat([habilitations, migrations]).query("GND == @gnd")
```

Or in R:

```r
url <- "https://raw.githubusercontent.com/Michael-E-Rose/German_Habilitations_1904-1922/main/"

habilitations <- read.csv(paste0(url, "habilitations.csv"), colClasses = "character", fileEncoding = "UTF-8-BOM")
migrations <- read.csv(paste0(url, "migrations.csv"), colClasses = "character", fileEncoding = "UTF-8-BOM")
```

The GND links the persons to further data:

- `https://d-nb.info/gnd/<GND>`: the GND record (full name, life dates, professions).
- `https://lobid.org/gnd/<GND>.json`: the same record as JSON, from the lobid API.
- The GND is also used by Wikidata (property P227), the Deutsche Biographie and many library
  catalogues.

To rebuild the target files after a change in `input/` or `correspondences/`, run (requires
Python with `pandas` and `jinja2`):

```bash
python combine_data.py
```

## Citation

[TODO: how to cite this dataset, e.g. author, year, title, DOI]

## License

The data and code are released under the MIT License, see [LICENSE](LICENSE).
