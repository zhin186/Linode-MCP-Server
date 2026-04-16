"""
闲置资源检测工具
"""

from datetime import datetime, timedelta
from typing import Dict, List, Any

from mcp.types import TextContent

from ..linode_client import LinodeClient
from ..utils.pricing import INSTANCE_PRICING


async def find_idle_resources(client: LinodeClient, arguments: Dict[str, Any]) -> List[TextContent]:
    """查找闲置资源"""
    days_offline = arguments.get("days_offline", 7)
    missing_tags = arguments.get("missing_tags", True)
    
    instances = await client.get_instances()
    idle_instances = []
    
    now = datetime.now()
    threshold = now - timedelta(days=days_offline)
    
    for instance in instances:
        reasons = []
        
        # 检查长期关机
        if instance.get("status") == "offline":
            updated = instance.get("updated")
            if updated:
                try:
                    updated_dt = datetime.fromisoformat(updated.replace("Z", "+00:00"))
                    if updated_dt < threshold:
                        reasons.append(f"关机超过{days_offline}天")
                except:
                    pass
        
        # 检查无标签
        tags = instance.get("tags", [])
        if missing_tags and (not tags or len(tags) == 0):
            reasons.append("无标签")
        
        # 检查 watchdog 禁用
        if not instance.get("watchdog_enabled", True):
            reasons.append("Watchdog已禁用")
        
        # 检查无 IPv4（可能是废弃实例）
        ipv4 = instance.get("ipv4", [])
        if not ipv4:
            reasons.append("无公网IP")
        
        if reasons:
            instance_type = instance.get("type", "unknown")
            monthly_cost = INSTANCE_PRICING.get(instance_type, {}).get("monthly", 0)
            
            idle_instances.append({
                "id": instance.get("id"),
                "label": instance.get("label"),
                "region": instance.get("region"),
                "type": instance_type,
                "status": instance.get("status"),
                "reasons": reasons,
                "monthly_cost": monthly_cost,
                "created": instance.get("created"),
            })
    
    # 计算潜在节省
    total_saving = sum(i["monthly_cost"] for i in idle_instances)
    
    report_lines = [
        "🔍 闲置资源检测报告",
        "",
        f"检测条件:",
        f"  关机超过: {days_offline}天",
        f"  检查无标签: {'是' if missing_tags else '否'}",
        "",
        f"发现闲置实例: {len(idle_instances)}台",
        f"潜在月度节省: ${total_saving:.2f}",
        f"潜在年度节省: ${total_saving * 12:.2f}",
    ]
    
    if idle_instances:
        report_lines.append("")
        report_lines.append("闲置实例列表:")
        
        for inst in sorted(idle_instances, key=lambda x: x["monthly_cost"], reverse=True):
            report_lines.extend([
                f"",
                f"🖥️ {inst['label']} (ID: {inst['id']})",
                f"  区域: {inst['region']} | 类型: {inst['type']} | 状态: {inst['status']}",
                f"  闲置原因: {', '.join(inst['reasons'])}",
                f"  月度费用: ${inst['monthly_cost']:.2f}",
                f"  创建时间: {inst['created'][:10] if inst['created'] else 'unknown'}",
            ])
        
        report_lines.extend([
            "",
            "💡 建议操作:",
            "  1. 对于长期关机实例，考虑删除而非保留",
            "  2. 为所有实例添加标签以便管理",
            "  3. 启用 Watchdog 防止实例无响应",
            "  4. 定期审查无公网IP的实例是否为测试遗留",
        ])
    else:
        report_lines.append("")
        report_lines.append("✅ 未发现闲置资源")
    
    return [TextContent(type="text", text="\n".join(report_lines))]
