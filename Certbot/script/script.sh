#!/bin/sh
certbot certonly \
--non-interactive \
--agree-tos \
--email ${user_email} \
--domain ${user_domain} \
--standalone -v \
--key-type ecdsa \
--elliptic-curve secp384r1 ;

cp /etc/letsencrypt/live/${user_domain}/fullchain.pem /certificate ;
cp /etc/letsencrypt/live/${user_domain}/privkey.pem /certificate