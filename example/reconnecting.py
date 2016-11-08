#!/usr/bin/env python
# -*- coding: utf-8 -*-

from sys import stdout

import txnats
from txnats import actions

from twisted.logger import globalLogPublisher
from twisted.internet import protocol
from simple_log_observer import simpleObserver
from twisted.logger import Logger
log = Logger()

from twisted.internet import reactor
from twisted.internet.endpoints import TCP4ClientEndpoint
from twisted.internet.endpoints import connectProtocol


def on_happy_msg(nats_protocol, sid, subject, reply_to, payload):
    stdout.write(
        "sid: {}, subject: {}, reply-to: {}\r\n".format(
        sid, subject, reply_to))
    stdout.write(payload.decode())
    stdout.write("\r\n*")


def create_client(reactor, host, port):
    """
    Start a Nats Protocol and connect it to a NATS endpoint over TCP4
    which subscribes to a subject.

    Reconnect and resubscribe.


Well, regardless, the logic would be the same

[9:14]  
Your subscription object should hold a notion of what the current autoUnsubscribe `max` is and what the current `delivered` is.

[9:16]  
During the reconnect sequence, once you’re reconnected, you should have a `resendSubscriptions` method/func that traverses the subscription map. For each subscription, you send a new `SUB` followed by `UNSUB <(max - delivered)>` (edited)

[9:17]  
(if `max - delivered > 0`, that is)

[9:19]  
Here’s the code from Go, which is the same logic we follow in Java, C#, and C:

[9:19]  
 ```// resendSubscriptions will send our subscription state back to the
// server. Used in reconnects
func (nc *Conn) resendSubscriptions() {
    for _, s := range nc.subs {
        adjustedMax := uint64(0)
        s.mu.Lock()
        if s.max > 0 {
            if s.delivered < s.max {
                adjustedMax = s.max - s.delivered
            }

            // adjustedMax could be 0 here if the number of delivered msgs
            // reached the max, if so unsubscribe.
            if adjustedMax == 0 {
                s.mu.Unlock()
                nc.bw.WriteString(fmt.Sprintf(unsubProto, s.sid, _EMPTY_))
                continue
            }
        }
        s.mu.Unlock()

        nc.bw.WriteString(fmt.Sprintf(subProto, s.Subject, s.Queue, s.sid))
        if adjustedMax > 0 {
            maxStr := strconv.Itoa(int(adjustedMax))
            nc.bw.WriteString(fmt.Sprintf(unsubProto, s.sid, maxStr))
        }
    }
}
    """
    log.info("Start client.")
    point = TCP4ClientEndpoint(reactor, host, port)
    backoff = txnats.Backoff()
    subscriptions = {
        "6": txnats.config_state.SubscriptionArgs(subject="happy", sid="6", on_msg=on_happy_msg)
        }
    pinger_keeper = []

    def retry(backoff, protocol):
        log.info("retry {}".format(backoff.retries))
        re_protocol = txnats.io.NatsProtocol(
            verbose=False, event_subscribers=protocol.event_subscribers)
        re_protocol.unsubs = protocol.unsubs

        #if backoff.retries < 100:
        #    log.info("reconnecting")
        #    connecting = connectProtocol(point, re_protocol)
        #    connecting.addErrback(lambda np: log.info("{p}", p=np))
        #    # Log what is returned by the connectProtocol.
        #    connecting.addCallback(lambda np: log.info("{p}", p=np))
            
    def event_subscriber(event):
        if isinstance(event, actions.Connect):
            for sid, sub in subscriptions.items():
                event.protocol.sub(sub.subject, sub.sid, sub.queue_group, sub.on_msg)
            
            event.protocol.ping_loop.start(10, now=True)
        elif isinstance(event, actions.Sub):
            subscriptions[event.sid]=txnats.config_state.SubscriptionArgs(
                subject=event.subject,
                sid=event.sid,
                queue_group=event.queue_group,
                on_msg=event.on_msg)
        elif isinstance(event, actions.Unsub):
            del subscriptions[event.sid]
        elif isinstance(event, actions.ReceivedPing):
            log.info("got Ping")
        elif isinstance(event, actions.ReceivedPong):
            log.info("got Pong")
        elif isinstance(event, actions.SendPing):
            log.info("Sending Ping")
        elif isinstance(event, actions.SendPong):
            log.info("Sending Pong")
        elif isinstance(event, actions.Disconnect):
            log.info("disconnect")
            if event.protocol.ping_loop.running:
                event.protocol.ping_loop.stop()
        elif isinstance(event, actions.ConnectionLost):
            # MAYBE defer reconnecting with a backoff
            log.info("connection lost")
            if event.protocol.ping_loop.running:
                event.protocol.ping_loop.stop()
            #connecting = connectProtocol(
            #    point, txnats.io.NatsProtocol(
            #        verbose=False, event_subscribers=event.protocol.event_subscribers))
            ## Log if there is an error making the connection.
            #connecting.addErrback(lambda np: retry(backoff, np))
            ## Log what is returned by the connectProtocol.
            #connecting.addCallback(lambda np: backoff.reset_delay())

    # Because NatsProtocol implements the Protocol interface, Twisted's
    # connectProtocol knows how to connected to the endpoint.
    connecting = connectProtocol(
        point, txnats.io.NatsProtocol(
            verbose=False, event_subscribers=[event_subscriber]))
    # Log if there is an error making the connection.
    connecting.addErrback(lambda np: log.info("{p}", p=np))
    # Log what is returned by the connectProtocol.
    connecting.addCallback(lambda np: log.info("{p}", p=np))


def main(reactor):
    host = "demo.nats.io"
    port = 4222
    create_client(reactor, host, port)

if __name__ == '__main__':
    globalLogPublisher.addObserver(simpleObserver)
    main(reactor)
    reactor.run()

