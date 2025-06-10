// RIFO: Full P4 Implementation with Score-based Admission Logic

#include <core.p4>
#include <v1model.p4>

const bit<16> ETYPE_IPV4 = 0x0800;

typedef bit<9>  egressSpec_t;
typedef bit<48> macAddr_t;
typedef bit<32> ip4Addr_t;

const bit<8> B = 4;
const bit<8> kB = 2;
const bit<16> T = 100;

register<bit<8>>(1) queue_length;

header ethernet_t {
    bit<48> dstAddr;
    bit<48> srcAddr;
    bit<16> etherType;
}

header ipv4_t {
    bit<4>  version;
    bit<4>  ihl;
    bit<8>  diffserv;
    bit<16> totalLen;
    bit<16> identification;
    bit<3>  flags;
    bit<13> fragOffset;
    bit<8>  ttl;
    bit<8>  protocol;
    bit<16> hdrChecksum;
    bit<32> srcAddr;
    bit<32> dstAddr;
}

header rifo_t {
    bit<16> rank;
}

struct headers {
    ethernet_t ethernet;
    ipv4_t ipv4;
    rifo_t rifo;
}

struct metadata {}

parser MyParser(packet_in packet, out headers hdr, inout metadata meta, inout standard_metadata_t standard_metadata) {
    state start {
        packet.extract(hdr.ethernet);
        transition select(hdr.ethernet.etherType) {
            ETYPE_IPV4: parse_ipv4;
            default: accept;
        }
    }
    state parse_ipv4 {
        packet.extract(hdr.ipv4);
        transition parse_rifo;
    }
    state parse_rifo {
        packet.extract(hdr.rifo);
        transition accept;
    }
}

control MyIngress(inout headers hdr, inout metadata meta, inout standard_metadata_t standard_metadata) {
    register<bit<16>>(1) reg_min;
    register<bit<16>>(1) reg_max;
    register<bit<16>>(1) reg_count;

    const bit<16> INIT_MIN = 0xFFFF;
    const bit<16> INIT_MAX = 0x0000;

    action update_min(bit<16> rank) {
        reg_min.write(0, rank);
    }

    action update_max(bit<16> rank) {
        reg_max.write(0, rank);
    }

    action reset_min_max(bit<16> rank) {
        reg_min.write(0, rank);
        reg_max.write(0, rank);
        reg_count.write(0, 1);
    }

    action increment_counter() {
        bit<16> c;
        reg_count.read(c, 0);
        reg_count.write(0, c + 1);
    }

    action drop() {
        mark_to_drop(standard_metadata);
    }

    action increment_queue() {
        bit<8> len;
        queue_length.read(len, 0);
        queue_length.write(0, len + 1);
    }

    action forward(egressSpec_t port) {
        increment_queue();
        standard_metadata.egress_spec = port;
    }

    table mac_forward {
        key = {
            hdr.ethernet.dstAddr: exact;
        }
        actions = {
            forward;
            drop;
            NoAction;
        }
        size = 1024;
    }

    action admit() {
        
    }

    apply {
        bit<1> forward_packet = 0;

        bit<16> count;
        reg_count.read(count, 0);

        if (count == 0) {
            reg_min.write(0, INIT_MIN);
            reg_max.write(0, INIT_MAX);
        }

        bit<16> min_rank;
        bit<16> max_rank;
        reg_min.read(min_rank, 0);
        reg_max.read(max_rank, 0);

        if (count >= T) {
            reset_min_max(hdr.rifo.rank);
        } else {
            if (hdr.rifo.rank < min_rank) {
                update_min(hdr.rifo.rank);
            }
            if (hdr.rifo.rank > max_rank) {
                update_max(hdr.rifo.rank);
            }
            increment_counter();
        }

        reg_min.read(min_rank, 0);
        reg_max.read(max_rank, 0);
        if (max_rank == min_rank) {
            forward_packet = 1;
        } else {
            bit<8> queue_len;
            queue_length.read(queue_len, 0);
            bit<8> available = (bit<8>)B - queue_len;
            bit<16> rank_diff = hdr.rifo.rank - min_rank;
            bit<16> range_val = max_rank - min_rank;

            bit<32> rank_expr = (bit<32>)rank_diff * (bit<32>)B;
            bit<32> range_expr = (bit<32>)range_val * (bit<32>)available;

            if (queue_len <= (bit<8>)kB) {
                forward_packet = 1;
            } else if (range_val != 0) {
                if (rank_expr <= range_expr) {
                    forward_packet = 1;
                }
            }
        }

        if (forward_packet == 1) {
            mac_forward.apply();
        } else {
            drop();
        }
    }

}

control MyEgress(inout headers hdr, inout metadata meta, inout standard_metadata_t standard_metadata) {
    action decrement_queue() {
        bit<8> len;
        queue_length.read(len, 0);
        if (len > 0) {
            queue_length.write(0, len - 1);
        }
    }

    apply { 
        decrement_queue();
    }
}

control MyVerifyChecksum(inout headers hdr, inout metadata meta) {
    apply { }
}

control MyComputeChecksum(inout headers hdr, inout metadata meta) {
    apply { }
}

control MyDeparser(packet_out packet, in headers hdr) {
    apply {
        packet.emit(hdr.ethernet);
        packet.emit(hdr.ipv4);
        packet.emit(hdr.rifo);
    }
}

V1Switch(
    MyParser(),
    MyVerifyChecksum(),
    MyIngress(),
    MyEgress(),
    MyComputeChecksum(),
    MyDeparser()
) main;
