import streamlit as st
import pytesseract
import openai
import pdfplumber
import re

# Configuration de l'API OpenAI
openai.api_key = st.secrets["openai_secret_key"]

# Fonction pour extraire du texte à partir d'un PDF
def extract_data_from_pdf(pdf_file):
    text = ""
    with pdfplumber.open(pdf_file) as pdf:
        for page in pdf.pages:
            text += page.extract_text()
    return text

# Fonction pour extraire automatiquement le TJM à partir du texte d'une facture
def extract_tjm(text):
    # Cherche le motif qui correspond à "PU HT" suivi d'un montant
    match = re.search(r"PU HT\s*[:\-]?\s*(\d+)\s*€", text)
    if match:
        return float(match.group(1))
    return None

# Fonction de comparaison entre le CRA et la Facture
def compare_cra_and_invoice(cra_data, invoice_data):
    # Extraction du TJM à partir des données de la facture
    tjm = extract_tjm(invoice_data)
    
    if tjm is None:
        return "Impossible de trouver le TJM dans les documents fournis."

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

# Fonction pour générer des suggestions en cas d'incohérence
def generate_suggestions(error_message):
    response = openai.Completion.create(
        engine="text-davinci-003",
        prompt=f"Voici une erreur : {error_message}. Propose une solution.",
        max_tokens=50
    )
    return response.choices[0].text.strip()

# Interface Streamlit
st.title("Vérification CRA et Factures")

# Formulaire de téléchargement des fichiers
cra_file = st.file_uploader("Téléchargez le CRA (en PDF)")
invoice_file = st.file_uploader("Téléchargez la Facture (en PDF)")

if cra_file and invoice_file:
    # Extraire les données des fichiers PDF
    cra_data = extract_data_from_pdf(cra_file)
    invoice_data = extract_data_from_pdf(invoice_file)

    # Comparer le CRA et la facture
    result = compare_cra_and_invoice(cra_data, invoice_data)
    st.write(result)

    # Si une incohérence est détectée, générer une suggestion
    if "Incohérence détectée" in result:
        suggestion = generate_suggestions(result)
        st.write("Suggestion : ", suggestion)
