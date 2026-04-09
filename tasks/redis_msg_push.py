import json
from typing import Any, Dict
from redis_client import get_redis_cluster
import logging


def _serialize_funboost_message(task_function_params: Dict[str, Any]) -> str:
    """按照 funboost 的方式序列化消息。"""
    funboost_message = {"body": task_function_params}
    return json.dumps(funboost_message, ensure_ascii=False, separators=(',', ':'))



def custom_push_to_funboost_queue(queue_name: str, task_function_params: Dict[str, Any]):
    """
    自定义推送函数，模拟 funboost 的消息格式。

    :param queue_name: 队列名称，例如 "task_add_queue"
    :param task_function_params: 任务函数的参数字典，例如 {"a": 1, "b": 2}
    """
    try:
        # 1. 序列化消息
        message_str = _serialize_funboost_message(task_function_params)

        # 2. 推送消息到 Redis List
        # 使用全局客户端
        get_redis_cluster().rpush(queue_name, message_str)

        logging.info(f"Message pushed to queue '{queue_name}': {task_function_params}")

    except Exception as e:
        error_msg = f"Failed to push message to queue '{queue_name}'. Params: {task_function_params}. Error: {e}"
        logging.error(error_msg)
        raise RuntimeError(error_msg) from e