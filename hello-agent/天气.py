# import requests
#
# def get_weather(city:str) -> str:
#     """
#     通过调用 wttr.in API查询真实的天气信息
#     """
#     # API端点 我们请求JSON格式的数据
#     url = f'http://wttr.in/{city}?format=j1'
#
#     try:
#         # 发起网络请求
#         response = requests.get(url)
#         # 检查响应状态码是否为200
#         response.raise_for_status()
#         # 解析返回的JSON数据
#         data = response.json()
#
#         # 提取当前天气状况
#         current_condition = data['current_condition'][0]
#         weather_desc = current_condition['weatherDesc'][0]['value']
#         temp_c = current_condition['temp_c']
#
#         # 格式化自然语言返回
#         return f"{city}当前天气:{weather_desc},气温{temp_c}摄氏度"
#
#     except requests.exceptions.RequestException as e:
#         # 处理网络错误
#         return f"错误：查询天气时遇到网络问题 - {e}"
#     except (KeyError, IndexError) as e:
#         # 处理数据解析数据
#         return f"错误：解析天气数据失败，可能是城市名称无效 - {e}"


import requests
# 导入URL编码工具，解决中文城市名请求失败的问题
from urllib.parse import quote


def get_weather(city: str) -> str:
    """
    调用 wttr.in 公共API，查询指定城市的实时天气信息

    参数:
        city: 需要查询天气的城市名称（支持中文，如：长沙、北京）

    返回:
        str: 格式化的天气信息字符串，或错误提示信息
    """
    # 基础API配置（常量大写，便于维护）
    BASE_API_URL = "https://wttr.in/"
    API_PARAMS = "?format=j1"

    try:
        # 1. 对中文城市名进行URL编码，防止API解析失败
        encoded_city = quote(city)
        # 2. 拼接完整的请求地址
        request_url = f"{BASE_API_URL}{encoded_city}{API_PARAMS}"

        # 3. 发送网络请求（设置超时时间，避免程序卡死）
        response = requests.get(request_url, timeout=10)
        # 4. 校验HTTP响应状态码（非200直接抛出异常）
        response.raise_for_status()

        # 5. 解析JSON格式的响应数据
        weather_data = response.json()

        # 6. 数据校验：判断API是否返回了有效的天气数据
        if "current_condition" not in weather_data or len(weather_data["current_condition"]) == 0:
            return f"查询失败：未找到【{city}】的天气数据，请输入正确的城市名"

        # 7. 提取核心天气数据（严格匹配API字段名）
        current_weather = weather_data["current_condition"][0]
        weather_description = current_weather["weatherDesc"][0]["value"]
        temperature = current_weather["temp_C"]

        # 8. 格式化输出友好的结果
        return f"{city}当前天气：{weather_description}，气温 {temperature} ℃"

    # 处理所有网络相关异常（超时、连接失败、HTTP错误等）
    except requests.exceptions.RequestException as network_error:
        return f"网络错误：无法连接天气服务 - {str(network_error)}"

    # 处理数据解析异常（字段不存在、索引越界等）
    except (KeyError, IndexError) as parse_error:
        return f"数据错误：天气信息解析失败 - {str(parse_error)}"