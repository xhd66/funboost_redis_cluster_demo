from dotenv import load_dotenv
import os

load_dotenv()

# 1. 先 monkey-patch RedisMixin，让 @boost 装饰器使用自定义 Redis 连接池
from redis_client import get_redis_cluster
from funboost.utils.redis_manager import RedisMixin

def _get_redis_cluster_instance(self):
    return get_redis_cluster()

RedisMixin.redis_db_frame = property(_get_redis_cluster_instance)

# 2. monkey-patch 完成后，再 import 任务模块（触发 @boost 装饰器注册）
from tasks.task_add import task_add
from tasks.redis_msg_push import custom_push_to_funboost_queue

import uvicorn
from contextlib import asynccontextmanager
from fastapi import FastAPI
from pydantic import BaseModel
from funboost import BoostersManager

project_root_path = os.path.dirname(os.path.abspath(__file__))

# ==================== Lifespan 管理器 ====================
@asynccontextmanager
async def lifespan(app: FastAPI):
    print("应用正在启动...")
    print("所有任务已注册。已发现并注册 %d 个任务消费者。" % len(BoostersManager.get_all_boosters()))

    # 启动消费者线程
    import threading
    consumer_thread = threading.Thread(
        target=BoostersManager.consume_all,
        daemon=False,
        name="FunBoost-Consumer-Thread"
    )
    consumer_thread.start()
    print("所有任务消费者已在后台线程中启动。")

    yield

    print("应用正在关闭，正在停止所有消费者...")
    try:
        BoostersManager.stop_all_consuming()
    except AttributeError:
        pass
    consumer_thread.join(timeout=10)
    if consumer_thread.is_alive():
        print("警告：消费者线程未能在10秒内完全停止。")
    else:
        print("所有消费者已成功停止。")
    print("应用已关闭。")


# ==================== FastAPI App ====================
app = FastAPI(title="Funboost Redis Cluster Demo", lifespan=lifespan)


# ==================== 任务接口 ====================
class AddRequest(BaseModel):
    x: int
    y: int


class EmailRequest(BaseModel):
    to: str
    subject: str
    body: str

class RedisSetRequest(BaseModel):
    key: str
    value: str

@app.post("/task/add")
def submit_add_task(req: AddRequest):
    # custom_push_to_funboost_queue("task_add_queue", {"x": req.x, "y": req.y})
    task_add.push({"x": req.x, "y": req.y})
    return {"msg": "加法任务已提交", "x": req.x, "y": req.y}

@app.post("/task/send_email")
def submit_email_task(req: EmailRequest):
    custom_push_to_funboost_queue("task_send_email_queue", {"to": req.to, "subject": req.subject,"body":req.body})
    return {"msg": "邮件任务已提交", "to": req.to}

@app.post("/redis/set")
def redis_set(req: RedisSetRequest):
    rc = get_redis_cluster()
    rc.set(req.key, req.value)
    return {"msg": "设置成功", "key": req.key, "value": req.value}


@app.get("/redis/get/{key}")
def redis_get(key: str):
    value = get_redis_cluster().get(key)
    if value is None:
        return {"msg": "key 不存在", "key": key, "value": None}
    return {"msg": "获取成功", "key": key, "value": value}


@app.delete("/redis/del/{key}")
def redis_del(key: str):
    deleted = get_redis_cluster().delete(key)
    return {"msg": "删除成功" if deleted else "key 不存在", "key": key, "deleted": deleted}


# ==================== Main ====================
if __name__ == "__main__":
    uvicorn.run("api:app", host="0.0.0.0", port=8000, reload=False)
