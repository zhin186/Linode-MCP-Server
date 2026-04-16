"""
成本计算工具
"""

from collections import defaultdict
from typing import Dict, List, Any

from mcp.types import TextContent

from ..linode_client import LinodeClient
from ..utils.pricing import INSTANCE_PRICING, VOLUME_PRICE_PER_GB


async def calculate_monthly_cost(client: LinodeClient, arguments: Dict[str, Any]) -> List[TextContent]:
    """计算月度费用"""
    group_by = arguments.get("group_by", "region")
    
    # 获取所有资源
    instances = await client.get_instances()
    volumes = await client.get_volumes()
    
    # 按分组统计成本
    cost_data = defaultdict(lambda: {
        "instances": 0,
        "volumes": 0,
        "instance_cost": 0.0,
        "volume_cost": 0.0,
        "total_cost": 0.0,
        "details": []
    })
    
    total_instance_cost = 0.0
    total_volume_cost = 0.0
    
    # 统计实例成本
    for instance in instances:
        key = instance.get(group_by, "unknown")
        instance_type = instance.get("type", "unknown")
        monthly_cost = INSTANCE_PRICING.get(instance_type, {}).get("monthly", 0)
        
        cost_data[key]["instances"] += 1
        cost_data[key]["instance_cost"] += monthly_cost
        cost_data[key]["total_cost"] += monthly_cost
        cost_data[key]["details"].append({
            "type": "instance",
            "label": instance.get("label"),
            "cost": monthly_cost
        })
        total_instance_cost += monthly_cost
    
    # 统计卷成本
    for volume in volumes:
        key = volume.get(group_by, "unknown")
        size = volume.get("size", 0)
        monthly_cost = size * VOLUME_PRICE_PER_GB
        
        cost_data[key]["volumes"] += 1
        cost_data[key]["volume_cost"] += monthly_cost
        cost_data[key]["total_cost"] += monthly_cost
        total_volume_cost += monthly_cost
    
    # 生成报告
    total_cost = total_instance_cost + total_volume_cost
    
    report_lines = [
        "💰 月度费用估算报告",
        "",
        f"总费用: ${total_cost:.2f}/月",
        f"  - 实例费用: ${total_instance_cost:.2f}",
        f"  - 卷费用: ${total_volume_cost:.2f}",
        f"年度预测: ${total_cost * 12:.2f}/年",
        "",
        f"按 {group_by} 分组详情:",
    ]
    
    # 按成本排序
    sorted_items = sorted(cost_data.items(), key=lambda x: x[1]["total_cost"], reverse=True)
    
    for key, data in sorted_items:
        pct = (data["total_cost"] / total_cost * 100) if total_cost > 0 else 0
        report_lines.extend([
            f"",
            f"📊 {key}:",
            f"  实例: {data['instances']} 台 (${data['instance_cost']:.2f})",
            f"  卷: {data['volumes']} 个 (${data['volume_cost']:.2f})",
            f"  小计: ${data['total_cost']:.2f}/月 ({pct:.1f}%)",
        ])
    
    report_lines.extend([
        "",
        "⚠️ 注意: 此估算不包含流量费、IP保留费、NodeBalancer等其他服务费用。"
    ])
    
    return [TextContent(type="text", text="\n".join(report_lines))]
