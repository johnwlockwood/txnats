# Make a service on a Raspberry Pi 2 running Rasbian jessie

Jessie comes with systemd installed, which can be used to
start services upon boot.

## Run a NATS worker on your pi.

Prerequisites:
 - Raspberry Pi 2 with Rasbian jessie
 - On your network
 - You learn the ip.
 - For convenience of not having enter a password every time
     authorize your public key on the pi.
    - `scp ~/.ssh/id_rsa.pub pi@`<ip>`:/home/pi/.ssh/jill_rsa.pub`
    - ssh into the pi and append the contents of `jill_rsa.pub` to ~/.ssh/authorized_keys

Steps:
 - download pypy for Rasbian: https://bitbucket.org/pypy/pypy/downloads/pypy-4.0.1-linux-armhf-raspbian.tar.bz2
 - bunzip2 it and put it in /home/pi/ on the pi.
 - Extract the tar: `tar -xvf  pypy-4.0.1-linux-armhf-raspbian.tar`
 - clone this repo to /home/pi/projects/ (hardcoded in the `.service` file)
 - copy this Makefile and nats.respond.1.service to /home/pi/ as that is where I wrote it and hardcoded some paths.  TODO: Use environmental variables or maybe do this [Chef](http://everydaytinker.com/raspberry-pi/installing-chef-client-on-a-raspberry-pi-2-model-b/)
 - ssh into the pi
 - download `get-pip.py` to /home/pi/
    - `curl -o get-pip2.py https://bootstrap.pypa.io/get-pip.py`
 - `make install-pypy`
 - `make pypy-get-pip`
 - `make install-txnats`

Setup and start the services
This will make four copies of the respond service.
 - `make add-services`
 - `make start-services`
 - `make enable-services`

See the status of the services:
 - `make status-services`

From your local machine you should now be able to run make_requests.py
and the services on the pi will respond.

