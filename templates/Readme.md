# Templates used by openvpn-config scripts

`vars.j2`:

Jinja2 template for easy-rsa. Used by `../generate-server-keys.py`. Substitutions
should be self-explanatory.

`openvpn.conf.j2`:

Template for `/etc/openvpn.conf`. Used by `../configure-openvpn.py`.

TODO: more experimentation needs to be done to ensure that this configuration
template supports discovery (zeroconf).
