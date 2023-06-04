# mqtt

Shitty setup for some fermentation control

    sudo apt install mosquitto mosquitto-clients
    pip3 install paho-mqtt


modify config (check local with sudo systemctl status mosquitto) to include

    listener 1883
    allow_anonymous true


can verify publish all g

    sudo mosquitto_sub -t ferm_hot/# -p 1883


still need to add auth, grafana and some sort of restart tolerance.

