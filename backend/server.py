"""无额外依赖的教学接口。Android模拟器访问 http://10.0.2.2:8765。"""
import argparse
import json
import threading
import time
from datetime import datetime, timezone
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import parse_qs, urlsplit

lock = threading.Lock()
seen = set()
names = ['实验台电源', '通风设备', '消防应急照明', '实验室温湿度传感器',
         '东侧实验台多功能供电控制设备及安全保护模块', '门窗状态传感器', '网络交换机', '灭火器']

class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        url = urlsplit(self.path)
        args = {k: v[0] for k, v in parse_qs(url.query).items()}
        room = args.get('room', 'A203')
        scenario = args.get('scenario', 'normal')
        key = args.get('key', '')
        status = 200
        data = {'room': room, 'tasks': []}
        if url.path == '/health':
            data = {'status': 'ok'}
        elif url.path != '/api/tasks':
            status, data = 404, {'error': 'not found'}
        elif room not in ('A203', 'A204'):
            status, data = 400, {'error': 'unknown room'}
        else:
            # 让加载状态可观察；slow用于取消和页面离开实验。
            time.sleep(6 if scenario == 'slow' else 0.6)
            with lock:
                first_retry = key not in seen
                if scenario == 'retry':
                    seen.add(key)
            if scenario == 'error' or (scenario == 'retry' and first_retry):
                status, data = 500, {'error': '教学用服务器错误，请重试'}
            elif scenario == 'malformed':
                data = {'room': room, 'tasks': [{'id': 'broken'}]}
            elif scenario != 'empty':
                count = 8 if room == 'A203' else 2
                data['tasks'] = [dict(id=f'{room}-T{i+1:03}', deviceName=names[i],
                                      location=f'{room} 第{i+1}巡检点',
                                      status='已完成' if i % 3 == 0 else '待巡检') for i in range(count)]
        body = json.dumps(data, ensure_ascii=False).encode('utf-8')
        try:
            self.send_response(status)
            self.send_header('Content-Type', 'application/json; charset=utf-8')
            self.send_header('Content-Length', str(len(body)))
            self.end_headers()
            self.wfile.write(body)
            result = 'sent'
        except (BrokenPipeError, ConnectionResetError, ConnectionAbortedError):
            result = 'client_disconnected'
        print(json.dumps(dict(time=datetime.now(timezone.utc).isoformat(), room=room,
                              scenario=scenario, key=key, status=status, result=result), ensure_ascii=False), flush=True)

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--port', type=int, default=8765)
    parser.add_argument('--bind', default='127.0.0.1')
    options = parser.parse_args()
    print(f'Teaching server http://{options.bind}:{options.port}', flush=True)
    ThreadingHTTPServer((options.bind, options.port), Handler).serve_forever()
