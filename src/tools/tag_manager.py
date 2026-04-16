"""
批量标签管理工具
"""

from typing import Dict, List, Any

from mcp.types import TextContent

from ..linode_client import LinodeClient


async def batch_tag_management(client: LinodeClient, arguments: Dict[str, Any]) -> List[TextContent]:
    """批量管理标签"""
    action = arguments.get("action")
    tags = arguments.get("tags", [])
    instance_ids = arguments.get("instance_ids", [])
    filter_by_region = arguments.get("filter_by_region")
    
    if not action or not tags:
        return [TextContent(type="text", text="Error: action and tags are required")]
    
    if action not in ["add", "remove", "replace"]:
        return [TextContent(type="text", text=f"Error: invalid action '{action}'. Use add, remove, or replace")]
    
    # 如果没有指定 ID，获取符合条件的实例
    if not instance_ids:
        filters = {}
        if filter_by_region:
            filters["region"] = filter_by_region
        
        instances = await client.get_instances(filters)
        instance_ids = [i.get("id") for i in instances]
    
    results = {
        "success": [],
        "failed": [],
    }
    
    for instance_id in instance_ids:
        try:
            # 获取当前实例
            instance = await client.get_instance(instance_id)
            current_tags = instance.get("tags", [])
            label = instance.get("label", f"ID:{instance_id}")
            
            # 计算新标签
            if action == "add":
                new_tags = list(set(current_tags + tags))
            elif action == "remove":
                new_tags = [t for t in current_tags if t not in tags]
            else:  # replace
                new_tags = tags
            
            # 更新
            await client.update_instance(instance_id, {"tags": new_tags})
            
            results["success"].append({
                "id": instance_id,
                "label": label,
                "old_tags": current_tags,
                "new_tags": new_tags,
            })
            
        except Exception as e:
            results["failed"].append({
                "id": instance_id,
                "error": str(e),
            })
    
    # 生成报告
    report_lines = [
        f"🏷️ 批量标签管理报告",
        "",
        f"操作类型: {action}",
        f"目标标签: {', '.join(tags)}",
        f"处理实例数: {len(instance_ids)}",
        "",
        f"✅ 成功: {len(results['success'])} 台",
    ]
    
    for success in results["success"]:
        report_lines.extend([
            f"",
            f"  {success['label']} (ID: {success['id']})",
            f"    {success['old_tags']} → {success['new_tags']}",
        ])
    
    if results["failed"]:
        report_lines.extend([
            f"",
            f"❌ 失败: {len(results['failed'])} 台",
        ])
        for failed in results["failed"]:
            report_lines.append(f"  ID {failed['id']}: {failed['error']}")
    
    return [TextContent(type="text", text="\n".join(report_lines))]
