# redis_client.py
from redis.cluster import RedisCluster, ClusterNode
from dotenv import load_dotenv
import os
import threading

load_dotenv(override=False)

REDIS_NODES = os.getenv('REDIS_CLUSTER_NODES', '')
REDIS_PASSWORD = os.getenv('REDIS_PASSWORD', '')


def _make_nodes(nodes_str):
    nodes = []
    for p in nodes_str.split(','):
        h, port = p.split(':')
        nodes.append(ClusterNode(host=h.strip(), port=int(port)))
    return nodes


_cluster_client = None
_cluster_lock = threading.Lock()


def get_redis_cluster():
    global _cluster_client
    if _cluster_client is None:
        with _cluster_lock:
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
