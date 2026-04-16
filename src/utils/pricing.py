"""
Linode 实例类型价格数据
实际项目中可以从 API 动态获取
"""

INSTANCE_PRICING = {
    "g6-nanode-1": {"hourly": 0.0075, "monthly": 5.0, "label": "Nanode 1GB"},
    "g6-standard-1": {"hourly": 0.015, "monthly": 10.0, "label": "Linode 2GB"},
    "g6-standard-2": {"hourly": 0.03, "monthly": 20.0, "label": "Linode 4GB"},
    "g6-standard-4": {"hourly": 0.06, "monthly": 40.0, "label": "Linode 8GB"},
    "g6-standard-6": {"hourly": 0.09, "monthly": 60.0, "label": "Linode 12GB"},
    "g6-standard-8": {"hourly": 0.12, "monthly": 80.0, "label": "Linode 16GB"},
    "g6-standard-16": {"hourly": 0.24, "monthly": 160.0, "label": "Linode 32GB"},
    "g6-standard-20": {"hourly": 0.30, "monthly": 200.0, "label": "Linode 40GB"},
    "g6-standard-24": {"hourly": 0.36, "monthly": 240.0, "label": "Linode 48GB"},
    "g6-standard-32": {"hourly": 0.48, "monthly": 320.0, "label": "Linode 64GB"},
    "g6-dedicated-2": {"hourly": 0.045, "monthly": 30.0, "label": "Dedicated 4GB"},
    "g6-dedicated-4": {"hourly": 0.09, "monthly": 60.0, "label": "Dedicated 8GB"},
    "g6-dedicated-8": {"hourly": 0.18, "monthly": 120.0, "label": "Dedicated 16GB"},
    "g6-dedicated-16": {"hourly": 0.36, "monthly": 240.0, "label": "Dedicated 32GB"},
    "g6-dedicated-32": {"hourly": 0.72, "monthly": 480.0, "label": "Dedicated 64GB"},
    "g6-dedicated-48": {"hourly": 1.08, "monthly": 720.0, "label": "Dedicated 96GB"},
    "g6-dedicated-50": {"hourly": 1.125, "monthly": 750.0, "label": "Dedicated 128GB"},
    "g6-dedicated-56": {"hourly": 1.26, "monthly": 840.0, "label": "Dedicated 256GB"},
    "g6-dedicated-64": {"hourly": 1.44, "monthly": 960.0, "label": "Dedicated 512GB"},
    "g6-highmem-1": {"hourly": 0.03, "monthly": 20.0, "label": "High Memory 4GB"},
    "g6-highmem-2": {"hourly": 0.06, "monthly": 40.0, "label": "High Memory 8GB"},
    "g6-highmem-4": {"hourly": 0.12, "monthly": 80.0, "label": "High Memory 16GB"},
    "g6-highmem-8": {"hourly": 0.24, "monthly": 160.0, "label": "High Memory 32GB"},
    "g6-highmem-16": {"hourly": 0.48, "monthly": 320.0, "label": "High Memory 64GB"},
    "g6-highmem-24": {"hourly": 0.72, "monthly": 480.0, "label": "High Memory 96GB"},
    "g6-highmem-32": {"hourly": 0.96, "monthly": 640.0, "label": "High Memory 128GB"},
    "g6-highmem-48": {"hourly": 1.44, "monthly": 960.0, "label": "High Memory 192GB"},
    "g6-highmem-64": {"hourly": 1.92, "monthly": 1280.0, "label": "High Memory 256GB"},
    "g6-highmem-96": {"hourly": 2.88, "monthly": 1920.0, "label": "High Memory 384GB"},
    "g6-highmem-128": {"hourly": 3.84, "monthly": 2560.0, "label": "High Memory 512GB"},
    "g6-highmem-200": {"hourly": 6.00, "monthly": 4000.0, "label": "High Memory 800GB"},
    "g6-highmem-300": {"hourly": 9.00, "monthly": 6000.0, "label": "High Memory 1200GB"},
    "g6-gpu-1": {"hourly": 1.5, "monthly": 1000.0, "label": "GPU Instance 1"},
    "g6-gpu-2": {"hourly": 3.0, "monthly": 2000.0, "label": "GPU Instance 2"},
    "g6-gpu-3": {"hourly": 4.5, "monthly": 3000.0, "label": "GPU Instance 3"},
    "g6-gpu-4": {"hourly": 6.0, "monthly": 4000.0, "label": "GPU Instance 4"},
}

VOLUME_PRICE_PER_GB = 0.10  # $0.10/GB/月
IP_PRICE_HOURLY = 0.004     # $0.004/小时/IP
