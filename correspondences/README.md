Correspondence tables linking the entries of `input/Universitaetskalender.csv` to other data. All three are read by `combine_data.py`.

- `GND.csv`: The GND ID (Gemeinsame Normdatei, https://d-nb.info/gnd/) of each habilitand, with one row per entry of the input list, identified by `Name`, `Hochschule` and `Semester` as printed there. `GND` is empty if no GND record could be found or the person could not be identified unambiguously.
- `Gebiet.csv`: Maps each spelling of the field (`Thema`) in the input list to its full German term (`Gebiet`), e.g. `Ophthalmol.` → `Augenheilkunde`; Latin clinical names are mapped to the German ones.
- `Hochschule.csv`: Maps the spellings of a university (`Schreibweise`, column `Hochschule` in the input list) that differ from its name (`Hochschule`), e.g. `Freiburg i. B.` → `Freiburg`; all other universities keep their spelling.
