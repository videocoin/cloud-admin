import os
import json

from web3 import Web3
from web3.utils.contracts import find_matching_event_abi
from web3.utils.events import get_event_data
from web3.utils.filters import construct_event_filter_params
from web3.middleware import geth_poa_middleware


VERBOSE = True


def log_print(data):
    if VERBOSE:
        print(data)


def handle_streammanager_event(event):
    log_print(event)


def handle_stream_event(event):
    log_print(event)


streammanager_events = [ 
 "StreamRequested",
 "StreamApproved",
 "StreamCreated",
 "ValidatorAdded",
 "RefundAllowed",
 "RefundRevoked",
 "InputChunkAdded",   
 "StreamEnded",
 "OwnershipTransferred",
]


stream_events = [
 "ChunkProofSubmited",
 "ChunkProofValidated",
 "ChunkProofScrapped",
 "Deposited",
 "Refunded",
 "AccountFunded",
 "OutOfFunds",
]


class Blockchain:
    sm_abi_file = '/abis/0.0.3/StreamManager.json'
    st_abi_file = '/abis/0.0.3/Stream.json'
    blockchain_url = ''
    fromBlock = 0
    toBlock = 'latest'

    def __init__(self, blockchain_url, stream_address, stream_manager_address):
        self.w3 = Web3(Web3.HTTPProvider(blockchain_url))
        self.w3.middleware_stack.inject(geth_poa_middleware, layer=0)
        connected = self.w3.isConnected()
        if not connected:
            log_print("/n!!!! No connection to blockchain !!!!/n")
        if stream_address:
            self.add_stream(stream_address)
        if stream_manager_address:
            self.add_stream_manager(stream_manager_address)

    def add_stream_manager(self, stream_manager_address):
        module_dir = os.path.dirname(__file__)
        file_path = module_dir + self.sm_abi_file
        with open(file_path) as f:
            info_streammanger_json = json.load(f)
            self.streammanager_abi = info_streammanger_json["abi"]
            self.stream_manager_contract = self.w3.eth.contract(address=self.w3.toChecksumAddress(stream_manager_address), abi=self.streammanager_abi)

    def add_stream(self, stream_address):
        module_dir = os.path.dirname(__file__)
        file_path = module_dir + self.st_abi_file
        with open(file_path) as f:
            info_stream_json = json.load(f)
            self.stream_abi = info_stream_json["abi"]
            self.stream_contract = self.w3.eth.contract(address=self.w3.toChecksumAddress(stream_address), abi=self.stream_abi)

    def get_block(self):
        return self.w3.eth.blockNumber

    def is_connected(self):
        return self.w3.isConnected()

    def get_event(self, contract_abi, contract_address, _event_name):
        try:
            event_abi = find_matching_event_abi(contract_abi, event_name=_event_name)
            _, event_filter_params = construct_event_filter_params(event_abi,
                                                                   contract_address,
                                                                   fromBlock=self.fromBlock,
                                                                   toBlock=self.toBlock)
            found_logs = self.w3.eth.getLogs(event_filter_params)
            event_data = []
            for log in found_logs:
                event_data.append(get_event_data(event_abi, log))
            return event_data
        except Exception as e:
            log_print("Error=" + str(e))
            return None
    
    def get_stream_manager_events(self, stream_id):
        stream_state_history = {}
        chunk_list = {}
        for event in streammanager_events:    
            log_print("Processing event=" + event)
            event_data = self.get_event(self.streammanager_abi, self.stream_manager_contract.address, event)

            for log in event_data:
                log_print(log)
                if event == "InputChunkAdded":
                    if 'chunkId' in log['args'] and 'streamId' in log['args'] and stream_id == log['args'].streamId:
                        crntState = {'block': log.blockNumber}
                        n_chunk_id = log['args'].chunkId
                        chunk_id = str(n_chunk_id)  # for use with dictionary
                        chunk_list[chunk_id] = crntState
                elif 'streamId' in log['args'] and stream_id == log['args'].streamId:
                    crntState = {'block': log.blockNumber}
                    stream_state_history[event] = crntState
        return stream_state_history, chunk_list

    def get_stream_events(self):
        result = {}
        chunk_trace = {}
        escrow_trace = {}
        out_of_funds_trace = {}
        account_funded_trace = {}
        crnt_chunk_id = "0"
        account_funded_count = 0
        for event in stream_events:
            result[event] = []
            log_print("Processing event=" + event)
            event_data = self.get_event(self.stream_abi, self.stream_contract.address, event)
            for log in event_data:
                result[event].append(log)
                log_print(log)
                # process ChunkProofSubmited, ChunkProofValidated events
                if 'chunkId' in log['args']:
                    #self.addChunkState(chunk_trace, log, event)
                    n_chunk_id = log['args'].chunkId
                    chunk_id = str(n_chunk_id)
                    crnt_chunk_id = chunk_id
                    if chunk_id not in chunk_trace:
                        chunk_trace[chunk_id] = {}
                    chunk_trace[chunk_id][event] = log.blockNumber
                    # log_print("TODO: Enable me")
                elif event == "OutOfFunds":
                    out_of_funds_trace[crnt_chunk_id] = {'block': log.blockNumber}
                elif event == "AccountFunded":
                    account_funded_trace[account_funded_count] = {'block': log.blockNumber, 'weiAmount': log['args'].weiAmount}
                    account_funded_count += 1
                elif event == "Refunded":
                    # skip additional Refunded events
                    if event in escrow_trace:
                        pass
                        # log_print("Skipping redundant Refunded event")
                    else:
                        escrow_trace[event] = {'block': log.blockNumber, 'weiAmount': log['args'].weiAmount}                    
                else:  # Streamwise state
                    pass
                    # escrow_trace[event] = {'block': log.blockNumber, 'weiAmount': log['args'].weiAmount}
        return result
