# nats.io client for the Twisted matrix

[![License MIT](https://img.shields.io/npm/l/express.svg)](http://opensource.org/licenses/MIT)

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

