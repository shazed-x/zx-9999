from __future__ import annotations

import json

from django.contrib import messages
from django.db import IntegrityError, transaction
from django.http import JsonResponse
from django.shortcuts import redirect, render

from .models import CommandTemplate, Tool


def _parse_tags(raw):
    if isinstance(raw, list):
        return [str(item).strip() for item in raw if str(item).strip()]
    if not raw:
        return []
    return [tag.strip() for tag in str(raw).split(',') if tag.strip()]


def _build_tools_context():
    tools = Tool.objects.prefetch_related('commands').all()
    tools_payload = []
    for tool in tools:
        commands_payload = []
        for cmd in tool.commands.all():
            commands_payload.append(
                {
                    'id': cmd.id,
                    'name': cmd.name,
                    'description': cmd.description,
                    'template': cmd.template,
                    'category': cmd.category,
                    'tags': cmd.tags,
                }
            )
        tools_payload.append(
            {
                'id': tool.id,
                'name': tool.name,
                'description': tool.description,
                'commands': commands_payload,
            }
        )
    return tools, tools_payload


def overview(request):
    tools = Tool.objects.prefetch_related('commands').all()
    command_count = CommandTemplate.objects.count()
    category_count = (
        CommandTemplate.objects.exclude(category='')
        .values_list('category', flat=True)
        .distinct()
        .count()
    )
    latest_command = CommandTemplate.objects.order_by('-updated_at').first()
    context = {
        'active_page': 'overview',
        'page_title': 'Overview',
        'tool_count': tools.count(),
        'command_count': command_count,
        'category_count': category_count,
        'latest_command': latest_command,
        'recent_tools': tools[:5],
    }
    return render(request, 'zxui/overview.html', context)


def composer(request):
    tools, tools_payload = _build_tools_context()
    context = {
        'active_page': 'composer',
        'page_title': 'Composer',
        'tools': tools,
        'tools_payload': tools_payload,
    }
    return render(request, 'zxui/composer.html', context)


def library(request):
    tools, tools_payload = _build_tools_context()
    context = {
        'active_page': 'library',
        'page_title': 'Library',
        'tools': tools,
        'tools_payload': tools_payload,
    }
    return render(request, 'zxui/library.html', context)


def manage(request):
    if request.method == 'POST':
        action = request.POST.get('action', '')

        if action == 'add_tool':
            name = request.POST.get('name', '').strip()
            description = request.POST.get('description', '').strip()
            if not name:
                messages.error(request, 'Tool name is required.')
                return redirect('zxui:manage')
            tool, created = Tool.objects.get_or_create(
                name=name,
                defaults={'description': description},
            )
            if created:
                messages.success(request, f'Tool "{tool.name}" added.')
            else:
                if description and description != tool.description:
                    tool.description = description
                    tool.save(update_fields=['description', 'updated_at'])
                    messages.success(request, f'Tool "{tool.name}" updated.')
                else:
                    messages.info(request, f'Tool "{tool.name}" already exists.')
            return redirect('zxui:manage')

        if action == 'add_command':
            tool_id = request.POST.get('tool_id', '').strip()
            name = request.POST.get('name', '').strip()
            description = request.POST.get('description', '').strip()
            template = request.POST.get('template', '').strip()
            category = request.POST.get('category', '').strip()
            tags = _parse_tags(request.POST.get('tags', ''))
            tool = Tool.objects.filter(id=tool_id).first() if tool_id else None
            if not tool:
                messages.error(request, 'Select a tool for the command.')
                return redirect('zxui:manage')
            if not name or not template:
                messages.error(request, 'Command name and template are required.')
                return redirect('zxui:manage')
            try:
                CommandTemplate.objects.create(
                    tool=tool,
                    name=name,
                    description=description,
                    template=template,
                    category=category,
                    tags=tags,
                )
            except IntegrityError:
                messages.error(request, 'A command with that name already exists for this tool.')
            else:
                messages.success(request, f'Command "{name}" added to {tool.name}.')
            return redirect('zxui:manage')

        if action == 'update_command':
            command_id = request.POST.get('command_id', '').strip()
            tool_id = request.POST.get('tool_id', '').strip()
            name = request.POST.get('name', '').strip()
            description = request.POST.get('description', '').strip()
            template = request.POST.get('template', '').strip()
            category = request.POST.get('category', '').strip()
            tags = _parse_tags(request.POST.get('tags', ''))
            command = CommandTemplate.objects.filter(id=command_id).first() if command_id else None
            tool = Tool.objects.filter(id=tool_id).first() if tool_id else None
            if not command:
                messages.error(request, 'Select a command to update.')
                return redirect('zxui:manage')
            if not tool:
                messages.error(request, 'Select a tool for the command.')
                return redirect('zxui:manage')
            if not name or not template:
                messages.error(request, 'Command name and template are required.')
                return redirect('zxui:manage')
            command.tool = tool
            command.name = name
            command.description = description
            command.template = template
            command.category = category
            command.tags = tags
            try:
                with transaction.atomic():
                    command.save()
            except IntegrityError:
                messages.error(request, 'A command with that name already exists for this tool.')
            else:
                messages.success(request, f'Command "{name}" updated.')
            return redirect('zxui:manage')

    tools, tools_payload = _build_tools_context()
    context = {
        'active_page': 'manage',
        'page_title': 'Manage',
        'tools': tools,
        'tools_payload': tools_payload,
    }
    return render(request, 'zxui/manage.html', context)


def import_export(request):
    if request.method == 'POST':
        action = request.POST.get('action', '')
        if action == 'import_data':
            payload = request.POST.get('payload', '').strip()
            overwrite = request.POST.get('overwrite') == 'on'
            if not payload:
                messages.error(request, 'Paste JSON data to import.')
                return redirect('zxui:import_export')
            try:
                data = json.loads(payload)
            except json.JSONDecodeError:
                messages.error(request, 'Invalid JSON. Please check the format and try again.')
                return redirect('zxui:import_export')
            tools_data = data.get('tools') if isinstance(data, dict) else data
            if not isinstance(tools_data, list):
                messages.error(request, 'JSON must be a list of tools or a { "tools": [...] } object.')
                return redirect('zxui:import_export')

            created_tools = 0
            created_commands = 0
            updated_commands = 0

            with transaction.atomic():
                for tool_entry in tools_data:
                    if not isinstance(tool_entry, dict):
                        continue
                    name = str(tool_entry.get('name', '')).strip()
                    if not name:
                        continue
                    description = str(tool_entry.get('description', '') or '').strip()
                    tool, created = Tool.objects.get_or_create(
                        name=name,
                        defaults={'description': description},
                    )
                    if created:
                        created_tools += 1
                    elif overwrite and description and description != tool.description:
                        tool.description = description
                        tool.save(update_fields=['description', 'updated_at'])

                    commands = tool_entry.get('commands', [])
                    if not isinstance(commands, list):
                        continue
                    for cmd_entry in commands:
                        if not isinstance(cmd_entry, dict):
                            continue
                        cmd_name = str(cmd_entry.get('name', '')).strip()
                        template = str(cmd_entry.get('template', '')).strip()
                        if not cmd_name or not template:
                            continue
                        cmd_description = str(cmd_entry.get('description', '') or '').strip()
                        category = str(cmd_entry.get('category', '') or '').strip()
                        tags = _parse_tags(cmd_entry.get('tags', []))

                        command, created = CommandTemplate.objects.get_or_create(
                            tool=tool,
                            name=cmd_name,
                            defaults={
                                'description': cmd_description,
                                'template': template,
                                'category': category,
                                'tags': tags,
                            },
                        )
                        if created:
                            created_commands += 1
                        elif overwrite:
                            command.description = cmd_description
                            command.template = template
                            command.category = category
                            command.tags = tags
                            command.save(
                                update_fields=['description', 'template', 'category', 'tags', 'updated_at']
                            )
                            updated_commands += 1

            messages.success(
                request,
                f'Import complete: {created_tools} tools, {created_commands} commands, '
                f'{updated_commands} updated.',
            )
            return redirect('zxui:import_export')

    context = {
        'active_page': 'import_export',
        'page_title': 'Import & Export',
    }
    return render(request, 'zxui/import_export.html', context)


def export_data(request):
    tools = Tool.objects.prefetch_related('commands').all()
    payload = {
        'tools': [
            {
                'name': tool.name,
                'description': tool.description,
                'commands': [
                    {
                        'name': command.name,
                        'description': command.description,
                        'template': command.template,
                        'category': command.category,
                        'tags': command.tags,
                    }
                    for command in tool.commands.all()
                ],
            }
            for tool in tools
        ]
    }
    return JsonResponse(payload, json_dumps_params={'indent': 2})
