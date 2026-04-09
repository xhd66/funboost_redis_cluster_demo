# 1. 启动 Redis 集群
docker compose -f docker-compose-redis-cluster.yml up -d

# 2. 等待容器和服务就绪
Start-Sleep -Seconds 10

# 3. 创建集群（容器内用 Docker DNS 互相通信，announce-ip 为宿主机 IP）
docker exec funboost_demo-redis-node-1-1 `
  redis-cli -a "123456" --cluster create `
  redis-node-1:6380 redis-node-2:6381 redis-node-3:6382 `
  redis-node-4:6383 redis-node-5:6384 redis-node-6:6385 `
  --cluster-replicas 1 --cluster-yes
