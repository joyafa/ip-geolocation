import ipaddress
import requests
import sys
import os
import socket
import threading
from flask import Flask, request, jsonify, render_template_string
import maxminddb

app = Flask(__name__)
reader = None


def init_geolite2():
    global reader
    if getattr(sys, 'frozen', False):
        base_path = sys._MEIPASS
        db_path = os.path.join(base_path, 'GeoLite2-City.mmdb')
    else:
        try:
            from _maxminddb_geolite2 import geolite2_database
            db_path = geolite2_database()
        except ImportError:
            db_path = os.path.join(os.path.dirname(__file__), 'GeoLite2-City.mmdb')
    reader = maxminddb.open_database(db_path)


def find_free_port(start_port=5000, max_attempts=100):
    for port in range(start_port, start_port + max_attempts):
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.bind(('127.0.0.1', port))
                return port
        except OSError:
            continue
    raise RuntimeError("无法找到可用端口")

CLOUD_PROVIDERS = {
    "aliyun": {
        "name": "阿里云",
        "full_name": "Alibaba Cloud",
        "type": "cloud",
        "as_numbers": ["AS45102", "AS37963"],
        "keywords": ["Alibaba Cloud", "Alibaba (US)", "Alibaba Cloud LLC", "Aliyun", "阿里巴巴", "阿里云计算"]
    },
    "tencent_cloud": {
        "name": "腾讯云",
        "full_name": "Tencent Cloud",
        "type": "cloud",
        "as_numbers": ["AS132203", "AS45090"],
        "keywords": ["Tencent Cloud", "Tencent Building", "Shenzhen Tencent", "腾讯云", "腾讯科技"]
    },
    "huawei_cloud": {
        "name": "华为云",
        "full_name": "Huawei Cloud",
        "type": "cloud",
        "as_numbers": ["AS55990", "AS136953"],
        "keywords": ["Huawei Cloud", "Huawei Technologies", "华为云", "华为技术"]
    },
    "aws": {
        "name": "亚马逊云 (AWS)",
        "full_name": "Amazon Web Services",
        "type": "cloud",
        "as_numbers": ["AS16509", "AS14618", "AS38895"],
        "keywords": ["Amazon.com", "Amazon EC2", "AWS", "Amazon Web Services", "亚马逊云"]
    },
    "azure": {
        "name": "微软云 (Azure)",
        "full_name": "Microsoft Azure",
        "type": "cloud",
        "as_numbers": ["AS8075", "AS12076"],
        "keywords": ["Microsoft Azure", "Microsoft Corporation", "微软云", "微软"]
    },
    "google_cloud": {
        "name": "谷歌云 (GCP)",
        "full_name": "Google Cloud Platform",
        "type": "cloud",
        "as_numbers": ["AS15169", "AS396982"],
        "keywords": ["Google Cloud", "Google LLC", "谷歌云", "谷歌"]
    },
    "oracle_cloud": {
        "name": "甲骨文云 (OCI)",
        "full_name": "Oracle Cloud Infrastructure",
        "type": "cloud",
        "as_numbers": ["AS31898"],
        "keywords": ["Oracle Cloud", "Oracle Corporation", "甲骨文"]
    },
    "ibm_cloud": {
        "name": "IBM云",
        "full_name": "IBM Cloud",
        "type": "cloud",
        "as_numbers": ["AS20057", "AS36351"],
        "keywords": ["IBM Cloud", "IBM Corporation"]
    },
    "digitalocean": {
        "name": "DigitalOcean",
        "full_name": "DigitalOcean",
        "type": "cloud",
        "as_numbers": ["AS14061"],
        "keywords": ["DigitalOcean", "Digital Ocean"]
    },
    "vultr": {
        "name": "Vultr",
        "full_name": "Vultr",
        "type": "cloud",
        "as_numbers": ["AS20473"],
        "keywords": ["Vultr", "Choopa"]
    },
    "linode": {
        "name": "Linode",
        "full_name": "Linode",
        "type": "cloud",
        "as_numbers": ["AS63949"],
        "keywords": ["Linode", "Akamai Connected Cloud"]
    },
    "baidu_cloud": {
        "name": "百度云",
        "full_name": "Baidu Cloud",
        "type": "cloud",
        "as_numbers": ["AS55967"],
        "keywords": ["Baidu Cloud", "Baidu", "百度云", "百度"]
    },
    "jd_cloud": {
        "name": "京东云",
        "full_name": "JD Cloud",
        "type": "cloud",
        "as_numbers": ["AS136349"],
        "keywords": ["JD Cloud", "Jingdong", "京东云", "京东"]
    },
    "netease_cloud": {
        "name": "网易云",
        "full_name": "NetEase Cloud",
        "type": "cloud",
        "as_numbers": ["AS45664"],
        "keywords": ["NetEase", "网易"]
    },
    "ucloud": {
        "name": "UCloud",
        "full_name": "UCloud",
        "type": "cloud",
        "as_numbers": ["AS135377"],
        "keywords": ["UCloud"]
    },
    "kingsoft_cloud": {
        "name": "金山云",
        "full_name": "Kingsoft Cloud",
        "type": "cloud",
        "as_numbers": ["AS138709"],
        "keywords": ["Kingsoft Cloud", "金山云"]
    },
    "china_telecom": {
        "name": "中国电信",
        "full_name": "China Telecom",
        "type": "isp",
        "as_numbers": ["AS4134", "AS4812", "AS23650"],
        "keywords": ["China Telecom", "中国电信", "Chinanet"]
    },
    "china_unicom": {
        "name": "中国联通",
        "full_name": "China Unicom",
        "type": "isp",
        "as_numbers": ["AS4808", "AS4837", "AS9929"],
        "keywords": ["China Unicom", "中国联通", "CHINA UNICOM"]
    },
    "china_mobile": {
        "name": "中国移动",
        "full_name": "China Mobile",
        "type": "isp",
        "as_numbers": ["AS9808", "AS56040", "AS24223"],
        "keywords": ["China Mobile", "中国移动"]
    },
    "cernet": {
        "name": "教育网 (CERNET)",
        "full_name": "China Education and Research Network",
        "type": "education",
        "as_numbers": ["AS4538", "AS23910", "AS23911"],
        "keywords": ["CERNET", "China Education", "教育网", "清华大学", "北京大学"]
    },
    "cstnet": {
        "name": "科技网 (CSTNET)",
        "full_name": "China Science and Technology Network",
        "type": "research",
        "as_numbers": ["AS7497", "AS131509"],
        "keywords": ["CSTNET", "Science and Technology", "科技网", "中科院"]
    },
    "cmb": {
        "name": "招商银行",
        "full_name": "China Merchants Bank",
        "type": "finance",
        "as_numbers": [],
        "keywords": ["China Merchants Bank", "招商银行"]
    },
    "icbc": {
        "name": "工商银行",
        "full_name": "Industrial and Commercial Bank of China",
        "type": "finance",
        "as_numbers": [],
        "keywords": ["ICBC", "工商银行"]
    },
    "alibaba_group": {
        "name": "阿里巴巴集团",
        "full_name": "Alibaba Group",
        "type": "enterprise",
        "as_numbers": [],
        "keywords": ["Alibaba Group", "阿里巴巴集团", "Alibaba.com"]
    },
    "tencent": {
        "name": "腾讯",
        "full_name": "Tencent",
        "type": "enterprise",
        "as_numbers": [],
        "keywords": ["Tencent Holdings", "腾讯控股", "腾讯公司"]
    },
    "baidu": {
        "name": "百度",
        "full_name": "Baidu",
        "type": "enterprise",
        "as_numbers": [],
        "keywords": ["Baidu Inc", "百度在线", "百度公司"]
    }
}

ORG_TYPE_MAP = {
    "cloud": "云服务商",
    "isp": "电信运营商",
    "education": "教育机构",
    "research": "科研机构",
    "finance": "金融机构",
    "enterprise": "企业机构",
    "government": "政府机构",
    "unknown": "未知"
}


def identify_org(as_info=None, isp=None, org=None):
    if not as_info and not isp and not org:
        return None

    as_number = None
    if as_info and as_info.startswith("AS"):
        as_number = as_info.split()[0] if " " in as_info else as_info

    for provider_id, provider in CLOUD_PROVIDERS.items():
        if as_number and as_number in provider["as_numbers"]:
            return {
                "id": provider_id,
                "name": provider["name"],
                "full_name": provider["full_name"],
                "type": provider["type"],
                "type_name": ORG_TYPE_MAP.get(provider["type"], "未知"),
                "matched_by": "as_number",
                "matched_value": as_number
            }

    search_text = " ".join(filter(None, [isp, org, as_info]))
    if search_text:
        search_lower = search_text.lower()
        for provider_id, provider in CLOUD_PROVIDERS.items():
            for keyword in provider["keywords"]:
                if keyword.lower() in search_lower:
                    return {
                        "id": provider_id,
                        "name": provider["name"],
                        "full_name": provider["full_name"],
                        "type": provider["type"],
                        "type_name": ORG_TYPE_MAP.get(provider["type"], "未知"),
                        "matched_by": "keyword",
                        "matched_value": keyword
                    }

    return None


def is_valid_ip(ip_str):
    try:
        ipaddress.ip_address(ip_str)
        return True
    except ValueError:
        return False


def is_private_ip(ip_str):
    try:
        ip = ipaddress.ip_address(ip_str)
        return ip.is_private or ip.is_loopback or ip.is_link_local or ip.is_multicast
    except ValueError:
        return False


def get_private_ip_info(ip_str):
    ip = ipaddress.ip_address(ip_str)
    info = {
        "ip": ip_str,
        "is_private": True,
        "ip_type": "",
        "description": "",
        "country": {"name": "局域网", "iso_code": "LAN"},
        "continent": {"name": "内网", "code": "INTERNAL"},
        "city": None,
        "postal": None,
        "location": {},
        "subdivisions": [],
        "timezone": None,
        "registered_country": {},
        "data_source": "local"
    }

    if ip.is_loopback:
        info["ip_type"] = "loopback"
        info["description"] = "回环地址（本机）"
        info["city"] = "本机"
    elif ip.is_link_local:
        info["ip_type"] = "link_local"
        info["description"] = "链路本地地址"
    elif ip.is_multicast:
        info["ip_type"] = "multicast"
        info["description"] = "组播地址"
    elif ip.is_private:
        info["ip_type"] = "private"
        if str(ip).startswith("10."):
            info["description"] = "A类私网地址 (10.0.0.0/8)"
        elif str(ip).startswith("172.1"):
            info["description"] = "B类私网地址 (172.16.0.0/12)"
        elif str(ip).startswith("192.168."):
            info["description"] = "C类私网地址 (192.168.0.0/16)"
        else:
            info["description"] = "私网地址"

    return info


def query_ip_api(ip):
    try:
        url = f"http://ip-api.com/json/{ip}?lang=zh-CN"
        response = requests.get(url, timeout=5)
        if response.status_code != 200:
            return None
        data = response.json()
        if data.get("status") != "success":
            return None

        location = {
            "ip": ip,
            "is_private": False,
            "country": {
                "iso_code": data.get("countryCode"),
                "name": data.get("country")
            },
            "continent": {
                "code": None,
                "name": None
            },
            "city": data.get("city"),
            "postal": data.get("zip"),
            "location": {
                "latitude": data.get("lat"),
                "longitude": data.get("lon"),
                "time_zone": data.get("timezone")
            },
            "subdivisions": [],
            "timezone": data.get("timezone"),
            "registered_country": {
                "name": data.get("country"),
                "iso_code": data.get("countryCode")
            },
            "isp": data.get("isp"),
            "org": data.get("org"),
            "as": data.get("as"),
            "data_source": "ip-api.com"
        }

        if data.get("regionName"):
            location["subdivisions"].append({
                "iso_code": data.get("region"),
                "name": data.get("regionName")
            })

        org_info = identify_org(
            as_info=data.get("as"),
            isp=data.get("isp"),
            org=data.get("org")
        )
        if org_info:
            location["organization"] = org_info

        return location
    except Exception:
        return None


def query_ip_location(ip):
    if is_private_ip(ip):
        return get_private_ip_info(ip)

    result = reader.get(ip)
    if not result:
        api_result = query_ip_api(ip)
        if api_result:
            return api_result
        return None

    location = {
        "ip": ip,
        "is_private": False,
        "country": {},
        "continent": {},
        "city": None,
        "postal": None,
        "location": {},
        "subdivisions": [],
        "timezone": None,
        "registered_country": {},
        "data_source": "geolite2"
    }

    if "country" in result:
        location["country"] = {
            "iso_code": result["country"].get("iso_code"),
            "name": result["country"].get("names", {}).get("zh-CN") or result["country"].get("names", {}).get("en"),
            "names": result["country"].get("names", {})
        }

    if "continent" in result:
        location["continent"] = {
            "code": result["continent"].get("code"),
            "name": result["continent"].get("names", {}).get("zh-CN") or result["continent"].get("names", {}).get("en"),
            "names": result["continent"].get("names", {})
        }

    if "city" in result:
        location["city"] = result["city"].get("names", {}).get("zh-CN") or result["city"].get("names", {}).get("en")

    if "postal" in result:
        location["postal"] = result["postal"].get("code")

    if "location" in result:
        location["location"] = {
            "latitude": result["location"].get("latitude"),
            "longitude": result["location"].get("longitude"),
            "accuracy_radius": result["location"].get("accuracy_radius"),
            "time_zone": result["location"].get("time_zone")
        }
        location["timezone"] = result["location"].get("time_zone")

    if "subdivisions" in result:
        for sub in result["subdivisions"]:
            location["subdivisions"].append({
                "iso_code": sub.get("iso_code"),
                "name": sub.get("names", {}).get("zh-CN") or sub.get("names", {}).get("en")
            })

    if "registered_country" in result:
        location["registered_country"] = {
            "iso_code": result["registered_country"].get("iso_code"),
            "name": result["registered_country"].get("names", {}).get("zh-CN") or result["registered_country"].get("names", {}).get("en")
        }

    api_result = query_ip_api(ip)
    if api_result:
        location["isp"] = api_result.get("isp")
        location["org"] = api_result.get("org")
        location["as"] = api_result.get("as")
        if "organization" in api_result:
            location["organization"] = api_result["organization"]
        location["data_source"] = "geolite2 + ip-api.com"

    return location


@app.route("/")
def index():
    return render_template_string(HTML_TEMPLATE)


@app.route("/api/ip/lookup", methods=["GET"])
def ip_lookup():
    ip = request.args.get("ip")
    if not ip:
        ip = request.remote_addr

    if not is_valid_ip(ip):
        return jsonify({
            "success": False,
            "error": "Invalid IP address",
            "message": "请提供有效的IP地址"
        }), 400

    try:
        result = query_ip_location(ip)
        if result:
            return jsonify({
                "success": True,
                "data": result
            })
        else:
            return jsonify({
                "success": False,
                "error": "IP not found",
                "message": "未找到该IP的归属地信息",
                "ip": ip
            }), 404
    except Exception as e:
        return jsonify({
            "success": False,
            "error": "Internal server error",
            "message": str(e)
        }), 500


@app.route("/api/ip/batch", methods=["POST"])
def batch_lookup():
    data = request.get_json()
    if not data or "ips" not in data:
        return jsonify({
            "success": False,
            "error": "Missing 'ips' parameter",
            "message": "请提供IP地址列表"
        }), 400

    ips = data["ips"]
    if not isinstance(ips, list):
        return jsonify({
            "success": False,
            "error": "'ips' must be an array",
            "message": "IP地址必须为数组格式"
        }), 400

    if len(ips) > 100:
        return jsonify({
            "success": False,
            "error": "Too many IPs",
            "message": "单次最多查询100个IP地址"
        }), 400

    results = []
    for ip in ips:
        if not is_valid_ip(ip):
            results.append({
                "ip": ip,
                "success": False,
                "error": "Invalid IP address"
            })
            continue

        try:
            location = query_ip_location(ip)
            if location:
                results.append({
                    "ip": ip,
                    "success": True,
                    "data": location
                })
            else:
                results.append({
                    "ip": ip,
                    "success": False,
                    "error": "IP not found"
                })
        except Exception as e:
            results.append({
                "ip": ip,
                "success": False,
                "error": str(e)
            })

    return jsonify({
        "success": True,
        "total": len(ips),
        "results": results
    })


@app.errorhandler(404)
def not_found(e):
    return jsonify({
        "success": False,
        "error": "Not found",
        "message": "接口不存在"
    }), 404


@app.errorhandler(405)
def method_not_allowed(e):
    return jsonify({
        "success": False,
        "error": "Method not allowed",
        "message": "请求方法不允许"
    }), 405


HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>IP归属地查询</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: #1a1b26;
            height: 100vh;
            overflow: hidden;
            display: flex;
            flex-direction: column;
            padding-bottom: 40px;
        }
        .header {
            display: flex;
            align-items: center;
            gap: 16px;
            padding: 14px 20px;
            background: #24253a;
            border-bottom: 1px solid #2e3246;
        }
        .header h1 {
            color: #8cb4ff;
            font-size: 20px;
            font-weight: 600;
        }
        .header p {
            color: #7a8aa4;
            font-size: 13px;
        }
        .main {
            flex: 1;
            padding: 16px;
            display: flex;
            flex-direction: column;
            gap: 12px;
            overflow: hidden;
        }
        .search-area {
            background: #24253a;
            border-radius: 10px;
            padding: 16px;
            border: 1px solid #2e3246;
        }
        .search-box {
            display: flex;
            gap: 12px;
        }
        .search-box input {
            flex: 1;
            padding: 12px 16px;
            border: 1px solid #2e3246;
            border-radius: 8px;
            font-size: 15px;
            outline: none;
            background: #1f2335;
            color: #e4eaf5;
            transition: border-color 0.2s;
        }
        .search-box input:focus {
            border-color: #7aa2f7;
        }
        .search-box input::placeholder {
            color: #6b7a94;
        }
        .search-box button {
            padding: 12px 22px;
            background: linear-gradient(135deg, #7aa2f7 0%, #5d6af7 100%);
            color: white;
            border: none;
            border-radius: 8px;
            font-size: 14px;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.2s;
            min-width: 80px;
        }
        .search-box button:hover:not(:disabled) {
            background: linear-gradient(135deg, #698ef7 0%, #4d5df7 100%);
        }
        .search-box button:disabled {
            background: #414868;
            cursor: not-allowed;
        }
        .error {
            background: rgba(247, 140, 140, 0.1);
            color: #ff9a9a;
            padding: 12px 16px;
            border-radius: 8px;
            font-size: 14px;
            display: none;
            border: 1px solid rgba(247, 140, 140, 0.3);
        }
        .error.show {
            display: block;
        }
        .loading {
            text-align: center;
            padding: 24px;
            color: #7a8aa4;
            font-size: 14px;
            display: none;
        }
        .loading.show {
            display: block;
        }
        .loading .spinner {
            width: 20px;
            height: 20px;
            border: 2px solid #2e3246;
            border-top-color: #7aa2f7;
            border-radius: 50%;
            animation: spin 0.8s linear infinite;
            margin: 0 auto 8px;
        }
        @keyframes spin {
            to { transform: rotate(360deg); }
        }
        .result {
            display: none;
            flex: 1;
            display: none;
            flex-direction: column;
            min-height: 0;
        }
        .result.show {
            display: flex;
        }
        .card {
            background: #24253a;
            border-radius: 10px;
            border: 1px solid #2e3246;
            overflow: hidden;
            flex: 1;
            display: flex;
            flex-direction: column;
        }
        .card-section {
            padding: 14px 18px;
        }
        .card-section + .card-section {
            border-top: 1px solid #2e3246;
        }
        .section-title {
            font-size: 13px;
            color: #8b9bb4;
            font-weight: 600;
            margin-bottom: 10px;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }
        .grid {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 10px 14px;
        }
        .info-row {
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 7px 0;
        }
        .info-label {
            color: #8b9bb4;
            font-size: 14px;
            flex-shrink: 0;
            width: 60px;
        }
        .info-value {
            color: #e4eaf5;
            font-size: 14px;
            font-weight: 500;
            text-align: right;
            flex: 1;
            margin-left: 10px;
            word-break: break-all;
        }
        .tag {
            display: inline-block;
            padding: 3px 10px;
            border-radius: 4px;
            font-size: 12px;
            font-weight: 600;
        }
        .tag-loopback { background: rgba(168, 85, 247, 0.2); color: #a855f7; }
        .tag-private { background: rgba(250, 204, 21, 0.2); color: #facc15; }
        .tag-public { background: rgba(34, 197, 94, 0.2); color: #22c55e; }
        .tag-cloud { background: rgba(59, 130, 246, 0.2); color: #3b82f6; }
        .tag-isp { background: rgba(14, 165, 233, 0.2); color: #0ea5e9; }
        .tag-education { background: rgba(148, 163, 184, 0.2); color: #94a3b8; }
        .tag-research { background: rgba(239, 68, 68, 0.2); color: #ef4444; }
        .tag-finance { background: rgba(250, 204, 21, 0.2); color: #facc15; }
        .tag-enterprise { background: rgba(34, 197, 94, 0.2); color: #22c55e; }
        .data-source {
            font-size: 12px;
            color: #6b7a94;
            text-align: center;
            padding-top: 10px;
            margin-top: auto;
        }
        .copyright {
            font-size: 12px;
            color: #6b7a94;
            text-align: center;
            padding: 10px 0;
            border-top: 1px solid #2e3246;
            position: fixed;
            bottom: 0;
            left: 0;
            right: 0;
            background: #1a1b26;
        }
    </style>
</head>
<body>
    <div class="header">
        <h1>🌍 IP归属地查询</h1>
        <p>输入IP地址获取归属信息</p>
    </div>
    
    <div class="main">
        <div class="search-area">
            <div class="search-box">
                <input type="text" id="ipInput" placeholder="输入IP地址，留空查询当前IP">
                <button id="queryBtn" onclick="queryIP()">查询</button>
            </div>
        </div>
        
        <div class="error" id="errorBox"></div>
        
        <div class="loading" id="loading">
            <div class="spinner"></div>
            <span>查询中...</span>
        </div>
        
        <div class="result" id="resultBox">
            <div class="card">
                <div class="card-section">
                    <div class="section-title">基本信息</div>
                    <div class="info-row">
                        <span class="info-label">IP</span>
                        <span class="info-value" id="resIp">-</span>
                    </div>
                    <div class="info-row">
                        <span class="info-label">类型</span>
                        <span class="info-value" id="resIpType">-</span>
                    </div>
                </div>
                
                <div class="card-section">
                    <div class="section-title">地理位置</div>
                    <div class="grid">
                        <div class="info-row">
                            <span class="info-label">国家</span>
                            <span class="info-value" id="resCountry">-</span>
                        </div>
                        <div class="info-row">
                            <span class="info-label">省份</span>
                            <span class="info-value" id="resProvince">-</span>
                        </div>
                        <div class="info-row">
                            <span class="info-label">城市</span>
                            <span class="info-value" id="resCity">-</span>
                        </div>
                        <div class="info-row">
                            <span class="info-label">邮编</span>
                            <span class="info-value" id="resPostal">-</span>
                        </div>
                        <div class="info-row">
                            <span class="info-label">时区</span>
                            <span class="info-value" id="resTimezone">-</span>
                        </div>
                        <div class="info-row">
                            <span class="info-label">经纬</span>
                            <span class="info-value" id="resCoords">-</span>
                        </div>
                    </div>
                </div>
                
                <div class="card-section">
                    <div class="section-title">机构信息</div>
                    <div class="info-row" id="resOrgTypeRow" style="display:none;">
                        <span class="info-label">类型</span>
                        <span class="info-value" id="resOrgType">-</span>
                    </div>
                    <div class="info-row" id="resOrgNameRow" style="display:none;">
                        <span class="info-label">机构</span>
                        <span class="info-value" id="resOrgName">-</span>
                    </div>
                    <div class="info-row" id="resIspRow" style="display:none;">
                        <span class="info-label">运营商</span>
                        <span class="info-value" id="resIsp">-</span>
                    </div>
                    <div class="info-row" id="resOrgRow" style="display:none;">
                        <span class="info-label">组织</span>
                        <span class="info-value" id="resOrg">-</span>
                    </div>
                </div>
                
                <div class="data-source" id="resDataSource"></div>
            </div>
        </div>
        
        <div class="copyright">Copyright © 2026 南昌市星纬智创科技有限公司</div>
    </div>

    <script>
        async function queryIP() {
            const ip = document.getElementById('ipInput').value.trim();
            const errorBox = document.getElementById('errorBox');
            const loading = document.getElementById('loading');
            const resultBox = document.getElementById('resultBox');
            const queryBtn = document.getElementById('queryBtn');

            errorBox.classList.remove('show');
            resultBox.classList.remove('show');
            loading.classList.add('show');
            queryBtn.disabled = true;
            queryBtn.textContent = '查询中';

            try {
                const url = ip ? `/api/ip/lookup?ip=${encodeURIComponent(ip)}` : '/api/ip/lookup';
                const res = await fetch(url);
                const data = await res.json();

                loading.classList.remove('show');
                queryBtn.disabled = false;
                queryBtn.textContent = '查询';

                if (data.success) {
                    const d = data.data;
                    document.getElementById('resIp').textContent = d.ip;
                    
                    const ipTypeEl = document.getElementById('resIpType');
                    if (d.ip_type === 'loopback') {
                        ipTypeEl.innerHTML = '<span class="tag tag-loopback">回环地址（本机）</span>';
                    } else if (d.is_private) {
                        ipTypeEl.innerHTML = '<span class="tag tag-private">内网/私网</span>';
                    } else {
                        ipTypeEl.innerHTML = '<span class="tag tag-public">公网</span>';
                    }
                    
                    document.getElementById('resCountry').textContent = d.country?.name || '-';
                    document.getElementById('resProvince').textContent = d.subdivisions?.[0]?.name || '-';
                    document.getElementById('resCity').textContent = d.city || '-';
                    document.getElementById('resPostal').textContent = d.postal || '-';
                    document.getElementById('resTimezone').textContent = d.timezone || '-';
                    const lat = d.location?.latitude;
                    const lon = d.location?.longitude;
                    document.getElementById('resCoords').textContent = 
                        (lat !== undefined && lon !== undefined) ? `${lat}, ${lon}` : '-';
                    
                    const orgTypeRow = document.getElementById('resOrgTypeRow');
                    const orgNameRow = document.getElementById('resOrgNameRow');
                    if (d.organization) {
                        orgTypeRow.style.display = 'flex';
                        orgNameRow.style.display = 'flex';
                        const typeClass = 'tag-' + d.organization.type;
                        document.getElementById('resOrgType').innerHTML = '<span class="tag ' + typeClass + '">' + d.organization.type_name + '</span>';
                        document.getElementById('resOrgName').textContent = d.organization.name;
                    } else {
                        orgTypeRow.style.display = 'none';
                        orgNameRow.style.display = 'none';
                    }
                    
                    const ispRow = document.getElementById('resIspRow');
                    if (d.isp) {
                        ispRow.style.display = 'flex';
                        document.getElementById('resIsp').textContent = d.isp;
                    } else {
                        ispRow.style.display = 'none';
                    }
                    
                    const orgRow = document.getElementById('resOrgRow');
                    if (d.org) {
                        orgRow.style.display = 'flex';
                        document.getElementById('resOrg').textContent = d.org;
                    } else {
                        orgRow.style.display = 'none';
                    }
                    
                    const dataSourceEl = document.getElementById('resDataSource');
                    const sourceMap = {
                        'geolite2': '数据来源: GeoLite2',
                        'ip-api.com': '数据来源: ip-api.com',
                        'geolite2 + ip-api.com': '数据来源: GeoLite2 + ip-api.com',
                        'local': '数据来源: 本地识别'
                    };
                    dataSourceEl.textContent = sourceMap[d.data_source] || '数据来源: 未知';
                    
                    resultBox.classList.add('show');
                } else {
                    errorBox.textContent = data.message || data.error;
                    errorBox.classList.add('show');
                }
            } catch (e) {
                loading.classList.remove('show');
                queryBtn.disabled = false;
                queryBtn.textContent = '查询';
                errorBox.textContent = '查询失败: ' + e.message;
                errorBox.classList.add('show');
            }
        }

        document.getElementById('ipInput').addEventListener('keypress', function(e) {
            if (e.key === 'Enter') queryIP();
        });
    </script>
</body>
</html>
"""

def run_flask(port):
    app.run(host="127.0.0.1", port=port, debug=False, use_reloader=False)


if __name__ == "__main__":
    init_geolite2()
    port = find_free_port()
    
    flask_thread = threading.Thread(target=run_flask, args=(port,), daemon=True)
    flask_thread.start()
    
    try:
        import webview
        webview.create_window("IP地址归属地查询", f"http://127.0.0.1:{port}", width=700, height=960)
        webview.start()
    except ImportError:
        import ctypes
        ctypes.windll.user32.MessageBoxW(None, f"服务已启动，请在浏览器中访问 http://127.0.0.1:{port}", "IP地址归属地查询", 0)
        flask_thread.join()
