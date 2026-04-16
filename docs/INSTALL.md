# 安装指南

## 系统要求

- Python 3.10+
- pip 或 uv

## 安装步骤

### 1. 克隆仓库

```bash
git clone https://github.com/yourusername/linode-mcp-server.git
cd linode-mcp-server
cat > docs/API.md << 'EOF'
# API 参考

## Linode API 端点使用

本 MCP Server 使用以下 Linode API v4 端点：

### 核心端点

| 端点 | 方法 | 用途 |
|------|------|------|
| `/linode/instances` | GET | 获取实例列表 |
| `/linode/instances/{id}` | GET/PUT | 获取/更新实例 |
| `/volumes` | GET | 获取卷列表 |
| `/networking/ips` | GET | 获取 IP 地址 |
| `/regions` | GET | 获取区域列表 |
| `/linode/types` | GET | 获取实例类型 |

### 过滤功能

使用 `X-Filter` 头部进行过滤：

```python
# 按区域过滤
headers["X-Filter"] = json.dumps({"region": "us-east"})

# 按状态过滤
headers["X-Filter"] = json.dumps({"status": "running"})

# 组合过滤
headers["X-Filter"] = json.dumps({
    "region": "us-east",
    "status": "running"
})
cat > .github/workflows/ci.yml << 'EOF'
name: CI

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main ]

jobs:
  test:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        python-version: ["3.10", "3.11", "3.12"]

    steps:
    - uses: actions/checkout@v4
    
    - name: Set up Python ${{ matrix.python-version }}
      uses: actions/setup-python@v5
      with:
        python-version: ${{ matrix.python-version }}
    
    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install -e ".[dev]"
    
    - name: Lint with ruff
      run: |
        ruff check src/
        ruff format --check src/
    
    - name: Type check with mypy
      run: |
        pip install mypy
        mypy src/ --ignore-missing-imports
    
    - name: Test with pytest
      run: |
        pytest tests/ -v --cov=src --cov-report=xml
    
    - name: Upload coverage
      uses: codecov/codecov-action@v3
      with:
        file: ./coverage.xml
        fail_ci_if_error: false

  publish:
    needs: test
    runs-on: ubuntu-latest
    if: github.event_name == 'push' && startsWith(github.ref, 'refs/tags/v')
    
    steps:
    - uses: actions/checkout@v4
    
    - name: Set up Python
      uses: actions/setup-python@v5
      with:
        python-version: "3.11"
    
    - name: Install build dependencies
      run: |
        python -m pip install --upgrade pip
        pip install build twine
    
    - name: Build package
      run: python -m build
    
    - name: Publish to PyPI
      env:
        TWINE_USERNAME: __token__
        TWINE_PASSWORD: ${{ secrets.PYPI_API_TOKEN }}
      run: twine upload dist/*
