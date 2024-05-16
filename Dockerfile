# Utiliser l'image de base de Jupyter Notebook
FROM jupyter/base-notebook:python-3.9

# Installer mysql-connector-python
RUN pip install mysql-connector-python pandas requests

# Copier les scripts dans le conteneur
COPY script /home/jovyan/scripts

# Définir le répertoire de travail
WORKDIR /home/jovyan/scripts

# Ajuster les permissions des répertoires
USER root
RUN mkdir -p /data  # Créer le répertoire /data si nécessaire
RUN chmod -R 777 /home/jovyan/scripts
RUN chmod -R 777 /home/jovyan/work
RUN chmod -R 777 /data

# Revenir à l'utilisateur par défaut (jovyan)
USER jovyan
