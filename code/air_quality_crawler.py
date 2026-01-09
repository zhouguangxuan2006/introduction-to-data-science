import requests
import pandas as pd
import os
from datetime import datetime

# AQICN API配置（使用真实API key）
API_KEY = "4b4e3b4f1ee1fe857e6c84641841613fa967a4de"  # 使用提供的真实API key
BASE_URL = "https://api.waqi.info"

# 保存数据目录
DATA_DIR = "../data"
if not os.path.exists(DATA_DIR):
    os.makedirs(DATA_DIR)

# 城市映射表（AQICN使用拼音或英文名称）
city_mapping = {
    # 华北地区
    "北京": "beijing",
    "天津": "tianjin",
    "石家庄": "shijiazhuang",
    "太原": "taiyuan",
    "呼和浩特": "hohhot",
    "唐山": "tangshan",
    "秦皇岛": "qinhuangdao",
    "邯郸": "handan",
    "邢台": "xingtai",
    "保定": "baoding",
    "张家口": "zhangjiakou",
    "承德": "chengde",
    "沧州": "cangzhou",
    "廊坊": "langfang",
    "衡水": "hengshui",
    "大同": "datong",
    "阳泉": "yangquan",
    "长治": "changzhi",
    "晋城": "jincheng",
    "朔州": "shuozhou",
    "晋中": "jinzhong",
    "运城": "yuncheng",
    "忻州": "xinzhou",
    "临汾": "linfen",
    "吕梁": "lvliang",
    "包头": "baotou",
    "乌海": "wuhai",
    "赤峰": "chifeng",
    "通辽": "tongliao",
    "鄂尔多斯": "ordos",
    "呼伦贝尔": "hulunbuir",
    "巴彦淖尔": "bayannur",
    "乌兰察布": "ulanchap",
    "兴安盟": "xinganmeng",
    "锡林郭勒盟": "xilinguole",
    "阿拉善盟": "alxa",
    
    # 东北地区
    "沈阳": "shenyang",
    "大连": "dalian",
    "鞍山": "anshan",
    "抚顺": "fushun",
    "本溪": "benxi",
    "丹东": "dandong",
    "锦州": "jinzhou",
    "营口": "yingkou",
    "阜新": "fuxin",
    "辽阳": "liaoyang",
    "铁岭": "tieling",
    "朝阳": "chaoyang",
    "盘锦": "panjin",
    "葫芦岛": "huludao",
    "长春": "changchun",
    "吉林": "jilin",
    "四平": "siping",
    "辽源": "liaoyuan",
    "通化": "tonghua",
    "白山": "baishan",
    "松原": "songyuan",
    "白城": "baicheng",
    "延边朝鲜族自治州": "yanbian",
    "哈尔滨": "harbin",
    "齐齐哈尔": "qiqihar",
    "鸡西": "jixi",
    "鹤岗": "hegang",
    "双鸭山": "shuangyashan",
    "大庆": "daqing",
    "伊春": "yichun",
    "佳木斯": "jiamusi",
    "七台河": "qitaihe",
    "牡丹江": "mudanjiang",
    "黑河": "heihe",
    "绥化": "suihua",
    "大兴安岭地区": "daxinganling",
    
    # 华东地区
    "上海": "shanghai",
    "南京": "nanjing",
    "无锡": "wuxi",
    "徐州": "xuzhou",
    "常州": "changzhou",
    "苏州": "suzhou",
    "南通": "nantong",
    "连云港": "lianyungang",
    "淮安": "huaian",
    "盐城": "yancheng",
    "扬州": "yangzhou",
    "镇江": "zhenjiang",
    "泰州": "taizhou",
    "宿迁": "suqian",
    "杭州": "hangzhou",
    "宁波": "ningbo",
    "温州": "wenzhou",
    "嘉兴": "jiaxing",
    "湖州": "huzhou",
    "绍兴": "shaoxing",
    "金华": "jinhua",
    "衢州": "quzhou",
    "舟山": "zhoushan",
    "台州": "taizhou",
    "丽水": "lishui",
    "合肥": "hefei",
    "芜湖": "wuhu",
    "蚌埠": "bengbu",
    "淮南": "huainan",
    "马鞍山": "maanshan",
    "淮北": "huaibei",
    "铜陵": "tongling",
    "安庆": "anqing",
    "黄山": "huangshan",
    "滁州": "chuzhou",
    "阜阳": "fuyang",
    "宿州": "suzhou-anhui",
    "六安": "liuan",
    "亳州": "bozhou",
    "池州": "chizhou",
    "宣城": "xuancheng",
    "福州": "fuzhou",
    "厦门": "xiamen",
    "莆田": "putian",
    "三明": "sanming",
    "泉州": "quanzhou",
    "漳州": "zhangzhou",
    "南平": "nanping",
    "龙岩": "longyan",
    "宁德": "ningde",
    "南昌": "nanchang",
    "景德镇": "jingdezhen",
    "萍乡": "pingxiang",
    "九江": "jiujiang",
    "新余": "xinyu",
    "鹰潭": "yingtan",
    "赣州": "ganzhou",
    "吉安": "jian",
    "宜春": "yichun-jiangxi",
    "抚州": "fuzhou-jiangxi",
    "上饶": "shangrao",
    "济南": "jinan",
    "青岛": "qingdao",
    "淄博": "zibo",
    "枣庄": "zaozhuang",
    "东营": "dongying",
    "烟台": "yantai",
    "潍坊": "weifang",
    "济宁": "jining",
    "泰安": "taian",
    "威海": "weihai",
    "日照": "rizhao",
    "临沂": "linyi",
    "德州": "dezhou",
    "聊城": "liaocheng",
    "滨州": "binzhou",
    "菏泽": "heze",
    
    # 中南地区
    "广州": "guangzhou",
    "深圳": "shenzhen",
    "珠海": "zhuhai",
    "汕头": "shantou",
    "佛山": "foshan",
    "韶关": "shaoguan",
    "湛江": "zhanjiang",
    "肇庆": "zhaoqing",
    "江门": "jiangmen",
    "茂名": "maoming",
    "惠州": "huizhou",
    "梅州": "meizhou",
    "汕尾": "shanwei",
    "河源": "heyuan",
    "阳江": "yangjiang",
    "清远": "qingyuan",
    "东莞": "dongguan",
    "中山": "zhongshan",
    "潮州": "chaozhou",
    "揭阳": "jieyang",
    "云浮": "yunfu",
    "南宁": "nanning",
    "柳州": "liuzhou",
    "桂林": "guilin",
    "梧州": "wuzhou",
    "北海": "beihai",
    "防城港": "fangchenggang",
    "钦州": "qinzhou",
    "贵港": "guigang",
    "玉林": "yulin",
    "百色": "baise",
    "贺州": "hezhou",
    "河池": "hechi",
    "来宾": "laibin",
    "崇左": "chongzuo",
    "海口": "haikou",
    "三亚": "sanya",
    "三沙": "sansha",
    "儋州": "danzhou",
    "五指山": "wuzhishan",
    "琼海": "qionghai",
    "文昌": "wenchang",
    "万宁": "wanning",
    "东方": "dongfang",
    "定安": "dingan",
    "屯昌": "tunchang",
    "澄迈": "chengmai",
    "临高": "lingao",
    "白沙黎族自治县": "baisha",
    "昌江黎族自治县": "changjiang",
    "乐东黎族自治县": "ledong",
    "陵水黎族自治县": "lingshui",
    "保亭黎族苗族自治县": "baoting",
    "琼中黎族苗族自治县": "qiongzhong",
    "武汉": "wuhan",
    "黄石": "huangshi",
    "十堰": "shiyan",
    "宜昌": "yichang",
    "襄阳": "xiangyang",
    "鄂州": "ezhou",
    "荆门": "jingmen",
    "孝感": "xiaogan",
    "荆州": "jingzhou",
    "黄冈": "huanggang",
    "咸宁": "xianning",
    "随州": "suizhou",
    "恩施土家族苗族自治州": "enshi",
    "仙桃": "xiantao",
    "潜江": "qianjiang",
    "天门": "tianmen",
    "神农架林区": "shennongjia",
    "长沙": "changsha",
    "株洲": "zhuzhou",
    "湘潭": "xiangtan",
    "衡阳": "hengyang",
    "邵阳": "shaoyang",
    "岳阳": "yueyang",
    "常德": "changde",
    "张家界": "zhangjiajie",
    "益阳": "yiyang",
    "郴州": "chenzhou",
    "永州": "yongzhou",
    "怀化": "huaihua",
    "娄底": "loudi",
    "湘西土家族苗族自治州": "xiangxi",
    
    # 西南地区
    "成都": "chengdu",
    "自贡": "zigong",
    "攀枝花": "panzhihua",
    "泸州": "luzhou",
    "德阳": "deyang",
    "绵阳": "mianyang",
    "广元": "guangyuan",
    "遂宁": "suining",
    "内江": "neijiang",
    "乐山": "leshan",
    "南充": "nanchong",
    "眉山": "meishan",
    "宜宾": "yibin",
    "广安": "guangan",
    "达州": "dazhou",
    "雅安": "yaan",
    "巴中": "bazhong",
    "资阳": "ziyang",
    "阿坝藏族羌族自治州": "aba",
    "甘孜藏族自治州": "ganzi",
    "凉山彝族自治州": "liangshan",
    "贵阳": "guiyang",
    "六盘水": "liupanshui",
    "遵义": "zunyi",
    "安顺": "anshun",
    "毕节": "bijie",
    "铜仁": "tongren",
    "黔西南布依族苗族自治州": "qianxinan",
    "黔东南苗族侗族自治州": "qiandongnan",
    "黔南布依族苗族自治州": "qiannan",
    "昆明": "kunming",
    "曲靖": "qujing",
    "玉溪": "yuxi",
    "保山": "baoshan",
    "昭通": "zhaotong",
    "丽江": "lijiang",
    "普洱": "puer",
    "临沧": "lincang",
    "楚雄彝族自治州": "chuxiong",
    "红河哈尼族彝族自治州": "honghe",
    "文山壮族苗族自治州": "wenshan",
    "西双版纳傣族自治州": "xishuangbanna",
    "大理白族自治州": "dali",
    "德宏傣族景颇族自治州": "dehong",
    "怒江傈僳族自治州": "nujiang",
    "迪庆藏族自治州": "diqing",
    "拉萨": "lhasa",
    "日喀则": "shigatse",
    "昌都": "changdu",
    "林芝": "linzhi",
    "山南": "shannan",
    "那曲": "naqu",
    "阿里": "ngari",
    "昌都市": "qamdo",
    "林芝市": "nyingchi",
    "山南市": "lhozhag",
    "那曲市": "naqu",
    "阿里地区": "ali",
    "西安": "xian",
    "铜川": "tongchuan",
    "宝鸡": "baoji",
    "咸阳": "xianyang",
    "渭南": "weinan",
    "延安": "yanan",
    "汉中": "hanzhong",
    "榆林": "yulin",
    "安康": "ankang",
    "商洛": "shangluo",
    "兰州": "lanzhou",
    "嘉峪关": "jiayuguan",
    "金昌": "jinchang",
    "白银": "baiyin",
    "天水": "tianshui",
    "武威": "wuwei",
    "张掖": "zhangye",
    "平凉": "pingliang",
    "酒泉": "jiuquan",
    "庆阳": "qingyang",
    "定西": "dingxi",
    "陇南": "longnan",
    "临夏回族自治州": "linxia",
    "甘南藏族自治州": "gannan",
    "西宁": "xining",
    "海东": "haidong",
    "海北藏族自治州": "haibei",
    "黄南藏族自治州": "huangnan",
    "海南藏族自治州": "hainan",
    "果洛藏族自治州": "goluo",
    "玉树藏族自治州": "yushu",
    "海西蒙古族藏族自治州": "haixi",
    "银川": "yinchuan",
    "石嘴山": "shizuishan",
    "吴忠": "wuzhong",
    "固原": "guyuan",
    "中卫": "zhongwei",
    "乌鲁木齐": "wulumuqi",
    "克拉玛依": "kelamayi",
    "吐鲁番": "turpan",
    "哈密": "hami",
    "昌吉回族自治州": "changji",
    "博尔塔拉蒙古自治州": "boertala",
    "巴音郭楞蒙古自治州": "bayinguoleng",
    "阿克苏地区": "akesu",
    "克孜勒苏柯尔克孜自治州": "kizilsu",
    "喀什地区": "kashi",
    "和田地区": "hetian",
    "伊犁哈萨克自治州": "yili",
    "塔城地区": "tacheng",
    "阿勒泰地区": "aletai",
    "石河子": "shihezi",
    "阿拉尔": "alal",
    "图木舒克": "tumushuke",
    "五家渠": "wujiaqu",
    "北屯": "beitun",
    "铁门关": "tieguanmen",
    "双河": "shuanghe",
    "可克达拉": "kekedala",
    "昆玉": "kunyu",
    "胡杨河": "huyanghe",
    "新星": "xinxing"
}

def get_air_quality_data(city_name, city_code):
    """
    从AQICN获取指定城市的真实空气质量数据
    :param city_name: 城市中文名称
    :param city_code: AQICN城市代码
    :return: 空气质量数据字典
    """
    try:
        # 构造请求URL
        url = f"{BASE_URL}/feed/{city_code}/?token={API_KEY}"
        
        # 发送请求
        response = requests.get(url, timeout=15)
        
        # 解析响应
        if response.status_code == 200:
            data = response.json()
            if data.get("status") == "ok":
                aqi_data = data["data"]
                
                # 提取需要的数据字段
                air_data = {
                    "城市": city_name,
                    "AQI": aqi_data["aqi"],
                    "PM2.5": aqi_data["iaqi"]["pm25"]["v"] if "pm25" in aqi_data["iaqi"] else 0,
                    "PM10": aqi_data["iaqi"]["pm10"]["v"] if "pm10" in aqi_data["iaqi"] else 0,
                    "O3": aqi_data["iaqi"]["o3"]["v"] if "o3" in aqi_data["iaqi"] else 0,
                    "NO2": aqi_data["iaqi"]["no2"]["v"] if "no2" in aqi_data["iaqi"] else 0,
                    "SO2": aqi_data["iaqi"]["so2"]["v"] if "so2" in aqi_data["iaqi"] else 0,
                    "CO": aqi_data["iaqi"]["co"]["v"] if "co" in aqi_data["iaqi"] else 0,
                    "空气质量等级": get_aqi_level(aqi_data["aqi"]),
                    "空气质量描述": get_aqi_description(aqi_data["aqi"]),
                    "爬取时间": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                }
                return air_data
            else:
                print(f"获取{city_name}数据失败：{data.get('data')}")
        else:
            print(f"请求失败，状态码：{response.status_code}")
    except Exception as e:
        print(f"获取{city_name}数据异常：{str(e)}")
    return None

def get_aqi_level(aqi):
    """
    根据AQI值返回空气质量等级
    :param aqi: AQI值
    :return: 空气质量等级
    """
    if aqi <= 50:
        return "优"
    elif aqi <= 100:
        return "良"
    elif aqi <= 150:
        return "轻度污染"
    elif aqi <= 200:
        return "中度污染"
    elif aqi <= 300:
        return "重度污染"
    else:
        return "严重污染"

def get_aqi_description(aqi):
    """
    根据AQI值返回空气质量描述
    :param aqi: AQI值
    :return: 空气质量描述
    """
    if aqi <= 50:
        return "空气质量优"
    elif aqi <= 100:
        return "空气质量良好"
    elif aqi <= 150:
        return "轻度污染"
    elif aqi <= 200:
        return "中度污染"
    elif aqi <= 300:
        return "重度污染"
    else:
        return "严重污染"

def crawl_all_cities():
    """
    爬取所有城市的空气质量数据
    """
    print("开始爬取真实空气质量数据...")
    print(f"爬取时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    all_data = []
    
    for city_name, city_code in city_mapping.items():
        print(f"正在爬取：{city_name} ({city_code})")
        data = get_air_quality_data(city_name, city_code)
        
        if data:
            all_data.append(data)
        
        # 控制请求频率，避免被封IP
        import time
        time.sleep(2)
    
    return all_data

def save_data_to_csv(data, filename="air_quality_data.csv"):
    """
    将数据保存到CSV文件
    :param data: 空气质量数据列表
    :param filename: 保存的文件名
    """
    if not data:
        print("没有数据可保存")
        return
    
    df = pd.DataFrame(data)
    file_path = os.path.join(DATA_DIR, filename)
    
    # 检查文件是否存在，不存在则创建，存在则追加
    if os.path.exists(file_path):
        # 追加模式
        df.to_csv(file_path, mode='a', header=False, index=False, encoding='utf-8-sig')
        print(f"数据已追加到：{file_path}")
    else:
        # 写入模式
        df.to_csv(file_path, index=False, encoding='utf-8-sig')
        print(f"数据已保存到：{file_path}")

def save_latest_data(data, filename="latest_air_quality.csv"):
    """
    保存最新数据（覆盖原有文件）
    :param data: 空气质量数据列表
    :param filename: 保存的文件名
    """
    if not data:
        print("没有数据可保存")
        return
    
    df = pd.DataFrame(data)
    file_path = os.path.join(DATA_DIR, filename)
    df.to_csv(file_path, index=False, encoding='utf-8-sig')
    print(f"最新数据已保存到：{file_path}")

def main():
    """
    主函数
    """
    # 爬取所有城市数据
    air_quality_data = crawl_all_cities()
    
    if air_quality_data:
        print(f"\n共爬取到{len(air_quality_data)}个城市的真实数据")
        
        # 保存最新数据
        save_latest_data(air_quality_data)
        
        # 保存到历史记录
        save_data_to_csv(air_quality_data)
        
        # 打印前5条数据
        print("\n前5条数据示例：")
        for i, data in enumerate(air_quality_data[:5]):
            print(f"{i+1}. {data['城市']} - AQI: {data['AQI']}, 等级: {data['空气质量等级']}")
    else:
        print("未爬取到任何数据")

if __name__ == "__main__":
    main()
