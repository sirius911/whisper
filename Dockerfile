# Utiliser une image de base Python compatible GPU
FROM python:3.10-bookworm

# Empêcher les invites interactives
ARG DEBIAN_FRONTEND=noninteractive

# Installer les dépendances système nécessaires
RUN apt-get update && apt-get install -y \
    portaudio19-dev \
    libsndfile1 \
    && rm -rf /var/lib/apt/lists/*

# Mise à jour de pip pour une meilleure gestion des dépendances
RUN pip install --no-cache-dir -U "pip>=24"

# Créer un répertoire de travail
WORKDIR /app

# Copier les dépendances Python
COPY requirements/server.txt /app/

# Installer les dépendances Python
RUN pip install --no-cache-dir -r server.txt && rm server.txt

# Configurer dynamiquement LD_LIBRARY_PATH pour les bibliothèques NVIDIA
RUN echo "export LD_LIBRARY_PATH=\$(python3 -c 'import os; import nvidia.cublas.lib; import nvidia.cudnn.lib; print(os.path.dirname(nvidia.cublas.lib.__file__) + \":\" + os.path.dirname(nvidia.cudnn.lib.__file__))'):\$LD_LIBRARY_PATH" >> /etc/profile

# Copier les fichiers de l'application
COPY whisper_live /app/whisper_live
COPY run_server.py /app

ENV LD_LIBRARY_PATH=/usr/local/lib/python3.10/site-packages/nvidia/cudnn/lib

# Commande par défaut pour démarrer le serveur
CMD ["/bin/bash", "-c", "source /etc/profile && /usr/local/bin/python3 run_server.py --port $PORT --backend faster_whisper --omp_num_threads $NB_PROC -fw $MODEL -d $DEBUG -c $CONTAINER -mc $MAX_CLIENT -mt $MAX_TIME"]
