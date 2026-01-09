// API基础URL
const API_BASE_URL = "http://localhost:5000/api";

// 城市空气质量与健康数据（初始为空，从API获取）
let cityData = [];
let correlationData = [];

// 县级/镇级数据缓存
let countyDataCache = {};

// 地图实例
let airQualityMap = null;

// 地图标记缓存
let markers = [];

// DOM加载完成后执行
document.addEventListener('DOMContentLoaded', function() {
    // 加载数据
    loadAirQualityData();
});

// 从API加载空气质量数据
async function loadAirQualityData() {
    try {
        // 显示加载状态
        console.log('正在从API加载空气质量数据...');
        
        // 从API获取数据
        const response = await fetch(`${API_BASE_URL}/air-quality/latest`);
        const result = await response.json();
        
        if (result.success) {
            // 处理数据格式，转换为前端所需格式
            cityData = result.data.map(item => {
                // 确保城市名称正确
                const cityName = item["城市"] || item.city || "未知城市";
                
                return {
                    city: cityName,
                    AQI: item.AQI,
                    PM25: item["PM2.5"] || item.PM25 || 0,
                    PM10: item.PM10,
                    O3: item.O3,
                    asthma: item["哮喘发病率"] || Math.random() * 2 + 2, // 模拟数据
                    cardio: item["心血管疾病发病率"] || Math.random() * 5 + 8, // 模拟数据
                    lat: getCityCoordinates(cityName).lat,
                    lng: getCityCoordinates(cityName).lng
                };
            });
            
            console.log('数据加载成功，共', cityData.length, '个城市');
            
            // 生成相关性数据（模拟）
            generateCorrelationData();
            
            // 初始化各个功能模块
            updateOverview();
            drawHeatmap();
            drawAQIHealthCharts();
            drawPM25HealthCharts();
            drawCityAQIChart();
            initAirQualityMap();
            fillDataTable();
        } else {
            console.error('数据加载失败:', result.message);
            // 如果API获取失败，使用默认模拟数据
            useDefaultData();
        }
    } catch (error) {
        console.error('API请求异常:', error);
        // 使用默认模拟数据
        useDefaultData();
    }
}

// 生成相关性数据（模拟）
function generateCorrelationData() {
    correlationData = [
        { name: "AQI", asthma: 0.985909, cardio: 0.974865 },
        { name: "PM2.5", asthma: 0.989581, cardio: 0.979894 },
        { name: "PM10", asthma: 0.990519, cardio: 0.983041 },
        { name: "O3", asthma: 0.987264, cardio: 0.989416 }
    ];
}

// 获取城市坐标
function getCityCoordinates(city) {
    // 城市坐标映射（包含更多中国城市）
    const cityCoords = {
        // 华北地区
        "北京": { lat: 39.9042, lng: 116.4074 },
        "天津": { lat: 39.3434, lng: 117.3616 },
        "石家庄": { lat: 38.0428, lng: 114.5149 },
        "太原": { lat: 37.8706, lng: 112.5489 },
        "呼和浩特": { lat: 40.8170, lng: 111.7619 },
        "唐山": { lat: 39.6345, lng: 118.1949 },
        "秦皇岛": { lat: 39.9434, lng: 119.5890 },
        "邯郸": { lat: 36.6172, lng: 114.4783 },
        "邢台": { lat: 37.0708, lng: 114.5085 },
        "保定": { lat: 38.8681, lng: 115.4833 },
        "张家口": { lat: 40.8109, lng: 114.8750 },
        "承德": { lat: 40.9700, lng: 117.9743 },
        "沧州": { lat: 38.3071, lng: 116.8207 },
        "廊坊": { lat: 39.5393, lng: 116.7087 },
        "衡水": { lat: 37.7295, lng: 115.7179 },
        "大同": { lat: 40.0902, lng: 113.3165 },
        "阳泉": { lat: 37.8590, lng: 113.5785 },
        "长治": { lat: 36.2000, lng: 113.1000 },
        "晋城": { lat: 35.5033, lng: 112.8069 },
        "朔州": { lat: 39.3333, lng: 112.4833 },
        "晋中": { lat: 37.7625, lng: 112.7336 },
        "运城": { lat: 35.0388, lng: 111.0195 },
        "忻州": { lat: 38.4188, lng: 112.7363 },
        "临汾": { lat: 36.0810, lng: 111.5140 },
        "吕梁": { lat: 37.5383, lng: 111.1094 },
        "包头": { lat: 40.6688, lng: 109.8375 },
        "乌海": { lat: 39.6742, lng: 106.8281 },
        "赤峰": { lat: 42.2700, lng: 118.8300 },
        "通辽": { lat: 43.6186, lng: 122.2739 },
        "鄂尔多斯": { lat: 39.8170, lng: 109.9000 },
        
        // 东北地区
        "沈阳": { lat: 41.8057, lng: 123.4315 },
        "大连": { lat: 38.9140, lng: 121.6147 },
        "鞍山": { lat: 41.1120, lng: 122.9925 },
        "抚顺": { lat: 41.8556, lng: 123.9541 },
        "本溪": { lat: 41.3278, lng: 123.7792 },
        "丹东": { lat: 40.1333, lng: 124.3750 },
        "锦州": { lat: 41.1167, lng: 121.1250 },
        "营口": { lat: 40.6681, lng: 122.1500 },
        "阜新": { lat: 42.0089, lng: 121.6573 },
        "辽阳": { lat: 41.2700, lng: 123.1700 },
        "铁岭": { lat: 42.3200, lng: 123.8400 },
        "朝阳": { lat: 41.5700, lng: 120.4500 },
        "盘锦": { lat: 41.1214, lng: 122.0767 },
        "葫芦岛": { lat: 40.7500, lng: 120.8700 },
        "长春": { lat: 43.8161, lng: 125.3238 },
        "吉林": { lat: 43.8438, lng: 125.3199 },
        "四平": { lat: 43.1667, lng: 124.3750 },
        "辽源": { lat: 42.9025, lng: 125.1442 },
        "通化": { lat: 41.7256, lng: 125.9000 },
        "白山": { lat: 41.9275, lng: 126.4153 },
        "松原": { lat: 45.1389, lng: 124.8181 },
        "白城": { lat: 45.6200, lng: 122.8200 },
        "哈尔滨": { lat: 45.8038, lng: 126.5349 },
        "齐齐哈尔": { lat: 47.3394, lng: 123.9641 },
        "鸡西": { lat: 45.3000, lng: 130.9800 },
        "鹤岗": { lat: 47.3300, lng: 130.3100 },
        "双鸭山": { lat: 46.6600, lng: 131.1600 },
        "大庆": { lat: 46.5800, lng: 125.0400 },
        "伊春": { lat: 47.7200, lng: 128.9100 },
        "佳木斯": { lat: 46.8333, lng: 130.3500 },
        "牡丹江": { lat: 44.5800, lng: 129.5800 },
        "黑河": { lat: 50.2500, lng: 127.4300 },
        "绥化": { lat: 46.6400, lng: 126.9900 },
        
        // 华东地区
        "上海": { lat: 31.2304, lng: 121.4737 },
        "南京": { lat: 32.0603, lng: 118.7969 },
        "无锡": { lat: 31.5589, lng: 120.3028 },
        "徐州": { lat: 34.2636, lng: 117.1784 },
        "常州": { lat: 31.7891, lng: 119.9959 },
        "苏州": { lat: 31.2989, lng: 120.5853 },
        "南通": { lat: 32.0165, lng: 120.8650 },
        "连云港": { lat: 34.5945, lng: 119.1784 },
        "淮安": { lat: 33.5914, lng: 119.0199 },
        "盐城": { lat: 33.3770, lng: 120.1300 },
        "扬州": { lat: 32.3932, lng: 119.4992 },
        "镇江": { lat: 32.2000, lng: 119.4557 },
        "泰州": { lat: 32.4542, lng: 119.9482 },
        "宿迁": { lat: 33.9664, lng: 118.2830 },
        "杭州": { lat: 30.2741, lng: 120.1551 },
        "宁波": { lat: 29.8683, lng: 121.5440 },
        "温州": { lat: 28.0100, lng: 120.6500 },
        "嘉兴": { lat: 30.7623, lng: 120.7685 },
        "湖州": { lat: 30.8685, lng: 120.0863 },
        "绍兴": { lat: 30.0000, lng: 120.5833 },
        "金华": { lat: 29.0800, lng: 119.6300 },
        "衢州": { lat: 28.9200, lng: 118.8800 },
        "舟山": { lat: 30.0000, lng: 122.2000 },
        "台州": { lat: 28.6400, lng: 121.4300 },
        "丽水": { lat: 28.4600, lng: 119.9400 },
        "合肥": { lat: 31.8206, lng: 117.2272 },
        "芜湖": { lat: 31.3500, lng: 118.3800 },
        "蚌埠": { lat: 32.9333, lng: 117.3000 },
        "淮南": { lat: 32.6333, lng: 117.0333 },
        "马鞍山": { lat: 31.6700, lng: 118.4800 },
        "淮北": { lat: 33.9667, lng: 116.7833 },
        "铜陵": { lat: 30.9200, lng: 117.8200 },
        "安庆": { lat: 30.5333, lng: 117.0500 },
        "黄山": { lat: 29.7275, lng: 118.3275 },
        "滁州": { lat: 32.3000, lng: 118.3167 },
        "阜阳": { lat: 32.8667, lng: 115.8167 },
        "宿州": { lat: 33.6333, lng: 116.9833 },
        "六安": { lat: 31.7333, lng: 116.4500 },
        "亳州": { lat: 33.8300, lng: 115.7800 },
        "池州": { lat: 30.6667, lng: 117.4833 },
        "宣城": { lat: 30.9400, lng: 118.7600 },
        "福州": { lat: 26.0745, lng: 119.2965 },
        "厦门": { lat: 24.4798, lng: 118.0894 },
        "莆田": { lat: 25.4428, lng: 119.0280 },
        "三明": { lat: 26.2500, lng: 117.6500 },
        "泉州": { lat: 24.8600, lng: 118.6200 },
        "漳州": { lat: 24.5167, lng: 117.6500 },
        "南平": { lat: 26.6300, lng: 118.1900 },
        "龙岩": { lat: 25.0800, lng: 117.0500 },
        "宁德": { lat: 26.6500, lng: 119.5200 },
        "南昌": { lat: 28.6827, lng: 115.8607 },
        "景德镇": { lat: 29.3000, lng: 117.2000 },
        "萍乡": { lat: 27.6000, lng: 113.8000 },
        "九江": { lat: 29.7194, lng: 115.9833 },
        "新余": { lat: 27.8000, lng: 114.9000 },
        "鹰潭": { lat: 28.2333, lng: 116.9333 },
        "赣州": { lat: 25.8478, lng: 114.9400 },
        "吉安": { lat: 27.1167, lng: 114.9667 },
        "宜春": { lat: 27.8000, lng: 114.3000 },
        "抚州": { lat: 27.9167, lng: 116.3500 },
        "上饶": { lat: 28.4667, lng: 117.9167 },
        "济南": { lat: 36.6512, lng: 117.1201 },
        "青岛": { lat: 36.0671, lng: 120.3826 },
        "淄博": { lat: 36.8000, lng: 118.0500 },
        "枣庄": { lat: 34.8667, lng: 117.5167 },
        "东营": { lat: 37.4667, lng: 118.6167 },
        "烟台": { lat: 37.5333, lng: 121.4000 },
        "潍坊": { lat: 36.6000, lng: 119.1300 },
        "济宁": { lat: 35.4167, lng: 116.5333 },
        "泰安": { lat: 36.1200, lng: 117.1300 },
        "威海": { lat: 37.5000, lng: 122.1167 },
        "日照": { lat: 35.4167, lng: 119.4167 },
        "临沂": { lat: 35.0500, lng: 118.3300 },
        "德州": { lat: 37.4333, lng: 116.2500 },
        "聊城": { lat: 36.4500, lng: 115.9833 },
        "滨州": { lat: 37.3667, lng: 118.0500 },
        "菏泽": { lat: 35.2483, lng: 115.4899 },
        
        // 中南地区
        "广州": { lat: 23.1291, lng: 113.2644 },
        "深圳": { lat: 22.5431, lng: 114.0579 },
        "珠海": { lat: 22.2783, lng: 113.5685 },
        "汕头": { lat: 23.3525, lng: 116.6950 },
        "佛山": { lat: 23.0258, lng: 113.1139 },
        "韶关": { lat: 24.8167, lng: 113.6167 },
        "湛江": { lat: 21.2000, lng: 110.3667 },
        "肇庆": { lat: 23.0498, lng: 112.4544 },
        "江门": { lat: 22.5700, lng: 113.0833 },
        "茂名": { lat: 21.6667, lng: 110.9333 },
        "惠州": { lat: 23.0969, lng: 114.4120 },
        "梅州": { lat: 24.2911, lng: 116.1163 },
        "汕尾": { lat: 22.7706, lng: 115.3650 },
        "河源": { lat: 23.7200, lng: 114.6833 },
        "阳江": { lat: 21.8500, lng: 111.9667 },
        "清远": { lat: 23.6833, lng: 113.0000 },
        "东莞": { lat: 23.0469, lng: 113.7544 },
        "中山": { lat: 22.5269, lng: 113.3836 },
        "潮州": { lat: 23.6667, lng: 116.6333 },
        "揭阳": { lat: 22.5700, lng: 116.3500 },
        "云浮": { lat: 22.9167, lng: 112.0833 },
        "南宁": { lat: 22.8156, lng: 108.3661 },
        "柳州": { lat: 23.6274, lng: 109.3700 },
        "桂林": { lat: 25.2711, lng: 110.2940 },
        "梧州": { lat: 23.4833, lng: 111.3667 },
        "北海": { lat: 21.4833, lng: 109.1333 },
        "防城港": { lat: 21.6167, lng: 108.3667 },
        "钦州": { lat: 21.9427, lng: 108.6153 },
        "贵港": { lat: 23.0667, lng: 109.6000 },
        "玉林": { lat: 22.6333, lng: 110.1500 },
        "百色": { lat: 23.9000, lng: 106.6167 },
        "贺州": { lat: 24.4200, lng: 111.5200 },
        "河池": { lat: 24.7000, lng: 108.0000 },
        "来宾": { lat: 23.7500, lng: 109.2250 },
        "崇左": { lat: 22.4000, lng: 107.3900 },
        "海口": { lat: 20.0300, lng: 110.3367 },
        "三亚": { lat: 18.2451, lng: 109.5000 },
        "武汉": { lat: 30.5928, lng: 114.3055 },
        "黄石": { lat: 30.2000, lng: 115.0500 },
        "十堰": { lat: 32.6333, lng: 110.7833 },
        "宜昌": { lat: 30.7000, lng: 111.3000 },
        "襄阳": { lat: 32.0600, lng: 112.1400 },
        "鄂州": { lat: 30.3833, lng: 114.8333 },
        "荆门": { lat: 31.0200, lng: 112.2200 },
        "孝感": { lat: 31.9167, lng: 113.9167 },
        "荆州": { lat: 30.3500, lng: 112.2000 },
        "黄冈": { lat: 30.4333, lng: 114.8500 },
        "咸宁": { lat: 29.8667, lng: 114.2667 },
        "随州": { lat: 31.7333, lng: 113.3833 },
        "长沙": { lat: 28.2278, lng: 112.9388 },
        "株洲": { lat: 27.8306, lng: 113.1675 },
        "湘潭": { lat: 27.8289, lng: 112.9381 },
        "衡阳": { lat: 26.8900, lng: 112.5700 },
        "邵阳": { lat: 27.2167, lng: 111.4500 },
        "岳阳": { lat: 29.3500, lng: 113.1200 },
        "常德": { lat: 29.0300, lng: 111.6700 },
        "张家界": { lat: 29.1200, lng: 110.4700 },
        "益阳": { lat: 28.5800, lng: 112.3500 },
        "郴州": { lat: 25.7900, lng: 113.0200 },
        "永州": { lat: 26.4167, lng: 111.6167 },
        "怀化": { lat: 27.5700, lng: 109.9700 },
        "娄底": { lat: 27.7167, lng: 112.0167 },
        
        // 西南地区
        "成都": { lat: 30.5728, lng: 104.0668 },
        "自贡": { lat: 29.3500, lng: 104.7750 },
        "攀枝花": { lat: 26.5833, lng: 101.7167 },
        "泸州": { lat: 28.8800, lng: 105.4400 },
        "德阳": { lat: 31.1300, lng: 104.3700 },
        "绵阳": { lat: 31.4500, lng: 104.7500 },
        "广元": { lat: 32.4500, lng: 105.8250 },
        "遂宁": { lat: 30.5300, lng: 105.5833 },
        "内江": { lat: 29.5800, lng: 105.0500 },
        "乐山": { lat: 29.5675, lng: 103.7606 },
        "南充": { lat: 30.7900, lng: 106.0833 },
        "眉山": { lat: 30.0500, lng: 103.8333 },
        "宜宾": { lat: 28.7700, lng: 104.6300 },
        "广安": { lat: 30.4700, lng: 106.6167 },
        "达州": { lat: 31.2000, lng: 107.5000 },
        "雅安": { lat: 29.9833, lng: 103.0000 },
        "巴中": { lat: 31.8500, lng: 106.7500 },
        "资阳": { lat: 30.1300, lng: 104.6667 },
        "贵阳": { lat: 26.5958, lng: 106.7078 },
        "六盘水": { lat: 26.5833, lng: 104.8333 },
        "遵义": { lat: 27.7000, lng: 106.9000 },
        "昆明": { lat: 25.0443, lng: 102.7122 },
        "曲靖": { lat: 25.5000, lng: 103.7833 },
        "玉溪": { lat: 24.3500, lng: 102.5417 },
        "昭通": { lat: 27.3300, lng: 103.7300 },
        "丽江": { lat: 26.8679, lng: 100.2583 },
        "大理": { lat: 25.6800, lng: 100.1900 },
        "拉萨": { lat: 29.6500, lng: 91.1500 },
        
        // 西北地区
        "西安": { lat: 34.2658, lng: 108.9541 },
        "铜川": { lat: 35.0617, lng: 109.1071 },
        "宝鸡": { lat: 34.3667, lng: 107.1500 },
        "咸阳": { lat: 34.3417, lng: 108.7167 },
        "渭南": { lat: 34.4900, lng: 109.5000 },
        "延安": { lat: 36.5900, lng: 109.5000 },
        "汉中": { lat: 33.0700, lng: 107.0333 },
        "榆林": { lat: 38.2833, lng: 109.7333 },
        "安康": { lat: 32.6900, lng: 109.0167 },
        "商洛": { lat: 33.8500, lng: 109.9250 },
        "兰州": { lat: 36.0611, lng: 103.8343 },
        "嘉峪关": { lat: 39.8186, lng: 98.1619 },
        "金昌": { lat: 38.5211, lng: 102.1764 },
        "白银": { lat: 36.5442, lng: 104.1250 },
        "天水": { lat: 34.5731, lng: 105.7381 },
        "武威": { lat: 37.9333, lng: 102.6333 },
        "张掖": { lat: 38.9300, lng: 100.4600 },
        "平凉": { lat: 35.5333, lng: 106.6833 },
        "酒泉": { lat: 39.7333, lng: 98.5167 },
        "庆阳": { lat: 35.7333, lng: 107.6833 },
        "西宁": { lat: 36.6172, lng: 101.7782 },
        "银川": { lat: 38.4680, lng: 106.2425 },
        "乌鲁木齐": { lat: 43.8256, lng: 87.6168 },
        "克拉玛依": { lat: 45.5900, lng: 84.8700 },
        "吐鲁番": { lat: 42.9400, lng: 89.1900 }
    };
    
    // 如果城市不在映射中，返回默认坐标（北京）
    return cityCoords[city] || { lat: 39.9042, lng: 116.4074 };
}

// 使用默认模拟数据
function useDefaultData() {
    console.log('使用默认模拟数据');
    
    // 使用默认模拟数据
    cityData = [
        { city: "北京", AQI: 85, PM25: 58, PM10: 89, O3: 120, asthma: 3.2, cardio: 12.5, lat: 39.9042, lng: 116.4074 },
        { city: "上海", AQI: 72, PM25: 45, PM10: 70, O3: 110, asthma: 2.8, cardio: 10.8, lat: 31.2304, lng: 121.4737 },
        { city: "广州", AQI: 68, PM25: 42, PM10: 65, O3: 105, asthma: 2.5, cardio: 9.5, lat: 23.1291, lng: 113.2644 },
        { city: "深圳", AQI: 65, PM25: 38, PM10: 60, O3: 100, asthma: 2.3, cardio: 9.0, lat: 22.5431, lng: 114.0579 },
        { city: "成都", AQI: 92, PM25: 65, PM10: 98, O3: 125, asthma: 3.5, cardio: 13.2, lat: 30.5728, lng: 104.0668 },
        { city: "杭州", AQI: 78, PM25: 50, PM10: 75, O3: 115, asthma: 2.9, cardio: 11.2, lat: 30.2741, lng: 120.1551 },
        { city: "武汉", AQI: 80, PM25: 52, PM10: 78, O3: 118, asthma: 3.0, cardio: 11.5, lat: 30.5928, lng: 114.3055 },
        { city: "西安", AQI: 105, PM25: 75, PM10: 110, O3: 130, asthma: 3.8, cardio: 14.0, lat: 34.2658, lng: 108.9541 },
        { city: "重庆", AQI: 95, PM25: 68, PM10: 102, O3: 128, asthma: 3.6, cardio: 13.5, lat: 29.5630, lng: 106.5516 },
        { city: "南京", AQI: 75, PM25: 48, PM10: 72, O3: 112, asthma: 2.7, cardio: 10.5, lat: 32.0603, lng: 118.7969 }
    ];
    
    // 生成相关性数据
    generateCorrelationData();
    
    // 初始化各个功能模块
    updateOverview();
    drawHeatmap();
    drawAQIHealthCharts();
    drawPM25HealthCharts();
    drawCityAQIChart();
    initAirQualityMap();
    fillDataTable();
}

// 更新数据概览
function updateOverview() {
    const cityCount = cityData.length;
    const avgAQI = (cityData.reduce((sum, item) => sum + item.AQI, 0) / cityCount).toFixed(0);
    const avgPM25 = (cityData.reduce((sum, item) => sum + item.PM25, 0) / cityCount).toFixed(1);
    const avgAsthma = (cityData.reduce((sum, item) => sum + item.asthma, 0) / cityCount).toFixed(2);
    
    document.getElementById('city-count').textContent = cityCount;
    document.getElementById('avg-aqi').textContent = avgAQI;
    document.getElementById('avg-pm25').textContent = avgPM25;
    document.getElementById('avg-asthma').textContent = avgAsthma + '‰';
}

// 绘制相关性热力图
function drawHeatmap() {
    const heatmapChart = echarts.init(document.getElementById('heatmap'));
    
    const heatmapOption = {
        title: {
            text: '空气质量与健康指标相关性热力图',
            left: 'center'
        },
        tooltip: {
            position: 'top'
        },
        grid: {
            height: '60%',
            top: '15%'
        },
        xAxis: {
            type: 'category',
            data: ['哮喘发病率(‰)', '心血管疾病发病率(‰)'],
            splitArea: {
                show: true
            }
        },
        yAxis: {
            type: 'category',
            data: ['AQI', 'PM2.5', 'PM10', 'O3'],
            splitArea: {
                show: true
            }
        },
        visualMap: {
            min: 0.97,
            max: 0.99,
            calculable: true,
            orient: 'horizontal',
            left: 'center',
            bottom: '5%',
            inRange: {
                color: ['#e0f3f8', '#2196f3', '#0d47a1']
            }
        },
        series: [
            {
                name: '相关性系数',
                type: 'heatmap',
                data: [
                    [0, 0, 0.985909], [1, 0, 0.974865],
                    [0, 1, 0.989581], [1, 1, 0.979894],
                    [0, 2, 0.990519], [1, 2, 0.983041],
                    [0, 3, 0.987264], [1, 3, 0.989416]
                ],
                label: {
                    show: true,
                    formatter: function(params) {
                        return params.value[2].toFixed(3);
                    }
                },
                emphasis: {
                    itemStyle: {
                        shadowBlur: 10,
                        shadowColor: 'rgba(0, 0, 0, 0.5)'
                    }
                }
            }
        ]
    };
    
    heatmapChart.setOption(heatmapOption);
    
    // 响应式调整
    window.addEventListener('resize', function() {
        heatmapChart.resize();
    });
}

// 绘制AQI与健康指标关系图
function drawAQIHealthCharts() {
    // AQI与哮喘发病率关系
    const aqiAsthmaCtx = document.getElementById('aqi-asthma-chart').getContext('2d');
    new Chart(aqiAsthmaCtx, {
        type: 'scatter',
        data: {
            datasets: [{
                label: 'AQI与哮喘发病率',
                data: cityData.map(item => ({ x: item.AQI, y: item.asthma, city: item.city })),
                backgroundColor: 'rgba(54, 162, 235, 0.8)',
                borderColor: 'rgba(54, 162, 235, 1)',
                borderWidth: 1,
                pointRadius: 6,
                pointHoverRadius: 8
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                title: {
                    display: true,
                    text: 'AQI与哮喘发病率关系',
                    font: {
                        size: 14
                    }
                },
                tooltip: {
                    callbacks: {
                        label: function(context) {
                            return `${context.raw.city}: AQI=${context.raw.x}, 哮喘发病率=${context.raw.y}‰`;
                        }
                    }
                }
            },
            scales: {
                x: {
                    title: {
                        display: true,
                        text: 'AQI指数'
                    }
                },
                y: {
                    title: {
                        display: true,
                        text: '哮喘发病率(‰)'
                    }
                }
            }
        }
    });
    
    // AQI与心血管疾病发病率关系
    const aqiCardioCtx = document.getElementById('aqi-cardio-chart').getContext('2d');
    new Chart(aqiCardioCtx, {
        type: 'scatter',
        data: {
            datasets: [{
                label: 'AQI与心血管疾病发病率',
                data: cityData.map(item => ({ x: item.AQI, y: item.cardio, city: item.city })),
                backgroundColor: 'rgba(255, 99, 132, 0.8)',
                borderColor: 'rgba(255, 99, 132, 1)',
                borderWidth: 1,
                pointRadius: 6,
                pointHoverRadius: 8
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                title: {
                    display: true,
                    text: 'AQI与心血管疾病发病率关系',
                    font: {
                        size: 14
                    }
                },
                tooltip: {
                    callbacks: {
                        label: function(context) {
                            return `${context.raw.city}: AQI=${context.raw.x}, 心血管疾病发病率=${context.raw.y}‰`;
                        }
                    }
                }
            },
            scales: {
                x: {
                    title: {
                        display: true,
                        text: 'AQI指数'
                    }
                },
                y: {
                    title: {
                        display: true,
                        text: '心血管疾病发病率(‰)'
                    }
                }
            }
        }
    });
}

// 绘制PM2.5与健康指标关系图
function drawPM25HealthCharts() {
    // PM2.5与哮喘发病率关系
    const pm25AsthmaCtx = document.getElementById('pm25-asthma-chart').getContext('2d');
    new Chart(pm25AsthmaCtx, {
        type: 'scatter',
        data: {
            datasets: [{
                label: 'PM2.5与哮喘发病率',
                data: cityData.map(item => ({ x: item.PM25, y: item.asthma, city: item.city })),
                backgroundColor: 'rgba(75, 192, 192, 0.8)',
                borderColor: 'rgba(75, 192, 192, 1)',
                borderWidth: 1,
                pointRadius: 6,
                pointHoverRadius: 8
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                title: {
                    display: true,
                    text: 'PM2.5与哮喘发病率关系',
                    font: {
                        size: 14
                    }
                },
                tooltip: {
                    callbacks: {
                        label: function(context) {
                            return `${context.raw.city}: PM2.5=${context.raw.x}μg/m³, 哮喘发病率=${context.raw.y}‰`;
                        }
                    }
                }
            },
            scales: {
                x: {
                    title: {
                        display: true,
                        text: 'PM2.5浓度 (μg/m³)'
                    }
                },
                y: {
                    title: {
                        display: true,
                        text: '哮喘发病率(‰)'
                    }
                }
            }
        }
    });
    
    // PM2.5与心血管疾病发病率关系
    const pm25CardioCtx = document.getElementById('pm25-cardio-chart').getContext('2d');
    new Chart(pm25CardioCtx, {
        type: 'scatter',
        data: {
            datasets: [{
                label: 'PM2.5与心血管疾病发病率',
                data: cityData.map(item => ({ x: item.PM25, y: item.cardio, city: item.city })),
                backgroundColor: 'rgba(255, 159, 64, 0.8)',
                borderColor: 'rgba(255, 159, 64, 1)',
                borderWidth: 1,
                pointRadius: 6,
                pointHoverRadius: 8
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                title: {
                    display: true,
                    text: 'PM2.5与心血管疾病发病率关系',
                    font: {
                        size: 14
                    }
                },
                tooltip: {
                    callbacks: {
                        label: function(context) {
                            return `${context.raw.city}: PM2.5=${context.raw.x}μg/m³, 心血管疾病发病率=${context.raw.y}‰`;
                        }
                    }
                }
            },
            scales: {
                x: {
                    title: {
                        display: true,
                        text: 'PM2.5浓度 (μg/m³)'
                    }
                },
                y: {
                    title: {
                        display: true,
                        text: '心血管疾病发病率(‰)'
                    }
                }
            }
        }
    });
}

// 绘制城市AQI对比图
function drawCityAQIChart() {
    const cityAQICtx = document.getElementById('city-aqi-chart').getContext('2d');
    new Chart(cityAQICtx, {
        type: 'bar',
        data: {
            labels: cityData.map(item => item.city),
            datasets: [{
                label: 'AQI指数',
                data: cityData.map(item => item.AQI),
                backgroundColor: cityData.map(item => {
                    if (item.AQI <= 50) return 'rgba(75, 192, 192, 0.8)';
                    if (item.AQI <= 100) return 'rgba(255, 206, 86, 0.8)';
                    return 'rgba(255, 99, 132, 0.8)';
                }),
                borderColor: cityData.map(item => {
                    if (item.AQI <= 50) return 'rgba(75, 192, 192, 1)';
                    if (item.AQI <= 100) return 'rgba(255, 206, 86, 1)';
                    return 'rgba(255, 99, 132, 1)';
                }),
                borderWidth: 1
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                title: {
                    display: true,
                    text: '各城市AQI对比',
                    font: {
                        size: 14
                    }
                },
                legend: {
                    display: false
                }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    title: {
                        display: true,
                        text: 'AQI指数'
                    }
                },
                x: {
                    title: {
                        display: true,
                        text: '城市'
                    }
                }
            }
        }
    });
}

// 初始化空气质量地图
function initAirQualityMap() {
    // 创建地图实例
    airQualityMap = L.map('air-quality-map').setView([35.8617, 104.1954], 4);
    
    // 添加底图图层
    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
    }).addTo(airQualityMap);
    
    // 添加地图缩放事件监听
    airQualityMap.on('zoomend', handleMapZoom);
    
    // 初始加载城市级数据
    loadMapData('city');
    
    // 添加图例
    const legend = L.control({ position: 'bottomright' });
    legend.onAdd = function() {
        const div = L.DomUtil.create('div', 'info legend');
        const grades = [0, 51, 101];
        const colors = ['green', 'orange', 'red'];
        const labels = ['优', '良', '污染'];
        
        div.innerHTML = '<h5>AQI级别</h5>';
        for (let i = 0; i < grades.length; i++) {
            div.innerHTML += `
                <i style="background:${colors[i]}"></i> 
                ${grades[i]}${grades[i + 1] ? '&ndash;' + grades[i + 1] + ' ' : '+'} ${labels[i]}<br>`;
        }
        return div;
    };
    legend.addTo(airQualityMap);
}

// 处理地图缩放事件
function handleMapZoom() {
    const zoomLevel = airQualityMap.getZoom();
    console.log('地图缩放级别:', zoomLevel);
    
    // 根据缩放级别加载不同层级的数据
    if (zoomLevel >= 10) {
        // 缩放级别较高，加载县级/镇级数据
        console.log('加载县级/镇级数据');
        loadMapData('county');
    } else {
        // 缩放级别较低，加载城市级数据
        console.log('加载城市级数据');
        loadMapData('city');
    }
}

// 加载地图数据
function loadMapData(level) {
    // 清除现有标记
    clearMarkers();
    
    if (level === 'city') {
        // 加载城市级数据
        addCityMarkers();
    } else if (level === 'county') {
        // 加载县级/镇级数据
        addCountyMarkers();
    }
}

// 清除地图标记
function clearMarkers() {
    markers.forEach(marker => {
        airQualityMap.removeLayer(marker);
    });
    markers = [];
}

// 添加城市标记
function addCityMarkers() {
    cityData.forEach(city => {
        // 根据AQI设置标记颜色
        let markerColor;
        if (city.AQI <= 50) markerColor = 'green';
        else if (city.AQI <= 100) markerColor = 'orange';
        else markerColor = 'red';
        
        // 创建标记
        const marker = L.marker([city.lat, city.lng], {
            icon: L.divIcon({
                className: 'custom-marker',
                html: `<div style="background-color: ${markerColor}; color: white; width: 20px; height: 20px; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-size: 12px; font-weight: bold;">${city.AQI}</div>`,
                iconSize: [20, 20],
                iconAnchor: [10, 10]
            })
        }).addTo(airQualityMap);
        
        // 添加弹出信息
        marker.bindPopup(`
            <h4>${city.city}</h4>
            <p><strong>AQI:</strong> ${city.AQI}</p>
            <p><strong>PM2.5:</strong> ${city.PM25} μg/m³</p>
            <p><strong>PM10:</strong> ${city.PM10} μg/m³</p>
            <p><strong>O3:</strong> ${city.O3} μg/m³</p>
            <p><strong>哮喘发病率:</strong> ${city.asthma}‰</p>
            <p><strong>心血管疾病发病率:</strong> ${city.cardio}‰</p>
            <button class="btn btn-sm btn-primary" onclick="showCountyData('${city.city}')">查看区县数据</button>
        `);
        
        // 添加到标记缓存
        markers.push(marker);
    });
}

// 添加县级/镇级标记
function addCountyMarkers() {
    // 获取当前地图中心点城市
    const center = airQualityMap.getCenter();
    const nearestCity = findNearestCity(center.lat, center.lng);
    
    if (nearestCity) {
        showCountyData(nearestCity.city);
    }
}

// 查找最近的城市
function findNearestCity(lat, lng) {
    let nearestCity = null;
    let minDistance = Infinity;
    
    cityData.forEach(city => {
        const distance = calculateDistance(lat, lng, city.lat, city.lng);
        if (distance < minDistance) {
            minDistance = distance;
            nearestCity = city;
        }
    });
    
    return nearestCity;
}

// 计算两点之间的距离（简单的欧几里得距离）
function calculateDistance(lat1, lng1, lat2, lng2) {
    const dLat = lat2 - lat1;
    const dLng = lng2 - lng1;
    return Math.sqrt(dLat * dLat + dLng * dLng);
}

// 显示县级/镇级数据
async function showCountyData(city) {
    try {
        console.log(`获取${city}的县级数据...`);
        
        // 检查缓存中是否已有数据
        if (countyDataCache[city]) {
            console.log(`使用缓存的${city}县级数据`);
            addCountyMarkersFromData(countyDataCache[city]);
            return;
        }
        
        // 从API获取县级数据
        const response = await fetch(`${API_BASE_URL}/air-quality/county/${encodeURIComponent(city)}`);
        const result = await response.json();
        
        if (result.success) {
            // 保存到缓存
            countyDataCache[city] = result.data;
            
            // 添加县级标记
            addCountyMarkersFromData(result.data);
        } else {
            console.error(`获取${city}县级数据失败:`, result.message);
            // 使用模拟数据
            const mockCountyData = generateMockCountyData(city);
            addCountyMarkersFromData(mockCountyData);
        }
    } catch (error) {
        console.error(`获取${city}县级数据异常:`, error);
        // 使用模拟数据
        const mockCountyData = generateMockCountyData(city);
        addCountyMarkersFromData(mockCountyData);
    }
}

// 添加县级标记
function addCountyMarkersFromData(countyData) {
    countyData.forEach(county => {
        // 根据AQI设置标记颜色
        let markerColor;
        const aqi = county.aqi || 0;
        if (aqi <= 50) markerColor = 'green';
        else if (aqi <= 100) markerColor = 'orange';
        else markerColor = 'red';
        
        // 创建标记
        const marker = L.marker([county.lat, county.lng], {
            icon: L.divIcon({
                className: 'custom-marker',
                html: `<div style="background-color: ${markerColor}; color: white; width: 18px; height: 18px; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-size: 10px; font-weight: bold;">${aqi}</div>`,
                iconSize: [18, 18],
                iconAnchor: [9, 9]
            })
        }).addTo(airQualityMap);
        
        // 添加弹出信息
        marker.bindPopup(`
            <h4>${county.name}</h4>
            <p><strong>AQI:</strong> ${aqi}</p>
            <p><strong>PM2.5:</strong> ${county.pm25 || 0} μg/m³</p>
            <p><strong>数据来源:</strong> ${county.source || '模拟数据'}</p>
        `);
        
        // 添加到标记缓存
        markers.push(marker);
    });
}

// 生成模拟县级数据
function generateMockCountyData(city) {
    // 城市中心点坐标
    const cityInfo = cityData.find(item => item.city === city);
    if (!cityInfo) return [];
    
    // 生成3-5个模拟区县
    const countyCount = Math.floor(Math.random() * 3) + 3;
    const mockCounties = [];
    
    for (let i = 0; i < countyCount; i++) {
        // 生成围绕城市中心点的随机坐标
        const latOffset = (Math.random() - 0.5) * 0.2;
        const lngOffset = (Math.random() - 0.5) * 0.3;
        
        const aqi = Math.floor(Math.random() * 100) + 50;
        
        mockCounties.push({
            name: `${city}${i+1}区`,
            lat: cityInfo.lat + latOffset,
            lng: cityInfo.lng + lngOffset,
            aqi: aqi,
            pm25: Math.floor(aqi * 0.7),
            source: '模拟数据'
        });
    }
    
    return mockCounties;
}

// 填充数据表格，只显示主要省城
function fillDataTable() {
    const tableBody = document.getElementById('data-table-body');
    tableBody.innerHTML = '';
    
    // 主要省城列表
    const majorCities = ['北京', '上海', '广州', '深圳', '成都', '杭州', '武汉', '西安', '重庆', '南京'];
    
    // 筛选出主要省城数据
    const majorCityData = cityData.filter(item => majorCities.includes(item.city));
    
    majorCityData.forEach(city => {
        const row = document.createElement('tr');
        row.innerHTML = `
            <td>${city.city}</td>
            <td>${city.AQI}</td>
            <td>${city.PM25}</td>
            <td>${city.PM10}</td>
            <td>${city.O3}</td>
            <td>${city.asthma}</td>
            <td>${city.cardio}</td>
        `;
        tableBody.appendChild(row);
    });
}
