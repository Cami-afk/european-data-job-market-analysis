"""Role classification rules for European Data Job Market project.

This module contains:
- RULES: regex patterns for titles and skills
- PRIORITY: evaluation order (highest priority first)
- categorize_dataframe(): main entry point used in the notebook

Design:
1) Phase 1: classify by job title
2) Phase 2: classify remaining by skills

The rules are intentionally heuristic and explainable (rule-based baseline).
"""

from __future__ import annotations

import re
from typing import Dict, List

import pandas as pd


RULES = {
    "business_analyst": {
        "title_include": [
            r"\bbusiness\b", r"\bbusiness analyst\b", r"\bbusiness intelligence\b",
            r"\banalyste métier\b", r"\banalyste fonctionnel\b", r"\bfunctional analyst\b",
            r"\banalista de negocio\b", r"\banalista funzionale\b", r"\bgeschäftsanalyst\b",
            r"\bmoa\b", r"\bBI analyst\b", r"\bBusiness Intelligence Analyst\b",
            r"\bconsultant(e)? fonctionnel(le)?\b"
        ],
        "title_exclude": [
            r"\bdata (analyst|scientist|engineer)\b", r"\bmachine learning\b",
            r"\bdata ops\b", r"\banalytics engineer\b"
        ],
        "skills_include": [
            r"\brequirements\b", r"\buser stories\b", r"\bprocess mapping\b",
            r"\buml\b", r"\bbpmn\b", r"\bcrm\b", r"\berp\b", r"\bmoa\b"
        ],
        "skills_exclude": []
    },

    "data_scientist": {
        "title_include": [
            r"\bdata scientist\b", r"\bscientist\b", r"\bscientifique des données\b",
            r"\bdata science\b", r"\bmachine learning\W", r"\bml engineer\b",
            r"\bml scientist\b", r"\bdeep learning\b", r"\bnlp\b"
        ],
        "title_exclude": [
            r"\banalyst\b", r"\bbusiness analyst\b", r"\bdata (analyst|engineer)\b"
        ],
        "skills_include": [
            r"\btensorflow\b", r"\bpytorch\b", r"\bscikit[- ]learn\b",
            r"\bnlp\b", r"\bdeep learning\b", r"\bxgboost\b", r"\blightgbm\b"
        ],
        "skills_exclude": []
    },

    "analytics_engineer": {
        "title_include": [
            r"\banalytics engineer\b", r"\bdata analytics engineer\b",
            r"\banalytics engineering\b", r"\bData Analyst & Engineer\b",
            r"\bdbt engineer\b"
        ],
        "title_exclude": [
            r"\banalyst\b", r"\bconsultant\b", r"\bspecialist\b", r"\bexpert\b",
            r"\blead\b", r"\bmanager\b", r"\barchitect\b", r"\bdeveloper\b",
            r"\bbi\b", r"\bmarketing\b", r"\bproduct\b"
        ],
        "skills_include": [
            r"\bdbt\b", r"\bdata modeling\b", r"\bdimensional modeling\b",
            r"\bsemantic layer\b", r"\bmetric layer\b"
        ],
        "skills_exclude": [
            r"\bpower bi\b", r"\btableau\b", r"\bexcel\b", r"\bbi\b",
            r"\breporting\b", r"\bvisuali(s|z)ation\b", r"\banalytics\b",
            r"\bconsult\b"
        ]
    },

    "data_ops": {
        "title_include": [
            r"\bdata ?ops\b", r"\bdata operations\b", r"\bml ?ops\b", r"\bmlops\b",
            r"\bdata reliability\b", r"\bdata platform\b", r"\bdata infrastructure\b",
            r"\bingénieur plateforme\b"
        ],
        "title_exclude": [
            r"\banalyst\b", r"\bbusiness analyst\b", r"\bdata engineer\b", r"\bdata (analyst|scientist|engineer)\b"
        ],
        "skills_include": [
            r"\bairflow\b", r"\bmlflow\b", r"\bkubernetes\b", r"\bk8s\b",
            r"\bprometheus\b", r"\bgrafana\b", r"\bdocker\b", r"\bci/cd\b",
            r"\bmonitoring\b", r"\bterraform\b", r"\bdata quality\b"
        ],
        "skills_exclude": []
    },

    "data_engineer": {
        "title_include": [
            r"\bdata engineer\b", r"\bmodeller\b", r"\bengineer\b", r"\bingénieur\b",
            r"\bingénieur data\b", r"\bdata engineering\b", r"\bbig data engineer\b",
            r"\bcloud\b", r"\betl developer\b", r"\betl engineer\b",
            r"\bdata pipeline\b", r"\bpyspark\b", r"\bspark developer\b"
        ],
        "title_exclude": [
            r"\banalytics engineer\b", r"\banalyst\b", r"\bbusiness analyst\b", r"\bdata (analyst|scientist)\b"
        ],
        "skills_include": [
            r"\b(pyspark|spark)\b", r"\bairflow\b", r"\bkafka\b", r"\bdatabricks\b",
            r"\b(etl|elt)\b", r"\bs3\b", r"\bgcs\b", r"\bdata pipelines?\b"
        ],
        "skills_exclude": []
    },

    "data_analyst": {
        "title_include": [
            r"\banalyst\b", r"\banalyste\b", r"\banalist\b", r"\bstatistician\b",
            r"\bdata analyst\b", r"\banalyst(e)? data\b", r"\banalyste données\b",
            r"\banalista de datos\b", r"\bdatenanalyst\b", r"\banalista dati\b",
            r"\breporting analyst\b", r"\binsights analyst\b", r"\bproduct analyst\b"
        ],
        "title_exclude": [
            r"\bbusiness analyst\b", r"\bproduct analyst\b", r"\bbi analyst\b",
            r"\bpower bi developer\b"
        ],
        "skills_include": [
            r"\bsql\b", r"\btableau\b", r"\bpower bi\b", r"\bexcel\b",
            r"\bdata visualization\b", r"\bga\b", r"\blook(er)? studio\b",
            r"\bdashboard\b"
        ],
        "skills_exclude": []
    }
}


# 2) Ordre de Priorité Conseillé (Du plus spécialisé au plus généraliste/fonctionnel)
PRIORITY = [
    "data_scientist",
    "data_ops",
    "analytics_engineer",
    "data_engineer",
    "business_analyst",
    "data_analyst"
]


# 3) Nettoyage des textes
def clean_text(text):
    text = text.lower()
    text = re.sub(r"[^a-z0-9+ ]", " ", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text


# 4) Compilation des Regex
def compile_rule_list(rule_list):
    return [re.compile(p, flags=re.IGNORECASE) for p in rule_list]

COMPILED = {}
for cat, rule in RULES.items():
    COMPILED[cat] = {
        "title_include": compile_rule_list(rule.get("title_include", [])),
        "title_exclude": compile_rule_list(rule.get("title_exclude", [])),
        "skills_include": compile_rule_list(rule.get("skills_include", [])),
        "skills_exclude": compile_rule_list(rule.get("skills_exclude", [])),
    }


# 5) Fonction de Classification en 2 Étapes (Titre d'abord, Skills ensuite)
def categorize_dataframe(df_job, title_col="job_title", skills_col="skills_list", verbose: bool = False):
    # Préparation des données
    titles = df_job[title_col].fillna("").astype(str).apply(clean_text)
    skills = df_job[skills_col].fillna("").astype(str).apply(clean_text)

    # Initialisation
    result = pd.Series(index=df_job.index, dtype="object")
    result[:] = "undefined"
    assigned_mask = pd.Series(False, index=df_job.index)

    # --- Étape 1 : Classification par TITRE (Critère Primaire) ---
    if verbose:
        print("Démarrage Phase 1 : Classification par Titre (Priorité Élevée)")
    for cat in PRIORITY:
        comp = COMPILED[cat]

        # Calcul des masques d'inclusion/exclusion pour le titre
        title_include_mask = pd.Series(False, index=df_job.index)
        for patt in comp["title_include"]:
            title_include_mask |= titles.str.contains(patt)

        title_exclude_mask = pd.Series(False, index=df_job.index)
        for patt in comp["title_exclude"]:
            title_exclude_mask |= titles.str.contains(patt)

        # Les postes doivent matcher l'inclusion ET ne pas matcher l'exclusion
        title_mask = title_include_mask & ~title_exclude_mask

        # Assignation uniquement si le poste n'a pas déjà été classé
        final_mask = title_mask & (~assigned_mask)

        result.loc[final_mask] = cat
        assigned_mask |= final_mask

    if verbose:
        print(f"Phase 1 terminée. {assigned_mask.sum()} postes classés par Titre.")


    # --- Étape 2 : Classification par SKILLS (Critère Secondaire/Départage) ---
    # Ne s'applique qu'aux postes NON assignés lors de la Phase 1
    if verbose:
        print("Démarrage Phase 2 : Classification par Compétences (Postes restants)")
    for cat in PRIORITY:
        comp = COMPILED[cat]

        # Calcul des masques d'inclusion/exclusion pour les compétences
        skills_include_mask = pd.Series(False, index=df_job.index)
        for patt in comp["skills_include"]:
            skills_include_mask |= skills.str.contains(patt)

        skills_exclude_mask = pd.Series(False, index=df_job.index)
        for patt in comp["skills_exclude"]:
            skills_exclude_mask |= skills.str.contains(patt)

        # Les postes doivent matcher l'inclusion ET ne pas matcher l'exclusion des skills
        skills_mask = skills_include_mask & ~skills_exclude_mask

        # Assignation uniquement si le poste n'a PAS été classé en Phase 1
        final_mask = skills_mask & (~assigned_mask)

        result.loc[final_mask] = cat
        assigned_mask |= final_mask

    if verbose:
        print(f"Phase 2 terminée. Total postes classés : {assigned_mask.sum()}.")


    return result
