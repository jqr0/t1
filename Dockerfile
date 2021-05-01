FROM benchao/newubuntu:1.0



RUN mkdir /root/.aria2
COPY config /root/.aria2/

COPY root /

RUN pip3 install -r requirements.txt

#COPY bot /bot

RUN sudo chmod 777 /root/.aria2/
RUN sudo chmod 777 /rclone
RUN mv /rclone /usr/bin/

CMD wget https://raw.githubusercontent.com/jqr0/t1/main/start.sh  && chmod 0777 start.sh && bash start.sh
