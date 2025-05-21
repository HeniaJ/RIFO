""" from p4runtime_lib.switch import ShutdownAllSwitchConnections
import p4runtime_lib.bmv2
import p4runtime_lib.helper

def main():
    helper = p4runtime_lib.helper.P4InfoHelper("rifo.p4info.txt")

    # Connect to switch
    sw = p4runtime_lib.bmv2.Bmv2SwitchConnection(
        name='s1',
        address='127.0.0.1:50051',
        device_id=0,
        proto_dump_file='logs/s1-p4runtime-requests.txt'
    )
    sw.MasterArbitrationUpdate()
    sw.SetForwardingPipelineConfig(p4info=helper.p4info, bmv2_json_file_path='rifo.json')

    # Table is not used directly anymore (now logic in apply), so no static rules here
    print("Pipeline set. Dynamic logic applies in ingress.")

    ShutdownAllSwitchConnections()

if __name__ == '__main__':
    main()
 """
 
import grpc
from p4.v1 import p4runtime_pb2, p4runtime_pb2_grpc
from p4.config.v1 import p4info_pb2

from google.protobuf import text_format

def read_p4info(path):
    with open(path, 'r') as f:
        return text_format.Parse(f.read(), p4info_pb2.P4Info())

def main():
    # 1. Csatlakozás a switch-hez
    channel = grpc.insecure_channel('127.0.0.1:50051')
    stub = p4runtime_pb2_grpc.P4RuntimeStub(channel)

    # 2. MasterArbitration
    request = p4runtime_pb2.StreamMessageRequest()
    request.arbitration.device_id = 0
    request.arbitration.election_id.high = 0
    request.arbitration.election_id.low = 1
    stream = stub.StreamChannel(iter([request]))
    response = next(stream)
    print("Arbitration response:", response)

    # 3. Forwarding pipeline betöltése
    p4info = read_p4info("rifo.p4info.txt")
    with open("rifo.json", "rb") as f:
        device_config = f.read()

    set_pipeline_req = p4runtime_pb2.SetForwardingPipelineConfigRequest()
    set_pipeline_req.device_id = 0
    set_pipeline_req.role_id = 0
    set_pipeline_req.action = p4runtime_pb2.SetForwardingPipelineConfigRequest.VERIFY_AND_COMMIT
    set_pipeline_req.config.p4info.CopyFrom(p4info)
    set_pipeline_req.config.p4_device_config = device_config

    stub.SetForwardingPipelineConfig(set_pipeline_req)
    print("Pipeline loaded successfully.")

if __name__ == '__main__':
    main()
    

""" 
import grpc
from p4.v1 import p4runtime_pb2, p4runtime_pb2_grpc
from google.protobuf import text_format

def read_register(stub, device_id, register_id):
    request = p4runtime_pb2.ReadRequest()
    request.device_id = device_id

    entity = p4runtime_pb2.Entity()
    entity.register_entry.register_id = register_id
    request.entities.append(entity)

    for response in stub.Read(request):
        for entity in response.entities:
            reg_entry = entity.register_entry
            print(f"Register ID: {reg_entry.register_id}")
            for data in reg_entry.data:
                # data.data egy bytes, konvertáljuk int-re (big endian)
                val = int.from_bytes(data.data, byteorder='big')
                print(f"Index: {data.index}, Value: {val}")


def main():
    # Kapcsolódás a switchhez
    channel = grpc.insecure_channel('127.0.0.1:50051')
    stub = p4runtime_pb2_grpc.P4RuntimeStub(channel)

    device_id = 0

    # A register ID-ket a P4-ből vagy JSON-ból kell kinyerni.
    # Például: reg_min, reg_max, reg_count id-jeit a JSON-ben keresd.
    reg_min_id = 0
    reg_max_id = 1
    reg_count_id = 2
    
    print("Reading reg_min:")
    read_register(stub, device_id, reg_min_id)

    print("Reading reg_max:")
    read_register(stub, device_id, reg_max_id)

    print("Reading reg_count:")
    read_register(stub, device_id, reg_count_id)

if __name__ == '__main__':
    main()
 """