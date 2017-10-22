# Templates used by openvpn-config scripts

`vars.j2`:

Jinja2 template for easy-rsa. Used by `../generate-server-keys.py`. 

`openvpn.conf.j2`:

Template for `/etc/openvpn.conf`. Used by `../configure-openvpn.py`.

`client.conf.j2`:

Template for client `.ovpn` files. Used by `../create-client-ovpn.py`
