#coding: utf-8
# +-------------------------------------------------------------------
# | 宝塔Linux面板
# +-------------------------------------------------------------------
# | Copyright (c) 2015-2020 宝塔软件(http://bt.cn) All rights reserved.
# +-------------------------------------------------------------------
# | Author: 黄文良 <287962566@qq.com>
# +-------------------------------------------------------------------

#+--------------------------------------------------------------------
#|   fecmall 自动部署
#+--------------------------------------------------------------------
import sys,os,json
os.chdir('/www/server/panel')
sys.path.insert(0,'class/')
import public
class fecmall_main:
    __log_file = '/tmp/panelExec.pl'
    __config_file = 'plugin/fecmall/config.json'

    def get_site_info(self,args):
        if not os.path.exists(self.__config_file): 
            import panelSite
            php_versions = panelSite.panelSite().GetPHPVersion(None)
            res_versions = []
            for php_version in php_versions:
                if int(php_version['version']) < 70: continue
                res_versions.insert(0,php_version)
            return public.returnMsg(False,res_versions)
        pdata = json.loads(public.readFile(self.__config_file))
        pdata['path'] = public.M('sites').where('id=?',(pdata['siteId'],)).getField('path')
        return pdata

    def install(self,args):
        pdata = json.loads(args.data)
        #写配置文件
        public.writeFile(self.__config_file,args.data)

        #创建运行目录
        dirs = ['appfront/web','apphtml5/web','appadmin/web','appimage/common','appserver/web','appapi/web','appbdmin/web']
        path = public.M('sites').where('id=?',(pdata['siteId'],)).getField('path')
        if not path: return public.returnMsg(False,'指定网站不存在!')
        for d in dirs: 
            filename = path + '/' + d
            if os.path.exists(filename): continue
            os.makedirs(filename)

        #下载文件
        s_file = path + '/src.zip'
        if not os.path.exists(s_file):
            s_url = 'https://fecmall-download.oss-cn-shenzhen.aliyuncs.com/download/fecmall-lasted.zip'
            public.ExecShell('wget -O {} {} -T 5'.format(s_file,s_url))

        #解压文件
        public.ExecShell('unzip -o {} -d {} &>> {}'.format(s_file,path,self.__log_file))

        if os.path.exists(path + '/fecmall/appadmin'):
            public.ExecShell("\cp -arf {} {} &> {}".format(path + '/fecmall/*',path + '/',self.__log_file))

        #设置权限
        public.ExecShell('chmod -R 755 {}'.format(path))
        public.ExecShell('chown -R www:www {}'.format(path))

        #运行初始化文件
        php_bin = '/www/server/php/{}/bin/php'.format(pdata['php_version'])
        if not os.path.exists(php_bin): 
            return public.returnMsg(False,'指定PHP版本未安装!')

        public.ExecShell('cd {} && {} {} &>> {}'.format(path,php_bin,path + '/init',self.__log_file))
        if os.path.exists(s_file): os.remove(s_file)
        return public.returnMsg(True,'初始化安装成功!')
        