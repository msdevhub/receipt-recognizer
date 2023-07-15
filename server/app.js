// 在这里导入你所需的模块和库
const express = require('express');
const bodyParser = require('body-parser');
const axios = require('axios');
const atob = require('atob');
const btoa = require('btoa');

// 创建 Express 应用
const app = express();

// 使用 bodyParser 解析请求体
app.use(bodyParser.json());

// 处理 /chat POST 请求
app.post('/chat', async (req, res) => {
  try {
    // 从请求体中获取聊天信息
    const { message } = req.body;
    // https://chat.vercel.ai/?_rsc=a768e99
    // 使用 Axios 发送类似的 GET 请求
    const response = await axios.get('https://chat.vercel.ai/openai.jpeg', {
      headers: {
        accept: '*/*',
        'accept-language': 'zh-CN,zh;q=0.9',
        'sec-ch-ua': '"Not.A/Brand";v="8", "Chromium";v="114", "Google Chrome";v="114"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"macOS"',
        'sec-fetch-dest': 'empty',
        'sec-fetch-mode': 'cors',
        'sec-fetch-site': 'same-origin',
        Referer: 'https://chat.vercel.ai/',
        'Referrer-Policy': 'strict-origin-when-cross-origin'
      }
    });

    const data = JSON.parse(atob(response.data));
    const ret = eval('('.concat(data.c, ')(data.a)'));

    // 对处理后的结果进行加密并返回
    const encryptedData = btoa(
      JSON.stringify({
        r: ret,
        t: data.t
      })
    );
    customEncoding = btoa(JSON.stringify({ r: [ret[0], [], 'sentinel'], t: data.t }));

    const chatResp = await axios.post(
      'https://chat.vercel.ai/api/chat',
      {
        messages: [
          {
            role: 'user',
            content: 'What is a "serverless function"?'
          }
        ],
        id: 'OcmqmmE'
      },
      {
        headers: {
          accept: '*/*',
          'accept-language': 'zh-CN,zh;q=0.9',
          'content-type': 'application/json',
          'custom-encoding': customEncoding,
          'sec-ch-ua': '"Not.A/Brand";v="8", "Chromium";v="114", "Google Chrome";v="114"',
          'sec-ch-ua-mobile': '?0',
          'sec-ch-ua-platform': '"macOS"',
          'sec-fetch-dest': 'empty',
          'sec-fetch-mode': 'cors',
          'sec-fetch-site': 'same-origin',
          Referer: 'https://chat.vercel.ai/',
          'Referrer-Policy': 'strict-origin-when-cross-origin'
        }
      }
    );

    res.json({ message: chatResp.data });
  } catch (error) {
    console.error(error);
    res.status(500).json({ error: '服务器发生错误' });
  }
});

// 监听端口 3000
app.listen(3000, () => {
  console.log('服务器正在运行，监听端口 3000...');
});
