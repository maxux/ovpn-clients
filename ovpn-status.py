import socket

class ClientStatus:
    def __init__(self, host, port):
        self.host = host
        self.port = port

        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.connect((host, port))

        self.clients = {}
        self.ordered = []

    def _parse(self, data):
        if data.startswith('CLIENT_LIST'):
            items = data.split(',')

            remote = items[2].split(":")

            self.clients[items[1]] = {
                'remote': remote[0],
                'local': items[3],
                'received': items[4],
                'sent': items[5],
                'since': items[7]
            }

        if data.startswith('ROUTING_TABLE'):
            items = data.split(',')
            self.clients[items[2]]['hwaddr'] = items[1]

    def status(self):
        buffer = ""

        while True:
            data = self.socket.recv(1024)
            buffer += data.decode('utf-8')

            if buffer.endswith("END\r\n"):
                break

        # parse result
        lines = buffer.split("\r\n")
        for l in lines:
            self._parse(l)

        for c in self.clients:
            self.ordered.append({'name': c, 'local': self.clients[c]['local']})

        self.ordered.sort(key=lambda x: socket.inet_aton(x['local']))

        return True

    def fetch(self):
        data = self.socket.recv(1024)
        data = data.decode('utf-8')

        if data.startswith('>INFO:OpenVPN Management'):
            self.socket.send(("status 2\n").encode())
            return self.status()

        print(data)

    def close(self):
        self.socket.close()

    def table(self):
        print("Client          | Local           | Remote          | MAC Address       | RX           | TX ")
        print("----------------+-----------------+-----------------+-------------------+--------------+---------------")

        for x in self.ordered:
            c = self.clients[x['name']]

            rx = int(c['received']) / (1024 * 1024)
            tx = int(c['sent']) / (1024 * 1024)

            print("%-15s | %-15s | %-15s | %s | %-9.2f MB | %-9.2f MB" % (x['name'], c['local'], c['remote'], c['hwaddr'], rx, tx))


ovpn = ClientStatus('10.242.1.1', 9580)
ovpn.fetch()
ovpn.table()
