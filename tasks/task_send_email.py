import logging
from funboost import boost, BrokerEnum, BoosterParams


def register_task_send_email():
    @boost(BoosterParams(
        queue_name="task_send_email_queue",
        broker_kind=BrokerEnum.REDIS,
        qps=10,
        concurrent_num=5,
    ))
    def task_send_email(body:dict):
        logging.info(f"task_send_email 执行: 发送邮件给 {body.get("to","")}, 主题: {body.get("subject","")}, 内容: {body.get("body","")}")
