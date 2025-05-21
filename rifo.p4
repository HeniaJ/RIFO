// RIFO: Full P4 Implementation with Score-based Admission Logic

#include <core.p4>
#include <v1model.p4>

const bit<16> ETYPE_IPV4 = 0x0800;

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

    const bit<8> B = 20;
    const bit<8> kB = 2;
    const bit<16> T = 100;

    register<bit<16>>(1) reg_min;
    register<bit<16>>(1) reg_max;
    register<bit<16>>(1) reg_count;

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

    action admit() {
        standard_metadata.egress_spec = 1;
    }

    action drop() {
        mark_to_drop(standard_metadata);

    }

    apply {
        bit<16> count;
        reg_count.read(count, 0);

        if (count >= T) {
            reset_min_max(hdr.rifo.rank);
        } else {
            increment_counter();
        }

        bit<16> min_rank;
        bit<16> max_rank;
        reg_min.read(min_rank, 0);
        reg_max.read(max_rank, 0);

        
        if (hdr.rifo.rank < min_rank) {
            update_min(hdr.rifo.rank);
        }
        if (hdr.rifo.rank > max_rank) {
            update_max(hdr.rifo.rank);
        }

        bit<19> queue_len = standard_metadata.deq_qdepth;
        bit<19> available = (bit<19>)B - queue_len;
        bit<16> rank_diff = hdr.rifo.rank - min_rank;
        bit<16> range_val = max_rank - min_rank;

        bit<32> rank_expr = (bit<32>)rank_diff * (bit<32>)B;
        bit<32> range_expr = (bit<32>)range_val * (bit<32>)available;

        if (queue_len <= (bit<19>)kB) {
            admit();
        } else if (range_val != 0) {
            if (rank_expr <= range_expr) {
                admit();
            } else {
                drop();
            }
        } else {
            admit();
        }


    }
}

control MyEgress(inout headers hdr, inout metadata meta, inout standard_metadata_t standard_metadata) {
    apply { }
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
