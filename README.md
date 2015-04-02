# Reliable Data Transfer by Go-Back-N

## Packet format(bits)
* srcport = packet[0:16]
* destport = packet[16: 32]
* seqnum = packet[32:64]
* ack = packet[64:96]
* checksum = packet[96:112]
* data = packet[112:]
* packet is binary string

## Sender
* Get data from upper layer
* Segmentation
* Get checksum and header
* Store into list and send by unreliable socket

Depends on difference data structure, the size of data will be different.
We calculate char by char rather than string. It will leads to cost more space.
Define one char needs 2 bytes.

Besides, this is simplistic implementation, so our header only contain
source port, destination port, sequence number, ack number, and checksum.

Also, we define the type of packet will be binary string.

## Receiver
* Get packet from unreliable data transfer
* checksum, error detection
* Send the ack back to sender
* Deliever data to upper layer