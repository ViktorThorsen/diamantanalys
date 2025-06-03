"""
Testfil för clean_diamond_data, cheap_diamonds_by_carat och calculate_volatility_groups funktionerna

Syfte:
Syftet med testerna är att säkerställa att databearbetningen är korrekt och robust mot felaktig eller ofullständig indata. Det garanterar att applikationen fungerar som förväntat även vid framtida kodförändringar.

Funktioner som testas:
- `clean_diamond_data`: Att korrekt CSV-data returnerar en DataFrame, medan ogiltig eller trasig data ger tydliga felmeddelanden.
- `cheap_diamonds_by_carat`: Att diamanter under medianpriset per carat-grupp identifieras korrekt.
- `calculate_volatility_groups`: Att funktionens logik för att hitta de mest volatila färg- eller klarhetsgrupperna per caratintervall fungerar som avsett, även på tomma dataset.

Dessa tester är viktiga för att upptäcka fel tidigt och förhindra att framtida kodändringar introducerar buggar.
"""

from Diamond import clean_diamond_data
from Diamond import cheap_diamonds_by_carat
from Diamond import calculate_volatility_groups
import pandas as pd

class MockUploadedFile:
    def __init__(self, content: str):
        self.content = content

    def read(self):
        return self.content.encode("utf-8")

    def getvalue(self):
        return self.read()


def test_valid_csv_returns_dataframe():
    csv_data = """index,cut,color,clarity,price,carat,x,y,z,depth
0,Ideal,E,SI1,3000,1.0,5.0,5.0,3.0,60.0
1,Premium,D,VVS1,4500,0.9,4.9,5.1,3.0,60.6
2,Good,G,VS2,2800,0.8,5.2,4.8,3.0,60.0
"""
    uploaded = MockUploadedFile(csv_data)
    df, error = clean_diamond_data(uploaded)

    assert error is None
    assert df is not None
    assert len(df) == 3
    assert "carat" in df.columns


def test_missing_columns_returns_error():
    csv_data = "this,is,not,the,right,columns\n1,2,3,4,5"
    uploaded = MockUploadedFile(csv_data)
    df, error = clean_diamond_data(uploaded)

    assert df is None
    assert error is not None
    assert "saknar följande kolumner" in error.lower()


def test_unreadable_csv_returns_error():
    broken_data = "\x00\x00\x00"
    uploaded = MockUploadedFile(broken_data)
    df, error = clean_diamond_data(uploaded)

    assert df is None
    assert error is not None
    assert "kunde inte läsa" in error.lower()

def test_cheap_diamonds_by_carat_returns_cheaper_subset():
    csv_data = """index,cut,color,clarity,price,carat,x,y,z,depth
                    0,Ideal,E,SI1,1000,0.5,5.0,5.0,3.0,60.0
                    1,Ideal,E,SI1,1100,0.5,5.0,5.0,3.0,60.0
                    2,Ideal,E,SI1,1200,0.5,5.0,5.0,3.0,60.0
                    3,Ideal,E,SI1,1300,0.5,5.0,5.0,3.0,60.0
                    4,Ideal,E,SI1,1400,0.5,5.0,5.0,3.0,60.0
                    5,Ideal,E,SI1,1500,0.5,5.0,5.0,3.0,60.0
                    6,Ideal,E,SI1,1600,0.5,5.0,5.0,3.0,60.0
                    7,Ideal,E,SI1,1700,0.5,5.0,5.0,3.0,60.0
                    8,Ideal,E,SI1,1800,0.5,5.0,5.0,3.0,60.0
                    9,Ideal,E,SI1,1900,0.5,5.0,5.0,3.0,60.0
                    10,Ideal,E,SI1,2000,0.5,5.0,5.0,3.0,60.0
                    11,Ideal,E,SI1,2100,0.5,5.0,5.0,3.0,60.0
                    """
    uploaded = MockUploadedFile(csv_data)
    df, error = clean_diamond_data(uploaded)
    assert error is None
    assert df is not None
    result = cheap_diamonds_by_carat(df, ['color', 'clarity', 'cut'])

    assert len(result) == 6
    assert all(result['price'] < result['med_price'])

def test_calculate_volatility_groups_color():
    data = {
        'carat': [0.2, 0.3, 0.2, 0.3, 0.4, 0.4],
        'price': [1000, 1100, 1050, 1150, 1300, 1700],
        'color': ['D', 'D', 'E', 'E', 'F', 'F'],
        'clarity': ['VS1', 'VS1', 'VS2', 'VS2', 'SI1', 'SI1']
    }
    df = pd.DataFrame(data)
    top_colors = calculate_volatility_groups(df, 'color')
    assert isinstance(top_colors, pd.Series)
    assert len(top_colors) <= 2

def test_calculate_volatility_groups_clarity():
    data = {
        'carat': [0.2, 0.2, 0.2, 0.2],
        'price': [1000, 1200, 900, 1400],
        'color': ['D', 'D', 'D', 'D'],
        'clarity': ['IF', 'VVS1', 'IF', 'VVS1']
    }
    df = pd.DataFrame(data)
    top_clarities = calculate_volatility_groups(df, 'clarity')
    assert isinstance(top_clarities, pd.Series)
    assert len(top_clarities) <= 2
    assert all(isinstance(val, str) for val in top_clarities.index)

def test_calculate_volatility_groups_cut():
    data = {
        'carat': [0.2, 0.3, 0.2, 0.3, 0.4, 0.4],
        'price': [1000, 1100, 1050, 1150, 1300, 1700],
        'cut': ['Ideal', 'Ideal', 'Good', 'Good', 'Fair', 'Fair'],
        'color': ['D'] * 6,
        'clarity': ['VS1'] * 6
    }
    df = pd.DataFrame(data)
    top_cuts = calculate_volatility_groups(df, 'cut')
    assert isinstance(top_cuts, pd.Series)
    assert not top_cuts.empty
    assert all(isinstance(cut, str) for cut in top_cuts.index)

def test_calculate_volatility_groups_empty():
    df = pd.DataFrame(columns=['carat', 'price', 'color'])
    result = calculate_volatility_groups(df, 'color')
    assert isinstance(result, pd.Series)
    assert result.empty