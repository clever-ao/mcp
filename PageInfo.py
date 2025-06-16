from datetime import datetime
import calendar
from DetectCharge import DetectCharge
import json

class PageInfo:

    def __init__(self, room_str, today):
        self.today = today
        self.room_str = room_str

    def getCurCharge(self):
        return DetectCharge(self.room_str).run(1)

    def getMonthDays(self):
        cal = calendar.TextCalendar(calendar.SUNDAY)
        list_monthday = cal.monthdayscalendar(self.today.year, self.today.month)
        return list_monthday

    def getChargesMap(self):
        responseRes = DetectCharge(self.room_str).run(2)
        list_charges = json.loads(responseRes)['d']['ResultList']
        if len(list_charges) != 0:
            list_charges = list_charges[0]['datas']
        else:
            return {}, 0
        map_charges = {}
        for charge in list_charges:
            month_days = int(datetime.utcfromtimestamp(charge['recordTime'] / 1000).strftime("%d"))
            map_charges[month_days] = charge['dataValue']
        max_key = max(map_charges, key=lambda k: map_charges[k])
        return map_charges, max_key

    def getMonthDaysContent(self):
        list_monthdays = self.getMonthDays()
        map_charges, max_key = self.getChargesMap()
        str_content = ""
        for i in list_monthdays:
            str_content += "<div>"
            for j in i:
                if j in map_charges.keys():
                    str_content += f'''
                                    <span {"class='event'" if j == max_key else ''}>{'%02d' % j}
                                    <p class="remain">{'%.2f' % (float(map_charges[j]) * 0.6259)}</p>
                                    </span>'''
                elif j == 0:
                    str_content += f'''<span class="last-month">++</span>'''
                else:
                    str_content += f'''
                                    <span>{'%02d' % j}
                                    <p class="remain null">{'暂无'}</p>
                                    </span>'''
            str_content += "</div>"
        return str_content

    def getCalendarContent(self):
        today = datetime.today()
        content = f'''
            <div id="calendar-container">
                <div class="calendar">
                    <div class="front">
                        <div class="current-date">
                            <h1>{'%02d' % today.day}日</h1>
                            <h1>{today.year} 年 {'%02d' % today.month} 月</h1>
                        </div>
                        <div class="current-month">
                            <ul class="week-days">
                                <li>日</li>
                                <li>一</li>
                                <li>二</li>
                                <li>三</li>
                                <li>四</li>
                                <li>五</li>
                                <li>六</li>
                            </ul>
                            <div class="weeks">
                                {self.getMonthDaysContent()}
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        '''
        return content

    def getInfoPage(self):
        html_content = f'''
        <html>
            <head></head>
            <body>
                <div>
                    <includetail>
                        <div style="font:Verdana normal 14px;color:#000;">
                            <div style="position:relative;">
                                <div class="eml-w eml-w-sys-layout">
                                    <div class="eml-w-sys-logo" style="display: flex; align-items: center;">
                                        <img src="https://www.jnu.edu.cn/_upload/tpl/00/f5/245/template245/images/list/logo.png"
                                            style="width: 108px; height: 126px;" onerror="">
                                        <div>
                                            <p style="font-size: 40px;">暨南大学番禺校区</p>
                                            <p style="text-align: right;">
                                                <span style="color: red;">{self.room_str}</span> 宿舍电费情况
                                            </p>
                                        </div>
                                    </div>
                                    <div style="font-size: 0px;">
                                        <div class="eml-w-sys-line">
                                            <div class="eml-w-sys-line-left"></div>
                                            <div class="eml-w-sys-line-right"></div>
                                        </div>
                                    </div>
                                    <div class="eml-w-sys-content">
                                        <div class="dragArea gen-group-list">
                                            <div class="gen-item">
                                                <div class="eml-w-item-block" style="padding: 0px;">
                                                    <div class="eml-w-title-level1">
                                                    {self.today.strftime("%Y年%m月%d日")}，{self.room_str} 宿舍当前电费为
                                                        <span style="font-weight: bolder; color: #2984ef;"> {self.getCurCharge()} 元
                                                        </span>
                                                    </div>
                                                </div>     
                                                <div class="eml-w-title-level2">
                                                    本月用电情况
                                                </div>
                                                {self.getCalendarContent()}
                                            </div>
                                            <div class="eml-w-sys-footer">WNDS 实验室</div>
                                        </div>
                                    </div>
                                </div>
                            </div>
                        </div>
            
                    </includetail>
                </div>
            </body>
        </html>'''
        with open('static/info.css', 'r', encoding='utf-8') as css:
            css_content = css.read()
        html_content += f"<style>{css_content}</style>"
        return html_content


# print(PageInfo('T110306').getInfoPage())
