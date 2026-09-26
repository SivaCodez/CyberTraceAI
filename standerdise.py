import pandas as pd
from rapidfuzz import process, fuzz
import dateutil.parser

# Standard relationship categories
STANDARD_RELATIONS = {
    "called": "CALLED",
    "phoned": "CALLED",
    "telephoned": "CALLED",
    "contacted": "CALLED",
    "transferred": "TRANSFERRED_MONEY",
    "paid": "TRANSFERRED_MONEY",
    "sent": "TRANSFERRED_MONEY",
    "met": "MET_WITH",
    "saw": "MET_WITH",
    "located": "LOCATED_AT",
    "visited": "LOCATED_AT",
    "owns": "OWNS",
    "has": "OWNS",
    "associated": "ASSOCIATED_WITH",
    "linked": "ASSOCIATED_WITH"
}

def standardize_data(df):
    """
    Cleans and standardizes the entire DataFrame (Dates, Relationships, and Names) 
    in a single function call.
    """
    if df.empty:
        return df

    # --- INTERNAL HELPER FUNCTIONS ---
    
    def clean_date(date_str):
        if pd.isna(date_str) or str(date_str).lower() == "unknown":
            return "Unknown"
        try:
            parsed_date = dateutil.parser.parse(str(date_str), fuzzy=True)
            return parsed_date.strftime("%d/%m/%Y")
        except Exception:
            return "Unknown"

    def clean_relationship(raw_relation):
        if pd.isna(raw_relation):
            return "ASSOCIATED_WITH"
        
        raw_relation = str(raw_relation).lower()
        match = process.extractOne(raw_relation, STANDARD_RELATIONS.keys(), scorer=fuzz.WRatio)
        
        if match and match[1] >= 75:
            return STANDARD_RELATIONS[match[0]]
        return "ASSOCIATED_WITH"

    # --- APPLY STANDARDIZATION ---
    
    df['Date'] = df['Date'].apply(clean_date)
    df['Relationship'] = df['Relationship'].apply(clean_relationship)
    df['Suspect'] = df['Suspect'].astype(str).str.strip().str.title()
    df['Target'] = df['Target'].astype(str).str.strip().str.title()
    
    return df