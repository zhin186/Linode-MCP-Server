"""
IP 资源审计工具
"""

from collections import defaultdict
from typing import Dict, List, Any

from mcp.types import TextContent

from ..linode_client import LinodeClient


async def audit_ip_resources(client: LinodeClient, arguments: Dict[str, Any]) -> List[TextContent]:
    """审计 IP 资源"""
    region_filter = arguments.get("region")
    
    # 获取所有 IP 和实例
    ips = await client.get_networking_ips()
    instances = await client.get_instances()
    
    # 创建实例 ID 映射
    instance_map = {i.get("id"): i for i in instances}
    
    # 统计
    stats = {
        "total_ipv4": 0,
        "public_ipv4": 0,
        "private_ipv4": 0,
        "shared": 0,
        "vpc_nat": 0,
        "reserved": 0,
        "unassigned": [],
    }
    
    region_stats = defaultdict(lambda: {
        "public": 0,
        "private": 0,
        "vpc": 0,
        "unassigned": 0,
    })
    
    for ip in ips:
        ip_region = ip.get("region", "unknown")
        
        if region_filter and ip_region != region_filter:
            continue
        
        ip_type = ip.get("type")
        is_public = ip.get("public", False)
        linode_id = ip.get("linode_id")
        
        if ip_type == "ipv4":
            stats["total_ipv4"] += 1
            
            if is_public:
                stats["public_ipv4"] += 1
                region_stats[ip_region]["public"] += 1
            else:
                stats["private_ipv4"] += 1
                region_stats[ip_region]["private"] += 1
        
        if ip.get("vpc_nat_1_1"):
            stats["vpc_nat"] += 1
            region_stats[ip_region]["vpc"] += 1
        
        if ip.get("shared"):
            stats["shared"] += 1
        
        # 检查是否分配
        if not linode_id:
            stats["unassigned"].append({
                "address": ip.get("address"),
                "region": ip_region,
                "type": "public" if is_public else "private",
            })
            region_stats[ip_region]["unassigned"] += 1
    
    # 计算未分配 IP 的潜在费用
    unassigned_public = [ip for ip in stats["unassigned"] if ip["type"] == "public"]
    potential_saving = len(unassigned_public) * 0.004 * 24 * 30  # $0.004/小时
    
    report_lines = [
        "🌐 IP 资源审计报告",
        "",
        "IPv4 统计:",
        f"  总数: {stats['total_ipv4']}",
        f"  公网 IP: {stats['public_ipv4']}",
        f"  私网 IP: {stats['private_ipv4']}",
        f"  共享 IP (IP Sharing): {stats['shared']}",
        f"  VPC NAT IP: {stats['vpc_nat']}",
        f"  未分配 IP: {len(stats['unassigned'])}",
        "",
        "区域分布:",
    ]
    
    for region, data in sorted(region_stats.items()):
        report_lines.append(
            f"  {region}: 公网{data['public']} 私网{data['private']} VPC{data['vpc']} 未分配{data['unassigned']}"
        )
    
    if stats["unassigned"]:
        report_lines.extend([
            "",
            f"⚠️ 未分配 IP 地址 (可节省费用: ${potential_saving:.2f}/月):",
        ])
        for ip in stats["unassigned"]:
            report_lines.append(f"  - {ip['address']} ({ip['region']}, {ip['type']})")
        
        report_lines.extend([
            "",
            "💡 建议: 释放未分配的公网 IP 以节省 $0.004/小时/IP ($2.88/月/IP)",
        ])
    
    # IP 使用效率分析
    total_instances = len(instances)
    public_ips = stats["public_ipv4"]
    avg_ip_per_instance = public_ips / total_instances if total_instances > 0 else 0
    
    report_lines.extend([
        "",
        "使用效率分析:",
        f"  实例总数: {total_instances}",
        f"  公网 IP 总数: {public_ips}",
        f"  平均每实例 IP 数: {avg_ip_per_instance:.2f}",
    ])
    
    if avg_ip_per_instance > 1.5:
        report_lines.append("  ⚠️ 平均 IP 数较高，建议检查是否有冗余 IP")
    
    return [TextContent(type="text", text="\n".join(report_lines))]
