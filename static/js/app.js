// Global state
let currentSession = null;
let currentStructure = null;
let selectedShape = null;
let currentSlideIndex = 0;
let isExpanded = false;
let buildMode = false;

// Sample minimal content for new users
const SAMPLE_MINIMAL = `## Slide 1
**Executive Summary**
- What we did
- What we found
- What it means

## Slide 2
**Next Steps**
- Action 1
- Action 2
- Owner & timeline`;

// ---------------------------------------------------------------------------
// Common slide recipes (id -> { name, text })
// ---------------------------------------------------------------------------
const RECIPES = {
    qbr: {
        name: 'Quarterly Business Review',
        text: `## Slide 1
**Quarterly Business Review**
- Agenda & objectives
- Key wins this quarter
- Challenges we faced
- Looking ahead

## Slide 2
**Performance Snapshot**
- Revenue growth: 12% QoQ
- Customer churn: 4%
- NPS: 62
- Major deals closed: 5

## Slide 3
**Challenges & Risks**
- Supply-chain delays
- Competitive pricing pressures
- Hiring gaps in engineering

## Slide 4
**Next Quarter Focus**
- Expand into APAC market
- Launch v2 of mobile app
- Reduce churn below 3%`
    },
    project_update: {
        name: 'Project Update',
        text: `## Slide 1
**Project Phoenix – Status Update**
- Goal: Modernise core platform
- Timeline: Jan – Jun 2025

## Slide 2
**Milestones Completed**
- Requirements gathered
- Architecture finalised
- Sprint 1 & 2 delivered

## Slide 3
**Current Risks**
- API integration delays
- Limited QA bandwidth

## Slide 4
**Next Steps**
- Complete Sprint 3 stories
- Security penetration test
- Prepare UAT environment`
    },
    consulting_proposal: {
        name: 'Consulting Proposal',
        text: `## Slide 1
**Consulting Proposal**
- Client: ACME Corp
- Objective: Increase operational efficiency by 30%
- Timeline: 12-week engagement

## Slide 2
**Current Business Challenges**
- Manual processes causing 40% productivity loss
- Data silos preventing cross-functional insights
- Inconsistent customer experience across channels

## Slide 3
**Recommended Solution**
- Process automation & workflow redesign
- Integrated data platform implementation
- Customer journey optimization

## Slide 4
**Expected Business Outcomes**
- 30% increase in operational efficiency
- $2.4M annual cost savings
- Improved customer satisfaction metrics
- Scalable foundation for future growth`
    },
    qual_mr_report: {
        name: 'Qualitative Market Research Report',
        text: `## Slide 1
**Qualitative Market Research Findings**
- Study objective: Understand customer perception of Product X
- Methodology: 24 in-depth interviews, 4 focus groups
- Research period: June-July 2025

## Slide 2
**Key Customer Insights**
- Users value simplicity over feature richness
- Price sensitivity varies significantly by segment
- Brand perception strongest among 35-45 demographic
- Competitor Y seen as "innovative but unreliable"

## Slide 3
**Voice of Customer Highlights**
- "I need something that works first time, every time"
- "The onboarding experience felt overwhelming"
- "Support team response time exceeded expectations"
- "Would recommend to colleagues but not for enterprise use"

## Slide 4
**Recommendations & Next Steps**
- Simplify user interface based on core user journeys
- Develop segment-specific messaging strategy
- Enhance enterprise reliability features
- Conduct quantitative validation study in Q4`
    }
};

// Execute command placeholder - will be defined later
let handleExecuteCommand;

// Wait for DOM to be ready
document.addEventListener('DOMContentLoaded', function() {
    console.log('DOM loaded, initializing application...');

    // DOM elements
    const appRoot = document.getElementById('app');
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
    const exportSection = document.getElementById('export-section');
    const exportPptxBtn = document.getElementById('export-pptx');
    const exportPdfBtn = document.getElementById('export-pdf');
    // Recipe elements
    const recipeSelect = document.getElementById('recipe-select');
    const insertRecipeBtn = document.getElementById('insert-recipe');
    // New elements
    const structureEmptyOverlay = document.getElementById('structure-empty-overlay');
    const previewEmptyOverlay = document.getElementById('preview-empty-overlay');
    const selectionHint = document.getElementById('selection-hint');
    const insertSampleBtn = document.getElementById('insert-sample');

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
        
        // Export button event listeners
        if (exportPptxBtn) {
            exportPptxBtn.addEventListener('click', handleExportPptx);
        }
        if (exportPdfBtn) {
            exportPdfBtn.addEventListener('click', handleExportPdf);
        }
        // Insert recipe handler
        if (insertRecipeBtn) {
            insertRecipeBtn.addEventListener('click', handleInsertRecipe);
        }
        // Insert sample handler
        if (insertSampleBtn) {
            insertSampleBtn.addEventListener('click', handleInsertSample);
        }
    } catch (error) {
        console.error('Error setting up event listeners:', error);
    }

    // ------------------------------------------------------------------
    // First-run UI management
    // ------------------------------------------------------------------
    function updateFirstRunUI() {
        const hasDeck = !!(currentSession && currentStructure && Array.isArray(currentStructure.slides));
        appRoot.classList.toggle('first-run', !hasDeck);
        appRoot.classList.toggle('in-build', buildMode);
        if (structureEmptyOverlay) structureEmptyOverlay.style.display = hasDeck ? 'none' : 'flex';
        const hasSlides = hasDeck && currentStructure.slides.length > 0;
        if (previewEmptyOverlay) previewEmptyOverlay.style.display = hasSlides ? 'none' : 'flex';
    }

    // ------------------------------------------------------------------
    // Recipe insertion logic
    // ------------------------------------------------------------------
    function handleInsertRecipe() {
        const recipeId = recipeSelect ? recipeSelect.value : '';
        if (!recipeId) {
            addConsoleMessage('❌ Please choose a recipe first', 'error');
            return;
        }
        const recipe = RECIPES[recipeId];
        if (!recipe) {
            addConsoleMessage('❌ Unknown recipe selected', 'error');
            return;
        }
        // Ensure we are in build mode
        if (!buildMode) {
            toggleBuildMode();
        }
        commandInput.value = recipe.text.trim();
        commandInput.focus();
        addConsoleMessage(`📋 Inserted "${recipe.name}" template. Edit as needed then click 🚀 Execute Build`, 'info');
    }

    // ------------------------------------------------------------------
    // Sample insertion logic
    // ------------------------------------------------------------------
    function handleInsertSample() {
        if (!buildMode) toggleBuildMode();
        if (!currentSession) {
            // will be created inside toggleBuildMode path below
        }
        commandInput.value = SAMPLE_MINIMAL.trim();
        commandInput.focus();
        addConsoleMessage('📋 Inserted minimal 2-slide sample. Edit then click 🚀 Execute Build', 'info');
    }

    // ------------------------------------------------------------------
    // Create blank session for first-run
    // ------------------------------------------------------------------
    async function createBlankSession() {
        try {
            showLoading();
            const resp = await fetch('/api/session/create', { method: 'POST' });
            if (!resp.ok) throw new Error('Failed to create session');
            const data = await resp.json();
            currentSession = data.session_id;
            currentStructure = data.structure;
            renderStructureTree();
            updateSlidePreview();
            addConsoleMessage('🆕 Created a new blank presentation. You can now build from text.', 'info');
            updateFirstRunUI();
            return true;
        } catch (e) {
            addConsoleMessage('❌ Could not create a new session: ' + e.message, 'error');
            return false;
        } finally {
            hideLoading();
        }
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
            showExportSection(); // Show export buttons when presentation is available
            
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
            
            updateFirstRunUI();
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
            updateFirstRunUI();
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
            
            // Hide selection hint when shape is selected
            if (selectionHint) selectionHint.classList.toggle('visible', false);
        }
        
        // Show selection hint if no shape is selected and not in build mode
        if (selectionHint) selectionHint.classList.toggle('visible', !buildMode && !selectedShape);
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
        
        // Show selection hint when enabling console but no shape is selected
        if (selectionHint && !buildMode && !selectedShape) {
            selectionHint.classList.toggle('visible', true);
        }
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
                createBlankSession().then((ok) => {
                    if (!ok) { buildMode = false; return; }
                    enterBuildModeUI();
                });
                return;
            }
            
            enterBuildModeUI();
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
                
                // Show selection hint when exiting build mode with no shape selected
                if (selectionHint) selectionHint.classList.toggle('visible', true);
            }
            
            addConsoleMessage('ℹ️ Build mode cancelled', 'info');
            updateFirstRunUI();
        }
    }
    
    // Enter build mode UI updates
    function enterBuildModeUI() {
        // Prefill with sample if empty
        commandInput.value = commandInput.value || SAMPLE_MINIMAL.trim();
        
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
        
        // Focus the input
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
        
        // Update first-run UI
        updateFirstRunUI();
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
            addConsoleMessage('🔧 Processing structured text with AI...', 'info');
            addConsoleMessage(`📝 Content preview: ${structuredText.substring(0, 100)}...`, 'info');
            
            console.log('Making API call to:', `/api/presentation/${currentSession}/build`);
            
            const response = await fetch(`/api/presentation/${currentSession}/build`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    structured_text: structuredText
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
            showExportSection(); // Show export buttons after successful build
            commandInput.value = '';
            
            // Exit build mode automatically after successful build
            buildMode = true; // Set to true so toggleBuildMode will switch it to false
            toggleBuildMode();
            
            updateFirstRunUI();
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
            
            const response = await fetch(`/api/presentation/${currentSession}/edit`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    shape_id: selectedShape,
                    command: command,
                    context_mode: contextMode
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

    // Export functionality
    function showExportSection() {
        if (exportSection && currentSession) {
            exportSection.style.display = 'block';
        }
    }

    function hideExportSection() {
        if (exportSection) {
            exportSection.style.display = 'none';
        }
    }

    // Handle PPTX export
    async function handleExportPptx() {
        if (!currentSession) {
            addConsoleMessage('❌ No presentation to export', 'error');
            return;
        }

        try {
            exportPptxBtn.textContent = 'Downloading...';
            exportPptxBtn.disabled = true;

            addConsoleMessage('📁 Downloading PPTX file...', 'info');

            // Create download link
            const downloadUrl = `/api/presentation/${currentSession}/download`;
            const link = document.createElement('a');
            link.href = downloadUrl;
            link.download = ''; // Let server determine filename
            document.body.appendChild(link);
            link.click();
            document.body.removeChild(link);

            addConsoleMessage('✅ PPTX download started', 'info');

        } catch (error) {
            addConsoleMessage(`❌ Export error: ${error.message}`, 'error');
        } finally {
            exportPptxBtn.textContent = '📁 Download PPTX';
            exportPptxBtn.disabled = false;
        }
    }

    // Handle PDF export
    async function handleExportPdf() {
        if (!currentSession) {
            addConsoleMessage('❌ No presentation to export', 'error');
            return;
        }

        try {
            exportPdfBtn.textContent = 'Converting...';
            exportPdfBtn.disabled = true;

            addConsoleMessage('📄 Converting to PDF (this may take a moment)...', 'info');

            const response = await fetch(`/api/presentation/${currentSession}/export/pdf`);
            
            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(errorData.error || 'PDF export failed');
            }

            // Create download from response blob
            const blob = await response.blob();
            const url = window.URL.createObjectURL(blob);
            const link = document.createElement('a');
            link.href = url;
            
            // Get filename from response header or use default
            const contentDisposition = response.headers.get('Content-Disposition');
            let filename = 'presentation.pdf';
            if (contentDisposition) {
                const match = contentDisposition.match(/filename="?([^"]+)"?/);
                if (match) filename = match[1];
            }
            
            link.download = filename;
            document.body.appendChild(link);
            link.click();
            document.body.removeChild(link);
            window.URL.revokeObjectURL(url);

            addConsoleMessage('✅ PDF export completed', 'info');

        } catch (error) {
            addConsoleMessage(`❌ PDF export error: ${error.message}`, 'error');
        } finally {
            exportPdfBtn.textContent = '📄 Export as PDF';
            exportPdfBtn.disabled = false;
        }
    }

    // Initialize first-run UI state
    updateFirstRunUI();

}); // End of DOMContentLoaded