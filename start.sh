sudo docker rm -f zeafrost

sudo docker run --name zeafrost \
	--restart=always \
	-p 5001:5000 \
	--network=bridge-net \
	-v /server/zeafrost:/app \
	-v /mnt:/mnt \
	-d \
	zeafrost:1.0
