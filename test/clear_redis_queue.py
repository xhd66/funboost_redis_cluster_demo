import redis_client
from redis.cluster import RedisCluster, ClusterNode


def clear_all_cluster_data():
    """
    连接 Redis 集群并清空所有数据库的数据（慎用，仅限本地开发测试环境）
    """
    try:
        # 重新实例化一个客户端，确保连接正常
        client = RedisCluster(
            startup_nodes=redis_client._make_nodes(redis_client.REDIS_NODES),
            password=redis_client.REDIS_PASSWORD,
            decode_responses=True
        )

        # 使用原生 cluster nodes 命令获取集群所有主节点信息
        nodes_info = client.execute_command('CLUSTER', 'NODES')
        master_nodes = []

        for line in nodes_info.splitlines():
            # 找到包含 'master' 的行
            if 'master' in line:
                parts = line.split()
                ip_port = parts[1].split('@')[0]  # 格式类似 192.168.20.111:6380
                master_nodes.append(ip_port)

        print(f"发现 {len(master_nodes)} 个主节点: {master_nodes}")

        # 遍历所有主节点，执行 FLUSHDB 清空当前节点所在槽的数据
        for node in master_nodes:
            ip, port = node.split(':')
            try:
                # 在特定节点上执行清空命令
                client.execute_command('FLUSHDB', target_nodes=[ClusterNode(host=ip, port=int(port))])
                print(f"成功清空节点: {node}")
            except Exception as e:
                print(f"清空节点 {node} 失败: {e}")

        print("\n✅ 集群数据清理完成！现在可以重新发送消息测试了。")
        client.close()

    except Exception as e:
        print(f"❌ 连接或清理失败，请检查配置: {e}")


if __name__ == '__main__':
    print("⚠️ 警告：此脚本将清空 Redis 集群中的【所有数据】！")
    confirm = input("确定要继续吗？(输入 yes 确认): ")

    if confirm.strip().lower() == 'yes':
        clear_all_cluster_data()
    else:
        print("已取消操作。")
