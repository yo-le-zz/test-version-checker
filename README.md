🧩 test-version-checker

Ce projet permet de mettre à jour automatiquement un script Python hébergé sur GitHub.

⚙️ Structure requise

Assurez-vous que votre dépôt GitHub respecte cette organisation :

version/
 ├── V1.0/
 │   ├── main.py < votre script
 │
 ├── V1.1/
 │   ├── main.py
 │
 ...

📌 Règles à suivre

Les dossiers de version doivent commencer par V, suivis d’un numéro avec un point — par exemple V1.0.
La version maximale supportée est V9.9.

Modifiez le script principal en adaptant :

votre nom d’utilisateur GitHub

le chemin de l’API GitHub (les variables correspondantes sont tout en haut du script)

Le script détecte et télécharge automatiquement la dernière version disponible sur GitHub.

Les dépendances nécessaires peuvent être installées via :

pip install -r requirements.txt

💡 Remarques

Vous pouvez ajouter votre propre script Python directement à la suite du projet.

Vérifiez toujours que la structure du dépôt est respectée avant de publier une nouvelle version.
