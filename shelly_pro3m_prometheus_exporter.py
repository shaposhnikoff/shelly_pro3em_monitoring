from prometheus_client import make_wsgi_app, Gauge
from prometheus_client.core import CollectorRegistry
import requests,time,threading
from flask import Flask

app = Flask(__name__)

shelly_url = 'http://192.168.10.69/rpc/Shelly.GetStatus'

registry = CollectorRegistry()

gauge_metrics = {
    'current': Gauge('shelly_current', 'Current', ['phase'], registry=registry),
    'voltage': Gauge('shelly_voltage', 'Voltage', ['phase'], registry=registry),
    'act_power': Gauge('shelly_act_power', 'Active Power', ['phase'], registry=registry),
    'aprt_power': Gauge('shelly_aprt_power', 'Apparent Power', ['phase'], registry=registry),
    'pf': Gauge('shelly_pf', 'Power Factor', ['phase'], registry=registry),
    'freq': Gauge('shelly_freq', 'Frequency', ['phase'], registry=registry),
    'total_current': Gauge('shelly_total_current', 'Total Current', registry=registry),
    'total_act_power': Gauge('shelly_total_act_power', 'Total Active Power', registry=registry),
    'total_aprt_power': Gauge('shelly_total_aprt_power', 'Total Apparent Power', registry=registry),
    'uptime': Gauge('shelly_uptime', 'System Uptime', registry=registry),
    'temperature_c': Gauge('shelly_temperature_c', 'Temperature in Celsius', registry=registry),
    'temperature_f': Gauge('shelly_temperature_f', 'Temperature in Fahrenheit', registry=registry),
    'ram_free': Gauge('shelly_ram_free', 'Free RAM', registry=registry),
    'fs_free': Gauge('shelly_fs_free', 'Free Filesystem Space', registry=registry),
    'a_total_act_energy': Gauge('shelly_a_total_act_energy', 'Total Active Energy A', ['phase'], registry=registry),
    'a_total_act_ret_energy': Gauge('shelly_a_total_act_ret_energy', 'Total Active Returned Energy A', ['phase'], registry=registry),
    'b_total_act_energy': Gauge('shelly_b_total_act_energy', 'Total Active Energy B', ['phase'], registry=registry),
    'b_total_act_ret_energy': Gauge('shelly_b_total_act_ret_energy', 'Total Active Returned Energy B', ['phase'], registry=registry),
    'c_total_act_energy': Gauge('shelly_c_total_act_energy', 'Total Active Energy C', ['phase'], registry=registry),
    'c_total_act_ret_energy': Gauge('shelly_c_total_act_ret_energy', 'Total Active Returned Energy C', ['phase'], registry=registry),
    'total_act_energy': Gauge('shelly_total_act_energy', 'Total active energy on all phases', registry=registry),
    'total_act_ret_energy': Gauge('shelly_total_act_ret_energy', 'Total Active Returned Energy', registry=registry)
}

def fetch_shelly_data():
    try:
        response = requests.get(shelly_url)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        print(f"Error fetching data: {e}")
        return None

def update_metrics(data):
    if data:
        phases = ['a', 'b', 'c']
        for phase in phases:
            gauge_metrics['current'].labels(phase=phase).set(data[f'em:0'][f'{phase}_current'])
            gauge_metrics['voltage'].labels(phase=phase).set(data[f'em:0'][f'{phase}_voltage'])
            gauge_metrics['act_power'].labels(phase=phase).set(data[f'em:0'][f'{phase}_act_power'])
            gauge_metrics['aprt_power'].labels(phase=phase).set(data[f'em:0'][f'{phase}_aprt_power'])
            gauge_metrics['pf'].labels(phase=phase).set(data[f'em:0'][f'{phase}_pf'])
            gauge_metrics['freq'].labels(phase=phase).set(data[f'em:0'][f'{phase}_freq'])
            gauge_metrics['total_current'].set(data['em:0']['total_current'])
            gauge_metrics['total_act_power'].set(data['em:0']['total_act_power'])
            gauge_metrics['total_aprt_power'].set(data['em:0']['total_aprt_power'])
            gauge_metrics['uptime'].set(data['sys']['uptime'])
            gauge_metrics['temperature_c'].set(data['temperature:0']['tC'])
            gauge_metrics['temperature_f'].set(data['temperature:0']['tF'])
            gauge_metrics['ram_free'].set(data['sys']['ram_free'])
            gauge_metrics['fs_free'].set(data['sys']['fs_free'])
            gauge_metrics['a_total_act_energy'].labels(phase='a').set(data['emdata:0']['a_total_act_energy'])
            gauge_metrics['a_total_act_ret_energy'].labels(phase='a').set(data['emdata:0']['a_total_act_ret_energy'])
            gauge_metrics['b_total_act_energy'].labels(phase='b').set(data['emdata:0']['b_total_act_energy'])
            gauge_metrics['b_total_act_ret_energy'].labels(phase='b').set(data['emdata:0']['b_total_act_ret_energy'])
            gauge_metrics['c_total_act_energy'].labels(phase='c').set(data['emdata:0']['c_total_act_energy'])
            gauge_metrics['c_total_act_ret_energy'].labels(phase='c').set(data['emdata:0']['c_total_act_ret_energy'])
            gauge_metrics['total_act_energy'].set(data['emdata:0']['total_act'])
            gauge_metrics['total_act_ret_energy'].set(data['emdata:0']['total_act_ret'])

@app.route('/metrics')
def metrics():
    return make_wsgi_app(registry)

def run_metrics_server():
    app.run(host='0.0.0.0', port=8000)

def fetch_and_update_loop():
    while True:
        data = fetch_shelly_data()
        update_metrics(data)
        time.sleep(10)

if __name__ == '__main__':
    threading.Thread(target=run_metrics_server).start()
    fetch_and_update_loop()
