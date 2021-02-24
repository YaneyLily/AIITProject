from flask_restful import reqparse, Resource
from flask import session, request, json, redirect, url_for
import datetime
from web import DB
import re


class FuncCompanyAPI(Resource):
    """厂商管理类"""

    def __init__(self):
        self.parser = reqparse.RequestParser()
        self.parser.add_argument("company_name", type=str, location='json')
        self.parser.add_argument("company_contact", type=str, location='json')
        self.parser.add_argument("page", type=int)
        self.parser.add_argument("limit", type=int)
        self.parser.add_argument("searchParams", type=str)

    def put(self):
        if not session.get('status'):
            return redirect(url_for('html_system_login'), 302)
        args = self.parser.parse_args()
        company_name = args.company_name
        company_contact = args.company_contact
        company_query = DB.db.company.find_one({'ename': company_name})
        if company_query:
            return {'status_code': 201, 'msg': f'已存在[{company_name}]厂商名'}
        new_company = {
            'ename': company_name,
            'econtact': company_contact,
        }
        DB.db.company.insert_one(new_company)
        return {'status_code': 200, 'msg': '添加厂商成功'}

    def get(self):
        if not session.get('status'):
            return redirect(url_for('system_login'), 302)
        args = self.parser.parse_args()
        company_name = args.company_name
        key_page = args.page
        key_limit = args.limit
        key_searchParams = args.searchParams
        count = DB.db.company.find().count()
        jsondata = {'code': 0, 'msg': '', 'count': count}
        if count == 0:  # 若没有数据返回空列表
            jsondata.update({'data': []})
            return jsondata
        if not key_searchParams:  # 若没有查询参数
            if not key_page or not key_limit:  # 判断是否有分页查询参数
                paginate = DB.db.company.find().limit(20).skip(0)
            else:
                paginate = DB.db.company.find().limit(key_limit).skip((key_page - 1) * key_limit)
        else:
            try:
                search_dict = json.loads(key_searchParams)  # 解析查询参数
            except:
                paginate = DB.db.company.find().limit(20).skip(0)
            else:
                if 'company_name' not in search_dict:  # 查询参数有误
                    paginate = DB.db.company.find().limit(20).skip(0)
                else:
                    paginate1 = DB.db.company.find({'ename': re.compile(company_name)})
                    paginate = paginate1.limit(key_limit).skip((key_page - 1) * key_limit)
                    jsondata = {'code': 0, 'msg': '', 'count': paginate1.count()}
        data = []
        if paginate:
            for i in paginate:
                data1 = {}
                # data1['id'] = index
                data1['company_name'] = i['ename']
                data1['company_contact'] = i['econtact']
                # data1['company_time'] = i.cus_time
                # data1['cus_number'] = len(i.src_assets)
                # data1['cus_number_port'] = len(i.src_ports)
                data.append(data1)
            jsondata.update({'data': data})
            return jsondata
        else:
            jsondata = {'code': 0, 'msg': '', 'count': 0}
            jsondata.update({'data': []})
            return jsondata

    def delete(self):
        if not session.get('status'):
            return redirect(url_for('html_system_login'), 302)
        args = self.parser.parse_args()
        searchdict = {'ename': args.company_name}
        company_query = DB.db.company.find_one(searchdict)
        if not company_query:  # 删除的厂商不存在
            return {'status_code': 500, 'msg': '删除厂商失败，无此厂商'}
        DB.db.company.delete_one(searchdict)
        return {'status_code': 200, 'msg': '删除厂商成功'}


class FuncTaskAPI(Resource):
    """src 资产任务管理"""

    def __init__(self):
        self.parser = reqparse.RequestParser()
        self.parser.add_argument("task_company", type=str, location='json')
        self.parser.add_argument("task_type", type=int, location='json')
        self.parser.add_argument("task_cycle", type=int, location='json')
        self.parser.add_argument("task_message", type=str, location='json')
        self.parser.add_argument("page", type=int)
        self.parser.add_argument("limit", type=int)
        self.parser.add_argument("searchParams", type=str)

    def put(self):
        """添加任务资产"""
        # if not session.get('status'):
        #     return redirect(url_for('html_system_login'), 302)
        args = self.parser.parse_args()
        task_company = args.task_company
        task_type = args.task_type
        task_cycle = args.task_cycle
        task_message = args.task_message
        company_query = DB.db.company.find_one({'ename': task_company})
        if not company_query:
            return {'status_code': 201, 'msg': f'不存在[{task_company}]厂商名，请检查'}
        eid = company_query['_id']
        # uname = session['username']
        new_task = {
            'tname': '',
            'ttype': task_type,
            'tcycle': task_cycle,
            'eid': eid,
            'tstatus': 2,   # 1完成/2未完成
            # 'uname': uname,
        }
        if task_type == 1 or task_type == 2:    # WEB任务/主机任务
            message_list = list(set(task_message.split()))  # 过滤重复内容
            for m in message_list:
                message = m.strip()
                if message:
                    task_sql = DB.db.task.find_one({'tname': message})   # 过滤已有重复任务
                    if task_sql:
                        continue
                    new_task['tname'] = message
                    DB.db.task.insert_one(new_task)

        return {'status_code': 200, 'msg': '添加任务成功'}
