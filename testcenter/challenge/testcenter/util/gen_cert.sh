#!/bin/sh
#
# CSCA key
#
set -e

OPENSSL=${OPENSSL:=openssl}

${OPENSSL} ecparam -name prime256v1 -genkey -noout -out ./res/csca.key
${OPENSSL} req -x509 \
        -new \
        -subj '/CN=KDCTF/CN=KD/' \
        -key ./res/csca.key \
        -out ./res/csca.pem -nodes \
        -days 3650
