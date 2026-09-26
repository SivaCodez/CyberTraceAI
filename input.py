import pandas as pd
import spacy
import os
import subprocess

# Load the spaCy NLP model
# Automatically download the model on Streamlit Cloud if it's missing
try:
    nlp = spacy.load("en_core_web_sm")
except OSError:
    print("Downloading spaCy model...")
    subprocess.run(["python", "-m", "spacy", "download", "en_core_web_sm"])
    nlp = spacy.load("en_core_web_sm")

def process_investigation_data(csv_path, txt_path, default_date="Unknown"):
    """
    Processes both structured CSV records and unstructured text reports 
    into a single standardized dataframe.
    """
    combined_data = []

    # 1. Process Structured Data (CSV)
    if os.path.exists(csv_path):
        df_csv = pd.read_csv(csv_path)
        # Rename columns to standardized format if they exist
        column_mapping = {"Source": "Suspect", "Relation": "Relationship"}
        df_csv.rename(columns=lambda c: column_mapping.get(c, c), inplace=True)
        combined_data.append(df_csv)
    else:
        print(f"[-] CSV file '{csv_path}' not found.")

    # 2. Process Unstructured Data (TXT)
    if os.path.exists(txt_path):
        with open(txt_path, 'r', encoding='utf-8') as file:
            text = file.read()

        doc = nlp(text)
        txt_extracted = []

        # Iterate through sentences to find entities and dynamic relationships
        for sent in doc.sents:
            # Extract entities (People, Locations, Organizations)
            entities = [ent.text for ent in sent.ents if ent.label_ in ["PERSON", "ORG", "GPE", "LOC", "FAC"]]
            
            # Use spaCy POS tagging to dynamically find the main action (VERB)
            relation = None
            for token in sent:
                if token.pos_ == "VERB":
                    # Grab the root word of the verb and uppercase it (e.g., "called" -> "CALL")
                    relation = token.lemma_.upper()
                    break
            
            # If we found at least 2 entities and an action verb connecting them
            if relation and len(entities) >= 2:
                txt_extracted.append({
                    "Suspect": entities[0],
                    "Relationship": relation,
                    "Target": entities[1],
                    "Date": default_date
                })
        
        if txt_extracted:
            combined_data.append(pd.DataFrame(txt_extracted))
    else:
        print(f"[-] TXT file '{txt_path}' not found.")

    # 3. Merge and Return
    if combined_data:
        final_df = pd.concat(combined_data, ignore_index=True)
        final_df.fillna("Unknown", inplace=True)
        return final_df
    else:
        return pd.DataFrame(columns=["Suspect", "Relationship", "Target", "Date"])

def main():
    csv_file = input("Enter CSV file path: ").strip()
    txt_file = input("Enter TXT file path: ").strip()

    print("\nProcessing data sources...")
    
    # Run the single processing function
    final_network_df = process_investigation_data(csv_file, txt_file)

    print("\n--- EXTRACTED CRIMINAL NETWORK DATA ---")
    if not final_network_df.empty:
        print(final_network_df.to_string(index=False))
    else:
        print("No connections extracted.")

if __name__ == "__main__":
    main()