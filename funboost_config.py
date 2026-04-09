# -*- coding: utf-8 -*-
import os
from dotenv import load_dotenv
from funboost.utils.simple_data_class import DataClassBase

load_dotenv(override=False)


class BrokerConnConfig(DataClassBase):
    REDIS_IS_USE_CLUSTER = int(os.getenv('REDIS_IS_USE_CLUSTER', '0'))
    REDIS_CLUSTER_NODES = os.getenv('REDIS_CLUSTER_NODES', '')
    REDIS_PASSWORD = os.getenv('REDIS_PASSWORD', '')


class FunboostCommonConfig(DataClassBase):
    pass
