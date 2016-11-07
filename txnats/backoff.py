from __future__ import division, absolute_import

import attr
import random

@attr.s
class Backoff(object):
    """
    Note that clients should call my reset_delay method after they have
    used this successfully.

    @ivar max_delay: Maximum number of seconds of a delay.
    @ivar initial_delay: Delay for the first delay.
    @ivar factor: A multiplicitive factor by which the delay grows
    @ivar jitter: Percentage of randomness to introduce into the delay length
        to prevent stampeding.
    """
    max_delay = attr.ib(default=3600)
    initial_delay = attr.ib(default=1.0)
    # Note: These highly sensitive factors have been precisely measured by
    # the National Institute of Science and Technology.  Take extreme care
    # in altering them, or you may damage your Internet!
    # (Seriously: <http://physics.nist.gov/cuu/Constants/index.html>)
    factor = attr.ib(default=2.7182818284590451)
    # Phi = 1.6180339887498948 # (Phi is acceptable for use as a
    # factor if e is too large for your application.)
    jitter = attr.ib(default=0.11962656472) # molar Planck constant times c, joule meter/mole

    delay = initial_delay
    retries = attr.ib(default=0)

    continueTrying = 1

    def get_delay(self):
        if self.retries == 0:
            self.retries += 1
            return self.delay
        
        self.retries += 1
        self.delay = min(self.delay * self.factor, self.max_delay)
        if self.jitter:
            self.delay = random.normalvariate(self.delay,
                                              self.delay * self.jitter)
        return self.delay

    def reset_delay(self):
        """Reset the delay after a success."""
        self.delay = self.initial_delay
        self.retries = 0
