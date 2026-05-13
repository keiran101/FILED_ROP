# FileDrop

局域网 / 公网文件快传工具。浏览器打开即用，无需安装客户端。
首先将代码部署到服务器上，然后其余设备既可通过浏览器使用功能。

## 初心
多设备间使用微信、飞书、网盘传文件非常繁琐，本软件解决此痛点，一次部署即可拥有私人快传工具。

## 核心功能

- 拖拽上传 / 点击下载
- 部署后即可局域网快传，配置内网穿透可实现公网快传
- 24 小时自动清理未锁定文件，维护快传体验
- 上传频率、上传大小、网站端口、密码均可自由配置，平衡安全与个性化

---

## 快速开始（本地运行）

```bash
git clone https://github.com/keiran101/FILED_ROP.git
cd FILED_ROP
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env   # 根据模板创建.env，在此修改端口密码等参数
python main.py #程序入口
```

浏览器访问 `http://localhost:1158`

---

## 服务器部署

### 方式一：Docker（推荐）

```bash
git clone https://github.com/keiran101/FILED_ROP.git
cd FILED_ROP
cp .env.example .env   # 修改配置
docker compose up -d
```

查看日志：`docker compose logs -f`

升级：
```bash
git pull
docker compose up -d --build
```

---

## 配置项

所有配置通过 `.env` 文件或环境变量设置，参考。

| 变量 | 默认值 | 说明 |
|------|--------|------|
| `HOST` | `0.0.0.0` | 监听地址 |
| `PORT` | `1158` | 监听端口 |
| `UPLOAD_DIR` | `uploads` | 文件存储目录 |
| `MAX_FILE_SIZE_MB` | `500` | 单文件大小上限（MB） |
| `RATE_LIMIT` | `30` | 每分钟每 IP 最多上传文件数，`0` 不限 |
| `BYPASS_PASSWORD` | `123` | 设置后，前端可输入密码绕过大小限制 |
| `DEVICE_NAME` | `FileDrop` | 界面显示的设备名称 |

---

### 方式二：systemd（裸机）

```bash
# 1. 部署代码
git clone https://github.com/keiran101/FILED_ROP.git /opt/filedrop
cd /opt/filedrop
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
cp .env.example .env   # 修改配置

# 2. 安装服务
sudo cp deploy/filedrop.service /etc/systemd/system/
sudo chown -R www-data:www-data /opt/filedrop
sudo systemctl daemon-reload
sudo systemctl enable --now filedrop
```

查看状态：`sudo systemctl status filedrop`  
查看日志：`sudo journalctl -u filedrop -f`

---

### Nginx 反代（可选，用于 HTTPS / 自定义域名）

```nginx
server {
    listen 80;
    server_name filedrop.example.com;

    client_max_body_size 0;   # 不在 nginx 层限制，由应用控制

    location / {
        proxy_pass http://127.0.0.1:1158;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_request_buffering off;
    }
}
```

配合 [Certbot](https://certbot.eff.org/) 申请 HTTPS 证书。


