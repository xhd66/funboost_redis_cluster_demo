# -*- coding: utf-8 -*-
from funboost.utils.simple_data_class import DataClassBase

class BrokerConnConfig(DataClassBase):
    # 启用集群模式
    REDIS_IS_USE_CLUSTER = 1
    # 指定集群启动节点（必须把你的集群节点写在这里）
    REDIS_CLUSTER_NODES = "192.168.20.111:6380,192.168.20.111:6381,192.168.20.111:6382"
    REDIS_PASSWORD = "123456"

    # 为了兼容 FunBoost 内部仍可能会用到的单节点 client（比如用于 SADD 等简单操作），
    # 同时把单节点连接点指向集群中的一个可连通节点（避免仍指向 127.0.0.1:6379 导致拒绝）。
    # REDIS_HOST = "192.168.20.111"
    # REDIS_PORT = 6380
    # REDIS_URL = "redis://:123456@192.168.20.111:6380"
    # REDIS_DB = 0

class FunboostCommonConfig(DataClassBase):
    pass