# 🦙 羊毛信息自动采集器

自动采集全网优惠/漏洞信息，筛选后推送到企业微信群。

## 架构

```
数据源 → 采集器 → 筛选引擎 → 企业微信群机器人
```

- **采集器**: 什么值得买、京东联盟API
- **筛选**: 折扣≥50%、品牌商品优先、去重
- **推送**: 企业微信群机器人（Markdown格式）

## 部署步骤

### 1. 克隆项目

```bash
git clone https://github.com/你的用户名/deals-monitor.git
cd deals-monitor
```

### 2. 配置企业微信群机器人

1. 打开微信群 → 右上角「...」→ 群机器人 → 添加企业微信群机器人
2. 复制 Webhook 地址

### 3. 配置 GitHub Secrets

在 GitHub 仓库 Settings → Secrets and variables → Actions 中添加：

| Secret 名称 | 说明 |
|-------------|------|
| `WECHAT_WEBHOOK_URL` | 企业微信群机器人 Webhook 地址（必填） |
| `JD_APP_KEY` | 京东联盟 AppKey（可选） |
| `JD_APP_SECRET` | 京东联盟 AppSecret（可选） |

### 4. 推送到 GitHub

```bash
git add .
git commit -m "初始化羊毛信息采集器"
git push
```

推送后，GitHub Actions 会自动每30分钟运行一次。

### 5. 验证

- 进入 GitHub → Actions 标签页
- 查看工作流运行状态
- 首次可手动触发测试：Actions → 优惠信息巡检 → Run workflow

## 本地开发

```bash
# 安装依赖
pip install -r requirements.txt

# 配置 .env 文件
echo "WECHAT_WEBHOOK_URL=你的webhook地址" > .env

# 运行测试
python main.py
```

## 扩展数据源

编辑 `deal_collector.py`，在 `collect_all()` 函数中添加新的采集器。

## 注意事项

- GitHub Actions 免费额度：每月 2000 分钟（每30分钟跑一次约 2 分钟，绰绰有余）
- 企业微信群机器人有频率限制（每分钟最多 20 条），本脚本已控制
- 谨慎使用爬虫，遵守目标网站 robots.txt
