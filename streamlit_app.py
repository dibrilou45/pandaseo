import streamlit as st
import openai
import pdfplumber

# Configuration de l'API OpenAI
openai.api_key = st.secrets["openai_secret_key"]

# Fonction pour extraire du texte à partir d'un PDF
def extract_data_from_pdf(pdf_file):
    text = ""
    with pdfplumber.open(pdf_file) as pdf:
        for page in pdf.pages:
            text += page.extract_text()
    return text

# Fonction de comparaison entre le CRA et la Facture
def compare_cra_and_invoice(cra_data, invoice_data, tjm):
    # Extraction des jours travaillés dans le CRA
    cra_days = sum([float(day) for day in cra_data.split() if day.replace('.', '', 1).isdigit()])

    # Extraction du montant de la facture
    invoice_amount = None
    for word in invoice_data.split():
        try:
            invoice_amount = float(word.replace('€', '').replace(',', '').strip())
            break
        except ValueError:
            continue
    
    if invoice_amount is None:
        return "Impossible de trouver le montant de la facture."

    # Calcul du montant attendu
    expected_amount = cra_days * tjm

    if invoice_amount == expected_amount:
        return "Les données sont cohérentes."
    else:
        return f"Incohérence détectée : Facture de {invoice_amount} € au lieu de {expected_amount} €."

# Fonction pour générer des suggestions en cas d'incohérence, en utilisant GPT-4-turbo-mini
def generate_suggestions(error_message):
    response = openai.ChatCompletion.create(
        model="gpt-4-turbo",  # Utilise le modèle GPT-4-mini ou turbo selon la configuration
        messages=[
            {"role": "system", "content": "You are an assistant that provides suggestions for fixing errors in invoice comparisons."},
            {"role": "user", "content": f"Voici une erreur : {error_message}. Propose une solution."}
        ],
        max_tokens=50
    )
    return response['choices'][0]['message']['content'].strip()

# Interface Streamlit
st.title("Vérification CRA et Factures")

# Formulaire de téléchargement des fichiers
cra_file = st.file_uploader("Téléchargez le CRA (en PDF)")
invoice_file = st.file_uploader("Téléchargez la Facture (en PDF)")

# Champ pour saisir le TJM
tjm = st.number_input("Entrez le TJM (en €)", min_value=0.0, step=0.01)

if cra_file and invoice_file and tjm > 0:
    # Extraire les données des fichiers PDF
    cra_data = extract_data_from_pdf(cra_file)
    invoice_data = extract_data_from_pdf(invoice_file)

    # Comparer le CRA et la facture
    result = compare_cra_and_invoice(cra_data, invoice_data, tjm)
    st.write(result)

    # Si une incohérence est détectée, générer une suggestion
    if "Incohérence détectée" in result:
        suggestion = generate_suggestions(result)
        st.write("Suggestion : ", suggestion)
