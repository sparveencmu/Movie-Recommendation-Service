sudo docker build -t fastapiv1 .

sudo docker run -d --restart unless-stopped --name fastapiv1container -p 8082:8082 fastapiv1 