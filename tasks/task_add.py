# task_add.py
import logging
from funboost import boost, BrokerEnum, BoosterParams

logger = logging.getLogger(__name__)


def register_task_add():
    @boost(BoosterParams(
        queue_name="task_add_queue",
        broker_kind=BrokerEnum.REDIS,
        qps=10,
        concurrent_num=5,
    ))
    def task_add(body:dict):
        logger.info("进入消费者了")
        logger.info(f"入参:{body}")
        logger.info(body.get("x",0) + body.get("y",0))
