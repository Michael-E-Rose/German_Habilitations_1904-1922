"""Combine the input list with GND IDs and full field names, and write:
1. the list of original habilitations
2. the moves of habilitated persons
"""

import re
from pathlib import Path

import pandas as pd

CORRESPONDENCES = Path("correspondences/")
OUTPUT = Path("output/")

KEY = ["Name", "Hochschule", "Semester"]
MIN_FIELD_COUNT = 10

UMLAUTS = str.maketrans({"ä": "a", "ö": "o", "ü": "u", "ß": "ss"})  # to sort them


def university_from(text, universities, spellings):
    """'früher Königsbg.' → 'Königsberg'; places not in the list stay as printed.
    Notes like 'in Basel beurl.' or 'zugleich Lektor in Marburg' are no move."""
    if re.search(r"beurl|zugleich", text):
        return ""
    name = re.sub(r"^früher\s*", "", text).strip(" .")
    name = spellings.get(name, name)
    if name in universities:
        return name
    hits = {uni for uni in universities if uni.startswith(name[:5])}
    return hits.pop() if len(hits) == 1 else name


def semester_order(jahr):
    """'1904 SS' → 3808, '1904/1905 WS' → 3809 (combined semesters by their WS)."""
    m = re.match(r"(\d{4})(?:/\d{4})? (SS|WS)", jahr)
    return 2 * int(m[1]) + (m[2] == "WS")


def semester_label(jahr):
    """'1904/1905 WS' → 'WS 1904/05', '1917/1918 WS u. 1918 SS' → 'WS 1917/18 + SS 1918'."""
    label = re.sub(r"(\d{4})/\d{2}(\d{2}) WS", r"WS \1/\2", jahr)
    return re.sub(r"(\d{4}) SS", r"SS \1", label).replace(" u. ", " + ")


if __name__ == "__main__":
    # Merge GND records
    df = pd.read_csv("input/Universitaetskalender.csv", dtype=str, keep_default_na=False)
    gnd = pd.read_csv(CORRESPONDENCES / "GND.csv", dtype=str)
    df = df.merge(gnd, on=KEY, how="left", validate="one_to_one")
    print(f"Entries with GND ID: {df['GND'].notna().sum():,} of {df.shape[0]:,} "
          f"({df['GND'].notna().mean():.1%}), unique: {df['GND'].nunique():,}")
    df = df.fillna("")

    # Normalize universities
    unis = pd.read_csv(CORRESPONDENCES / "Hochschule.csv", index_col="Schreibweise")["Hochschule"]
    df = df.replace({"Hochschule": unis.to_dict()})

    # Normalize fields
    fields = pd.read_csv(CORRESPONDENCES / "Gebiet.csv", index_col="Thema")["Gebiet"]
    missing = set(df["Thema"]) - set(fields.index) - {""}
    assert not missing, f"Thema values missing from Gebiet.csv: {sorted(missing)}"
    df.insert(df.columns.get_loc("Thema"), "Gebiet", df.pop("Thema").map(fields).fillna(""))

    # A person is identified by the GND; an entry without GND stands alone.
    # A person listed twice at the same university counts once, at the
    # earliest entry, with the university transferred from if either names it
    df = df.iloc[df["Semester"].map(semester_order).argsort(kind="stable")]
    df["Umhabilitierung"] = [university_from(u, set(df["Hochschule"]), unis) if u else ""
                             for u in df["Umhabilitierung"]]
    person = df["GND"].where(df["GND"] != "", df.index.astype(str))
    df["Umhabilitierung"] = df.groupby([person, "Hochschule"])["Umhabilitierung"].transform("max")
    df = df[~pd.concat([person, df["Hochschule"]], axis=1).duplicated()]

    # A person's first entry is the habilitation, unless it names a university
    # transferred from; every later entry is a move from the previous one
    previous = df.groupby(person[df.index])["Hochschule"].shift()
    moved = (df["Umhabilitierung"] != "") | previous.notna()
    df["Umhabilitierung"] = df["Umhabilitierung"].where(
        df["Umhabilitierung"] != "", previous.fillna(""))
    new = df[~moved].drop(columns="Umhabilitierung").sort_index()
    new.to_csv("habilitations.csv", index=False, encoding="utf-8-sig")
    df[moved].sort_index().to_csv("migrations.csv", index=False, encoding="utf-8-sig")

    semesters = sorted(set(new["Semester"]), key=semester_order)
    columns = sorted(set(df["Hochschule"]), key=lambda uni: uni.translate(UMLAUTS))
    table = (pd.crosstab(new["Semester"], new["Hochschule"], margins=True, margins_name="Total")
             .reindex(index=semesters + ["Total"], columns=columns + ["Total"])
             .rename(index=semester_label).rename_axis(index=None, columns=None))
    styler = table.style.format(lambda v: f"{v:.0f}" if v else "", na_rep="--")
    styler.format_index("\\rotatebox{{90}}{{{}}}", axis=1)
    styler.set_table_styles([{"selector": "scriptsize", "props": ":;"},
                             {"selector": "setlength", "props": ":{\\tabcolsep}{1.5pt};"}])
    latex = styler.to_latex(environment="sidewaystable", position_float="centering", hrules=True)
    (OUTPUT / "habilitations_university_semester.tex").write_text(latex, encoding="utf-8")

    counts = new["Gebiet"].replace("", "(ohne Angabe)").value_counts()
    small = counts < MIN_FIELD_COUNT
    counts = pd.concat([counts[~small], pd.Series(
        {f"Übrige ({small.sum()} Gebiete)": counts[small].sum()})])
    table = pd.DataFrame({"Anzahl": counts, "Anteil (%)": 100 * counts / counts.sum()})
    table.loc["Total"] = table.sum()
    latex = table.rename_axis("Gebiet").reset_index().to_latex(
        index=False, escape=True, formatters={"Anzahl": "{:.0f}".format, "Anteil (%)": "{:.1f}".format})
    (OUTPUT / "habilitations_fields.tex").write_text(latex, encoding="utf-8")
