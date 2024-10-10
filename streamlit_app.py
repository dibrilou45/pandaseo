import streamlit as st
from datetime import datetime
import pandas as pd
import openai

# Initialisation de la clé API OpenAI
openai.api_key = st.secrets["openai_secret_key"]

# Titre de l'application
st.title("Assistant Comptabilité LMNP : Guide Pas à Pas")

# Variables d'état pour suivre le parcours
if 'step' not in st.session_state:
    st.session_state.step = 1

# Fonction pour revenir à une étape précédente
def previous_step():
    if st.session_state.step > 1:
        st.session_state.step -= 1

# Fonction pour avancer à l'étape suivante
def next_step():
    st.session_state.step += 1

# Données collectées (dictionnaire pour stocker les réponses)
if 'data' not in st.session_state:
    st.session_state.data = {}

# Fonction d'aide pour chaque étape
def help_text(step):
    if step == 1:
        return "Dans cette étape, nous allons recueillir des informations de base sur votre bien immobilier. Cela nous aidera à calculer vos revenus et vos dépenses."
    elif step == 2:
        return "Ici, vous devez entrer combien vous louez votre bien chaque mois, ainsi que les charges que vous facturez à vos locataires."
    elif step == 3:
        return "Cette étape vous demande de saisir toutes les dépenses que vous avez pour gérer votre bien, comme les frais de maintenance ou de gestion."
    elif step == 4:
        return "Vous devez maintenant choisir un régime fiscal. Le régime réel vous permet de déduire vos frais réels, tandis que le Micro-BIC offre une déduction forfaitaire. Choisissez celui qui vous semble le plus approprié."
    elif step == 5:
        return "Voici un résumé de toutes les informations que vous avez fournies. Cela vous aidera à remplir vos déclarations fiscales."

# Étape 1 : Informations sur le bien
if st.session_state.step == 1:
    st.header("Étape 1 : Informations sur votre bien immobilier")
    st.write(help_text(1))
    
    property_type = st.selectbox("Quel type de bien possédez-vous ?", ["Appartement", "Maison", "Studio"])
    purchase_date = st.date_input("Quand avez-vous acheté ce bien ?", value=datetime.now())
    purchase_price = st.number_input("Quel est le prix d'achat de ce bien ? (€)", min_value=0.0, step=500.0)
    
    # Enregistrement des données
    st.session_state.data['property_type'] = property_type
    st.session_state.data['purchase_date'] = purchase_date
    st.session_state.data['purchase_price'] = purchase_price
    
    # Navigation
    if st.button("Suivant"):
        next_step()

# Étape 2 : Revenus locatifs
elif st.session_state.step == 2:
    st.header("Étape 2 : Revenus locatifs")
    st.write(help_text(2))
    
    rent_income = st.number_input("Combien louez-vous votre bien chaque mois ? (€)", min_value=0.0, step=50.0)
    rental_charges = st.number_input("Y a-t-il des charges que vous facturez à vos locataires chaque mois ? (€)", min_value=0.0, step=10.0)
    
    # Enregistrement des données
    st.session_state.data['rent_income'] = rent_income
    st.session_state.data['rental_charges'] = rental_charges
    
    # Navigation
    st.button("Précédent", on_click=previous_step)
    if st.button("Suivant"):
        next_step()

# Étape 3 : Dépenses
elif st.session_state.step == 3:
    st.header("Étape 3 : Dépenses")
    st.write(help_text(3))
    
    maintenance_costs = st.number_input("Quelles sont vos dépenses de maintenance annuelles ? (€)", min_value=0.0, step=50.0)
    management_fees = st.number_input("Avez-vous des frais de gestion annuels ? (€)", min_value=0.0, step=50.0)
    taxes = st.number_input("Quelles taxes ou impôts payez-vous pour ce bien ? (€)", min_value=0.0, step=50.0)
    
    # Enregistrement des données
    st.session_state.data['maintenance_costs'] = maintenance_costs
    st.session_state.data['management_fees'] = management_fees
    st.session_state.data['taxes'] = taxes
    
    # Navigation
    st.button("Précédent", on_click=previous_step)
    if st.button("Suivant"):
        next_step()

# Étape 4 : Choix du régime fiscal
elif st.session_state.step == 4:
    st.header("Étape 4 : Choix du régime fiscal")
    st.write(help_text(4))
    
    fiscal_regime = st.selectbox("Choisissez votre régime fiscal", ["Régime réel", "Micro-BIC"])
    
    # Enregistrement des données
    st.session_state.data['fiscal_regime'] = fiscal_regime
    
    # Navigation
    st.button("Précédent", on_click=previous_step)
    if st.button("Suivant"):
        next_step()

# Étape 5 : Résumé et génération des résultats
elif st.session_state.step == 5:
    st.header("Étape 5 : Résumé de vos informations")
    st.write(help_text(5))

    # Affichage des informations saisies
    st.write("Voici le résumé des informations que vous avez fournies :")
    
    summary_df = pd.DataFrame.from_dict(st.session_state.data, orient='index', columns=['Valeur'])
    st.dataframe(summary_df)

    # Simuler des résultats (ex. calcul d'amortissements ou bénéfices nets)
    total_income = st.session_state.data['rent_income'] * 12
    total_expenses = (st.session_state.data['maintenance_costs'] + 
                      st.session_state.data['management_fees'] + 
                      st.session_state.data['taxes'])
    
    if st.session_state.data['fiscal_regime'] == 'Régime réel':
        # Amortissement simplifié : pas nécessaire d'expliquer aux utilisateurs
        amortissement = st.session_state.data['purchase_price'] / 30  # Amortissement sur 30 ans
        net_profit = total_income - total_expenses - amortissement
        st.write(f"Votre bien peut avoir un amortissement annuel de : {amortissement:.2f} €.")
    else:
        net_profit = total_income - total_expenses
    
    st.write(f"Revenus nets annuels estimés : {net_profit:.2f} €")
    
    # Navigation
    st.button("Précédent", on_click=previous_step)
    st.button("Terminer")
