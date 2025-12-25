(() => {
  const toolsDataElement = document.getElementById('tools-data');
  const toolsData = toolsDataElement ? JSON.parse(toolsDataElement.textContent) : [];

  const toolSelect = document.getElementById('tool-select');
  const commandSearchInput = document.getElementById('command-search');
  const commandSelect = document.getElementById('command-select');
  const templatePreview = document.getElementById('template-preview');
  const commandMeta = document.getElementById('command-meta');
  const commandDescription = document.getElementById('command-description');
  const paramFields = document.getElementById('param-fields');
  const extraArgsInput = document.getElementById('extra-args');
  const commandOutput = document.getElementById('command-output');
  const copyButton = document.getElementById('copy-command');
  const librarySearchInput = document.getElementById('library-search');
  const categoryFilter = document.getElementById('category-filter');

  const editCommandSelect = document.getElementById('edit-command-select');
  const editToolSelect = document.getElementById('edit-tool-select');
  const editName = document.getElementById('edit-name');
  const editDescription = document.getElementById('edit-description');
  const editCategory = document.getElementById('edit-category');
  const editTags = document.getElementById('edit-tags');
  const editTemplate = document.getElementById('edit-template');

  const labelMap = {
    target: 'Target',
    port: 'Port',
    lhost: 'LHOST',
    lport: 'LPORT',
    rhost: 'RHOST',
    rport: 'RPORT',
    domain: 'Domain',
    iface: 'Interface',
    protocol: 'Protocol',
    file: 'File path',
    script: 'Script',
  };

  const toNumber = (value) => {
    const parsed = Number(value);
    return Number.isNaN(parsed) ? null : parsed;
  };

  const normalize = (value) => (value || '').toString().toLowerCase().trim();

  const getToolById = (toolId) => toolsData.find((tool) => tool.id === toolId);

  const getCommandById = (commandId) => {
    for (const tool of toolsData) {
      const command = tool.commands.find((entry) => entry.id === commandId);
      if (command) {
        return { ...command, toolId: tool.id, toolName: tool.name };
      }
    }
    return null;
  };

  const createOption = (value, label) => {
    const option = document.createElement('option');
    option.value = value;
    option.textContent = label;
    return option;
  };

  const filterCommands = (commands, searchTerm) => {
    const term = normalize(searchTerm);
    if (!term) {
      return commands;
    }
    return commands.filter((command) => {
      const haystack = [
        command.name,
        command.description,
        command.template,
        command.category,
        (command.tags || []).join(' '),
      ]
        .join(' ')
        .toLowerCase();
      return haystack.includes(term);
    });
  };

  const populateTools = () => {
    if (!toolSelect) {
      return;
    }
    toolSelect.innerHTML = '';
    if (!toolsData.length) {
      toolSelect.appendChild(createOption('', 'No tools available'));
      toolSelect.disabled = true;
      return;
    }
    toolSelect.disabled = false;
    toolsData.forEach((tool) => {
      toolSelect.appendChild(createOption(tool.id, tool.name));
    });
  };

  const populateCommands = (tool, searchTerm = '') => {
    if (!commandSelect) {
      return [];
    }
    commandSelect.innerHTML = '';
    const commands = tool ? tool.commands : [];
    const filtered = filterCommands(commands, searchTerm);
    if (!tool || !filtered.length) {
      commandSelect.appendChild(createOption('', 'No commands available'));
      commandSelect.disabled = true;
      return [];
    }
    commandSelect.disabled = false;
    filtered.forEach((command) => {
      commandSelect.appendChild(createOption(command.id, command.name));
    });
    return filtered;
  };

  const renderParameterFields = (template) => {
    if (!paramFields) {
      return [];
    }
    paramFields.innerHTML = '';
    const tokens = [];
    const seen = new Set();
    const regex = /\{([a-zA-Z0-9_]+)\}/g;
    let match = regex.exec(template);
    while (match) {
      const key = match[1];
      if (!seen.has(key)) {
        tokens.push(key);
        seen.add(key);
      }
      match = regex.exec(template);
    }
    if (!tokens.length) {
      const note = document.createElement('div');
      note.className = 'notice';
      note.textContent = 'No variables detected. Add {target} or other placeholders to template.';
      paramFields.appendChild(note);
      return tokens;
    }

    tokens.forEach((key) => {
      const label = document.createElement('label');
      label.textContent = labelMap[key] || key;
      const input = document.createElement('input');
      input.type = 'text';
      input.dataset.paramKey = key;
      input.placeholder = `Enter ${labelMap[key] || key}`;
      input.addEventListener('input', updateCommandOutput);
      label.appendChild(input);
      paramFields.appendChild(label);
    });

    return tokens;
  };

  const getParamValues = () => {
    const values = {};
    if (!paramFields) {
      return values;
    }
    paramFields.querySelectorAll('input[data-param-key]').forEach((input) => {
      const key = input.dataset.paramKey;
      if (!key) {
        return;
      }
      values[key] = input.value.trim();
    });
    return values;
  };

  const buildCommand = (template) => {
    let output = template || '';
    const values = getParamValues();
    output = output.replace(/\{([a-zA-Z0-9_]+)\}/g, (match, key) => {
      const value = values[key];
      return value ? value : match;
    });
    const extraArgs = extraArgsInput ? extraArgsInput.value.trim() : '';
    if (extraArgs) {
      output = `${output} ${extraArgs}`.trim();
    }
    return output;
  };

  const updateCommandOutput = () => {
    if (!commandOutput) {
      return;
    }
    const commandId = toNumber(commandSelect?.value);
    const command = commandId ? getCommandById(commandId) : null;
    const template = command ? command.template : '';
    commandOutput.value = template ? buildCommand(template) : '';
  };

  const updateCommandPreview = () => {
    const commandId = toNumber(commandSelect?.value);
    const command = commandId ? getCommandById(commandId) : null;
    if (!command) {
      if (templatePreview) {
        templatePreview.textContent = 'Select a command to preview.';
      }
      if (commandMeta) {
        commandMeta.textContent = '';
      }
      if (commandDescription) {
        commandDescription.textContent = '';
      }
      renderParameterFields('');
      updateCommandOutput();
      return;
    }

    if (templatePreview) {
      templatePreview.textContent = command.template;
    }
    if (commandMeta) {
      const metaParts = [];
      if (command.category) {
        metaParts.push(`Category: ${command.category}`);
      }
      if (command.tags && command.tags.length) {
        metaParts.push(`Tags: ${command.tags.join(', ')}`);
      }
      commandMeta.textContent = metaParts.join(' · ');
    }
    if (commandDescription) {
      commandDescription.textContent = command.description || '';
    }
    renderParameterFields(command.template);
    updateCommandOutput();
  };

  const getActiveTool = () => {
    const toolId = toNumber(toolSelect?.value);
    return toolId ? getToolById(toolId) : null;
  };

  const initializeComposer = () => {
    if (!toolSelect || !commandSelect) {
      return;
    }
    populateTools();

    const firstTool = toolsData[0];
    if (firstTool) {
      toolSelect.value = firstTool.id;
      const commands = populateCommands(firstTool, commandSearchInput?.value);
      if (commands[0]) {
        commandSelect.value = commands[0].id;
      }
    }

    updateCommandPreview();

    toolSelect.addEventListener('change', () => {
      const toolId = toNumber(toolSelect.value);
      const tool = toolId ? getToolById(toolId) : null;
      const commands = populateCommands(tool, commandSearchInput?.value);
      if (commands[0]) {
        commandSelect.value = commands[0].id;
      }
      updateCommandPreview();
    });

    commandSelect.addEventListener('change', updateCommandPreview);

    if (commandSearchInput) {
      commandSearchInput.addEventListener('input', () => {
        const tool = getActiveTool();
        const commands = populateCommands(tool, commandSearchInput.value);
        if (commands[0]) {
          commandSelect.value = commands[0].id;
        }
        updateCommandPreview();
      });
    }

    if (extraArgsInput) {
      extraArgsInput.addEventListener('input', updateCommandOutput);
    }
  };

  const initializeEditForm = () => {
    if (!editCommandSelect || !editToolSelect) {
      return;
    }
    editCommandSelect.innerHTML = '';
    editToolSelect.innerHTML = '';

    toolsData.forEach((tool) => {
      editToolSelect.appendChild(createOption(tool.id, tool.name));
      tool.commands.forEach((command) => {
        const label = `${tool.name}: ${command.name}`;
        editCommandSelect.appendChild(createOption(command.id, label));
      });
    });

    if (!editCommandSelect.options.length) {
      editCommandSelect.appendChild(createOption('', 'No commands available'));
      editCommandSelect.disabled = true;
      editToolSelect.appendChild(createOption('', 'No tools available'));
      editToolSelect.disabled = true;
      if (editName) editName.value = '';
      if (editDescription) editDescription.value = '';
      if (editCategory) editCategory.value = '';
      if (editTags) editTags.value = '';
      if (editTemplate) editTemplate.value = '';
      return;
    }

    const firstCommand = getCommandById(toNumber(editCommandSelect.value));
    if (firstCommand) {
      editToolSelect.value = firstCommand.toolId;
      if (editName) editName.value = firstCommand.name;
      if (editDescription) editDescription.value = firstCommand.description || '';
      if (editCategory) editCategory.value = firstCommand.category || '';
      if (editTags) editTags.value = (firstCommand.tags || []).join(', ');
      if (editTemplate) editTemplate.value = firstCommand.template;
    }

    editCommandSelect.addEventListener('change', () => {
      const command = getCommandById(toNumber(editCommandSelect.value));
      if (!command) {
        return;
      }
      editToolSelect.value = command.toolId;
      if (editName) editName.value = command.name;
      if (editDescription) editDescription.value = command.description || '';
      if (editCategory) editCategory.value = command.category || '';
      if (editTags) editTags.value = (command.tags || []).join(', ');
      if (editTemplate) editTemplate.value = command.template;
    });
  };

  const initializeCopy = () => {
    if (!copyButton || !commandOutput) {
      return;
    }
    copyButton.addEventListener('click', async () => {
      const value = commandOutput.value;
      if (!value) {
        return;
      }
      try {
        await navigator.clipboard.writeText(value);
        copyButton.textContent = 'Copied';
        setTimeout(() => {
          copyButton.textContent = 'Copy';
        }, 1500);
      } catch (error) {
        commandOutput.select();
        document.execCommand('copy');
      }
    });
  };

  const populateCategoryFilter = () => {
    if (!categoryFilter) {
      return;
    }
    const categories = new Set();
    toolsData.forEach((tool) => {
      tool.commands.forEach((command) => {
        if (command.category) {
          categories.add(command.category);
        }
      });
    });
    categoryFilter.innerHTML = '';
    categoryFilter.appendChild(createOption('', 'All categories'));
    Array.from(categories)
      .sort((a, b) => a.localeCompare(b))
      .forEach((category) => {
        categoryFilter.appendChild(createOption(category, category));
      });
  };

  const applyLibraryFilters = () => {
    const term = normalize(librarySearchInput?.value);
    const category = normalize(categoryFilter?.value);
    const cards = document.querySelectorAll('.tool-card');

    cards.forEach((card) => {
      const toolName = normalize(card.dataset.toolName);
      const toolMatches = !term || toolName.includes(term);
      let visibleCount = 0;
      const commandItems = card.querySelectorAll('li[data-command-name]');

      commandItems.forEach((item) => {
        const commandText = [
          item.dataset.commandName,
          item.dataset.commandTemplate,
          item.dataset.commandDescription,
          item.dataset.commandTags,
        ]
          .join(' ')
          .toLowerCase();
        const matchesSearch = toolMatches || (!term ? true : commandText.includes(term));
        const itemCategory = normalize(item.dataset.commandCategory);
        const matchesCategory = !category || itemCategory === category;
        const visible = matchesSearch && matchesCategory;
        item.style.display = visible ? '' : 'none';
        if (visible) {
          visibleCount += 1;
        }
      });

      const mutedItem = card.querySelector('li.muted');
      if (mutedItem) {
        mutedItem.style.display = toolMatches && !category ? '' : 'none';
      }

      const shouldShow =
        visibleCount > 0 || (toolMatches && !category && commandItems.length === 0);
      card.style.display = shouldShow ? '' : 'none';
    });
  };

  const initializeLibraryFilters = () => {
    populateCategoryFilter();
    if (librarySearchInput) {
      librarySearchInput.addEventListener('input', applyLibraryFilters);
    }
    if (categoryFilter) {
      categoryFilter.addEventListener('change', applyLibraryFilters);
    }
    applyLibraryFilters();
  };

  const revealPanels = () => {
    const panels = document.querySelectorAll('[data-animate]');
    panels.forEach((panel, index) => {
      setTimeout(() => {
        panel.classList.add('visible');
      }, 120 * index);
    });
  };

  initializeComposer();
  initializeEditForm();
  initializeCopy();
  initializeLibraryFilters();
  revealPanels();
})();
