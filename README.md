# [NATS.io](http://nats.io) messaging system client for the Twisted matrix

[![License MIT](https://img.shields.io/npm/l/express.svg)](http://opensource.org/licenses/MIT)

[NATS Documentation](http://nats.io/documentation/)

## HOW TO microservice communication.

How do I get my services to talk to each other with out registering each
one in a directory?

How do I scale a back end service and allow front end services to use all of
them quickly?

How do I have a fast, scalable, resilient communication service with out a lot
of headaches?

A good answer to all of these is to use NATS.
NATS is a masterpiece protocol designed with the cloud in mind. HTTP 
was good, but it was designed for servers sending single resources to
clients on an uncontrolled network.

## Install dependencies
I suggest creating a virtualenv.

    $ make deps

## Try the demo:

    $ make prepare-example

Open two extra terminal windows and from one run:

    $ ./example/respond.py
    
from the other run:

    $ ./example/sub_only.py 
    
Then from the first window run:

    ./example/nats_demo.py

## Usage

###Make a subject subscriber. 
for full context see [sub_only.py](example/sub_only.py):

First, define a message handler for a subscription:

    def on_happy_msg(nats_protocol, sid, subject, reply_to, payload):
        print "got message", sid, subject

Then in create the endpoint, nats protocol instance and connect them:

    point = TCP4ClientEndpoint(reactor, "demo.nats.io", 4222)

    nats_protocol = txnats.io.NatsProtocol(
        verbose=False,
        on_connect=lambda np: np.sub("happy", "6", on_msg=on_happy_msg))

    connecting = connectProtocol(point, nats_protocol)
    reactor.run()

When a message comes in for the subject "happy" `on_happy_msg` will be called.

###Make a subject responder.

The only difference from a subscriber is that the `on_msg` function
will publish a message to the `reply_to` subject of the message:

    def respond_on_msg(nats_protocol, sid, subject, reply_to, payload):
        if reply_to:
            nats_protocol.pub(reply_to, "Roger, from {}!".format(responder_id))

...:

    nats_protocol = txnats.io.NatsProtocol(
        verbose=False,
        on_connect=lambda np: np.sub("getResponse", "6", on_msg=respond_on_msg))

For full context see [respond.py](example/respond.py)

###Distribute the responder load.

To distribute the load: subscribe with a queue-group
and any message will go to one of the responders:

    nats_protocol = txnats.io.NatsProtocol(
        verbose=False,
        on_connect=lambda np: np.sub("getResponse", "6", 
                                     queue_group="excelsior", 
                                     on_msg=respond_on_msg))

However many processes you have subscribed to this subject and queue group
will have the messages sent to only one of them. If there are four running,
and 100 messages are sent on the "get-response" subject, each one should 
only have to respond to 25, distributing the work load.

For full context see [queue_respond.py](example/queue_respond.py) and
something that will make a bunch of requests on that subject.
[make_requests.py](example/make_requests.py)

