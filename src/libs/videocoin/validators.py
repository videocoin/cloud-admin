import requests

import m3u8


CHUNKS_EVENTS = [
    'ChunkProofSubmited',
    'ChunkProofValidated',
    'ChunkProofScrapped',
]


class VCValidationError:
    text = ''

    def __init__(self, text):
        self.text = text


class Chunk:
    number = 0
    duration = 0

    def __init__(self, number, duration):
        self.number = number
        self.duration = duration

    def __eq__(self, other):
        if self.number == other.number and self.duration == other.duration:
            return True
        return False


class BaseValidator:
    name = ''
    description = ''
    errors = []
    is_valid = True

    def get_playlist(self, url):
        r = requests.get(url)
        return r.text

    def get_chunks(self, url):
        chunks = []
        playlist = self.get_playlist(url)
        m3u8_obj = m3u8.loads(playlist)
        for i, c in enumerate(m3u8_obj.segments):
            chunks.append(Chunk(i+1, c.duration))
        return chunks

    def to_json(self):
        return {self.name: {
            'description': self.description,
            'errors': [x.text for x in self.errors],
            'is_valid': self.is_valid,
        }}


class ChunkEventsValidator(BaseValidator):
    name = 'ChunkEventsValidator'
    description = 'Check stream chunk events'

    def __init__(self, events, input_url, output_url):
        self.events = [x for x in events if x.get('event') in CHUNKS_EVENTS]
        self.input_url = input_url
        self.output_url = output_url

    def validate(self):
        output_chunks = self.get_chunks(self.output_url)
        for chunk in output_chunks:
            chunk_events = [x for x in self.events if x['args']['chunkId'] == chunk.number]
            if 'ChunkProofSubmited' not in [x.get('event') for x in chunk_events]:
                self.errors.append(VCValidationError('No corresponding ChunkProofSubmited event for chunk #{}'.
                                                     format(chunk.number)))
                self.is_valid = False
            if 'ChunkProofValidated' not in [x.get('event') for x in chunk_events]:
                self.errors.append(VCValidationError('No corresponding ChunkProofValidated event for chunk #{}'.
                                                     format(chunk.number)))
                self.is_valid = False

            if 'ChunkProofScrapped' in [x.get('event') for x in chunk_events]:
                self.errors.append(VCValidationError('ChunkProofScrapped event for chunk #{}'.
                                                     format(chunk.number)))
                self.is_valid = False


class InOutValidator(BaseValidator):
    name = 'InOutValidator'
    description = 'Compare input and output playlists'

    def __init__(self, input_url, output_url):
        self.input_url = input_url
        self.output_url = output_url

    def validate(self):
        r = requests.get(self.input_url)
        if r.status_code != 200:
            self.errors.append(VCValidationError('Can\'t access input url'))
            self.is_valid = False
            return
        input_chunks = self.get_chunks(self.input_url)
        output_chunks = self.get_chunks(self.output_url)
        if len(input_chunks) != len(output_chunks):
            self.errors.append(VCValidationError('Different chunk count in input and output'))
            self.is_valid = False
            return
        for i in range(len(input_chunks)):
            if output_chunks[i] != input_chunks[i]:
                self.errors.append(VCValidationError('Different chunk #{} in input and output'.
                                                     format(input_chunks[i].number)))
                self.is_valid = False
