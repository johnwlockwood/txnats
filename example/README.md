# Command and control

Run `python sense_led_serve.py` from a Raspberry Pi with a SenseHat installed


Run `send_sense.py` from another computer to send messages to be displayed on the SenseHat's 8x8 LED grid.

```
$python send_sense.py hello, world

```

This is an example of controlling devices over the network.

I recommend downloading the `gnatsd` server from [nats.io](http://nats.io) and running it and then run these scripts with `--host` set to the address of the computer running it.

