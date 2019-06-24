# Example
Shows example usage

(`set -x` is fish's notation for bash's `export`)

## No https
Example:

    set -x HOSTNAME <<yourhostname>>; set -x CONFIG_BINDING_SERVICE <<cbshost>>;  python testclient.py

## Https
The value of the environment variable `DCAE_CA_CERTPATH` must be a path to a cacert file to verify the running CBS.
The following excerpt is from the curl manpage:

    --cacert <file>
    (TLS) Tells curl to use the specified certificate file to verify the peer.
    The file may contain multiple CA certificates.

Example:

    set -x HOSTNAME <<yourhostname>>; set -x CONFIG_BINDING_SERVICE <<cbshost>>;  set -x DCAE_CA_CERTPATH /opt/onapcacert.pem; python testclient.py
