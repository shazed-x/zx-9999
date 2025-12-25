from django.db import migrations


def seed_network_utilities(apps, schema_editor):
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

    nslookup = ensure_tool(
        'nslookup',
        'DNS resolver lookup utility.',
    )
    host = ensure_tool(
        'host',
        'DNS lookup utility with record types.',
    )
    wget = ensure_tool(
        'wget',
        'HTTP client for downloading or probing URLs.',
    )
    ipconfig = ensure_tool(
        'ipconfig',
        'Windows IP configuration utility.',
    )
    ifconfig = ensure_tool(
        'ifconfig',
        'Unix network interface configuration tool.',
    )
    ip = ensure_tool(
        'ip',
        'Linux network configuration utility.',
    )
    netstat = ensure_tool(
        'netstat',
        'Network statistics and connections.',
    )
    ss = ensure_tool(
        'ss',
        'Socket statistics (Linux).',
    )
    route = ensure_tool(
        'route',
        'Routing table display.',
    )
    arp = ensure_tool(
        'arp',
        'ARP table inspection.',
    )
    openssl = ensure_tool(
        'openssl',
        'TLS inspection and certificate utilities.',
    )

    upsert_command(
        nslookup,
        'Lookup',
        'nslookup {domain}',
        'Query DNS for a domain.',
        'DNS',
        ['dns', 'safe'],
    )
    upsert_command(
        nslookup,
        'MX records',
        'nslookup -type=MX {domain}',
        'Query MX records for a domain.',
        'DNS',
        ['dns'],
    )
    upsert_command(
        nslookup,
        'TXT records',
        'nslookup -type=TXT {domain}',
        'Query TXT records for a domain.',
        'DNS',
        ['dns'],
    )

    upsert_command(
        host,
        'Lookup',
        'host {domain}',
        'Resolve a domain.',
        'DNS',
        ['dns', 'safe'],
    )
    upsert_command(
        host,
        'All records',
        'host -a {domain}',
        'Request all DNS records.',
        'DNS',
        ['dns'],
    )

    upsert_command(
        wget,
        'Spider check',
        'wget --spider {target}',
        'Probe a URL without downloading content.',
        'HTTP',
        ['http', 'safe'],
    )
    upsert_command(
        wget,
        'Fetch body',
        'wget -qO- {target}',
        'Fetch a URL and print output.',
        'HTTP',
        ['http'],
    )

    upsert_command(
        ipconfig,
        'Full config',
        'ipconfig /all',
        'Show detailed interface configuration.',
        'Network',
        ['windows'],
    )
    upsert_command(
        ipconfig,
        'DNS cache',
        'ipconfig /displaydns',
        'Display the DNS resolver cache.',
        'Network',
        ['windows', 'dns'],
    )

    upsert_command(
        ifconfig,
        'All interfaces',
        'ifconfig -a',
        'Show all interfaces and addresses.',
        'Network',
        ['linux', 'macos'],
    )

    upsert_command(
        ip,
        'IP addresses',
        'ip addr show',
        'Show IP addressing details.',
        'Network',
        ['linux'],
    )
    upsert_command(
        ip,
        'Routes',
        'ip route show',
        'Show routing table.',
        'Network',
        ['linux'],
    )

    upsert_command(
        netstat,
        'Active connections (Windows)',
        'netstat -ano',
        'Show all connections with PID.',
        'Network',
        ['windows'],
    )
    upsert_command(
        netstat,
        'Listening ports (Linux)',
        'netstat -tulpen',
        'Show listening ports and processes.',
        'Network',
        ['linux'],
    )

    upsert_command(
        ss,
        'Listening ports',
        'ss -tulpen',
        'Show listening ports and processes.',
        'Network',
        ['linux'],
    )

    upsert_command(
        route,
        'Routing table (Windows)',
        'route print',
        'Display routing table.',
        'Network',
        ['windows'],
    )
    upsert_command(
        route,
        'Routing table (Linux)',
        'route -n',
        'Display routing table with numeric addresses.',
        'Network',
        ['linux'],
    )

    upsert_command(
        arp,
        'ARP table',
        'arp -a',
        'Show ARP table entries.',
        'Network',
        ['windows', 'linux', 'macos'],
    )

    upsert_command(
        openssl,
        'TLS handshake',
        'openssl s_client -connect {target}:{port} -servername {domain}',
        'Inspect TLS certificate and handshake.',
        'TLS',
        ['tls'],
    )
    upsert_command(
        openssl,
        'Read certificate file',
        'openssl x509 -in {file} -text -noout',
        'Parse a local certificate file.',
        'TLS',
        ['tls'],
    )


class Migration(migrations.Migration):
    dependencies = [
        ('zxui', '0004_seed_safe_defaults'),
    ]

    operations = [
        migrations.RunPython(seed_network_utilities, migrations.RunPython.noop),
    ]
