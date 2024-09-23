import streamlit as st
import pytesseract
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
def compare_cra_and_invoice(cra_data, invoice_data, hourly_rate):
    cra_hours = sum([float(hour) for hour in cra_data.split() if hour.replace('.', '', 1).isdigit()])
    invoice_amount = float(invoice_data.split()[0])  # Assumons que le montant est le premier nombre trouvé dans la facture
    expected_amount = cra_hours * hourly_rate

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

# Saisie du taux horaire
hourly_rate = st.number_input("Taux horaire du consultant (€)", min_value=0.0, step=0.01)

if cra_file and invoice_file:
    # Extraire les données des fichiers PDF
    cra_data = extract_data_from_pdf(cra_file)
    invoice_data = extract_data_from_pdf(invoice_file)

    # Comparer le CRA et la facture
    result = compare_cra_and_invoice(cra_data, invoice_data, hourly_rate)
    st.write(result)

    # Si une incohérence est détectée, générer une suggestion
    if "Incohérence détectée" in result:
        suggestion = generate_suggestions(result)
        st.write("Suggestion : ", suggestion)
