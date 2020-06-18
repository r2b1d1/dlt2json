#-*- coding: utf-8 -*-
'''
convert a dlt file into json
focused only on logs
'''
import struct
import string
import json
from textwrap import wrap
from logzero import logger, loglevel
import logging
from argparse import ArgumentParser

__author__ = 'Riadh Abidi'
__email__ = 'riadh.abidi@outlook.com'
__version__ = '0.0.1'

STORAGE_HEADER_OFFSET = 0x00
STANDARD_HEADER_OFFSET = 0x10
STANDARD_HEADER_EXTRA_OFFSET = 0x14
ECU_ID_OFFSET = 0x04
SESSION_ID_OFFSET = 0x04
TIMESTAMP_OFFSET = 0x04
EXTENDED_HEADER_OFFSET = 0x0a

HAS_EXTENDED_HEADER = 0x01
HAS_ECU_ID = 0x04
HAS_SESSION_ID = 0x08
HAS_TIMESTAMP = 0x10

MSG_TYPE = 0x0e
MSG_TYPE_INFO = 0xf0
MSG_TYPE_SHIFT = 1
MSG_TYPE_INFO_SHIFT = 4

ARG_TYPE_OFFSET = 0x00
ARG_OFFSET = 0x04

BOOL = 0x00000010
SIGNED_INT = 0x00000020
UNSIGNED_INT = 0x00000040
FLOAT = 0x00000080
STRING = 0x00000200
RAW_DATA = 0x00000400

TYLE = 0x0000000f
TYLE_8BIT = 0x00000001
TYLE_16BIT = 0x00000002
TYLE_32BIT = 0x00000003
TYLE_64BIT = 0x00000004
TYLE_128BIT = 0x00000005

TYPES = ['log', 'app trace', 'network trace', 'control']
INFO = {
    'log': ['off', 'fatal', 'error', 'warning', 'info', 'debug', 'verbose'],
    'control': ['', 'request', 'response', 'time'],
    'app trace': ['', 'variable', 'func_in', 'func_out', 'state', 'vfb'],
    'network trace': ['', 'ipc', 'can', 'flexray', 'most', 'vfb']
}


def decode_str(s):
    s = s.decode(errors='replace')
    return ''.join(list(map(lambda x: x if x in string.printable else '', s)))


def decode_info(info):
    if info == 'N/A':
        return 'N/A', 'N/A'

    msg_type = TYPES[(info & MSG_TYPE) >> MSG_TYPE_SHIFT]
    msg_info = INFO[msg_type][(info & MSG_TYPE_INFO) >> MSG_TYPE_INFO_SHIFT]

    return msg_type, msg_info


def parse_bool(offset, payload):
    value, = struct.unpack_from('B', payload, offset)
    offset += 1
    return offset, value


def parse_num(arg_type, ntype, sign, offset, payload):
    if ((arg_type & TYLE) == TYLE_8BIT):
        fmt = sign == 's' and 'b' or 'B'
        value, = struct.unpack_from(fmt, payload, offset)
        offset += 1
    elif ((arg_type & TYLE) == TYLE_16BIT):
        fmt = sign == 's' and 'h' or 'H'
        value, = struct.unpack_from(fmt, payload, offset)
        offset += 2
    elif ((arg_type & TYLE) == TYLE_32BIT):
        fmt = ntype == 'f' and 'f' or (sign == 's' and 'i' or 'I')
        value, = struct.unpack_from(fmt, payload, offset)
        offset += 4
    elif ((arg_type & TYLE) == TYLE_64BIT):
        fmt = ntype == 'f' and 'd' or (sign == 's' and 'q' or 'Q')
        value, = struct.unpack_from(fmt, payload, offset)
        offset += 8
    elif ((arg_type & TYLE) == TYLE_128BIT):
        value = payload[:16].hex()
        offset += 16
    return offset, fmt, value


def parse_string(offset, payload):
    length, = struct.unpack_from('H', payload, offset)
    offset += 2
    string, = struct.unpack_from(f'{length}s', payload, offset)
    offset += length
    return offset, decode_str(string)


def parse_raw(offset, payload):
    length, = struct.unpack_from('H', payload, offset)
    offset += 2
    if length:
        raw, = struct.unpack_from(f'{length}p', payload, offset)
        offset += length
    else:
        return offset, ''
    return offset, ' '.join(wrap(raw.hex(), 2))


def parse_payload(msg_type, payload):
    if msg_type != 'log':
        payload_decoded = ' '.join(wrap(payload.hex(), 2))
        logger.warn(f'not supported {payload_decoded}')
        return payload_decoded

    offset = 0
    payload_decoded = []
    while offset < len(payload):
        arg_type, = struct.unpack_from('I', payload, offset)
        offset += ARG_OFFSET
        if arg_type & BOOL:
            offset, value = parse_bool(offset, payload)
            payload_decoded.append(value)
            logger.debug(f'bool: {value}')
        elif arg_type & SIGNED_INT:
            offset, fmt, value = parse_num(arg_type, 'i', 's', offset, payload)
            payload_decoded.append(value)
            logger.debug(f'signed: {fmt} {value}')
        elif arg_type & UNSIGNED_INT:
            offset, fmt, value = parse_num(arg_type, 'i', 'u', offset, payload)
            payload_decoded.append(value)
            logger.debug(f'unsigned: {fmt} {value}')
        elif arg_type & FLOAT:
            offset, fmt, value = parse_num(arg_type, 'f', 'f', offset, payload)
            payload_decoded.append(value)
            logger.debug(f'float: {fmt} {value}')
        elif arg_type & STRING:
            offset, string = parse_string(offset, payload)
            payload_decoded.append(string)
            string = [string]
            logger.debug(f'string: {string}')
        elif arg_type & RAW_DATA:
            offset, raw = parse_raw(offset, payload)
            payload_decoded.append(raw)
            logger.debug(f'raw: {raw}')
        else:
            payload_decoded = ' '.join(wrap(payload[offset:].hex(), 2))
            offset = len(payload)
            logger.warn(f'not supported {payload_decoded}')

    return ' '.join(str(x) for x in payload_decoded)


def parse_msg(msg):
    pattern, sec, msec, ecu = struct.unpack_from(
                                                    '4sIi4s',
                                                    msg,
                                                    STORAGE_HEADER_OFFSET
                                                )
    htyp, mcnt, length = struct.unpack_from('BBH', msg, STANDARD_HEADER_OFFSET)

    offset = STANDARD_HEADER_EXTRA_OFFSET
    if htyp & HAS_ECU_ID:
        ecu, = struct.unpack_from('4s', msg, offset)
        offset += ECU_ID_OFFSET
    if htyp & HAS_SESSION_ID:
        sid, = struct.unpack_from('I', msg, offset)
        offset += SESSION_ID_OFFSET
    else:
        sid = 'N/A'
    if htyp & HAS_TIMESTAMP:
        tmsp, = struct.unpack_from('I', msg, offset)
        offset += TIMESTAMP_OFFSET
    else:
        tmsp = 'N/A'

    if htyp & HAS_EXTENDED_HEADER:
        info, args, app, ctx = struct.unpack_from('BB4s4s', msg, offset)
        offset += EXTENDED_HEADER_OFFSET
    else:
        info, args, app, ctx = ('N/A', 'N/A', b'N/A', b'N/A')

    info = decode_info(info)
    msg_type = info[0]
    msg_info = info[1]

    logger.debug(f'type: {msg_type}')

    return {
                'seconds': sec,
                'microSeconds': msec,
                'ecu': decode_str(ecu),
                'sid': sid,
                'timestamp': tmsp,
                'app': decode_str(app),
                'ctx': decode_str(ctx),
                'type': msg_type,
                'info': msg_info,
                'args': args,
                'payload': parse_payload(msg_type, msg[offset:])
    }


def parse_buffer(data):
    if not data:
        raise Exception('data missing')
    if (data[0] != 0x44 or
            data[1] != 0x4c or
            data[2] != 0x54 or
            data[3] != 0x01):
        raise TypeError('not a dlt file')

    i = 0
    j = 0
    msgs = []
    while i < len(data):
        if (data[i] == 0x44 and
                data[i+1] == 0x4c and
                data[i+2] == 0x54 and
                data[i+3] == 0x01):
            if i > 0:
                msgs.append(data[j:i])
                j = i
        i += 1
    msgs.append(data[j:i])

    length = len(msgs)
    logger.info(f'found {length} messages')

    decoded = []
    for i, msg in enumerate(msgs):
        logger.debug(f'raw: {msg.hex()}')
        index = str(i).zfill(len(str(length)))
        msg = parse_msg(msg)
        decoded.append({index: msg})
        logger.info({index: msg})

    return decoded


def main():
    parser = ArgumentParser(description='convert dlt to json')
    parser.add_argument('file', help='dlt file to convert')
    parser.add_argument('--log',
                        '-l',
                        choices=['off', 'dbg', 'info', 'warn', 'err', 'crit'],
                        help='set log level')
    args = parser.parse_args()

    if args.file:
        with open(args.file, 'rb') as file:
            data = file.read()

    if args.log:
        level = {
            'off': logging.NOTSET,
            'dbg': logging.DEBUG,
            'info': logging.INFO,
            'warn': logging.WARNING,
            'err': logging.ERROR,
            'crit': logging.CRITICAL

        }
        loglevel(level[args.log])
    else:
        loglevel(logging.ERROR)

    try:
        try:
            decoded = parse_buffer(data)
            print(json.dumps(decoded, indent=2))
        except TypeError as err:
            logger.error(err)
            exit(1)
    except KeyboardInterrupt:
        exit(0)

if __name__ == '__main__':
    main()
