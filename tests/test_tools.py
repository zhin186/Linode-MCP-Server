"""工具测试"""
import pytest
from unittest.mock import AsyncMock, MagicMock

from src.linode_client import LinodeClient
from src.tools.region_stats import get_region_instance_stats


@pytest.fixture
def mock_client():
    client = MagicMock(spec=LinodeClient)
    client.get_instances = AsyncMock()
    return client


@pytest.mark.asyncio
async def test_get_region_instance_stats_empty(mock_client):
    """测试空区域"""
    mock_client.get_instances.return_value = []
    
    result = await get_region_instance_stats(mock_client, {"region": "us-test"})
    
    assert len(result) == 1
    assert "没有找到实例" in result[0].text


@pytest.mark.asyncio
async def test_get_region_instance_stats_with_data(mock_client):
    """测试有数据的区域"""
    mock_client.get_instances.return_value = [
        {
            "id": 1,
            "label": "test-1",
            "type": "g6-standard-1",
            "status": "running",
            "region": "us-east",
            "specs": {"vcpus": 1, "memory": 2048, "disk": 51200},
            "tags": ["test"]
        }
    ]
    
    result = await get_region_instance_stats(mock_client, {"region": "us-east"})
    
    assert len(result) == 1
    assert "us-east" in result[0].text
    assert "1" in result[0].text  # 实例数
