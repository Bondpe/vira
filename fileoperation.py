import pickle

def pack_stream(stream):
    if stream.saveDefault:
        args = {}
        for k in stream.args:
            if k == 'child':
                args[k] = pack_stream(stream.args[k])
            else:
                args[k] = stream.args[k]
    else:
        args = stream.save(pack_stream)
    return [stream.__class__, args, stream.saveDefault, stream.name]

def load_stream(stream_class, args, default, name):
    stream = stream_class()
    if default:
        stream.args = args
        for k in args:
            if k == 'child':
                stream.args[k] = load_stream(*args[k])
        stream.setup()
    else:
        stream.load(args, load_stream)
    stream.name = name
    return stream

def to_bytes(composition, files, system_data):
    streams = []
    for stream, delta in composition:
        streams.append([delta, pack_stream(stream)])
    return pickle.dumps([streams, files, system_data])

def from_bytes(byte_data, load_fles_func):
    streams,files,system_data = pickle.loads(byte_data)
    load_fles_func(files)
    composition = []
    for delta, stream_data in streams:
        stream = load_stream(*stream_data)
        composition.append([stream, delta])
    return composition, system_data
