# Online_Shop_IEP
Dockerized python application made with flask and sql alchemy,  for online shop with three types of users, JWT authentication,

pip install -r requirements.txt
docker-compose -f development up -d (probaj bez d)
 python manage.py db init        
python manage.py db migrate -m "Initial migration"
python manage.py db upgrade -> da doda migraciju u bazu tj date tabele
kad napravis migracije one su u okviru projekta, treba samo da pozivas upgrade
 docker build -f authentification.dockerfile -t authentification . 
docker volume ls -  za proveru da li je disk ok
docker volume rm ime_voluma
