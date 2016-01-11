init-logs:
	sudo mkdir /app-logs
	sudo chmod ugo+w /app-logs

install-pypy:
	sudo mv pypy-4.0.1-linux-armhf-raspbian /usr/local/
	sudo chmod -R ugo+x /usr/local/pypy-4.0.1-linux-armhf-raspbian 
	sudo chown -R root:staff /usr/local/pypy-4.0.1-linux-armhf-raspbian 

pypy-get-pip:
	sudo /usr/local/pypy-4.0.1-linux-armhf-raspbian/bin/pypy ./get-pip.py

install-txnats:
	sudo /usr/local/pypy-4.0.1-linux-armhf-raspbian/bin/pip install txnats

link-pypy:
	sudo ln -s /usr/local/pypy-4.0.1-linux-armhf-raspbian/bin/pypy ~/bin/ 

add-services:
	sudo cp nats.respond.1.service /etc/systemd/system/nats.respond.1.service
	sudo cp nats.respond.1.service /etc/systemd/system/nats.respond.2.service
	sudo cp nats.respond.1.service /etc/systemd/system/nats.respond.3.service
	sudo cp nats.respond.1.service /etc/systemd/system/nats.respond.4.service
	sudo systemctl daemon-reload

start-services:
	sudo systemctl start nats.respond.1
	sudo systemctl start nats.respond.2
	sudo systemctl start nats.respond.3
	sudo systemctl start nats.respond.4

restart-services:
	sudo systemctl restart nats.respond.1
	sudo systemctl restart nats.respond.2
	sudo systemctl restart nats.respond.3
	sudo systemctl restart nats.respond.4

stop-services:
	sudo systemctl stop nats.respond.1
	sudo systemctl stop nats.respond.2
	sudo systemctl stop nats.respond.3
	sudo systemctl stop nats.respond.4

enable-services:
	sudo systemctl enable nats.respond.1.service
	sudo systemctl enable nats.respond.2.service
	sudo systemctl enable nats.respond.3.service
	sudo systemctl enable nats.respond.4.service

disable-services:
	sudo systemctl disable nats.respond.1.service
	sudo systemctl disable nats.respond.2.service
	sudo systemctl disable nats.respond.3.service
	sudo systemctl disable nats.respond.4.service

status-services:
	sudo systemctl status nats.respond.1.service
	sudo systemctl status nats.respond.2.service
	sudo systemctl status nats.respond.3.service
	sudo systemctl status nats.respond.4.service
