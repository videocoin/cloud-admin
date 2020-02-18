from django.conf import settings

from videocoin.blockchain import Blockchain
from videocoin.validators import ValidatorCollection


class BlockchainConnectionError(Exception):
    pass


def get_blockchain_events(stream):
    blockchain = Blockchain(
        settings.RPC_NODE_HTTP_ADDR,
        stream_id=stream.stream_contract_id,
        stream_address=stream.stream_contract_address,
        stream_manager_address=settings.STREAM_MANAGER_CONTRACT_ADDR
    )
    if not blockchain.is_connected():
        raise BlockchainConnectionError
    events = blockchain.get_all_events()
    return events


def validate_stream(stream):
    events = get_blockchain_events(stream)
    validator = ValidatorCollection(
        events=events,
        input_url=stream.input_url,
        output_url=stream.output_url
    )
    return validator
