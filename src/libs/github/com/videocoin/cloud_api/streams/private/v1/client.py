import logging

import grpc
from django.conf import settings

from github.com.videocoin.cloud_api.streams.private.v1 import streams_service_pb2
from github.com.videocoin.cloud_api.streams.private.v1 import streams_service_pb2_grpc

logger = logging.getLogger(__name__)


class Singleton(type):
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = \
                super(Singleton, cls).__call__(*args, **kwargs)

        return cls._instances[cls]


class StreamsServiceClient(metaclass=Singleton):
    TIMEOUT = 5
    LIVE_TIMEOUT = 20

    def __init__(self, *args, **kwargs):
        self.channel = grpc.insecure_channel(settings.PRIVATE_STREAMS_RPC_ADDR)
        self.stub = streams_service_pb2_grpc.StreamsServiceStub(self.channel)
        super().__init__(*args, **kwargs)

    def get_stream(self, stream_id):
        req = streams_service_pb2.StreamRequest(id=stream_id)
        return self.stub.Get(req, timeout=self.TIMEOUT)

    def start_stream(self, stream_id):
        req = streams_service_pb2.StreamRequest(id=stream_id)
        return self.stub.Run(req, timeout=self.LIVE_TIMEOUT)

    def stop_stream(self, stream_id):
        req = streams_service_pb2.StreamRequest(id=stream_id)
        return self.stub.Stop(req, timeout=self.LIVE_TIMEOUT)
