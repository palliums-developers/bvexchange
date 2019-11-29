# -*- coding: utf-8 -*-
# Generated by the protocol buffer compiler.  DO NOT EDIT!
# source: ledger_info.proto

import sys
_b=sys.version_info[0]<3 and (lambda x:x) or (lambda x:x.encode('latin1'))
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from google.protobuf import reflection as _reflection
from google.protobuf import symbol_database as _symbol_database
# @@protoc_insertion_point(imports)

_sym_db = _symbol_database.Default()


import validator_set_pb2 as validator__set__pb2


DESCRIPTOR = _descriptor.FileDescriptor(
  name='ledger_info.proto',
  package='types',
  syntax='proto3',
  serialized_options=None,
  serialized_pb=_b('\n\x11ledger_info.proto\x12\x05types\x1a\x13validator_set.proto\"\xd5\x01\n\nLedgerInfo\x12\x0f\n\x07version\x18\x01 \x01(\x04\x12$\n\x1ctransaction_accumulator_hash\x18\x02 \x01(\x0c\x12\x1b\n\x13\x63onsensus_data_hash\x18\x03 \x01(\x0c\x12\x1a\n\x12\x63onsensus_block_id\x18\x04 \x01(\x0c\x12\r\n\x05\x65poch\x18\x05 \x01(\x04\x12\x17\n\x0ftimestamp_usecs\x18\x06 \x01(\x04\x12/\n\x12next_validator_set\x18\x07 \x01(\x0b\x32\x13.types.ValidatorSet\"q\n\x18LedgerInfoWithSignatures\x12-\n\nsignatures\x18\x01 \x03(\x0b\x32\x19.types.ValidatorSignature\x12&\n\x0bledger_info\x18\x02 \x01(\x0b\x32\x11.types.LedgerInfo\"=\n\x12ValidatorSignature\x12\x14\n\x0cvalidator_id\x18\x01 \x01(\x0c\x12\x11\n\tsignature\x18\x02 \x01(\x0c\x62\x06proto3')
  ,
  dependencies=[validator__set__pb2.DESCRIPTOR,])




_LEDGERINFO = _descriptor.Descriptor(
  name='LedgerInfo',
  full_name='types.LedgerInfo',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='version', full_name='types.LedgerInfo.version', index=0,
      number=1, type=4, cpp_type=4, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='transaction_accumulator_hash', full_name='types.LedgerInfo.transaction_accumulator_hash', index=1,
      number=2, type=12, cpp_type=9, label=1,
      has_default_value=False, default_value=_b(""),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='consensus_data_hash', full_name='types.LedgerInfo.consensus_data_hash', index=2,
      number=3, type=12, cpp_type=9, label=1,
      has_default_value=False, default_value=_b(""),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='consensus_block_id', full_name='types.LedgerInfo.consensus_block_id', index=3,
      number=4, type=12, cpp_type=9, label=1,
      has_default_value=False, default_value=_b(""),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='epoch', full_name='types.LedgerInfo.epoch', index=4,
      number=5, type=4, cpp_type=4, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='timestamp_usecs', full_name='types.LedgerInfo.timestamp_usecs', index=5,
      number=6, type=4, cpp_type=4, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='next_validator_set', full_name='types.LedgerInfo.next_validator_set', index=6,
      number=7, type=11, cpp_type=10, label=1,
      has_default_value=False, default_value=None,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
  ],
  serialized_options=None,
  is_extendable=False,
  syntax='proto3',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=50,
  serialized_end=263,
)


_LEDGERINFOWITHSIGNATURES = _descriptor.Descriptor(
  name='LedgerInfoWithSignatures',
  full_name='types.LedgerInfoWithSignatures',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='signatures', full_name='types.LedgerInfoWithSignatures.signatures', index=0,
      number=1, type=11, cpp_type=10, label=3,
      has_default_value=False, default_value=[],
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='ledger_info', full_name='types.LedgerInfoWithSignatures.ledger_info', index=1,
      number=2, type=11, cpp_type=10, label=1,
      has_default_value=False, default_value=None,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
  ],
  serialized_options=None,
  is_extendable=False,
  syntax='proto3',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=265,
  serialized_end=378,
)


_VALIDATORSIGNATURE = _descriptor.Descriptor(
  name='ValidatorSignature',
  full_name='types.ValidatorSignature',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='validator_id', full_name='types.ValidatorSignature.validator_id', index=0,
      number=1, type=12, cpp_type=9, label=1,
      has_default_value=False, default_value=_b(""),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='signature', full_name='types.ValidatorSignature.signature', index=1,
      number=2, type=12, cpp_type=9, label=1,
      has_default_value=False, default_value=_b(""),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
  ],
  serialized_options=None,
  is_extendable=False,
  syntax='proto3',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=380,
  serialized_end=441,
)

_LEDGERINFO.fields_by_name['next_validator_set'].message_type = validator__set__pb2._VALIDATORSET
_LEDGERINFOWITHSIGNATURES.fields_by_name['signatures'].message_type = _VALIDATORSIGNATURE
_LEDGERINFOWITHSIGNATURES.fields_by_name['ledger_info'].message_type = _LEDGERINFO
DESCRIPTOR.message_types_by_name['LedgerInfo'] = _LEDGERINFO
DESCRIPTOR.message_types_by_name['LedgerInfoWithSignatures'] = _LEDGERINFOWITHSIGNATURES
DESCRIPTOR.message_types_by_name['ValidatorSignature'] = _VALIDATORSIGNATURE
_sym_db.RegisterFileDescriptor(DESCRIPTOR)

LedgerInfo = _reflection.GeneratedProtocolMessageType('LedgerInfo', (_message.Message,), {
  'DESCRIPTOR' : _LEDGERINFO,
  '__module__' : 'ledger_info_pb2'
  # @@protoc_insertion_point(class_scope:types.LedgerInfo)
  })
_sym_db.RegisterMessage(LedgerInfo)

LedgerInfoWithSignatures = _reflection.GeneratedProtocolMessageType('LedgerInfoWithSignatures', (_message.Message,), {
  'DESCRIPTOR' : _LEDGERINFOWITHSIGNATURES,
  '__module__' : 'ledger_info_pb2'
  # @@protoc_insertion_point(class_scope:types.LedgerInfoWithSignatures)
  })
_sym_db.RegisterMessage(LedgerInfoWithSignatures)

ValidatorSignature = _reflection.GeneratedProtocolMessageType('ValidatorSignature', (_message.Message,), {
  'DESCRIPTOR' : _VALIDATORSIGNATURE,
  '__module__' : 'ledger_info_pb2'
  # @@protoc_insertion_point(class_scope:types.ValidatorSignature)
  })
_sym_db.RegisterMessage(ValidatorSignature)


# @@protoc_insertion_point(module_scope)
