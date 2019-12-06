# -*- coding: utf-8 -*-
# Generated by the protocol buffer compiler.  DO NOT EDIT!
# source: account_state_blob.proto

import sys
_b=sys.version_info[0]<3 and (lambda x:x) or (lambda x:x.encode('latin1'))
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from google.protobuf import reflection as _reflection
from google.protobuf import symbol_database as _symbol_database
# @@protoc_insertion_point(imports)

_sym_db = _symbol_database.Default()


import proof_pb2 as proof__pb2


DESCRIPTOR = _descriptor.FileDescriptor(
  name='account_state_blob.proto',
  package='types',
  syntax='proto3',
  serialized_options=None,
  serialized_pb=_b('\n\x18\x61\x63\x63ount_state_blob.proto\x12\x05types\x1a\x0bproof.proto\" \n\x10\x41\x63\x63ountStateBlob\x12\x0c\n\x04\x62lob\x18\x01 \x01(\x0c\"x\n\x15\x41\x63\x63ountStateWithProof\x12\x0f\n\x07version\x18\x01 \x01(\x04\x12%\n\x04\x62lob\x18\x02 \x01(\x0b\x32\x17.types.AccountStateBlob\x12\'\n\x05proof\x18\x03 \x01(\x0b\x32\x18.types.AccountStateProofb\x06proto3')
  ,
  dependencies=[proof__pb2.DESCRIPTOR,])




_ACCOUNTSTATEBLOB = _descriptor.Descriptor(
  name='AccountStateBlob',
  full_name='types.AccountStateBlob',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='blob', full_name='types.AccountStateBlob.blob', index=0,
      number=1, type=12, cpp_type=9, label=1,
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
  serialized_start=48,
  serialized_end=80,
)


_ACCOUNTSTATEWITHPROOF = _descriptor.Descriptor(
  name='AccountStateWithProof',
  full_name='types.AccountStateWithProof',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='version', full_name='types.AccountStateWithProof.version', index=0,
      number=1, type=4, cpp_type=4, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='blob', full_name='types.AccountStateWithProof.blob', index=1,
      number=2, type=11, cpp_type=10, label=1,
      has_default_value=False, default_value=None,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='proof', full_name='types.AccountStateWithProof.proof', index=2,
      number=3, type=11, cpp_type=10, label=1,
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
  serialized_start=82,
  serialized_end=202,
)

_ACCOUNTSTATEWITHPROOF.fields_by_name['blob'].message_type = _ACCOUNTSTATEBLOB
_ACCOUNTSTATEWITHPROOF.fields_by_name['proof'].message_type = proof__pb2._ACCOUNTSTATEPROOF
DESCRIPTOR.message_types_by_name['AccountStateBlob'] = _ACCOUNTSTATEBLOB
DESCRIPTOR.message_types_by_name['AccountStateWithProof'] = _ACCOUNTSTATEWITHPROOF
_sym_db.RegisterFileDescriptor(DESCRIPTOR)

AccountStateBlob = _reflection.GeneratedProtocolMessageType('AccountStateBlob', (_message.Message,), {
  'DESCRIPTOR' : _ACCOUNTSTATEBLOB,
  '__module__' : 'account_state_blob_pb2'
  # @@protoc_insertion_point(class_scope:types.AccountStateBlob)
  })
_sym_db.RegisterMessage(AccountStateBlob)

AccountStateWithProof = _reflection.GeneratedProtocolMessageType('AccountStateWithProof', (_message.Message,), {
  'DESCRIPTOR' : _ACCOUNTSTATEWITHPROOF,
  '__module__' : 'account_state_blob_pb2'
  # @@protoc_insertion_point(class_scope:types.AccountStateWithProof)
  })
_sym_db.RegisterMessage(AccountStateWithProof)


# @@protoc_insertion_point(module_scope)