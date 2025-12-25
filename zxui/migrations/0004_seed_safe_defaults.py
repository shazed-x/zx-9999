from django.db import migrations


def seed_safe_defaults(apps, schema_editor):
    Tool = apps.get_model('zxui', 'Tool')
    CommandTemplate = apps.get_model('zxui', 'CommandTemplate')

    def ensure_tool(name, description):
        tool, created = Tool.objects.get_or_create(
            name=name,
            defaults={'description': description},
        )
        if not created and description and tool.description != description:
            tool.description = description
            tool.save(update_fields=['description', 'updated_at'])
        return tool

    def upsert_command(tool, name, template, description='', category='', tags=None):
        tags = tags or []
        command, created = CommandTemplate.objects.get_or_create(
            tool=tool,
            name=name,
            defaults={
                'description': description,
                'template': template,
                'category': category,
                'tags': tags,
            },
        )
        if not created:
            command.description = description
            command.template = template
            command.category = category
            command.tags = tags
            command.save(update_fields=['description', 'template', 'category', 'tags', 'updated_at'])

    CommandTemplate.objects.filter(
        tool__name__iexact='netcat',
        name__icontains='reverse shell',
    ).delete()

    nmap = ensure_tool(
        'nmap',
        'Network mapper for host discovery and service enumeration.',
    )
    netcat = ensure_tool(
        'netcat',
        'Networking utility for TCP/UDP checks and listeners.',
    )
    ngrok = ensure_tool(
        'ngrok',
        'Secure tunnel to expose local services.',
    )
    curl = ensure_tool(
        'curl',
        'HTTP client for quick requests and header checks.',
    )
    dig = ensure_tool(
        'dig',
        'DNS lookup utility.',
    )
    whois = ensure_tool(
        'whois',
        'Domain registration lookup.',
    )
    traceroute = ensure_tool(
        'traceroute',
        'Trace the path to a host.',
    )
    ping = ensure_tool(
        'ping',
        'Check reachability and latency.',
    )

    upsert_command(
        nmap,
        'Host discovery (ping scan)',
        'nmap -sn {target}',
        'Discover live hosts without port scanning.',
        'Recon',
        ['safe', 'discovery'],
    )
    upsert_command(
        nmap,
        'Top ports (fast)',
        'nmap --top-ports 100 {target}',
        'Quick scan of common TCP ports.',
        'Recon',
        ['safe', 'ports'],
    )
    upsert_command(
        nmap,
        'Full TCP scan',
        'nmap -p- -T4 {target}',
        'Scan all TCP ports with faster timing.',
        'Recon',
        ['ports', 'tcp'],
    )
    upsert_command(
        nmap,
        'Service detection',
        'nmap -sV {target}',
        'Detect running services and versions.',
        'Enumeration',
        ['service', 'tcp'],
    )
    upsert_command(
        nmap,
        'Default scripts + versions',
        'nmap -sC -sV {target}',
        'Run default scripts with version detection.',
        'Enumeration',
        ['scripts', 'service'],
    )
    upsert_command(
        nmap,
        'OS fingerprinting',
        'nmap -O {target}',
        'Attempt OS detection (requires privileges).',
        'Enumeration',
        ['os', 'tcp'],
    )
    upsert_command(
        nmap,
        'UDP top ports',
        'nmap -sU --top-ports 50 {target}',
        'Scan common UDP ports.',
        'Recon',
        ['udp', 'ports'],
    )
    upsert_command(
        nmap,
        'Vuln scripts (read-only)',
        'nmap --script vuln {target}',
        'Run vulnerability detection scripts where authorized.',
        'Audit',
        ['vuln', 'scripts'],
    )
    upsert_command(
        nmap,
        'Custom script',
        'nmap --script {script} {target}',
        'Run a specific NSE script by name.',
        'Audit',
        ['scripts'],
    )

    upsert_command(
        netcat,
        'TCP connect',
        'nc -v {target} {port}',
        'Connect to a TCP port and read banners.',
        'Connectivity',
        ['safe', 'tcp'],
    )
    upsert_command(
        netcat,
        'TCP port check',
        'nc -vz {target} {port}',
        'Zero-I/O TCP port check.',
        'Connectivity',
        ['tcp', 'ports'],
    )
    upsert_command(
        netcat,
        'UDP port check',
        'nc -vu {target} {port}',
        'Send UDP probe to a port.',
        'Connectivity',
        ['udp', 'ports'],
    )
    upsert_command(
        netcat,
        'Listen for TCP',
        'nc -lvnp {port}',
        'Open a local TCP listener.',
        'Utility',
        ['listener'],
    )
    upsert_command(
        netcat,
        'Send file',
        'nc {target} {port} < {file}',
        'Send a file over TCP.',
        'Utility',
        ['transfer'],
    )
    upsert_command(
        netcat,
        'Receive file',
        'nc -lvnp {port} > {file}',
        'Receive a file over TCP.',
        'Utility',
        ['transfer'],
    )

    upsert_command(
        ngrok,
        'HTTP tunnel',
        'ngrok http {port}',
        'Expose a local HTTP service.',
        'Tunneling',
        ['http', 'tunnel'],
    )
    upsert_command(
        ngrok,
        'TCP tunnel',
        'ngrok tcp {port}',
        'Expose a local TCP service.',
        'Tunneling',
        ['tcp', 'tunnel'],
    )
    upsert_command(
        ngrok,
        'Start all tunnels',
        'ngrok start --all',
        'Start all tunnels from the config file.',
        'Tunneling',
        ['config'],
    )

    upsert_command(
        curl,
        'GET request',
        'curl -s {target}',
        'Fetch a URL silently.',
        'HTTP',
        ['http', 'safe'],
    )
    upsert_command(
        curl,
        'HEAD request',
        'curl -I {target}',
        'Fetch response headers.',
        'HTTP',
        ['http', 'headers'],
    )
    upsert_command(
        curl,
        'POST request',
        'curl -X POST {target}',
        'Send a POST request to a URL.',
        'HTTP',
        ['http', 'post'],
    )

    upsert_command(
        dig,
        'A record lookup',
        'dig A {domain} +short',
        'Resolve A records.',
        'DNS',
        ['dns', 'safe'],
    )
    upsert_command(
        dig,
        'MX record lookup',
        'dig MX {domain} +short',
        'Resolve MX records.',
        'DNS',
        ['dns'],
    )

    upsert_command(
        whois,
        'Domain lookup',
        'whois {domain}',
        'Check domain registration details.',
        'DNS',
        ['whois'],
    )

    upsert_command(
        traceroute,
        'Traceroute (Unix)',
        'traceroute {target}',
        'Trace network hops to a target.',
        'Connectivity',
        ['trace'],
    )
    upsert_command(
        traceroute,
        'Tracert (Windows)',
        'tracert {target}',
        'Trace network hops to a target (Windows).',
        'Connectivity',
        ['trace', 'windows'],
    )

    upsert_command(
        ping,
        'Ping (Linux/macOS)',
        'ping -c 4 {target}',
        'Send 4 ICMP echo requests.',
        'Connectivity',
        ['icmp'],
    )
    upsert_command(
        ping,
        'Ping (Windows)',
        'ping -n 4 {target}',
        'Send 4 ICMP echo requests (Windows).',
        'Connectivity',
        ['icmp', 'windows'],
    )


def remove_safe_defaults(apps, schema_editor):
    Tool = apps.get_model('zxui', 'Tool')
    Tool.objects.filter(
        name__in=[
            'ngrok',
            'curl',
            'dig',
            'whois',
            'traceroute',
            'ping',
        ]
    ).delete()


class Migration(migrations.Migration):
    dependencies = [
        ('zxui', '0003_add_metadata_fields'),
    ]

    operations = [
        migrations.RunPython(seed_safe_defaults, remove_safe_defaults),
    ]
