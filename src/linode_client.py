"""
Linode API 客户端封装
"""

import json
import os
from typing import Optional, Dict, List, Any

import httpx


class LinodeClient:
    """Linode API 客户端"""
    
    def __init__(self, token: Optional[str] = None):
        self.token = token or os.environ.get("LINODE_API_TOKEN")
        if not self.token:
            raise ValueError("Linode API token is required")
        
        self.base_url = "https://api.linode.com/v4"
        self.headers = {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json",
        }
    
    async def _request(
        self,
        method: str,
        endpoint: str,
        params: Optional[Dict] = None,
        json_data: Optional[Dict] = None,
        extra_headers: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """发送 HTTP 请求"""
        url = f"{self.base_url}{endpoint}"
        headers = self.headers.copy()
        if extra_headers:
            headers.update(extra_headers)
        
        async with httpx.AsyncClient() as client:
            response = await client.request(
                method=method,
                url=url,
                params=params,
                json=json_data,
                headers=headers,
                timeout=30.0
            )
            response.raise_for_status()
            return response.json()
    
    async def get_instances(self, filters: Optional[Dict] = None) -> List[Dict]:
        """获取实例列表，支持过滤"""
        extra_headers = {}
        if filters:
            extra_headers["X-Filter"] = json.dumps(filters)
        
        result = await self._request("GET", "/linode/instances", extra_headers=extra_headers)
        return result.get("data", [])
    
    async def get_instance(self, instance_id: int) -> Dict:
        """获取单个实例详情"""
        return await self._request("GET", f"/linode/instances/{instance_id}")
    
    async def update_instance(self, instance_id: int, data: Dict) -> Dict:
        """更新实例"""
        return await self._request("PUT", f"/linode/instances/{instance_id}", json_data=data)
    
    async def get_volumes(self, filters: Optional[Dict] = None) -> List[Dict]:
        """获取卷列表"""
        extra_headers = {}
        if filters:
            extra_headers["X-Filter"] = json.dumps(filters)
        
        result = await self._request("GET", "/volumes", extra_headers=extra_headers)
        return result.get("data", [])
    
    async def get_networking_ips(self) -> List[Dict]:
        """获取所有 IP 地址"""
        result = await self._request("GET", "/networking/ips")
        return result.get("data", [])
    
    async def get_regions(self) -> List[Dict]:
        """获取所有区域"""
        result = await self._request("GET", "/regions")
        return result.get("data", [])
    
    async def get_types(self) -> List[Dict]:
        """获取所有实例类型"""
        result = await self._request("GET", "/linode/types")
        return result.get("data", [])
    
    async def get_nodebalancers(self) -> List[Dict]:
        """获取 NodeBalancer 列表"""
        result = await self._request("GET", "/nodebalancers")
        return result.get("data", [])
    
    async def get_firewalls(self) -> List[Dict]:
        """获取防火墙列表"""
        result = await self._request("GET", "/networking/firewalls")
        return result.get("data", [])
    
    async def get_account(self) -> Dict:
        """获取账户信息"""
        return await self._request("GET", "/account")
