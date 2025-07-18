// RIFO: Full P4 Implementation with Score-based Admission Logic

#include <core.p4>
#include <v1model.p4>

const bit<16> ETYPE_IPV4 = 0x0800;

typedef bit<9>  egressSpec_t;
typedef bit<48> macAddr_t;
typedef bit<32> ip4Addr_t;

const bit<8> B = 5;
const bit<8> kB = 3;
const bit<16> T = 100;

register<bit<8>>(1) queue_length;

// header definiciok
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

// rifo_t egy egyedi fejlecmezo amiben a csomag rangja van
header rifo_t {
    bit<16> rank;
}

// csomag fejlecenek reprezentacioja
struct headers {
    ethernet_t ethernet;
    ipv4_t ipv4;
    rifo_t rifo;
}

struct metadata {}

// fejlecek kibontasa
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

    // rang adat kinyerese
    state parse_rifo {
        packet.extract(hdr.rifo);
        transition accept;
    }
}

// logika
control MyIngress(inout headers hdr, inout metadata meta, inout standard_metadata_t standard_metadata) {

    // reg_min es reg_max taroljak az eddigi legkisebb és legnagyobb rangokat
    // reg_count szamolja hogy hany csomagot dolgoztunk fel az aktuális ablakban
    // queue_length a sor aktualis hosszat tartolja

    register<bit<16>>(1) reg_min;
    register<bit<16>>(1) reg_max;
    register<bit<16>>(1) reg_count;

    // init
    // ha a csomag meg nem volt feldolgozva - default ertek beallitasa
    const bit<16> INIT_MIN = 0xFFFF;
    const bit<16> INIT_MAX = 0x0000;

    // min max ertek frissitese
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

    // csomag eldobasa
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

    // cimzett keresese
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

    // a csomag eldobasarol vagy tovabbkuldeserol dontes
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

        // uj meresi ablak nyitasa ha a csomagok szama elerte a 100-at
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

        // nincs rangkulonbseg
        if (max_rank == min_rank) {
            forward_packet = 1;
        } else {

            // rangkulonbseg eseten pontszam szamolasa
            // eleg jo rang eseten a csomag tovabbitasa
            bit<8> queue_len;
            queue_length.read(queue_len, 0);
            bit<8> available = (bit<8>)B - queue_len;
            bit<16> rank_diff = hdr.rifo.rank - min_rank;
            bit<16> range_val = max_rank - min_rank;

            bit<32> rank_expr = (bit<32>)rank_diff * (bit<32>)B;
            bit<32> range_expr = (bit<32>)range_val * (bit<32>)available;

            // ha keves csomag van automatikus a csomagtovabbitas
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

// sorhossz csokkentese a csomag kilepese utan hogy a sor ne torzuljon
control MyEgress(inout headers hdr, inout metadata meta, inout standard_metadata_t standard_metadata) {
    action decrement_queue() {
        bit<8> len;
        queue_length.read(len, 0);
        bit<8> new_len;
        if (len == 0) {
            new_len = 0;
        } else {
            new_len = len - 1;
        }
        queue_length.write(0, new_len);
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
