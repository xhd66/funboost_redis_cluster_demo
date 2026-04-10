# FunBoost + Redis Cluster + FastAPI 项目

基于 FunBoost 框架的异步任务队列 Demo，使用 Redis Cluster 作为消息中间件，FastAPI 提供 HTTP 接口。

## 技术栈

- **FunBoost**: 任务队列框架，通过 `@boost` 装饰器声明消费者
- **Redis Cluster**: 消息中间件（6 节点: 6380-6385，3 主 3 从）
- **FastAPI + Uvicorn**: HTTP 服务
- **Python 3.12**
- **uv**: 包管理器

## 项目结构

```
funboost_demo/
├── .env                        # Redis 连接配置（唯一配置源）
├── funboost_config.py          # FunBoost 框架配置（从 .env 读取）
├── redis_client.py             # Redis Cluster 客户端（线程安全懒加载单例）
├── api.py                      # FastAPI 入口 + 消费者启动
├── tasks/
│   ├── task_add.py             # 加法任务消费者
│   └── task_send_email.py      # 邮件任务消费者
├── test/                       # 测试脚本
├── docker-compose-redis-cluster.yml  # Redis Cluster Docker 配置
└── redis_cluster.bat/ps1       # Redis Cluster 启动脚本
```

## 快速开始

### 1. 启动 Redis Cluster

直接运行 `redis_cluster.bat` 脚本开启 Redis 集群（要求安装 Docker 且内部有 Redis 7.2镜像(默认只用本地镜像)，否则修改 `docker-compose-redis-cluster.yml` 文件）

### 2. 安装依赖

通过 uv 安装所需依赖：

```bash
uv sync
```

### 3. 启动服务

```bash
uv run python api.py
```

## Redis Cluster 管理

### 正常关闭集群

```bash
docker-compose -f docker-compose-redis-cluster.yml down
```

### 正常重启集群

```bash
docker-compose -f docker-compose-redis-cluster.yml up -d
```

### 从头开启集群（清除节点信息及数据）

```bash
# 清空所有节点数据
docker exec -it funboost_demo-redis-node-1-1 redis-cli -p 6380 -a "123456" FLUSHALL
docker exec -it funboost_demo-redis-node-1-1 redis-cli -p 6380 -a "123456" CLUSTER RESET HARD
docker exec -it funboost_demo-redis-node-2-1 redis-cli -p 6381 -a "123456" FLUSHALL
docker exec -it funboost_demo-redis-node-2-1 redis-cli -p 6381 -a "123456" CLUSTER RESET HARD
docker exec -it funboost_demo-redis-node-3-1 redis-cli -p 6382 -a "123456" FLUSHALL
docker exec -it funboost_demo-redis-node-3-1 redis-cli -p 6382 -a "123456" CLUSTER RESET HARD
docker exec -it funboost_demo-redis-node-4-1 redis-cli -p 6383 -a "123456" FLUSHALL
docker exec -it funboost_demo-redis-node-4-1 redis-cli -p 6383 -a "123456" CLUSTER RESET HARD
docker exec -it funboost_demo-redis-node-5-1 redis-cli -p 6384 -a "123456" FLUSHALL
docker exec -it funboost_demo-redis-node-5-1 redis-cli -p 6384 -a "123456" CLUSTER RESET HARD
docker exec -it funboost_demo-redis-node-6-1 redis-cli -p 6385 -a "123456" FLUSHALL
docker exec -it funboost_demo-redis-node-6-1 redis-cli -p 6385 -a "123456" CLUSTER RESET HARD

# 创建集群
docker exec -it funboost_demo-redis-node-1-1 redis-cli --cluster create \
  192.168.20.93:6380 192.168.20.93:6381 192.168.20.93:6382 \
  192.168.20.93:6383 192.168.20.93:6384 192.168.20.93:6385 \
  --cluster-replicas 1 -a "123456"
```

## 核心架构

### 启动流程

1. `api.py` 启动时：先 monkey-patch `RedisMixin.redis_db_frame` → 再 import 任务模块 → `@boost` 自动注册到 `BoostersManager`
2. HTTP 接口通过 `task_xxx.push(**kwargs)` 发送消息（funboost 原生方式）
3. `BoostersManager.consume_all()` 在后台线程启动所有消费者
4. 新增任务只需在 `tasks/` 下新建文件 + `@boost` 装饰器，`api.py` 无需改动

### Redis Cluster 接入

FunBoost 默认不支持 Redis Cluster，通过 monkey-patch 实现：

```python
# api.py 中，必须在 import tasks 之前执行
from funboost.utils.redis_manager import RedisMixin
RedisMixin.redis_db_frame = property(lambda self: get_redis_cluster())
```

### 任务发布方式

- `func.push(x=1, y=2)` — 简写，只传函数参数
- `func.delay(x=1, y=2)` — push 的别名
- `func.publish({"x":1, "y":2})` — 完整版，可传 task_options

## 关键技术点

### Import 顺序规则（重要）

`@boost` 装饰器在 import 时被触发，此时 funboost 会读取 `RedisMixin.redis_db_frame` 连接 Redis。如果 import 顺序不对，会导致连到默认的 `localhost:6379` 而非集群。

**正确的 import 顺序（api.py 顶部）：**
1. `load_dotenv()` — 加载环境变量
2. monkey-patch `RedisMixin.redis_db_frame` — 替换连接逻辑
3. `from tasks.xxx import task_xxx` — 触发 `@boost` 注册

**关键规则：**
- `RedisMixin` 是类属性，monkey-patch 一次全局生效，不需要重复修改
- 只要入口是 `api.py`，patch 在最顶部完成，后续任何文件 import 任务模块都不需要再 patch
- 间接 import 也受影响：如果 A import B，B import task_add，那 A 的 import 也必须在 patch 之后

### 两种消息推送方式的区别

| | `task_xxx.push()` | `custom_push_to_funboost_queue()` |
|---|---|---|
| 走 funboost 内部连接 | 是 | 否，直接用 `get_redis_cluster()` |
| 需要 monkey-patch | 是 | 否 |
| 需要先 import 任务模块 | 是 | 否 |

- 用 `custom_push_to_funboost_queue()` 推消息不需要 monkey-patch，它直接用项目自己的 Redis Cluster 客户端
- 用 `task_xxx.push()` 必须先 patch，因为它走 funboost 的 `RedisMixin.redis_db_frame`
- 消费端不受影响，两种方式推的消息消费者都能正常处理

### 配置管理

- `.env` 作为唯一配置源
- `redis_client.py` 和 `funboost_config.py` 都从 `os.getenv` 读取，不再硬编码
- 两个模块各自调用 `load_dotenv(override=False)`，不依赖调用方

### Redis 客户端线程安全

- `get_redis_cluster()` 使用双重检查锁定（Double-Checked Locking）+ `threading.Lock`
- 保证多线程环境下只创建一个 RedisCluster 实例

## 清空 Redis 集群数据

`test/clear_redis_standalone.py` — 以单机模式逐个连接节点执行 FLUSHALL，适用于集群无法启动时清空数据后重建。

## 新增任务

1. 在 `tasks/` 目录下新建文件（如 `task_xxx.py`）
2. 使用 `@boost` 装饰器定义任务函数
3. 在 `api.py` 中 import 该任务模块（确保在 monkey-patch 之后）
4. 无需其他改动，`BoostersManager` 会自动注册并启动消费
