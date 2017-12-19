# hollapy
A simple python client for the hollaback server.

# Setup
You need a config file. From your hollaback server run:
```sh

# php /opt/hollaback/createuser.php user
{
  "default" : {
    "serv" : "<server location>",
      "creds" : {
      "user" : "user",
      "pass" : "b1dc3540ac7db138c4568dfc04251723"
    }
  }
}
```

put that into ~/.config/hollaback.json. On your client machine. Change the
value of "serv" to point to your hollaback server. Then run hollapy with -h to
get options.

```sh
$ python hollaback.py -h
usage: hollaback.py [-h] [-q] [-g] [-c] [-b] [-t TOKEN] [-v VISIT] [-l]
                    [--comment COMMENT] [--test_name TEST_NAME]
                    [--cust_name CUST_NAME] [--ttl TTL]
                    [--reply_method REPLY_METHOD] [--consume CONSUME]
                    [--payid PAYID] [--payparam PAYPARAM] [--clean] [--nc]

Interact with a Hollaback Server

optional arguments:
  -h, --help            show this help message and exit
  -q, --quick           Like tailing the logs for a single URL, ctrl+c to stop
  -g, --get             Get a callback url
  -c, --check           Check on a callback token (-t required)
  -b, --block           Check every second until callback is used (-t
                        required)
  -t TOKEN, --token TOKEN
                        Token value
  -v VISIT, --visit VISIT
                        Get details of visit for visit numer
  -l, --list            List the payloads on the server
  --comment COMMENT     Comment to save on server
  --test_name TEST_NAME
                        Test name to save on server
  --cust_name CUST_NAME
                        Customer name to save on server
  --ttl TTL             TTL of callback URL
  --reply_method REPLY_METHOD
                        How it should respond
  --consume CONSUME     Int number of times used before consumed
  --payid PAYID         index of payload to be used
  --payparam PAYPARAM   String to be passed as a parameter to the payload
  --clean               Remove token info from the server when you are done
  --nc                  Remove color display

```

## demo

[![asciicast](https://asciinema.org/a/Mw2GDPrIAJMBi8RzlVE6NYzWu.png)](https://asciinema.org/a/Mw2GDPrIAJMBi8RzlVE6NYzWu)
