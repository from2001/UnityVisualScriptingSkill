# Unity Visual Scripting Agent Skill

A Claude Code skill that enables AI-assisted generation of Unity Visual Scripting graphs through C# editor scripts.

<img width="1769" height="1091" alt="VisualScripting" src="https://github.com/user-attachments/assets/ff22d3dd-ded3-45ec-9095-9f5e2343df5f" />


## What This Does

When installed as a Claude Code skill, it allows Claude to:

- **Create Script Graphs** programmatically using the `Unity.VisualScripting` API
- **Create State Graphs** for state machine-based logic
- **Assign graphs to GameObjects** via `ScriptMachine` / `StateMachine` components
- **Wire nodes** with proper control flow and data connections

## Usage

Once installed, Claude Code will automatically activate the skill when you mention keywords like "visual scripting", "script graph", "state graph", "flow graph", or "ScriptMachine".

**Example prompts:**

- "Create a Visual Scripting graph that rotates an object every frame"
- "Make a script graph that handles player input with WASD keys"
- "Generate a state graph with Idle and Walking states"
- "Assign the graph to the Player GameObject"
