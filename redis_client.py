# redis_client.py
from redis.cluster import RedisCluster, ClusterNode
import os

REDIS_NODES = os.getenv('REDIS_CLUSTER_NODES', '192.168.20.111:6380,192.168.20.111:6381,192.168.20.111:6382')
REDIS_PASSWORD = os.getenv('REDIS_PASSWORD', '123456')

def _make_nodes(nodes_str):
    nodes = []
    for p in nodes_str.split(','):
        h, port = p.split(':')
        nodes.append(ClusterNode(host=h.strip(), port=int(port)))
    return nodes

# Create client lazily at import time (ok if module imported in worker process)
_cluster_client = None

def get_redis_cluster():
    global _cluster_client
    if _cluster_client is None:
        _cluster_client = RedisCluster(
            startup_nodes=_make_nodes(REDIS_NODES),
            password=REDIS_PASSWORD,
            decode_responses=True,
        )
    return _cluster_client

def close_redis_cluster():
    global _cluster_client
    if _cluster_client is not None:
        try:
            _cluster_client.close()
        except Exception:
            pass
        _cluster_client = None