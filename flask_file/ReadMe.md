✅ Commandes de déploiement

🧱 1. Construire l’image :
```docker-compose build```

🚀 2. Lancer le conteneur :
```docker-compose up -d```

🔍 3. Vérifier les logs :

```docker-compose logs -f```

🧼 4. Stopper :
```docker-compose down```

📤 Faire un curl d'upload
```curl -F "file=@/chemin/vers/fichier.txt" http://localhost:5001/upload```

📥 Faire un curl pour télécharger
```curl http://localhost:5001/files/fichier.txt -o fichier.txt```