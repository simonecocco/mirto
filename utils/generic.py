from subprocess import run as run_cmd

def add_iptables_rule(action, direction, proto, comm_port, port, queue_num):
    run_cmd([
        'sudo', 'iptables',
        action, direction,
        '-p', proto,
        f'--{comm_port}port', str(port),
        '-j', 'NFQUEUE', '--queue-num', queue_num
    ])