"""
区域实例统计工具
"""

from collections import defaultdict
from typing import Dict, List, Any

from mcp.types import TextContent

from ..linode_client import LinodeClient
from ..utils.pricing import INSTANCE_PRICING


async def get_region_instance_stats(client: LinodeClient, arguments: Dict[str, Any]) -> List[TextContent]:
    """获取指定区域的实例统计"""
    region = arguments.get("region")
    include_cost = arguments.get("include_cost", True)
    
    if not region:
        return [TextContent(type="text", text="Error: region parameter is required")]
    
    # 使用 X-Filter 过滤特定区域
    filters = {"region": region}
    instances = await client.get_instances(filters)
    
    if not instances:
        return [TextContent(type="text", text=f"ℹ️ 区域 '{region}' 中没有找到实例")]
    
    # 统计数据
    stats = {
        "total": len(instances),
        "status": defaultdict(int),
        "types": defaultdict(int),
        "vcpus": 0,
        "memory_gb": 0,
        "disk_gb": 0,
        "monthly_cost": 0.0,
    }
    
    for instance in instances:
        status = instance.get("status", "unknown")
        instance_type = instance.get("type", "unknown")
        specs = instance.get("specs", {})
        
        stats["status"][status] += 1
        stats["types"][instance_type] += 1
        stats["vcpus"] += specs.get("vcpus", 0)
        stats["memory_gb"] += specs.get("memory", 0) / 1024
        stats["disk_gb"] += specs.get("disk", 0) / 1024
        
        if include_cost and instance_type in INSTANCE_PRICING:
            stats["monthly_cost"] += INSTANCE_PRICING[instance_type]["monthly"]
    
    # 生成报告
    report_lines = [
        f"📊 区域实例统计报告: {region}",
        "",
        "总体概况:",
        f"  实例总数: {stats['total']}",
        f"  总 vCPU: {stats['vcpus']} 核",
        f"  总内存: {stats['memory_gb']:.1f} GB",
        f"  总磁盘: {stats['disk_gb']:.1f} GB",
    ]
    
    if include_cost:
        report_lines.append(f"  月度费用估算: ${stats['monthly_cost']:.2f}")
    
    report_lines.extend(["", "状态分布:"])
    for status, count in sorted(stats["status"].items()):
        pct = count / stats["total"] * 100
        report_lines.append(f"  {status}: {count} ({pct:.1f}%)")
    
    report_lines.extend(["", "实例类型分布:"])
    for instance_type, count in sorted(stats["types"].items()):
        pricing = INSTANCE_PRICING.get(instance_type, {})
        label = pricing.get("label", instance_type)
        report_lines.append(f"  {label} ({instance_type}): {count}")
    
    return [TextContent(type="text", text="\n".join(report_lines))]
