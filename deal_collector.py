"""
deal_collector.py - 优惠信息采集器
采集来源：京东联盟API + 什么值得买
"""

import requests
import json
import time
import re
from datetime import datetime
from bs4 import BeautifulSoup

# ============ 配置区（实际使用前填写） ============

# 京东联盟API配置（https://union.jd.com 注册获取）
JD_APP_KEY = ""       # 你的京东联盟AppKey
JD_APP_SECRET = ""    # 你的京东联盟AppSecret

# 什么值得买（不需要配置）

# ==============================================


def collect_jd_deals():
    """
    采集京东联盟优惠商品
    需要注册京东联盟开放平台：https://union.jd.com
    注册后获取 AppKey 和 AppSecret
    """
    if not JD_APP_KEY:
        return []

    deals = []
    try:
        # 京东联盟API - 获取秒杀商品
        url = "https://api.jd.com/routerjson"
        params = {
            "method": "jd.union.open.goods.jingfen.query",
            "app_key": JD_APP_KEY,
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "format": "json",
            "v": "1.0",
            "param_json": json.dumps({
                "goodsReq": {
                    "pageIndex": 1,
                    "pageSize": 20,
                    "isCoupon": 1,       # 有优惠券
                    "eliteType": 2,       # 2=平价仓(高佣), 3=好券商品
                    "sortName": "price",   # 按价格排序
                    "sort": "asc"
                }
            })
        }
        # 注意：实际需要签名，这里简化了
        # resp = requests.get(url, params=params, timeout=15)
        # data = resp.json()
        # 解析逻辑...

        # 演示数据
        # deals = parse_jd_response(data)

    except Exception as e:
        print(f"[京东采集] 错误: {e}")

    return deals


def collect_smzdm_deals():
    """
    采集什么值得买实时爆料
    不需要API，直接爬取公开页面
    """
    deals = []
    headers = {
        "User-Agent": "Mozilla/5.0 (Linux; Android 13) AppleWebKit/537.36 "
                       "(KHTML, like Gecko) Chrome/120.0.0.0 Mobile Safari/537.36",
        "Referer": "https://www.smzdm.com/",
    }

    try:
        # 什么值得买 - 今日热门板块
        urls = [
            "https://www.smzdm.com/pai/p1/",     # 所有分类
            "https://www.smzdm.com/fenlei/diannaobangong/",  # 电脑办公
            "https://www.smzdm.com/fenlei/shumajiadian/",    # 数码家电
        ]

        for url in urls:
            resp = requests.get(url, headers=headers, timeout=15)
            resp.encoding = "utf-8"

            soup = BeautifulSoup(resp.text, "lxml")
            items = soup.select("li.list-item")

            for item in items:
                try:
                    title_el = item.select_one("h5.item-name a")
                    if not title_el:
                        continue
                    title = title_el.get_text(strip=True)

                    link = title_el.get("href", "")
                    if link and not link.startswith("http"):
                        link = "https://www.smzdm.com" + link

                    # 价格
                    price_el = item.select_one("span.red, span.J_red")
                    price = price_el.get_text(strip=True) if price_el else ""

                    # 原价
                    old_price_el = item.select_one("span.old_price, del")
                    old_price = old_price_el.get_text(strip=True) if old_price_el else ""

                    # 标签（如"历史低价""神价格"等）
                    tag_el = item.select_one("span.tag, span.J_tag")
                    tag = tag_el.get_text(strip=True) if tag_el else ""

                    # 商品图片
                    img_el = item.select_one("img")
                    img_url = ""
                    if img_el:
                        img_url = img_el.get("src") or img_el.get("data-src") or ""

                    # 算折扣
                    discount = 0
                    deal = {
                        "source": "什么值得买",
                        "title": title,
                        "price": price,
                        "old_price": old_price,
                        "discount": discount,
                        "url": link,
                        "tag": tag,
                        "img_url": img_url,
                        "time": datetime.now().strftime("%Y-%m-%d %H:%M"),
                    }

                    # 提取数字做简单折扣计算
                    price_num = extract_number(price)
                    old_price_num = extract_number(old_price)
                    if price_num > 0 and old_price_num > 0:
                        deal["discount"] = round(1 - price_num / old_price_num, 2)

                    deals.append(deal)

                except Exception as e:
                    print(f"  解析单条失败: {e}")
                    continue

            time.sleep(2)  # 礼貌爬取

        print(f"[什么值得买] 采集到 {len(deals)} 条商品")

    except Exception as e:
        print(f"[什么值得买采集] 错误: {e}")

    return deals


def extract_number(text):
    """从文本中提取数字"""
    if not text:
        return 0
    text = text.replace(",", "").replace("，", "")
    nums = re.findall(r"(\d+\.?\d*)", text)
    return float(nums[0]) if nums else 0


def collect_all():
    """采集所有来源"""
    all_deals = []

    print("=" * 50)
    print(f"开始采集优惠信息... {datetime.now().strftime('%H:%M:%S')}")
    print("=" * 50)

    # 1. 什么值得买
    smzdm = collect_smzdm_deals()
    all_deals.extend(smzdm)
    print(f"什么值得买: {len(smzdm)} 条")

    # 2. 京东联盟（如果配置了）
    if JD_APP_KEY:
        jd = collect_jd_deals()
        all_deals.extend(jd)
        print(f"京东联盟: {len(jd)} 条")
    else:
        print("京东联盟: 未配置（跳过）")

    # 3. 可以继续添加更多源...

    print(f"总计: {len(all_deals)} 条")
    print("=" * 50)

    return all_deals


if __name__ == "__main__":
    deals = collect_all()
    for d in deals[:5]:
        print(f"  [{d['tag']}] {d['title']} - ¥{d['price']}")
