# TP DevOps — Demontis Matisse

## Stack Dockerisée
- Backend: FastAPI (Python)
- Frontend: Node.js (Express)
- Base de données: PostgreSQL

## Démarrage rapide
- Prérequis: Docker et Docker Compose

1. Construire et lancer les services:
   - `docker compose up -d --build`
2. Ouvrir le frontend:
   - `http://localhost:3000/`
3. Tester le backend:
   - `http://localhost:8000/health`
   - `http://localhost:8000/items`
   - `http://localhost:8000/db-check`

## Structure
- `backend/`: application FastAPI et Dockerfile
- `frontend/`: serveur Express et Dockerfile
- `docker-compose.yml`: orchestration des services

## Variables et DB
- Postgres tourne avec `app:app` et base `appdb`.
- Le backend utilise `DATABASE_URL=postgresql://app:app@db:5432/appdb`.

## Arrêt / Nettoyage
- Arrêter: `docker compose down`
- Supprimer volumes DB: `docker compose down -v`
## commandes de bases :
docker run hello-world : Hello-world d’exemple avec Docker
```
TP-DevOps-1> docker run hello-world

Hello from Docker!
This message shows that your installation appears to be working correctly.

To generate this message, Docker took the following steps:
 1. The Docker client contacted the Docker daemon.
 2. The Docker daemon pulled the "hello-world" image from the Docker Hub.
    (amd64)
 3. The Docker daemon created a new container from that image which runs the
    executable that produces the output you are currently reading.
 4. The Docker daemon streamed that output to the Docker client, which sent it
    to your terminal.

To try something more ambitious, you can run an Ubuntu container with:
 $ docker run -it ubuntu bash

Share images, automate workflows, and more with a free Docker ID:
 https://hub.docker.com/

For more examples and ideas, visit:
 https://docs.docker.com/get-started/
```
docker run -it ubuntu bash : Création d’un conteneur et utilisation d’un bash en interactif exit ou Ctrl+D - Pour sortir du conteneur
```
TP-DevOps-1> docker run -it ubuntu bash
Unable to find image 'ubuntu:latest' locally
latest: Pulling from library/ubuntu
6e3729cf69e0: Pull complete
Digest: sha256:27cb6e6ccef575a4698b66f5de06c7ecd61589132d5a91d098f7f3f9285415a9
Status: Downloaded newer image for ubuntu:latest
root@9c5819f5a2f6:/#
```
docker images : Afficher les images Docker disponibles en local
```
 docker images
REPOSITORY     TAG       IMAGE ID       CREATED         SIZE
ma_super_app   latest    31202a646c98   2 days ago      136MB
ubuntu         latest    6b7dfa7e8fdb   3 weeks ago     77.8MB
mysql          8.0       7484689f290f   3 weeks ago     538MB
nginx          latest    ac8efec875ce   4 weeks ago     142MB
hello-world    latest    feb5d9fea6a5   15 months ago   13.3kB
```
docker ps -a : Affiche tous les conteneurs (en exécution ou pas, grâce à l’option -a)
```
docker ps -a
CONTAINER ID   IMAGE          COMMAND                  CREATED              STATUS                          PORTS     NAMES
9c5819f5a2f6   ubuntu         "bash"                   42 seconds ago       Exited (130) 16 seconds ago               flamboyant_borg
386d314e7ab4   hello-world    "/hello"                 About a minute ago   Exited (0) About a minute ago             peaceful_allen
6e403a1c4ec6   mysql:8.0      "docker-entrypoint.s…"   2 days ago           Exited (0) 30 hours ago                   tp-devops-2-mysql-1
540ef58a2ad5   ma_super_app   "docker-entrypoint.s…"   2 days ago           Exited (137) 30 hours ago                 tp-devops-2-app-1
e21d363e4326   ma_super_app   "docker-entrypoint.s…"   2 days ago           Exited (1) 2 days ago                     practical_bouman
caaaed3dfa8a   ma_super_app   "docker-entrypoint.s…"   2 days ago           Exited (1) 2 days ago                     strange_hofstadter
41735515a502   nginx:latest   "/docker-entrypoint.…"   3 weeks ago          Exited (0) 3 weeks ago                    nginx-lrdI
```
docker run -p 80:80 nginx et docker run -p -d 80:80 nginx : Démarre un serveur web disponible sur votre navigateur à l’adresse localhost:80
```
sudo docker run -p 80:80 nginx

[sudo] Mot de passe de demontis : 

Désolé, essayez de nouveau.

[sudo] Mot de passe de demontis : 

/docker-entrypoint.sh: /docker-entrypoint.d/ is not empty, will attempt to perform configuration

/docker-entrypoint.sh: Looking for shell scripts in /docker-entrypoint.d/

/docker-entrypoint.sh: Launching /docker-entrypoint.d/10-listen-on-ipv6-by-default.sh

10-listen-on-ipv6-by-default.sh: info: Getting the checksum of /etc/nginx/conf.d/default.conf

10-listen-on-ipv6-by-default.sh: info: Enabled listen on IPv6 in /etc/nginx/conf.d/default.conf

/docker-entrypoint.sh: Launching /docker-entrypoint.d/20-envsubst-on-templates.sh

/docker-entrypoint.sh: Launching /docker-entrypoint.d/30-tune-worker-processes.sh

/docker-entrypoint.sh: Configuration complete; ready for start up

2023/01/03 13:32:02 [notice] 1#1: using the "epoll" event method

2023/01/03 13:32:02 [notice] 1#1: nginx/1.23.3

2023/01/03 13:32:02 [notice] 1#1: built by gcc 10.2.1 20210110 (Debian 10.2.1-6) 

2023/01/03 13:32:02 [notice] 1#1: OS: Linux 5.15.0-56-generic

2023/01/03 13:32:02 [notice] 1#1: getrlimit(RLIMIT_NOFILE): 1048576:1048576

2023/01/03 13:32:02 [notice] 1#1: start worker processes

2023/01/03 13:32:02 [notice] 1#1: start worker process 29

2023/01/03 13:32:02 [notice] 1#1: start worker process 30

2023/01/03 13:32:02 [notice] 1#1: start worker process 31

2023/01/03 13:32:02 [notice] 1#1: start worker process 32

```

# Debut du tp 

## Exécuter un serveur web (apache, nginx, …) dans un conteneur docker
### Récupérer l’image sur le Docker Hub
```
$ docker run --name some-nginx -v /some/content:/usr/share/nginx/html:ro -d nginx
```
voici sur mon dossier :
```
sudo docker run --name some-nginx -v /Bureau/tp-1-dev-ops/TP-DevOps-1:/usr/share/nginx/html:ro -d nginx

97c0ade87015585ba0ba9be71bb455f5cfc9d06b1881fece9bd5496a6fd45660
```
### Vérifier que cette image est présente en local

```
sudo docker run --name some-nginx -v /Bureau/tp-1-dev-ops/TP-DevOps-1:/usr/share/nginx/html:ro -d nginx
```

### Créer un fichier index.html simple

```
<p>Bitbucket has the following space stations:</p>
<p>
   <b>Earth's Moon</b><br>
   Headquarters
</p>
<p>
   <b>Mars</b><br>
   Recreation Department
</p>

```

### Démarrer un conteneur et servir la page html créée précédemment à l’aide d’un volume (option -v de docker run)

```
sudo docker run --name some-nginx -v /home/demontis/Bureau/tp-1-dev-ops/TP-DevOps-1:/usr/share/nginx/html:ro -d nginx -v

7b4548491529dcac52ca430d269b0d89d20e5b60595f7b8c1cb25ff8cffcc22d
```

### Supprimer le conteneur précédent et arriver au même résultat que précédemment à l’aide de la commande docker cp

```
demontis@demontis-VirtualBox:~$ sudo docker stop 7b4

7b4

demontis@demontis-VirtualBox:~$ sudo docker rm 7b4

7b4

demontis@demontis-VirtualBox:~$ sudo docker ps -a

CONTAINER ID   IMAGE     COMMAND                  CREATED       STATUS                   PORTS     NAMES

e468eb9fe9fb   nginx     "/docker-entrypoint.…"   2 hours ago   Exited (0) 2 hours ago             gallant_joliot

f5ac1bebfa0d   nginx     "/docker-entrypoint.…"   2 hours ago   Created                            quizzical_rubin

08f8f817349a   nginx     "/docker-entrypoint.…"   2 hours ago   Created                            intelligent_feistel

ce3a282ab92f   nginx     "/docker-entrypoint.…"   2 weeks ago   Exited (0) 2 weeks ago             compassionate_feistel

5aa89f7542be   nginx     "/docker-entrypoint.…"   2 weeks ago   Created                            magical_raman
```
commande cp :
```
demontis@demontis-VirtualBox:~$ sudo docker run --name some-nginx -d -p 8080:80 nginx

88f4529c59ed7a3f9e28d58bdb0361872bc9bd610cd30cbb191b904669e811f8

demontis@demontis-VirtualBox:~$ sudo docker cp /home/demontis/Bureau/tp-1-dev-ops/TP-DevOps-1/index.html 88f4:/usr/share/nginx/html/index.html

```

## Builder une image

### A l’aide d’un Dockerfile, créer une image (commande docker build)

```

```

### Exécuter cette nouvelle image de manière à servir la page html (commande docker run)

### Quelles différences observez-vous entre les procédures 5. et 6. ? Avantages et inconvénients de l’une et de l’autre méthode ? (Mettre en relation ce qui est observé avec ce qui a été présenté pendant le cours)


## Utiliser une base de données dans un conteneur docker

### Récupérer les images mysql:5.7 et phpmyadmin/phpmyadmin depuis le Docker Hub

### Exécuter deux conteneurs à partir des images et ajouter une table ainsi que quelques enregistrements dans la base de données à l’aide de phpmyadmin


## Faire la même chose que précédemment en utilisant un fichier docker-compose.yml

### Qu’apporte le fichier docker-compose par rapport aux commandes docker run ? Pourquoi est-il intéressant ? (cf. ce qui a été présenté pendant le cours)

### Quel moyen permet de configurer (premier utilisateur, première base de données, mot de passe root, …) facilement le conteneur mysql au lancement ?


## Observation de l’isolation réseau entre 3 conteneurs

### A l’aide de docker-compose et de l’image praqma/network-multitool disponible sur le Docker Hub créer 3 services (web, app et db) et 2 réseaux (frontend et backend). Les services web et db ne devront pas pouvoir effectuer de ping de l’un vers l’autre

### Quelles lignes du résultat de la commande docker inspect justifient ce comportement ?

### Dans quelle situation réelles (avec quelles images) pourrait-on avoir cette configuration réseau ? Dans quel but ?
