const AnyProxy = require('anyproxy');
var fs = require('fs')
var moment = require('moment')

/*
{
  protocol: 'http',
  url: 'http://anyproxy.io/',
  requestOptions: {
    hostname: 'anyproxy.io',
    port: 80,
    path: '/',
    method: 'GET',
    headers: {
      Host: 'anyproxy.io',
      'Proxy-Connection': 'keep-alive',
      'User-Agent': '...'
    }
  },
  requestData: '...',
  _req: { }
}

*/

var account_num = 0
var pre_load_all_url = ''

var interest_url = {
    "load_all":     "https://mp.weixin.qq.com/mp/profile_ext?action=home",          //加载历史消息 
    "load_more":    "https://mp.weixin.qq.com/mp/profile_ext?action=getmsg",        //更多历史消息
    "getappmsgext":     "https://mp.weixin.qq.com/mp/getappmsgext?",                //阅读消息
    "appmsg_comment":   "https://mp.weixin.qq.com/mp/appmsg_comment?",              //评论信息
    "content": "https://mp.weixin.qq.com/s?",                                       //文章正文html
}


function sendToRedis(key, value) {
    var redis = require("redis");
    client = redis.createClient(6379, 'localhost', {});
    client.on("error", function (err) {
        console.log("error:" + err);
        console.log("有可能是redis尚未启动...")
    });
    client.rpush(key, value, redis.print)
    client.quit();
};

const rule = {
    // 模块介绍
    summary: 'my customized rule for AnyProxy',
    // 发送请求前拦截处理
    *beforeSendRequest(requestDetail) {

        // 每一请求的关键信息
        var data_needed = {}
        data_needed['protocol'] = requestDetail.protocol
        data_needed['url'] = requestDetail.url
        data_needed['requestOptions'] = requestDetail.requestOptions
        data_needed['requestData'] = requestDetail.requestData
        // 请求的url感兴趣就保存本次请求的信息到文件中

        for (url in interest_url){
            if (requestDetail.url.includes(interest_url[url])){
                var rd_buf = Buffer(requestDetail.requestData)
                var rd_str = rd_buf.toString('utf8')
                data_needed['requestData'] = rd_str
                // timestamp = moment().format('YY-MM-DD-HH-mm-ss-SSS')
                timestamp = Date.now().toString()
                key = timestamp+'.'+url+'.req'
                value = JSON.stringify(data_needed)
                // 分别将截取的代理文件写入redis 和 文件
                sendToRedis(key, value)
                // fs.writeFile(".\\proxy_file\\"+key, value)
            }
        }
    },
    // 发送响应前处理
    *beforeSendResponse(requestDetail, responseDetail) { /* ... */ },
    // 是否处理https请求
    *beforeDealHttpsRequest(requestDetail) {
        return true
    },
    // 请求出错的事件
    *onError(requestDetail, error) { /* ... */ },
    // https连接服务器出错
    *onConnectError(requestDetail, error) { /* ... */ }
};

const options = {
    port: 8001,
    rule: rule,
    webInterface: {
        enable: true,
        webPort: 8002
    },
    throttle: 10000,
    forceProxyHttps: true,
    wsIntercept: false, // 不开启websocket代理
    silent: true
};
const proxyServer = new AnyProxy.ProxyServer(options);

proxyServer.on('ready', () => { /* */ });
proxyServer.on('error', (e) => { /* */ });
proxyServer.start();

//when finished
// proxyServer.close();