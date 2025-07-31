// Global state
let currentSession = null;
let currentStructure = null;
let selectedShape = null;
let currentSlideIndex = 0;
let isExpanded = false;
let buildMode = false;
let selectedProvider = 'anthropic';
let selectedOllamaModel = 'llama2';

// Execute command placeholder - will be defined later
let handleExecuteCommand;

// Wait for DOM to be ready
document.addEventListener('DOMContentLoaded', function() {
    console.log('DOM loaded, initializing application...');

    // DOM elements
    const uploadPresentationBtn = document.getElementById('upload-presentation-btn');
    const presentationFileInput = document.getElementById('presentation-file');
    const ingestDocumentBtn = document.getElementById('ingest-document-btn');
    const buildPresentationBtn = document.getElementById('build-presentation-btn');
    const documentFileInput = document.getElementById('document-file');
    const structureTree = document.getElementById('structure-tree');
    const consoleOutput = document.getElementById('console-output');
    const commandInput = document.getElementById('command-input');
    const executeCommand = document.getElementById('execute-command');
    const toggleInputSize = document.getElementById('toggle-input-size');
    const slidePreview = document.getElementById('slide-preview');
    const prevSlideBtn = document.getElementById('prev-slide');
    const nextSlideBtn = document.getElementById('next-slide');
    const slideIndicator = document.getElementById('slide-indicator');
    const editModeSection = document.getElementById('edit-mode-section');
    const commandSectionTitle = document.getElementById('command-section-title');
    const modeIndicator = document.getElementById('mode-indicator');
    const llmProviderSelect = document.getElementById('llm-provider');
    const providerStatus = document.getElementById('provider-status');
    const ollamaModelSection = document.getElementById('ollama-model-section');
    const ollamaModelSelect = document.getElementById('ollama-model');

    // Check if critical elements exist
    console.log('Build button found:', !!buildPresentationBtn);
    console.log('Execute button found:', !!executeCommand);
    console.log('Command input found:', !!commandInput);

    // Event listeners - wrapped in try-catch for debugging
    try {
        if (uploadPresentationBtn) {
            uploadPresentationBtn.addEventListener('click', () => presentationFileInput.click());
        }
        if (presentationFileInput) {
            presentationFileInput.addEventListener('change', handlePresentationUpload);
        }
        if (ingestDocumentBtn) {
            ingestDocumentBtn.addEventListener('click', () => documentFileInput.click());
        }
        if (documentFileInput) {
            documentFileInput.addEventListener('change', handleDocumentUpload);
        }
        if (executeCommand) {
            executeCommand.addEventListener('click', () => {
                console.log('Execute button clicked!');
                handleExecuteCommand();
            });
        }
        if (buildPresentationBtn) {
            buildPresentationBtn.addEventListener('click', () => {
                console.log('Build presentation button clicked!');
                toggleBuildMode();
            });
        } else {
            console.error('Build presentation button not found!');
        }
        if (toggleInputSize) {
            toggleInputSize.addEventListener('click', toggleInputExpanded);
        }
        if (prevSlideBtn) {
            prevSlideBtn.addEventListener('click', () => navigateSlide(-1));
        }
        if (nextSlideBtn) {
            nextSlideBtn.addEventListener('click', () => navigateSlide(1));
        }
        if (llmProviderSelect) {
            llmProviderSelect.addEventListener('change', handleProviderChange);
            // Set initial provider from stored value
            const storedProvider = localStorage.getItem('llmProvider') || 'anthropic';
            llmProviderSelect.value = storedProvider;
            selectedProvider = storedProvider;
            updateProviderStatus(storedProvider);
        }
    } catch (error) {
        console.error('Error setting up event listeners:', error);
    }

    // Handle presentation upload
    async function handlePresentationUpload(event) {
        const file = event.target.files[0];
        if (!file) return;

        const formData = new FormData();
        formData.append('file', file);

        try {
            showLoading();
            const response = await fetch('/api/upload/presentation', {
                method: 'POST',
                body: formData
            });

            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(errorData.error || 'Upload failed');
            }

            const data = await response.json();
            console.log('Upload response:', data);
            
            currentSession = data.session_id;
            currentStructure = data.structure;
            
            renderStructureTree();
            enableConsole();
            updateSlidePreview();
            
            addConsoleMessage('✅ Presentation uploaded successfully!');
            
            const totalShapes = currentStructure.slides.reduce((acc, s) => acc + s.shapes.length, 0);
            addConsoleMessage(`📊 Found ${currentStructure.slides.length} slides with ${totalShapes} shapes`);
            
            if (totalShapes === 0) {
                addConsoleMessage('⚠️ This presentation appears to be empty or has no content');
                addConsoleMessage('💡 Perfect! Use "Build from Text" to create your slides from scratch');
                addConsoleMessage('🚀 Click the green "Build from Text" button to get started');
                // Hide edit mode settings for empty presentations
                editModeSection.style.display = 'none';
            } else {
                addConsoleMessage('💡 Tip: Click on a shape in the Structure Explorer to edit it, or use "Build from Text" to create slides');
                // Show edit mode settings when there's content to edit
                editModeSection.style.display = 'block';
            }
        } catch (error) {
            console.error('Upload error:', error);
            addConsoleMessage('❌ Error: ' + error.message, 'error');
        } finally {
            hideLoading();
            // Clear the file input
            event.target.value = '';
        }
    }

    // Handle document upload for ingestion
    async function handleDocumentUpload(event) {
        const file = event.target.files[0];
        if (!file) return;

        const formData = new FormData();
        formData.append('file', file);

        try {
            showLoading();
            const response = await fetch('/api/upload/document', {
                method: 'POST',
                body: formData
            });

            if (!response.ok) throw new Error('Upload failed');

            const data = await response.json();
            currentSession = data.session_id;
            
            // Show plan in console
            addConsoleMessage('Document analyzed. Proposed presentation structure:');
            addConsoleMessage(JSON.stringify(data.plan, null, 2));
            
            // Ask for confirmation
            const confirmed = confirm('Create presentation from this plan?');
            if (confirmed) {
                await executePlan();
            }
        } catch (error) {
            addConsoleMessage('Error: ' + error.message, 'error');
        } finally {
            hideLoading();
        }
    }

    // Execute the presentation plan
    async function executePlan() {
        try {
            showLoading();
            const response = await fetch(`/api/presentation/${currentSession}/plan`, {
                method: 'POST'
            });

            if (!response.ok) throw new Error('Plan execution failed');

            const data = await response.json();
            currentStructure = data.structure;
            
            renderStructureTree();
            enableConsole();
            updateSlidePreview();
            
            addConsoleMessage('Presentation created successfully!');
        } catch (error) {
            addConsoleMessage('Error: ' + error.message, 'error');
        } finally {
            hideLoading();
        }
    }

    // Render the structure tree
    function renderStructureTree() {
        console.log('Rendering structure tree...');
        console.log('Current structure:', currentStructure);
        
        if (!currentStructure || !currentStructure.slides) {
            console.error('No structure to render');
            return;
        }

        let html = '';
        let totalShapes = 0;
        
        currentStructure.slides.forEach((slide, idx) => {
            html += `
                <div class="tree-node slide-node" data-slide="${idx}">
                    <div class="tree-node-content">
                        <span class="tree-node-icon">📑</span>
                        <span><strong>Slide ${idx + 1}</strong></span>
                    </div>
                    <div class="tree-children">`;
            
            if (slide.shapes.length === 0) {
                html += `
                    <div class="tree-node empty-slide">
                        <div class="tree-node-content">
                            <span class="tree-node-icon">📝</span>
                            <span style="color: #6c757d; font-style: italic;">Empty slide - ready for content</span>
                        </div>
                    </div>`;
            } else {
                slide.shapes.forEach((shape, shapeIdx) => {
                    const text = shape.text ? shape.text.substring(0, 40) : `Shape: ${shape.type}`;
                    const icon = shape.text ? '📝' : '📦';
                    html += `
                        <div class="tree-node shape-node" data-slide="${idx}" data-shape="${shape.id}">
                            <div class="tree-node-content">
                                <span class="tree-node-icon">${icon}</span>
                                <span>${text}</span>
                            </div>
                        </div>`;
                    totalShapes++;
                });
            }
            
            html += '</div></div>';
        });

        // If completely empty, show helpful message
        if (totalShapes === 0 && currentStructure.slides.length <= 1) {
            html = `
                <div class="empty-presentation">
                    <div style="text-align: center; padding: 2rem; color: #6c757d;">
                        <div style="font-size: 2rem; margin-bottom: 1rem;">📝</div>
                        <div style="font-weight: 600; margin-bottom: 0.5rem;">Empty Presentation</div>
                        <div style="font-size: 0.875rem;">Ready to build from your content!</div>
                        <div style="font-size: 0.75rem; margin-top: 1rem; padding: 0.5rem; background-color: #e3f2fd; border-radius: 4px;">
                            💡 Use "Build from Text" to create slides
                        </div>
                    </div>
                </div>`;
        }

        console.log('Generated HTML:', html);
        structureTree.innerHTML = html;

        // Add click handlers
        document.querySelectorAll('.tree-node').forEach(node => {
            node.addEventListener('click', handleTreeNodeClick);
        });
        
        console.log('Structure tree rendered with', currentStructure.slides.length, 'slides');
    }

    // Handle tree node selection
    function handleTreeNodeClick(event) {
        event.stopPropagation();
        
        // Remove previous selection
        document.querySelectorAll('.tree-node').forEach(n => n.classList.remove('selected'));
        
        // Add selection to current node
        const node = event.currentTarget;
        node.classList.add('selected');
        
        // Update selected shape
        selectedShape = node.dataset.shape || null;
        const slideIndex = parseInt(node.dataset.slide);
        
        if (slideIndex !== currentSlideIndex) {
            currentSlideIndex = slideIndex;
            updateSlidePreview();
        }
        
        // Enable editing when shape is selected (only if not in build mode)
        if (selectedShape && !buildMode) {
            commandInput.disabled = false;
            executeCommand.disabled = false;
            commandInput.placeholder = 'Enter your edit command for the selected shape...';
            addConsoleMessage(`✅ Shape selected: ${node.textContent.trim()}`, 'info');
            addConsoleMessage('💡 Now you can type edit commands in the text box below', 'info');
        }
    }

    // Update slide preview
    async function updateSlidePreview() {
        if (!currentSession || !currentStructure) return;

        const totalSlides = currentStructure.slides.length;
        if (totalSlides === 0) return;

        // Update navigation
        slideIndicator.textContent = `Slide ${currentSlideIndex + 1} / ${totalSlides}`;
        prevSlideBtn.disabled = currentSlideIndex === 0;
        nextSlideBtn.disabled = currentSlideIndex >= totalSlides - 1;

        // Load preview image
        const previewUrl = `/api/presentation/${currentSession}/slide/${currentSlideIndex}/preview.png`;
        
        // Check if this is an empty slide
        const currentSlide = currentStructure.slides[currentSlideIndex];
        if (currentSlide && currentSlide.shapes.length === 0) {
            slidePreview.innerHTML = `
                <div style="display: flex; flex-direction: column; align-items: center; justify-content: center; height: 100%; color: #6c757d;">
                    <div style="font-size: 3rem; margin-bottom: 1rem;">📝</div>
                    <div style="font-weight: 600; margin-bottom: 0.5rem;">Empty Slide</div>
                    <div style="font-size: 0.875rem; text-align: center;">This slide has no content yet.<br>Use "Build from Text" to add content.</div>
                </div>`;
        } else {
            slidePreview.innerHTML = `<img src="${previewUrl}?t=${Date.now()}" alt="Slide preview">`;
        }
    }

    // Navigate slides
    function navigateSlide(direction) {
        const totalSlides = currentStructure?.slides.length || 0;
        currentSlideIndex = Math.max(0, Math.min(totalSlides - 1, currentSlideIndex + direction));
        updateSlidePreview();
    }

    // Console utilities
    function addConsoleMessage(message, type = 'info') {
        const msgDiv = document.createElement('div');
        msgDiv.className = `console-message console-${type}`;
        msgDiv.textContent = message;
        consoleOutput.appendChild(msgDiv);
        consoleOutput.scrollTop = consoleOutput.scrollHeight;
    }

    function enableConsole() {
        commandInput.disabled = false;
        executeCommand.disabled = false;
    }

    // Loading states
    function showLoading() {
        document.body.classList.add('loading');
    }

    function hideLoading() {
        document.body.classList.remove('loading');
    }

    // Toggle input expanded state
    function toggleInputExpanded() {
        isExpanded = !isExpanded;
        commandInput.classList.toggle('expanded', isExpanded);
        toggleInputSize.textContent = isExpanded ? 'Collapse' : 'Expand';
    }

    // Toggle build mode
    function toggleBuildMode() {
        console.log('toggleBuildMode called, current buildMode:', buildMode);
        buildMode = !buildMode;
        console.log('New buildMode:', buildMode);
        
        if (buildMode) {
            // Enter build mode
            if (!currentSession) {
                addConsoleMessage('❌ Please upload a presentation first', 'error');
                buildMode = false;
                return;
            }
            
            // Update UI for build mode
            commandInput.placeholder = 'Paste your structured presentation content here (e.g., ## Slide 1...)';
            commandInput.disabled = false;
            commandInput.style.backgroundColor = '#fffbf0';
            commandInput.style.border = '2px solid #ff9800';
            executeCommand.textContent = '🚀 Execute Build';
            executeCommand.disabled = false;
            executeCommand.classList.add('btn-warning');
            buildPresentationBtn.textContent = '❌ Cancel Build Mode';
            buildPresentationBtn.classList.remove('btn-secondary');
            buildPresentationBtn.classList.add('btn-danger');
            
            // Hide edit mode settings in build mode
            editModeSection.style.display = 'none';
            
            // Update section title and indicator
            commandSectionTitle.textContent = 'Build Mode - Paste Content';
            modeIndicator.style.display = 'block';
            modeIndicator.innerHTML = '🏗️ <strong>BUILD MODE:</strong> Paste your structured text below and click "Execute Build"';
            
            // Automatically expand the input
            if (!isExpanded) {
                toggleInputExpanded();
            }
            
            // Clear any existing content
            commandInput.value = '';
            commandInput.focus();
            
            // Force scroll the command input into view
            commandInput.scrollIntoView({ behavior: 'smooth', block: 'center' });
            
            // Also scroll the console output to show recent messages
            consoleOutput.scrollTop = consoleOutput.scrollHeight;
            
            // Add clear instructions
            addConsoleMessage('🏗️ BUILD MODE ACTIVATED!', 'info');
            addConsoleMessage('📝 Instructions:', 'info');
            addConsoleMessage('1. Paste your structured text in the expanded box below', 'info');
            addConsoleMessage('2. Use ## Slide X for slide markers', 'info');
            addConsoleMessage('3. Use **text** for titles and bold content', 'info');
            addConsoleMessage('4. Click "🚀 Build Presentation" when ready', 'info');
            addConsoleMessage('', 'info');
            addConsoleMessage('Example format:', 'info');
            addConsoleMessage('## Slide 1', 'info');
            addConsoleMessage('**Your Title Here**', 'info');
            addConsoleMessage('- Bullet point 1', 'info');
            addConsoleMessage('- Bullet point 2', 'info');
            
            // Scroll to bottom of console
            consoleOutput.scrollTop = consoleOutput.scrollHeight;
        } else {
            // Exit build mode
            commandInput.placeholder = 'Select a shape first, then enter your command here...';
            commandInput.style.backgroundColor = '';
            commandInput.style.border = '';
            executeCommand.textContent = 'Execute Edit';
            executeCommand.classList.remove('btn-warning');
            buildPresentationBtn.textContent = '🏗️ Build from Text';
            buildPresentationBtn.classList.remove('btn-danger');
            buildPresentationBtn.classList.add('btn-secondary');
            
            // Update section title and indicator
            commandSectionTitle.textContent = 'Command Input';
            modeIndicator.style.display = 'none';
            
            // Show/hide edit mode settings based on content
            const totalShapes = currentStructure ? currentStructure.slides.reduce((acc, s) => acc + s.shapes.length, 0) : 0;
            if (totalShapes > 0) {
                editModeSection.style.display = 'block';
            } else {
                editModeSection.style.display = 'none';
            }
            
            // Only enable if shape is selected
            if (!selectedShape) {
                commandInput.disabled = true;
                executeCommand.disabled = true;
            }
            
            addConsoleMessage('ℹ️ Build mode cancelled', 'info');
        }
    }

    // Modified execute command to handle both modes
    async function handleBuildPresentation() {
        console.log('handleBuildPresentation called');
        console.log('Current session:', currentSession);
        console.log('Build mode:', buildMode);
        
        const structuredText = commandInput.value.trim();
        console.log('Structured text length:', structuredText.length);
        
        // Add immediate feedback
        addConsoleMessage('🚀 Starting build process...', 'info');
        
        if (!structuredText) {
            addConsoleMessage('❌ Please enter structured presentation content', 'error');
            return;
        }
        
        if (!currentSession) {
            addConsoleMessage('❌ No active session - please upload a presentation first', 'error');
            return;
        }
        
        try {
            showLoading();
            if (selectedProvider === 'ollama') {
                addConsoleMessage('🔧 Processing with Ollama (this may take longer for local models)...', 'info');
                addConsoleMessage(`🤖 Using model: ${selectedOllamaModel}`, 'info');
            } else {
                addConsoleMessage('🔧 Processing structured text with AI...', 'info');
            }
            addConsoleMessage(`📝 Content preview: ${structuredText.substring(0, 100)}...`, 'info');
            
            console.log('Making API call to:', `/api/presentation/${currentSession}/build`);
            
            const response = await fetch(`/api/presentation/${currentSession}/build`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    structured_text: structuredText,
                    provider: selectedProvider,
                    ollama_model: selectedProvider === 'ollama' ? selectedOllamaModel : null
                })
            });
            
            console.log('Response status:', response.status);
            console.log('Response ok:', response.ok);
            
            if (!response.ok) {
                const errorData = await response.json();
                console.error('Error response:', errorData);
                throw new Error(errorData.error || 'Build failed');
            }
            
            const data = await response.json();
            console.log('Success response:', data);
            currentStructure = data.structure;
            
            renderStructureTree();
            updateSlidePreview();
            
            addConsoleMessage('✅ Presentation built successfully!', 'info');
            addConsoleMessage(`📊 Created ${data.structure.slides.length} slides`, 'info');
            commandInput.value = '';
            
            // Exit build mode automatically after successful build
            buildMode = true; // Set to true so toggleBuildMode will switch it to false
            toggleBuildMode();
            
        } catch (error) {
            console.error('Build error:', error);
            addConsoleMessage('❌ Error: ' + error.message, 'error');
            addConsoleMessage('💡 Try checking your content format or contact support', 'error');
        } finally {
            hideLoading();
        }
    }

    // Store the original execute command function
    const originalExecuteCommand = async function() {
        const command = commandInput.value.trim();
        
        console.log('Execute command:', {
            command,
            selectedShape,
            currentSession
        });
        
        if (!command) {
            addConsoleMessage('Please enter a command', 'error');
            return;
        }
        
        if (!selectedShape) {
            addConsoleMessage('Please select a shape first', 'error');
            return;
        }
        
        if (!currentSession) {
            addConsoleMessage('No active session', 'error');
            return;
        }

        const contextMode = document.querySelector('input[name="context-mode"]:checked').value;

        try {
            showLoading();
            addConsoleMessage(`> ${command}`);
            if (selectedProvider === 'ollama') {
                addConsoleMessage(`🤖 Processing with Ollama model: ${selectedOllamaModel}`, 'info');
            }
            
            const response = await fetch(`/api/presentation/${currentSession}/edit`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    shape_id: selectedShape,
                    command: command,
                    context_mode: contextMode,
                    provider: selectedProvider,
                    ollama_model: selectedProvider === 'ollama' ? selectedOllamaModel : null
                })
            });

            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(errorData.error || 'Edit failed');
            }

            const data = await response.json();
            currentStructure = data.structure;
            
            renderStructureTree();
            updateSlidePreview();
            
            addConsoleMessage('Edit applied successfully!');
            commandInput.value = '';
        } catch (error) {
            console.error('Command error:', error);
            addConsoleMessage('Error: ' + error.message, 'error');
        } finally {
            hideLoading();
        }
    };

    // Replace the original handleExecuteCommand function
    handleExecuteCommand = async function() {
        console.log('handleExecuteCommand called, buildMode:', buildMode);
        
        if (buildMode) {
            console.log('Routing to handleBuildPresentation');
            await handleBuildPresentation();
        } else {
            console.log('Routing to originalExecuteCommand');
            await originalExecuteCommand();
        }
    };

    // Handle LLM provider change
    async function handleProviderChange(event) {
        selectedProvider = event.target.value;
        localStorage.setItem('llmProvider', selectedProvider);
        updateProviderStatus(selectedProvider);
        addConsoleMessage(`✅ Switched to ${getProviderName(selectedProvider)}`, 'info');
        
        // Show/hide Ollama model selection
        if (selectedProvider === 'ollama') {
            ollamaModelSection.style.display = 'block';
            await loadOllamaModels();
        } else {
            ollamaModelSection.style.display = 'none';
        }
    }

    // Update provider status message
    function updateProviderStatus(provider) {
        const statusMessages = {
            'anthropic': 'Using Anthropic API (Claude)',
            'openai': 'Using OpenAI API (GPT-4)',
            'ollama': 'Using Ollama (Local Model)'
        };
        if (providerStatus) {
            providerStatus.textContent = statusMessages[provider] || 'Unknown provider';
        }
    }

    // Get friendly provider name
    function getProviderName(provider) {
        const names = {
            'anthropic': 'Anthropic (Claude)',
            'openai': 'OpenAI (GPT-4)',
            'ollama': 'Ollama (Local)'
        };
        return names[provider] || provider;
    }

    // Load available Ollama models
    async function loadOllamaModels() {
        try {
            ollamaModelSelect.innerHTML = '<option value="">Loading models...</option>';
            
            const response = await fetch('/api/ollama/models');
            if (!response.ok) {
                throw new Error('Failed to fetch Ollama models');
            }
            
            const data = await response.json();
            const models = data.models || [];
            
            if (models.length === 0) {
                ollamaModelSelect.innerHTML = '<option value="">No models found - install with: ollama pull llama2</option>';
                return;
            }
            
            ollamaModelSelect.innerHTML = '';
            models.forEach(model => {
                const option = document.createElement('option');
                option.value = model.name;
                option.textContent = `${model.name} (${formatSize(model.size)})`;
                ollamaModelSelect.appendChild(option);
            });
            
            // Restore previously selected model or use first available
            const storedModel = localStorage.getItem('ollamaModel');
            if (storedModel && models.some(m => m.name === storedModel)) {
                ollamaModelSelect.value = storedModel;
                selectedOllamaModel = storedModel;
            } else if (models.length > 0) {
                selectedOllamaModel = models[0].name;
                ollamaModelSelect.value = selectedOllamaModel;
            }
            
        } catch (error) {
            console.error('Error loading Ollama models:', error);
            ollamaModelSelect.innerHTML = '<option value="">Error loading models - is Ollama running?</option>';
        }
    }

    // Format file size
    function formatSize(bytes) {
        const gb = bytes / (1024 * 1024 * 1024);
        return gb >= 1 ? `${gb.toFixed(1)}GB` : `${(bytes / (1024 * 1024)).toFixed(1)}MB`;
    }

    // Handle Ollama model selection
    if (ollamaModelSelect) {
        ollamaModelSelect.addEventListener('change', (event) => {
            selectedOllamaModel = event.target.value;
            localStorage.setItem('ollamaModel', selectedOllamaModel);
            addConsoleMessage(`✅ Selected Ollama model: ${selectedOllamaModel}`, 'info');
        });
    }

    // Check if provider is Ollama on load
    if (selectedProvider === 'ollama' && ollamaModelSection) {
        ollamaModelSection.style.display = 'block';
        loadOllamaModels();
    }

}); // End of DOMContentLoaded