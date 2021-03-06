#!/usr/bin/env python
# -*- coding:utf-8 -*-


from pyh import *
import time
import os


class HtmlReport:
    def __init__(self, db, log, view_id, run_mode, run_case_list):
        self.title = 'test_report_page'   # 网页标签名称
        self.filename = ''                   # 结果文件名
        self.time_took = '00:00:00'         # 测试耗时
        self.success_num = 0                  # 测试通过的用例数
        self.fail_num = 0                     # 测试失败的用例数
        self.error_num = 0                    # 运行出错的用例数
        self.case_total = 0                   # 运行测试用例总数
        self.db = db
        self.log = log
        self.view_id = view_id
        self.run_mode = run_mode
        self.run_case_list = run_case_list


    # 生成HTML报告
    def generate_html(self,head, file):
        page = PyH(self.title)
        page << h1(head, align='center')  # 标题居中
        page << p('测试总耗时：' + self.time_took)
        # 查询测试用例总数
        query = ('SELECT count(case_number) FROM test_result where view_id="{}"'.format(self.view_id))
        if self.run_mode == 0:
            self.case_total = len(self.run_case_list)
        else:
            cursor = self.db.run_sql(query)
            self.case_total = cursor.fetchone()[0]
        # 查询测试失败的用例数
        cursor = self.db.run_sql(
            'SELECT count(case_number) FROM test_result WHERE result = "{}" and view_id="{}"'.format('Fail',
                                                                                                         self.view_id))
        self.fail_num = cursor.fetchone()[0]
        # 查询测试通过的用例数
        cursor = self.db.run_sql(
            'SELECT count(case_number) FROM test_result WHERE result = "{}" and view_id="{}"'.format('Pass',
                                                                                                         self.view_id))
        self.success_num = cursor.fetchone()[0]
        # 查询测试出错的用例数
        cursor = self.db.run_sql(
            'SELECT count(case_number) FROM test_result WHERE result = "{}" and view_id="{}"'.format('Error',
                                                                                                         self.view_id))
        self.error_num = cursor.fetchone()[0]
        self.log.info(
            "total:{}; sucess:{}; failed:{}; error:{}".format(self.case_total, self.success_num, self.fail_num,
                                                              self.error_num))
        page << p('测试用例数：' + str(self.case_total) + '&nbsp' * 10 + '成功用例数：' + str(self.success_num) +
                  '&nbsp' * 10 + '失败用例数：' + str(self.fail_num) + '&nbsp' * 10 + '出错用例数：' + str(self.error_num))
        #  表格标题caption 表格边框border 单元边沿与其内容之间的空白cellpadding 单元格之间间隔为cellspacing
        tab = table(border='1', cellpadding='1', cellspacing='0', cl='table')
        tab1 = page << tab
        tab1 << tr(td('case id', bgcolor='#ABABAB', align='center')
                   + td('http method', bgcolor='#ABABAB', align='center')
                   + td('interface name', bgcolor='#ABABAB', align='center')
                   + td('description', bgcolor='#ABABAB', align='center')
                   + td('apply data', bgcolor='#ABABAB')
                   + td('except return', bgcolor='#ABABAB')
                   + td('acture return', bgcolor='#ABABAB')
                   + td('acture response', bgcolor='#ABABAB')
                   + td('test method', bgcolor='#ABABAB', align='center')
                   + td('result', bgcolor='#ABABAB', align='center')
                   + td('remarks', bgcolor='#ABABAB', align='center'))
        # if self.run_mode == 0:
        #     db_cursor = self.db.run_sql("select u.case_number, "
        #                                 "u.http_method, "
        #                                 "u.case_name, "
        #                                 "u.description, "
        #                                 "t.queryparameters, "
        #                                 "u.except_response_code, "
        #                                 "t.actual_response_code, "
        #                                 "t.actual_response, "
        #                                 "u.test_method, "
        #                                 "t.result, "
        #                                 "t.description "
        #                                 "from usercase u, "
        #                                 "test_result t, "
        #                                 "file_bag f, "
        #                                 "case_view v "
        #                                 "where f.file_number = v.from_id and u.from_view_id = f.file_number and t.case_number = u.case_number and v.to_id = t.view_id and t.view_id = {} and t.case_number in {}".format(
        #         self.view_id, tuple(self.run_case_list)))
        # else:
        db_cursor = self.db.run_sql("select u.case_number, "
                                        "u.http_method, "
                                        "u.case_name, "
                                        "u.description, "
                                        "t.queryparameters, "
                                        "u.except_response_code, "
                                        "t.actual_response_code, "
                                        "t.actual_response, "
                                        "u.test_method, "
                                        "t.result, "
                                        "t.description "
                                        "from usercase u, "
                                        "test_result t, "
                                        "case_view v "
                                    "where  u.from_view_id = v.from_id and t.case_number = u.case_number and v.to_id = t.view_id and t.view_id = {}".format(
                self.view_id))
        # self.cursor.execute(query)
        query_result = db_cursor.fetchall()
        self.log.debug(query_result)
        for row in query_result:
            tab1 << tr(td((row[0]), align='center')
                       + td(row[1])
                       + td(row[2])
                       + td(row[3])
                       + td(row[4])
                       + td(row[5])
                       + td(row[6])
                       + td(row[7], align='center')
                       + td(row[8])
                       + td(row[9])
                       + td(row[10]))
        self._set_result_filename(file)
        page.printOut(self.filename)
        # try:
        #     print('delete')
        #     # query = ('DELETE FROM test_result')
        #     # self.cursor.execute(query)
        #     # self.cursor.execute('commit')
        # except Exception as e:
        #     print('%s' % e)
        #     cursor.execute('rollback')
        #     cursor.close()

    def _set_result_filename(self, filename):
        self.filename = filename
        if os.path.isdir(self.filename):
            raise IOError("%s must point to a file" % path)
        elif '' == self.filename:
            raise IOError('filename can not be empty')
        else:
            parent_path, ext = os.path.splitext(filename)
            tm = time.strftime('%Y%m%d%H%M%S', time.localtime())
            self.filename = parent_path + tm + ext
            self.log.info("Report file:{}".format(self.filename))
            self.log.info("Visit web site: http://192.168.168.146/report{}{}".format(tm,ext)) 

    def set_time_took(self, time):
        self.time_took = time
        return self.time_took

    def get_info(self):
        return (self.case_total,self.success_num,self.error_num,self.fail_num,self.filename)
