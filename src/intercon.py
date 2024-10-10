 # -*- coding: utf-8 -*-
import requests
import sys

CUR_OS = sys.platform

class Intercon(object):
    prod_divs = [1,2,4,12]

    def __init__(self, collection='', fields=''):

        self.intercon_config = {
                "url_linux_legacy": "http://192.168.100.47/intercon/search.js",
                "url_linux": "http://192.168.100.57/intercon/search",
                "url_win": "http://ygg-app/intercon/search.js",
                "key": "YGGIC872adbgCGB863sTh5185X" }

        self.intercon_proj_config = {
                "url_linux": "http://192.168.100.57/intercon/search",
                "url_win": "http://ygg-app/intercon/search.js",  
                "key": "YGGIC889adbgCGBe19s8h5192X"}

        if CUR_OS.startswith('win'):
            self.url = self.intercon_config['url_win']
            self.proj_url = self.intercon_proj_config['url_win']
            
        elif CUR_OS.startswith('linux'):
            self.url = self.intercon_config['url_linux']
            self.proj_url = self.intercon_proj_config['url_linux']

        self.key = self.intercon_config['key']
        self.proj_key = self.intercon_proj_config['key']

        self.collections = [
            'user',
            'empstatus',
            'division',
            'department',
            'level',
            'project' ]

        self.headers = {
            'Content-type':'application/json',
            'Accept': 'application/json' }

        self.filters = { 'CONNECT_KEY':self.key }

        self.collection = collection
        self.fields = fields
    
    def interconRequest(self, data):
        res = requests.post(self.url, data=data, headers=self.headers)
        if res.status_code == 200:
            return res.json()
        else:
            return []
    
    def interconProjectRequest(self, data):
        res = requests.post(self.proj_url, data=data, headers=self.headers)
        if res.status_code == 200:
            return res.json()
        else:
            return []
        
    def user(self):
        self.collection = 'user'
        self.fields = 'uid, empid, domain_login, fname_en, sname_en, nickname_en, div_id, dept_id, lvid, pos_title, status'
        
        self.filters['FIELDS'] = self.fields
        self.filters['REQT'] = self.collection
        
        return self.interconRequest(self.filters)
    
    def empStatus(self):
        self.collection = 'empstatus'
        self.fields = 'stid, stname_th, stname_en, stname_en'

        self.filters['FIELDS'] = self.fields
        self.filters['REQT'] = self.collection

        return self.interconRequest(self.filters)

    def division(self):
        self.collection = 'division'
        self.fields = 'divid, divname, shortname, status'
        
        self.filters['FIELDS'] = self.fields
        self.filters['REQT'] = self.collection
        self.filters['FT_FIELD'] = ['divid', 'divid', 'divid']
        self.filters['FT_OP'] = ['is', 'is', 'is']
        self.filters['FT_VALUE'] = self.prod_divs
        self.filters['FT_COMB'] = ['OR', 'OR']

        return self.interconRequest(self.filters)

    def department(self):
        self.collection = 'department'
        self.fields = 'dept_id, shortname, name, shortname, sup_yggid'
        
        self.filters['FIELDS'] = self.fields
        self.filters['REQT'] = self.collection

        return self.interconRequest(self.filters)

    def userLevel(self):
        self.collection = 'level'
        self.fields = 'lvid, title'
        
        self.filters['FIELDS'] = self.fields
        self.filters['REQT'] = self.collection

        return self.interconRequest(self.filters)
    
    def project(self):
        self.collection = 'project'
        self.filters['CONNECT_KEY'] = self.proj_key
        self.filters['FIELDS'] = '*'
        self.filters['REQT'] = self.collection

        return self.interconProjectRequest(self.filters)

class FieldMapping(Intercon):
    @classmethod
    def user_fields(cls):
        return {
            'uid': 'InterconID',
            'empid': 'EmployeeID',
            'domain_login': 'UserDomain',
            'fname_en': 'FirstName',
            'sname_en': 'LastName',
            'nickname_en': 'Nickname',
            'div_id': 'DivisionID',
            'dept_id': 'DepartmentID',
            'lvid': 'LevelID',
            'pos_title': 'Position',
            'status': 'StatusID'
        }
