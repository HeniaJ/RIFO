import grpc
from p4.v1 import p4runtime_pb2, p4runtime_pb2_grpc
from p4.config.v1 import p4info_pb2

from google.protobuf import text_format

def read_p4info(path):
    with open(path, 'r') as f:
        return text_format.Parse(f.read(), p4info_pb2.P4Info())

def read_register(stub, device_id, register_name, index, p4info):
    entity = p4runtime_pb2.Entity()
    register = entity.register_entry
    register.register_id = get_register_id(p4info, register_name)
    register.index.index = index

    request = p4runtime_pb2.ReadRequest()
    request.device_id = device_id
    request.entities.append(entity)

    for response in stub.Read(request):
        for entity in response.entities:
            data = int.from_bytes(entity.register_entry.data, byteorder='big')
            return data
    return None

def get_register_id(p4info, name):
    for reg in p4info.registers:
        if reg.preamble.name == name or reg.preamble.alias == name:
            return reg.preamble.id
    raise ValueError(f"Register '{name}' not found in P4Info")


def main():
    # Kapcsolat
    channel = grpc.insecure_channel('127.0.0.1:50051')
    stub = p4runtime_pb2_grpc.P4RuntimeStub(channel)

    # Arbitration
    request = p4runtime_pb2.StreamMessageRequest()
    request.arbitration.device_id = 0
    request.arbitration.election_id.high = 0
    request.arbitration.election_id.low = 1
    stream = stub.StreamChannel(iter([request]))
    response = next(stream)
    print("Arbitration OK:", response)

    # Pipeline betöltés
    p4info = read_p4info("rifo.p4info.txt")
    with open("rifo.json", "rb") as f:
        device_config = f.read()

    config_req = p4runtime_pb2.SetForwardingPipelineConfigRequest()
    config_req.device_id = 0
    config_req.action = p4runtime_pb2.SetForwardingPipelineConfigRequest.VERIFY_AND_COMMIT
    config_req.config.p4info.CopyFrom(p4info)
    config_req.config.p4_device_config = device_config

    stub.SetForwardingPipelineConfig(config_req)
    print("Pipeline loaded successfully.")

    # Regiszterek lekérdezése
    for reg_name in ["reg_min", "reg_max", "reg_count"]:
        val = read_register(stub, 0, reg_name, 0, p4info)
        print(f"{reg_name}[0] = {val}")

if __name__ == '__main__':
    main()
