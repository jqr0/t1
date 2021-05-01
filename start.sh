#!/bin/bash

service caddy start
yes "4" | bash status.sh s

yes "4" | bash status.sh c


touch /root/.aria2/aria2.session
chmod 0777 /root/.aria2/ -R

mkdir /.config/
mkdir /.config/rclone
touch /.config/rclone/rclone.conf
echo "$Rclone" >>/.config/rclone/rclone.conf
wget git.io/tracker.sh
chmod 0777 /tracker.sh
/bin/bash tracker.sh "/root/.aria2/aria2.conf"

git clone https://github.com/jqr0/t1
mkdir /bot/
mv /new_bot/bot/* /bot/
chmod 0777 /bot/ -R
rm -rf /new_bot

nohup aria2c --conf-path=/root/.aria2/aria2.conf --rpc-listen-port=8080 --rpc-secret=$Aria2_secret &
nohup python3 /bot/web.py &

python3 /bot/main.py
