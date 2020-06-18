# dlt2json

Convert a [GENIVI]'s dlt file to json format.

This is a draft version and only supports log type for now.

Control, app trace and network trace payload is encoded in hexadecimal.

## DLT message format

### Header

0..3    header pattern DLT1

4..7    4 bytes epoch time (little endian)

8..11   4 bytes microseconds (little endian)

12..15  4 bytes ECU ID

16      1 byte header type contains some configuration data

* use extended header
* MSB first
* with ECU ID
* with session ID
* with timestamp
* version number, 0x1

17      1 byte message counter

18..19  2 bytes lentgh of complete message without header

20..23  4 bytes ECU ID again

24..27  4 bytes session number

28..31  4 bytes timestamp since system start in 0.1 milliseconds

32      1 byte message info contains some configuration data too

* message type (log, app trace, network trace, control)
* message type info (debug, error, ...)

33      1 byte number of arguments

34..37  4 bytes application ID

38..41  4 bytes context id

### payload

0..4    4 bytes argument type

5..6    2 argument size

....    argument


## install

```sh
$ python setup.py install
```

## Usage

For a quick test, download [testfile.dlt] and run

```sh
$ dlt2json testfile.dlt
[
  {
    "000": {
      "seconds": 1305029670,
      "microSeconds": 828120,
      "ecu": "ECU",
      "sid": "N/A",
      "timestamp": 979535935,
      "app": "APP",
      "ctx": "CON",
      "type": "control",
      "info": "request",
      "args": 1,
      "payload": "11 00 00 00 04 72 65 6d 6f"
    }
  },
  ...
  {
    "030": {
      "seconds": 1305029677,
      "microSeconds": 562582,
      "ecu": "ECU",
      "sid": "N/A",
      "timestamp": "N/A",
      "app": "LOG",
      "ctx": "TES4",
      "type": "log",
      "info": "info",
      "args": 2,
      "payload": "0 Hello world"
    }
  },
  ...
  {
    "104": {
      "seconds": 1305029689,
      "microSeconds": 47104,
      "ecu": "ECU",
      "sid": "N/A",
      "timestamp": "N/A",
      "app": "N/A",
      "ctx": "N/A",
      "type": "N/A",
      "info": "N/A",
      "args": "N/A",
      "payload": "91 01 00 00 1a 00 00 00 0c 00 48 65 6c 6c 6f 20 77 6f 72 6c 64 00"
    }
  }
]
```

[GENIVI]: https://at.projects.genivi.org/wiki/display/PROJ/Diagnostic+Log+and+Trace
[testfile.dlt]: https://github.com/GENIVI/dlt-daemon/blob/master/tests/testfile.dlt?raw=true
