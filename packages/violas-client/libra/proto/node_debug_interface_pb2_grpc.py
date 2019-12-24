# Generated by the gRPC Python protocol compiler plugin. DO NOT EDIT!
import grpc

import node_debug_interface_pb2 as node__debug__interface__pb2


class NodeDebugInterfaceStub(object):
  # missing associated documentation comment in .proto file
  pass

  def __init__(self, channel):
    """Constructor.

    Args:
      channel: A grpc.Channel.
    """
    self.GetNodeDetails = channel.unary_unary(
        '/debug.NodeDebugInterface/GetNodeDetails',
        request_serializer=node__debug__interface__pb2.GetNodeDetailsRequest.SerializeToString,
        response_deserializer=node__debug__interface__pb2.GetNodeDetailsResponse.FromString,
        )
    self.GetEvents = channel.unary_unary(
        '/debug.NodeDebugInterface/GetEvents',
        request_serializer=node__debug__interface__pb2.GetEventsRequest.SerializeToString,
        response_deserializer=node__debug__interface__pb2.GetEventsResponse.FromString,
        )


class NodeDebugInterfaceServicer(object):
  # missing associated documentation comment in .proto file
  pass

  def GetNodeDetails(self, request, context):
    """Returns debug information about node
    """
    context.set_code(grpc.StatusCode.UNIMPLEMENTED)
    context.set_details('Method not implemented!')
    raise NotImplementedError('Method not implemented!')

  def GetEvents(self, request, context):
    """Returns recent events generated by event! macro
    """
    context.set_code(grpc.StatusCode.UNIMPLEMENTED)
    context.set_details('Method not implemented!')
    raise NotImplementedError('Method not implemented!')


def add_NodeDebugInterfaceServicer_to_server(servicer, server):
  rpc_method_handlers = {
      'GetNodeDetails': grpc.unary_unary_rpc_method_handler(
          servicer.GetNodeDetails,
          request_deserializer=node__debug__interface__pb2.GetNodeDetailsRequest.FromString,
          response_serializer=node__debug__interface__pb2.GetNodeDetailsResponse.SerializeToString,
      ),
      'GetEvents': grpc.unary_unary_rpc_method_handler(
          servicer.GetEvents,
          request_deserializer=node__debug__interface__pb2.GetEventsRequest.FromString,
          response_serializer=node__debug__interface__pb2.GetEventsResponse.SerializeToString,
      ),
  }
  generic_handler = grpc.method_handlers_generic_handler(
      'debug.NodeDebugInterface', rpc_method_handlers)
  server.add_generic_rpc_handlers((generic_handler,))
