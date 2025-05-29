# 💎 Diamantanalys – Kunskapskontroll

Detta projekt är en datadriven analys av diamantpriser och kvaliteter, som en del av en **kunskapskontroll inom dataanalys**. Projektet består av en **Jupyter Notebook-presentation**, en **Streamlit-app**, **automatiserade tester**, och testdata i form av mockfiler.

---

## 📁 Projektstruktur

| Fil/Folder                                                    | Beskrivning                                                                                                           |
| ------------------------------------------------------------- | --------------------------------------------------------------------------------------------------------------------- |
| `KunskapsKontrollExercises.ipynb`                             | **Avsnitt1** i kunskapskontrollen, mindre övningar.                                                                   |
| `DiamondsKunskapsKontrollDataStory.ipynb`                     | **Huvudpresentationen** av datastoryn med analys, visualiseringar och scenariosituation.                              |
| `Diamond.py`                                                  | **Streamlit-appen** Funktioner för datarensning, beräkning av volatilitet och analys av prisvärda köp.                |
| `DiamondUI.py`                                                | Streamlit-frontend med menyer, filter, tabs och interaktiva visualiseringar.                                          |
| `test_app.py`                                                 | Enhetstester med `pytest` för att säkerställa korrekt datahantering och funktionalitet.                               |
| `Mockdata_real_set_ok.xlsx`                                   | Det riktiga datasettet med diamanter.                                                                                 |
| `Mockdata_testfile_ok.xlsx`                                   | En korrekt formatterad testfil som ska **passera alla tester**.                                                       |
| `Mockdata_testfile_fail.xlsx`, `Mockdata_testfile_fail2.xlsx` | Medvetet **felaktiga filer** för att testa att appen och rensningen hanterar trasig data korrekt.                     |
| `requirements.txt`                                            | Lista på alla externa Python-bibliotek (t.ex. `streamlit`, `pandas`, `matplotlib`) som behövs för att köra projektet. |

---

## ▶️ Hur man kör projektet

1. **Installera beroenden**  
   Skapa en virtuell miljö och installera kraven:

   ```bash
   python -m venv .venv
   source .venv/Scripts/activate  # Windows
   pip install -r requirements.txt
   ```

2. **Starta appen**  
   streamlit run Diamonds.py

3. **Kör tester**  
   pytest test_app.py
