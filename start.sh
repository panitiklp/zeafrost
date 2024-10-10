sudo docker rm -f zeafrost

sudo docker run --name zeafrost \
	--restart=always \
	-p 5002:5000 \
	--network=spw-bridge \
	-v /server/zeafrost:/app \
	-v /mnt:/mnt \
	-d \
	zeafrost:1.0
