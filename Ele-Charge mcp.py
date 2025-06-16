from datetime import datetime
from DailyEmail import DailyEmail
from DetectCharge import DetectCharge
import uvicorn
from fastapi import FastAPI, Depends, HTTPException, Header
from fastapi_mcp import FastApiMCP
import re

app = FastAPI()

# 注意：要设置添加明确的 operation_id 参数，这会让大模型更容易理解工具的作用
# 编写一个获取当前时间的接口
@app.get("/getCurrentTime", operation_id="get_current_time")
async def get_current_time():
    return {"current_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S")}


def validate_and_adjust_dorm_number(dorm_number):
    """
    验证并调整宿舍号码格式
    
    参数:
        dorm_number (str): 输入的宿舍号码字符串
        
    返回:
        tuple: (bool, str) 
               - 第一个元素表示是否有效
               - 第二个元素是调整后的正确格式或错误信息
    """
    # 定义正则表达式模式
    if not dorm_number or not isinstance(dorm_number, str):
        return (False, "宿舍号不能为空且必须是字符串")
    
    pattern = r'^T(0?[1-9]|1[0-9])(\d{3,4})$'
    
    # 尝试匹配
    match = re.fullmatch(pattern, dorm_number)
    
    if not match:
        return (False, "格式错误：宿舍号应以T开头，栋号T1-T20，房间号0101-1999")
    
    # 提取栋号和房间号
    building = match.group(1)
    room = match.group(2)
    
    # 标准化栋号格式 (去掉前导0)
    building = str(int(building))
    
    # 标准化房间号格式 (补齐前导0)
    room = room.zfill(4)
    
    # 验证房间号范围
    if len(room) != 4:
        return (False, "房间号应为4位数字")
    
    room_num = int(room)
    if room_num < 101 or room_num > 1999:
        return (False, "房间号范围应为0101-1999")
    
    # 组合成标准格式
    standardized = f"T{building}栋-{room}"
    
    return (True, standardized)

    
@app.get("/room/{room_number}", operation_id="get_electricityBalance_by_room_number")
async def get_electricityBalance(room_number: str):  # 验证请求头，需要授权访问
    # 统一处理中文"栋"字和各种分隔符
    room_number = room_number.replace("栋", "0").replace("_", "0").replace(" ", "0").replace("t", "T").replace("-","0")
    validation = validate_and_adjust_dorm_number(room_number)
    if validation[0] == False:  # 验证房间号
        return {"message": f"Invalid room number {validation[1]}"}
    charge = DetectCharge(room_number).run(1)
    if charge == "error":
        charge = "输入的房间号不合法（如：T11栋110，请以T11-110或T110110的格式输入）"
    data = {"room_number": validation[1], "Balance": charge}
    return data


@app.get("/room/{room_number}/{email_code}", operation_id="send_email_electricityBalance")
async def send_email_electricityBalance(room_number: str,email_code: str):
    room_number = room_number.replace("栋", "0").replace("_", "0").replace(" ", "0").replace("t", "T").replace("-","0")
    try:
        DailyEmail(email_code, room_number, datetime.today()).lowChargeWarning(
            1000
        )
        return {"room_number": room_number, "status": "邮件发送成功！！！"}
    except Exception as e:
        print()
        return {"room_number": room_number, "status": f"邮件发送失败，请保证查询房间号码和邮箱地址的正确性，错误信息为{e}"}


# 创建 MCP 服务器实例，绑定到 FastAPI app
mcp = FastApiMCP(app)
# 挂载 MCP 服务器，默认路径是 /mcp（可以修改）
mcp.mount()

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8090)
