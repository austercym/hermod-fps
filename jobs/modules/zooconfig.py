from kazoo.client import KazooClient


def get_config(zookeeper_url, path):

    print 'Retrieving zookeeper config from node: ', path

    zk = KazooClient(hosts=zookeeper_url, read_only=True)
    zk.start()

    #get all children nodes and populate the result dictionary
    nodes = zk.get_children(path)

    result = {}

    for node in nodes:
        value, stat = zk.get(path + node)
        result[node] = value

    zk.stop()
    return result
