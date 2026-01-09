import pandas as pd
import os
from datetime import datetime

# 保存数据目录
DATA_DIR = "../data"
if not os.path.exists(DATA_DIR):
    os.makedirs(DATA_DIR)

# 生成模拟的空气质量数据
cities = [
    "北京", "上海", "广州", "深圳", "成都", "杭州", "武汉", "西安", "重庆", "南京",
    "天津", "苏州", "郑州", "长沙", "沈阳", "青岛", "济南", "哈尔滨", "长春", "大连"
]

# 生成模拟数据
mock_data = []
for city in cities:
    # 生成随机AQI数据（50-150之间）
    import random
    aqi = random.randint(50, 150)
    
    # 根据AQI生成其他污染物数据
    pm25 = int(aqi * 0.6 + random.randint(-10, 10))
    pm10 = int(aqi * 0.9 + random.randint(-15, 15))
    o3 = int(aqi * 1.2 + random.randint(-20, 20))
    no2 = random.randint(20, 80)
    so2 = random.randint(5, 30)
    co = round(random.uniform(0.5, 2.5), 1)
    
    # 根据AQI确定空气质量等级和描述
    if aqi <= 50:
        level = "优"
        quality = "空气质量优"
    elif aqi <= 100:
        level = "良"
        quality = "空气质量良好"
    elif aqi <= 150:
        level = "轻度污染"
        quality = "轻度污染"
    else:
        level = "中度污染"
        quality = "中度污染"
    
    # 添加到数据列表
    mock_data.append({
        "城市": city,
        "AQI": aqi,
        "PM2.5": pm25,
        "PM10": pm10,
        "O3": o3,
        "NO2": no2,
        "SO2": so2,
        "CO": co,
        "空气质量等级": level,
        "空气质量描述": quality,
        "爬取时间": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    })

# 转换为DataFrame
df = pd.DataFrame(mock_data)

# 保存到CSV文件
latest_file = os.path.join(DATA_DIR, "latest_air_quality.csv")
history_file = os.path.join(DATA_DIR, "air_quality_data.csv")

df.to_csv(latest_file, index=False, encoding='utf-8-sig')
df.to_csv(history_file, index=False, encoding='utf-8-sig')

print(f"模拟数据生成完成！")
print(f"共生成了{len(mock_data)}个城市的数据")
print(f"最新数据已保存到：{latest_file}")
print(f"历史数据已保存到：{history_file}")
print("\n数据示例：")
print(df.head())