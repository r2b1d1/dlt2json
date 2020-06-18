# dlt2json

Convert a [GENIVI]'s dlt file to json format.

This is a draft version and only supports log type for now.

Control, app trace and network trace payload is encoded in hexadecimal.

- DLT message format

##*Header*

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

##*payload*

0..4    4 bytes argument type

5..6    2 argument size

....    argument













[GENIVI]: https://at.projects.genivi.org/wiki/display/PROJ/Diagnostic+Log+and+Trace
