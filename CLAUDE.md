# Vibe Coder Guide - Complete System

## Who I Am
- Solo developer working on personal/small projects and sometimes complex inherited codebases
- I prefer working code over perfect architecture  
- I trust Claude to find the right files and make smart decisions
- I want to ship, not over-engineer
- I'm building to share with my team, not to impress engineers

## Core Philosophy
**"Make it work, make it nice, make it ship"**

Working code > Clean code  
Shipped > Perfect  
Simple > Complex

## Two Scenarios

### Scenario 1: New/Simple Projects (Default)
**Examples:** Chrome extensions, single-page apps, scripts, API wrappers, calculators, portfolio sites, utility CLIs

**Approach:** Start simple, stay simple
- Use: `/build`, `/add`, `/fix`, `/ship`, `/clean`
- One file until painful (300+ lines)
- Hardcode before configuring
- Ship fast, iterate

### Scenario 2: Existing Complex Projects
**Examples:** Inherited codebases, over-engineered projects, complex systems that need streamlining

**Approach:** Understand fully, then simplify strategically
- Use: `/audit`, `/map`, `/streamline`
- Read everything first (tokens don't matter for understanding)
- Strategic simplification while preserving functionality
- Make it maintainable and shippable

## Project Phases

### For Simple Projects
**POC (Default)** → **MVP** → **Ship-Ready**

- **POC**: One file if possible, hardcode everything, just prove it works
- **MVP**: Make it usable daily, add basic error handling, clean UI
- **Ship-Ready**: Polish for public use, essential features only

### For Complex Projects  
**Audit** → **Streamline** → **Ship-Ready**

- **Audit**: Comprehensive understanding of entire codebase
- **Streamline**: Remove complexity while preserving functionality  
- **Ship-Ready**: Final polish for team sharing

## Commands

### Simple Project Commands
- **`/build [description]`** - Create simplest version that works (POC approach)
- **`/add [feature]`** - Add feature with minimal changes
- **`/fix [issue]`** - Fix directly without over-engineering
- **`/clean [scope]`** - Organize and move to next phase
- **`/ship [project]`** - Polish for public sharing

### Complex Project Commands
- **`/audit [focus]`** - Comprehensive codebase analysis and understanding
- **`/map [scope]`** - Create structural overview of components and relationships
- **`/streamline [target]`** - Strategic simplification while preserving functionality

## What NOT to Do (Critical)
❌ Don't create tons of test files unless I ask  
❌ Don't add security layers for personal projects  
❌ Don't create multiple documentation files  
❌ Don't suggest "best practices" - suggest what works  
❌ Don't create config files for things that won't change  
❌ Don't split into multiple files until it's too big (300+ lines)  
❌ Don't add features I didn't ask for  
❌ Don't over-abstract or create unnecessary patterns  
❌ Don't optimize prematurely  
❌ Don't build for imaginary future needs

## What TO Do
✅ Start with the simplest thing that could work  
✅ Keep everything in one file until it's painful  
✅ Use inline styles before stylesheets  
✅ Hardcode values before making them configurable  
✅ Copy-paste before abstracting  
✅ Make it work before making it "right"  
✅ For complex projects: understand everything first, then simplify strategically  
✅ Preserve working functionality while removing complexity

## Trust Rules

### For Simple Projects
1. I trust you to keep it simple
2. I trust you to not over-engineer
3. I trust you to focus on shipping
4. I trust you to start with one file

### For Complex Projects  
1. I trust you to read my entire codebase (tokens don't matter for understanding)
2. I trust you to understand relationships and dependencies
3. I trust you to make smart simplification decisions
4. I trust you to preserve what works while cutting what doesn't

### Always
- I trust you to find the right files
- I trust you to make good decisions
- I trust you to ask when unsure

## File Creation Rules
- **Simple projects**: Start with one file, only split when over 300 lines
- **Complex projects**: Consolidate and simplify existing structure
- Only create tests if I ask
- Only create docs if I ask  
- Name files obviously (app.js, style.css, index.html)

## Natural Language Workflow

### Simple Projects
```
"build a todo app" → Creates single-file POC
"add dark mode" → Adds feature inline
"make it prettier" → Improves UI simply
"ship it" → Polishes for sharing
```

### Complex Projects
```  
"audit this project" → Comprehensive analysis
"what can be simplified?" → Identifies complexity
"streamline the auth system" → Strategic simplification
"make this ready to ship" → Final optimization
```

## Project Structure Preferences
- **New projects**: One file → organize only when needed
- **Complex projects**: Simplify existing structure → consolidate where possible
- Prefer fewer files over many files
- Prefer flat structure over deep nesting
- Only create folders when absolutely necessary

## Technology Preferences
- JavaScript/TypeScript for most web things
- Python for scripts and backends
- Simple CSS over frameworks (until they're actually needed)
- HTML that just works
- Whatever gets to shipping fastest

## Sub-Agent Usage

### For Simple Projects
- **builder**: Creates simple, working solutions (default for new projects)
- **shipper**: Polishes POC/MVP for public sharing

### For Complex Projects
- **auditor**: Comprehensive codebase analysis and understanding
- **simplifier**: Strategic code simplification while preserving functionality

## Quality Gates

### Simple Projects
- POC: Does it work at all?
- MVP: Can I use it daily without frustration?
- Ship-Ready: Would I be embarrassed to share this?

### Complex Projects  
- Audit: Do I understand what this actually does?
- Streamline: Is this simpler while still working?
- Ship-Ready: Can my team easily understand and use this?

## What This Project Will NEVER Have (Unless Explicitly Requested)
- Settings/config systems for things that rarely change
- Multiple themes or extensive customization
- Complex abstractions for simple problems  
- Over-engineered architecture patterns
- Extensive test suites for personal tools
- Multiple documentation files
- Advanced error handling for unlikely edge cases

## When in Doubt, Ask
- "Would copy-pasting be simpler than generic code?" → If yes, copy-paste
- "Is this actually needed for shipping?" → If no, skip it
- "Will this make it harder to understand?" → If yes, simplify
- "Am I building for problems I don't have?" → If yes, stop

## Success Metrics
- **Simple projects**: Days from idea to shipped
- **Complex projects**: Weeks from complex to maintainable  
- **Always**: Can my team understand and use this?

## Remember
I'm building to share with my team, not to impress architects.  
For simple projects: Start simple, stay simple.  
For complex projects: Understand first, then simplify strategically.  
The goal is always shipping something valuable.
