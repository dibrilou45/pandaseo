import streamlit as st
import openai

# Si vous utilisez pytrends (optionnel)
# from pytrends.request import TrendReq
# pytrends = TrendReq(hl='fr-FR', tz=360)

# Configuration de l'API OpenAI
openai.api_key = st.secrets["openai_api_key"]

# Fonction pour analyser la problématique et générer des mots-clés avec GPT-4o
def analyze_problem(problem_statement):
    response = openai.ChatCompletion.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": "Tu es un expert en marketing digital et SEO. Analyse la problématique donnée et génère une liste de mots-clés pertinents pour le SEO."},
            {"role": "user", "content": f"Problématique : {problem_statement}"}
        ],
        temperature=0.7,
        max_tokens=500
    )
    keywords = response['choices'][0]['message']['content']
    # Extraction des mots-clés
    keywords_list = [keyword.strip() for keyword in keywords.split(',')]
    return keywords_list

# Fonction pour générer des sujets d'articles avec GPT-4o Mini
def generate_article_topics(keywords):
    keywords_text = ', '.join(keywords)
    response = openai.ChatCompletion.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "Tu es un rédacteur web spécialisé en SEO. Génère une liste de 10 sujets d'articles optimisés pour le SEO basés sur les mots-clés fournis."},
            {"role": "user", "content": f"Mots-clés : {keywords_text}"}
        ],
        temperature=0.7,
        max_tokens=700
    )
    topics = response['choices'][0]['message']['content']
    topics_list = topics.strip().split('\n')
    return topics_list

# Fonction pour générer une stratégie SEO avec GPT-4o
def generate_seo_strategy(topic):
    response = openai.ChatCompletion.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": "Tu es un expert en SEO. Pour le sujet donné, génère une stratégie SEO détaillée incluant le titre optimisé, la méta description, les mots-clés à utiliser, et des conseils sur la manière de placer les mots-clés dans l'article."},
            {"role": "user", "content": f"Sujet : {topic}"}
        ],
        temperature=0.7,
        max_tokens=700
    )
    strategy = response['choices'][0]['message']['content']
    return strategy

# Fonction pour générer un article avec GPT-4o Mini
def generate_article(topic, seo_strategy):
    response = openai.ChatCompletion.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "Tu es un rédacteur web qui écrit des articles optimisés pour le SEO en suivant la stratégie fournie."},
            {"role": "user", "content": f"Sujet : {topic}\n\nStratégie SEO : {seo_strategy}\n\nMerci d'écrire un article complet en respectant la stratégie ci-dessus."}
        ],
        temperature=0.7,
        max_tokens=3000
    )
    article = response['choices'][0]['message']['content']
    return article

# Interface utilisateur Streamlit
def main():
    st.title("Générateur d'Articles SEO")
    st.write("Cet outil vous aide à générer des articles optimisés pour le SEO en fonction de la problématique de votre produit.")

    # Étape 1 : Saisie de la problématique
    problem_statement = st.text_area("Entrez la problématique de votre produit/SaaS :", height=100)

    if st.button("Générer des sujets d'articles"):
        if problem_statement.strip() != "":
            # Étape 2 : Analyse de la problématique et génération des mots-clés
            with st.spinner("Analyse de la problématique et génération des mots-clés..."):
                keywords = analyze_problem(problem_statement)
                st.subheader("Mots-clés générés :")
                st.write(', '.join(keywords))

            # Étape 3 : Génération des sujets d'articles
            with st.spinner("Génération des sujets d'articles..."):
                topics = generate_article_topics(keywords)
                st.subheader("Sujets d'articles proposés :")
                for idx, topic in enumerate(topics):
                    st.write(f"{idx+1}. {topic}")

            # Étape 4 : Sélection des sujets favoris
            st.subheader("Sélectionnez les sujets que vous souhaitez développer :")
            selected_topics = []
            for idx, topic in enumerate(topics):
                if st.checkbox(topic, key=idx):
                    selected_topics.append(topic)

            if selected_topics:
                for topic in selected_topics:
                    # Étape 5 : Génération de la stratégie SEO
                    with st.spinner(f"Génération de la stratégie SEO pour : {topic}"):
                        seo_strategy = generate_seo_strategy(topic)
                        st.markdown(f"### Stratégie SEO pour '{topic}':")
                        st.write(seo_strategy)

                    # Étape 6 : Génération de l'article
                    with st.spinner(f"Génération de l'article pour : {topic}"):
                        article = generate_article(topic, seo_strategy)
                        st.markdown(f"### Article généré pour '{topic}':")
                        st.write(article)

                        # Option de téléchargement
                        st.download_button(
                            label="Télécharger l'article",
                            data=article,
                            file_name=f"{topic}.txt",
                            mime="text/plain"
                        )
            else:
                st.info("Veuillez sélectionner au moins un sujet pour générer un article.")
        else:
            st.warning("Veuillez entrer une problématique avant de continuer.")

if __name__ == "__main__":
    main()
