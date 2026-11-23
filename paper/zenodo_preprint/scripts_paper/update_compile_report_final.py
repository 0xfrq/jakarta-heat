from pathlib import Path
p = Path(r"D:\jakarta-heat-paper\paper\zenodo_preprint\COMPILATION_REPORT.md")
s = p.read_text(encoding="utf-8")
s = s.replace(
    "| `Manuscript-submission-candidate.pdf` | 23 | 2,416,403 bytes | `66302DA1618D519A39152CAE618981AF4FAB3D30B42EC47E49A6A5AF5E470066` |",
    "| `Manuscript-submission-candidate.pdf` | 24 | 2,418,475 bytes | `92BA6A2B57467F952D4A07A1A954B35AA68198F0CA1D10C286015AB8D61F3F31` |")
s = s.replace(
    "| `Manuscript-internal-review.pdf` | 23 | 2,416,668 bytes | `34F84957BE807149DF9BD333A261DEA1902987C92DAC08B6F83878934CC7666D` |",
    "| `Manuscript-internal-review.pdf` | 24 | 2,418,729 bytes | `F8043E882A4C224F56F2D682AC1DF6141CB7C7571707049071EB2EA4A986592C` |")
s = s.replace(
    "| `Supplementary-submission-candidate.pdf` | 7 | 799,191 bytes | `1CD6992723632236D61F4E0A85EA054268E373EFEE02A3B6277843ABB82A2675` |",
    "| `Supplementary-submission-candidate.pdf` | 8 | 801,426 bytes | `9CD990B91FDC94DAD04D5CE5663D42CD80920C8E9ECEC8908387133ACE096A58` |")
s = s.replace(
    "input/Manuscript.tex        96E3C474E8BB9AF6F90B2C921A407561CB6CB1C0AC657C71F6D20C54D226AFBE",
    "input/Manuscript.tex        D8AA81617C408957606CE7623B33ED19CA3223410971A373B2073687E9F3D147")
s = s.replace(
    "input/Supplementary.tex     B3E5C6E1D7135FD5DC95B2BB8BA48EB1646E80B859A1BE12553E766AC093EF68",
    "input/Supplementary.tex     02B1DB866EBB4B086BFCD3A517D8E77DBD6D1FD07E9535711EC036EE3E043A34")
s = s.replace(
    "The clean publication candidate is **23 pages**; the supplement is **7 pages**.",
    "The clean publication candidate is **24 pages**; the supplement is **8 pages**.")
p.write_text(s, encoding="utf-8")
print("compilation report updated")
