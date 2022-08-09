# How to guide

Please install the requirements using

<code>
pip3 install -r requirements.txt
</code>

The server has to be started before the client.

---
## Server

Run the server using 

<code>
python3 producer.py
</code>


---
## Client

Run the client using 

<code>
python3 consumer.py
</code>


---


To mimic a broken connection use <code>iptables</code> to drop packets on one of the ports. The client identifies that the connection is broken and recreates a new one in some time. 

<code>
sudo iptables -A INPUT -p tcp --destination-port $PORT -j DROP
</code>

here, $PORT is the client port you want to block for mimicking a broken connection. 
---
Parameters to play around. 

**ping_interval**: This sets a time interval after which the server/client send a ping request, to which a pong response is sent. No pong response implies a broken connection.

