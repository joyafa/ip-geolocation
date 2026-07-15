import ipaddress
import requests
from flask import Flask, request, jsonify, render_template_string
from geolite2 import geolite2

app = Flask(__name__)
reader = geolite2.reader()

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
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            display: flex;
            align-items: center;
            justify-content: center;
            padding: 20px;
        }
        .container {
            background: white;
            border-radius: 16px;
            box-shadow: 0 20px 60px rgba(0,0,0,0.3);
            padding: 40px;
            max-width: 600px;
            width: 100%;
        }
        h1 {
            text-align: center;
            color: #333;
            margin-bottom: 30px;
            font-size: 28px;
        }
        .search-box {
            display: flex;
            gap: 10px;
            margin-bottom: 30px;
        }
        input {
            flex: 1;
            padding: 14px 18px;
            border: 2px solid #e0e0e0;
            border-radius: 8px;
            font-size: 16px;
            outline: none;
            transition: border-color 0.3s;
        }
        input:focus {
            border-color: #667eea;
        }
        button {
            padding: 14px 28px;
            background: #667eea;
            color: white;
            border: none;
            border-radius: 8px;
            font-size: 16px;
            cursor: pointer;
            transition: background 0.3s;
        }
        button:hover {
            background: #5568d3;
        }
        .result {
            background: #f8f9fa;
            border-radius: 12px;
            padding: 24px;
            display: none;
        }
        .result.show {
            display: block;
        }
        .result-item {
            display: flex;
            justify-content: space-between;
            padding: 10px 0;
            border-bottom: 1px solid #e0e0e0;
        }
        .result-item:last-child {
            border-bottom: none;
        }
        .result-label {
            color: #666;
            font-weight: 500;
        }
        .result-value {
            color: #333;
            font-weight: 600;
            text-align: right;
            max-width: 60%;
            word-break: break-all;
        }
        .result-tag {
            display: inline-block;
            padding: 2px 8px;
            border-radius: 4px;
            font-size: 12px;
            font-weight: 500;
        }
        .tag-private {
            background: #fff3cd;
            color: #856404;
        }
        .tag-public {
            background: #d4edda;
            color: #155724;
        }
        .tag-cloud {
            background: #cce5ff;
            color: #004085;
        }
        .tag-isp {
            background: #d1ecf1;
            color: #0c5460;
        }
        .tag-education {
            background: #e2e3e5;
            color: #383d41;
        }
        .tag-research {
            background: #f8d7da;
            color: #721c24;
        }
        .tag-finance {
            background: #ffeeba;
            color: #856404;
        }
        .tag-enterprise {
            background: #d4edda;
            color: #155724;
        }
        .data-source {
            margin-top: 12px;
            padding-top: 12px;
            border-top: 1px dashed #e0e0e0;
            font-size: 12px;
            color: #999;
            text-align: right;
        }
        .error {
            background: #fee;
            color: #c33;
            padding: 16px;
            border-radius: 8px;
            display: none;
            margin-bottom: 20px;
        }
        .error.show {
            display: block;
        }
        .loading {
            text-align: center;
            padding: 20px;
            color: #666;
            display: none;
        }
        .loading.show {
            display: block;
        }
        .api-info {
            margin-top: 30px;
            padding-top: 20px;
            border-top: 1px solid #e0e0e0;
            font-size: 14px;
            color: #666;
        }
        .api-info h3 {
            margin-bottom: 10px;
            color: #333;
        }
        .api-info code {
            background: #eef;
            padding: 2px 6px;
            border-radius: 4px;
            font-family: monospace;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>🌍 IP归属地查询</h1>
        <div class="search-box">
            <input type="text" id="ipInput" placeholder="输入IP地址，留空查询当前IP">
            <button onclick="queryIP()">查询</button>
        </div>
        <div class="error" id="errorBox"></div>
        <div class="loading" id="loading">查询中...</div>
        <div class="result" id="resultBox">
            <div class="result-item">
                <span class="result-label">IP地址</span>
                <span class="result-value" id="resIp">-</span>
            </div>
            <div class="result-item">
                <span class="result-label">IP类型</span>
                <span class="result-value" id="resIpType">-</span>
            </div>
            <div class="result-item" id="resOrgTypeRow" style="display:none;">
                <span class="result-label">机构类型</span>
                <span class="result-value" id="resOrgType">-</span>
            </div>
            <div class="result-item" id="resOrgNameRow" style="display:none;">
                <span class="result-label">机构/云服务商</span>
                <span class="result-value" id="resOrgName">-</span>
            </div>
            <div class="result-item" id="resDescRow" style="display:none;">
                <span class="result-label">描述</span>
                <span class="result-value" id="resDesc">-</span>
            </div>
            <div class="result-item">
                <span class="result-label">国家</span>
                <span class="result-value" id="resCountry">-</span>
            </div>
            <div class="result-item">
                <span class="result-label">省份/州</span>
                <span class="result-value" id="resProvince">-</span>
            </div>
            <div class="result-item">
                <span class="result-label">城市</span>
                <span class="result-value" id="resCity">-</span>
            </div>
            <div class="result-item">
                <span class="result-label">邮编</span>
                <span class="result-value" id="resPostal">-</span>
            </div>
            <div class="result-item">
                <span class="result-label">时区</span>
                <span class="result-value" id="resTimezone">-</span>
            </div>
            <div class="result-item">
                <span class="result-label">经纬度</span>
                <span class="result-value" id="resCoords">-</span>
            </div>
            <div class="result-item" id="resIspRow" style="display:none;">
                <span class="result-label">运营商</span>
                <span class="result-value" id="resIsp">-</span>
            </div>
            <div class="result-item" id="resOrgRow" style="display:none;">
                <span class="result-label">组织</span>
                <span class="result-value" id="resOrg">-</span>
            </div>
            <div class="data-source" id="resDataSource"></div>
        </div>
        <div class="api-info">
            <h3>API 接口</h3>
            <p><code>GET /api/ip/lookup?ip=8.8.8.8</code> - 查询单个IP</p>
            <p><code>POST /api/ip/batch</code> - 批量查询（最多100个）</p>
        </div>
    </div>
    <script>
        async function queryIP() {
            const ip = document.getElementById('ipInput').value.trim();
            const errorBox = document.getElementById('errorBox');
            const loading = document.getElementById('loading');
            const resultBox = document.getElementById('resultBox');

            errorBox.classList.remove('show');
            resultBox.classList.remove('show');
            loading.classList.add('show');

            try {
                const url = ip ? `/api/ip/lookup?ip=${encodeURIComponent(ip)}` : '/api/ip/lookup';
                const res = await fetch(url);
                const data = await res.json();

                loading.classList.remove('show');

                if (data.success) {
                    const d = data.data;
                    document.getElementById('resIp').textContent = d.ip;
                    
                    const ipTypeEl = document.getElementById('resIpType');
                    if (d.is_private) {
                        ipTypeEl.innerHTML = '<span class="result-tag tag-private">内网/私网</span>';
                    } else {
                        ipTypeEl.innerHTML = '<span class="result-tag tag-public">公网</span>';
                    }
                    
                    const descRow = document.getElementById('resDescRow');
                    if (d.description) {
                        descRow.style.display = 'flex';
                        document.getElementById('resDesc').textContent = d.description;
                    } else {
                        descRow.style.display = 'none';
                    }
                    
                    const orgTypeRow = document.getElementById('resOrgTypeRow');
                    const orgNameRow = document.getElementById('resOrgNameRow');
                    if (d.organization) {
                        orgTypeRow.style.display = 'flex';
                        orgNameRow.style.display = 'flex';
                        const orgTypeEl = document.getElementById('resOrgType');
                        const typeClass = 'tag-' + d.organization.type;
                        orgTypeEl.innerHTML = '<span class="result-tag ' + typeClass + '">' + d.organization.type_name + '</span>';
                        document.getElementById('resOrgName').textContent = d.organization.name;
                    } else {
                        orgTypeRow.style.display = 'none';
                        orgNameRow.style.display = 'none';
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
                        'geolite2': 'GeoLite2 本地数据库',
                        'ip-api.com': 'ip-api.com 在线API',
                        'geolite2 + ip-api.com': 'GeoLite2 + ip-api.com',
                        'local': '本地识别'
                    };
                    dataSourceEl.textContent = '数据来源: ' + (sourceMap[d.data_source] || d.data_source || '未知');
                    
                    resultBox.classList.add('show');
                } else {
                    errorBox.textContent = data.message || data.error;
                    errorBox.classList.add('show');
                }
            } catch (e) {
                loading.classList.remove('show');
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

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
