# IP地址归属地查询

基于 Flask 的 IP 归属地查询服务，支持单 IP 查询和批量查询，集成 GeoLite2 本地数据库和 ip-api.com 在线 API 双重数据源，能够识别云服务商、电信运营商、教育机构等多种组织类型。

## 功能特性

- **单 IP 查询**：支持查询单个 IP 地址的归属地信息
- **批量查询**：支持一次查询最多 100 个 IP 地址
- **组织识别**：自动识别云服务商、电信运营商、教育机构、金融机构等
- **私网检测**：自动识别内网 IP、回环地址、组播地址等
- **双重数据源**：优先使用 GeoLite2 本地数据库，数据不足时自动补充 ip-api.com 在线数据
- **桌面应用**：双击即可直接打开应用窗口，无需手动打开浏览器
- **端口自动分配**：启动时自动检测并使用可用端口（优先5000），避免端口冲突
- **深色主题界面**：采用现代化深色主题设计，美观简洁

## 支持的组织类型

### 云服务商
- 阿里云、腾讯云、华为云、百度云、京东云、网易云、UCloud、金山云
- 亚马逊云 (AWS)、微软云 (Azure)、谷歌云 (GCP)、甲骨文云 (OCI)、IBM 云
- DigitalOcean、Vultr、Linode

### 电信运营商
- 中国电信、中国联通、中国移动

### 教育与科研机构
- 教育网 (CERNET)、科技网 (CSTNET)

### 金融机构
- 招商银行、工商银行

### 企业机构
- 阿里巴巴集团、腾讯、百度

## 技术栈

- **框架**: Flask 3.0
- **IP 库**: GeoLite2 (maxminddb-geolite2)
- **在线 API**: ip-api.com
- **HTTP 客户端**: requests
- **桌面窗口**: pywebview

## 安装与运行

### 方式一：直接运行（推荐）

```bash
python app.py
```

程序启动后会自动弹出应用窗口，无需手动打开浏览器。

### 方式二：使用可执行文件

```bash
./dist/ip-geolocation.exe
```

### 方式三：使用安装程序

双击 `installer/ip-geolocation-setup.exe` 启动安装向导，安装完成后可通过桌面快捷方式或开始菜单启动程序。

## API 接口

### 查询单个 IP

**请求地址**: `GET /api/ip/lookup`

**请求参数**:

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| ip | string | 否 | 要查询的 IP 地址，留空则查询客户端 IP |

**示例**:

```bash
# 查询指定 IP
curl "http://localhost:5000/api/ip/lookup?ip=8.8.8.8"

# 查询当前客户端 IP
curl "http://localhost:5000/api/ip/lookup"
```

**响应示例**:

```json
{
  "success": true,
  "data": {
    "ip": "8.8.8.8",
    "is_private": false,
    "country": {
      "iso_code": "US",
      "name": "美国"
    },
    "continent": {
      "code": "NA",
      "name": "北美洲"
    },
    "city": "莫菲特场",
    "postal": "94035",
    "location": {
      "latitude": 37.4229,
      "longitude": -122.085,
      "time_zone": "America/Los_Angeles"
    },
    "subdivisions": [
      {
        "iso_code": "CA",
        "name": "加利福尼亚州"
      }
    ],
    "timezone": "America/Los_Angeles",
    "registered_country": {
      "iso_code": "US",
      "name": "美国"
    },
    "isp": "Google LLC",
    "org": "Google LLC",
    "as": "AS15169 Google LLC",
    "organization": {
      "id": "google_cloud",
      "name": "谷歌云 (GCP)",
      "full_name": "Google Cloud Platform",
      "type": "cloud",
      "type_name": "云服务商",
      "matched_by": "as_number",
      "matched_value": "AS15169"
    },
    "data_source": "geolite2 + ip-api.com"
  }
}
```

### 批量查询 IP

**请求地址**: `POST /api/ip/batch`

**请求体**:

```json
{
  "ips": ["8.8.8.8", "1.1.1.1", "192.168.1.1"]
}
```

**说明**: 单次最多查询 100 个 IP 地址。

**示例**:

```bash
curl -X POST "http://localhost:5000/api/ip/batch" \
  -H "Content-Type: application/json" \
  -d '{"ips": ["8.8.8.8", "1.1.1.1"]}'
```

**响应示例**:

```json
{
  "success": true,
  "total": 2,
  "results": [
    {
      "ip": "8.8.8.8",
      "success": true,
      "data": {
        "ip": "8.8.8.8",
        "is_private": false,
        "country": { "iso_code": "US", "name": "美国" },
        "continent": { "code": "NA", "name": "北美洲" },
        "city": "莫菲特场",
        "postal": "94035",
        "location": { "latitude": 37.4229, "longitude": -122.085 },
        "subdivisions": [{ "iso_code": "CA", "name": "加利福尼亚州" }],
        "timezone": "America/Los_Angeles",
        "isp": "Google LLC",
        "org": "Google LLC",
        "as": "AS15169 Google LLC",
        "organization": {
          "id": "google_cloud",
          "name": "谷歌云 (GCP)",
          "type": "cloud",
          "type_name": "云服务商"
        },
        "data_source": "geolite2 + ip-api.com"
      }
    },
    {
      "ip": "1.1.1.1",
      "success": true,
      "data": {
        "ip": "1.1.1.1",
        "is_private": false,
        "country": { "iso_code": "AU", "name": "澳大利亚" },
        "continent": { "code": "OC", "name": "大洋洲" },
        "city": "悉尼",
        "location": { "latitude": -33.8688, "longitude": 151.2093 },
        "timezone": "Australia/Sydney",
        "isp": "Cloudflare, Inc.",
        "org": "Cloudflare, Inc.",
        "as": "AS13335 Cloudflare, Inc.",
        "data_source": "geolite2 + ip-api.com"
      }
    }
  ]
}
```

### 回环地址查询示例

**请求**:

```bash
curl "http://localhost:5000/api/ip/lookup?ip=127.0.0.1"
```

**响应**:

```json
{
  "success": true,
  "data": {
    "ip": "127.0.0.1",
    "is_private": true,
    "ip_type": "loopback",
    "description": "回环地址",
    "country": {
      "name": "本机",
      "iso_code": "LOCAL"
    },
    "continent": {
      "name": "本地",
      "code": "LOCAL"
    },
    "city": null,
    "postal": null,
    "location": {},
    "subdivisions": [],
    "timezone": null,
    "registered_country": {},
    "data_source": "local"
  }
}
```

### 错误响应

| 状态码 | 错误类型 | 说明 |
|--------|----------|------|
| 400 | Invalid IP address | 提供的 IP 地址无效 |
| 404 | IP not found | 未找到该 IP 的归属地信息 |
| 404 | Not found | 请求的接口不存在 |
| 405 | Method not allowed | 请求方法不允许 |
| 500 | Internal server error | 服务器内部错误 |

**错误响应示例**:

```json
{
  "success": false,
  "error": "Invalid IP address",
  "message": "请提供有效的IP地址"
}
```

## 响应字段说明

| 字段 | 类型 | 说明 |
|------|------|------|
| ip | string | 查询的 IP 地址 |
| is_private | boolean | 是否为私网地址 |
| ip_type | string | 私网 IP 类型（private/loopback/link_local/multicast） |
| description | string | 私网 IP 描述信息 |
| country.name | string | 国家名称 |
| country.iso_code | string | 国家 ISO 代码 |
| continent.name | string | 大洲名称 |
| city | string | 城市名称 |
| postal | string | 邮政编码 |
| location.latitude | number | 纬度 |
| location.longitude | number | 经度 |
| timezone | string | 时区 |
| subdivisions | array | 省/州信息列表 |
| registered_country | object | 注册国家信息 |
| isp | string | 互联网服务提供商 |
| org | string | 组织名称 |
| as | string | AS 号及描述 |
| organization | object | 识别到的组织信息 |
| data_source | string | 数据来源 |

## 数据来源

1. **GeoLite2**：本地 IP 地理数据库，提供基础的国家、城市、经纬度等信息
2. **ip-api.com**：在线 API，补充 ISP、组织、AS 号等详细信息

系统会优先使用 GeoLite2 本地数据，同时调用 ip-api.com 获取更完整的信息，最终结果合并两个数据源的内容。

## 打包构建

### 生成可执行文件

项目已配置好打包脚本，可以将应用打包为 Windows 单文件可执行程序：

```bash
python build_exe.py
```

### 前置条件

1. 安装 PyInstaller：`pip install pyinstaller`
2. GeoLite2 数据库文件（`GeoLite2-City.mmdb`）需存在于项目根目录

### 打包流程

1. 脚本会自动复制 GeoLite2 数据库文件到打包目录
2. 使用 PyInstaller 构建单文件 exe（带图标）
3. 生成的可执行文件位于 `dist/ip-geolocation.exe`

### 生成安装程序

项目已配置好 NSIS 安装脚本，可以生成 Windows 安装程序：

```bash
makensis installer.nsi
```

### 前置条件

1. 安装 NSIS：`winget install --id JRSoftware.InnoSetup.7`
2. 已生成可执行文件：`python build_exe.py`

### 安装程序特性

- 现代化安装向导界面（NSIS Modern UI）
- 创建桌面快捷方式
- 创建开始菜单快捷方式
- 自动创建卸载程序
- 安装后可选择立即启动应用

### 软件特性

- **端口自动分配**：启动时自动检测并使用可用端口（优先5000），避免端口冲突
- **原生窗口界面**：双击即可直接打开应用窗口，无需手动打开浏览器
- **一键关闭**：关闭窗口即退出程序，无需手动停止服务
- **固定版权信息**：版权信息固定显示在窗口底部
- **深色主题**：采用现代化深色主题设计

### 系统依赖

- **WebView2 Runtime**：Windows 10/11 通常已内置。如果未安装，请从 [Microsoft 官网](https://developer.microsoft.com/zh-cn/microsoft-edge/webview2/) 下载安装。

## 许可证

Copyright © 2026 南昌市星纬智创科技有限公司

Apache License 2.0