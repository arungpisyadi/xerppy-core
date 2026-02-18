# CrewAI Integration Documentation

This document provides comprehensive documentation for the Xerppy AI Core module using CrewAI v1.9.3+ (Flows Edition).

## Table of Contents

1. [Overview](#overview)
2. [Architecture](#architecture)
3. [Installation](#installation)
4. [Configuration](#configuration)
5. [LLM Factory](#llm-factory)
6. [Agents](#agents)
7. [Tasks](#tasks)
8. [Crew Orchestration](#crew-orchestration)
9. [Usage Examples](#usage-examples)
10. [API Reference](#api-reference)
11. [Troubleshooting](#troubleshooting)

---

## Overview

The Xerppy AI Core module leverages CrewAI v1.9.3+ (Flows Edition) to provide a robust, multi-agent AI orchestration system. This integration supports multiple LLM providers including OpenAI, Google Gemini, and Hugging Face.

### Key Features

- **Multi-Provider Support**: Seamlessly switch between OpenAI, Gemini, and Hugging Face LLMs
- **YAML-Based Configuration**: Define agents and tasks in human-readable YAML files
- **Dynamic LLM Injection**: Runtime configuration of LLM providers per agent
- **Flows Architecture**: Modern CrewAI v1.9+ decorator-based implementation
- **Production Ready**: Built-in validation and error handling

---

## Architecture

```
core/ai/
|-- __init__.py              # Package exports
|-- crew.py                  # XerppyCrew implementation with @CrewBase decorator
|-- llm_factory.py           # LLMFactory for multi-provider support
|-- crew_manager.py          # Legacy crew management (backward compatibility)
|-- database_query_tool.py   # Database query tool for agents
|-- config/
    |-- agents.yaml          # Agent definitions
    |-- tasks.yaml           # Task definitions
    |-- crews.yaml           # Crew configurations
```

### Component Relationships

```
+----------------+     +----------------+     +----------------+
|   agents.yaml  |---->|  XerppyCrew    |---->|     Crew       |
+----------------+     |  (@CrewBase)   |     |  (Orchestrator)|
                       +-------+--------+     +----------------+
                               |                       |
+----------------+             |                       |
|  llm_factory.py|<------------+                       |
| (LLMFactory)   |                                     |
+-------+--------+                                     |
        |                                              |
        v                                              |
+----------------+                                     |
| Environment    |                                     |
| Variables      |-------------------------------------+
| (API Keys)     |
+----------------+
```

---

## Installation

### Prerequisites

- Python 3.11 or higher (CrewAI requires `>=3.10,<3.14`)
- uv package manager (recommended) or pip

### Dependencies

The following dependencies are automatically installed:

```toml
crewai>=1.9.3           # Core CrewAI framework (Flows Edition)
crewai-tools>=1.9.3     # CrewAI tools integration
langchain-huggingface>=0.1.0  # Hugging Face integration
huggingface_hub>=0.23.0       # Hugging Face Hub API
python-dotenv>=1.0.0          # Environment variable management
```

### Install via uv

```bash
# Install all dependencies
uv sync

# Or install specifically
uv pip install -e .
```

### Install via pip

```bash
pip install -e .
```

---

## Configuration

### Environment Variables

Set the following environment variables in your `.env` file:

```env
# OpenAI Configuration
OPENAI_API_KEY=sk-your-openai-api-key

# Google Gemini Configuration
GEMINI_API_KEY=your-gemini-api-key

# Hugging Face Configuration
HUGGINGFACE_API_KEY=your-huggingface-api-key
```

> **Note**: You only need to set the API keys for the providers you intend to use.

### Agent Configuration (`core/ai/config/agents.yaml`)

Agents are defined in YAML format with the following structure:

```yaml
agent_name:
  role: "Agent Role Description"
  goal: "Agent Goal Statement"
  backstory: |
    Detailed backstory that shapes the agent's personality and expertise.
  verbose: true                    # Enable verbose logging
  allow_delegation: false          # Allow agent to delegate tasks
  llm_config:
    provider: "openai"             # Provider: openai, gemini, or huggingface
    model: "gpt-4o"                # Model identifier
```

#### Default Agents

| Agent | Role | Provider | Model |
|-------|------|----------|-------|
| `strategist` | AI Strategy Architect | OpenAI | gpt-4o |
| `writer` | Content Strategist & Writer | OpenAI | gpt-4o |
| `privacy_officer` | AI Privacy & Compliance Officer | OpenAI | gpt-4o |

### Task Configuration (`core/ai/config/tasks.yaml`)

Tasks define the work to be performed by agents:

```yaml
task_name:
  description: "Task description"
  agent: "agent_name"              # Assigned agent
  expected_output: "Expected output description"
```

---

## LLM Factory

The `LLMFactory` class provides a unified interface for creating LLM instances from different providers.

### Usage

```python
from core.ai import LLMFactory

# Create an OpenAI LLM
openai_llm = LLMFactory.create_llm("openai", "gpt-4o")

# Create a Gemini LLM
gemini_llm = LLMFactory.create_llm("gemini", "gemini-1.5-pro")

# Create a Hugging Face LLM
hf_llm = LLMFactory.create_llm("huggingface", "meta-llama/Llama-3-70b")
```

### Supported Providers

| Provider | Model Prefix | API Key Required |
|----------|--------------|-----------------|
| OpenAI | None (direct model name) | `OPENAI_API_KEY` |
| Gemini | `gemini/` | `GEMINI_API_KEY` |
| Hugging Face | `huggingface/` | `HUGGINGFACE_API_KEY` |

### Error Handling

The factory validates API keys and raises descriptive errors:

```python
try:
    llm = LLMFactory.create_llm("openai", "gpt-4o")
except ValueError as e:
    print(f"Configuration error: {e}")
    # Output: "Configuration error: OPENAI_API_KEY environment variable is required"
```

---

## Agents

### Strategist (AI Strategy Architect)

The strategist agent develops comprehensive AI strategies aligned with business objectives.

**Capabilities:**
- Strategic planning and analysis
- Business-AI alignment assessment
- Risk mitigation strategies
- Sustainable AI adoption planning

**Configuration:**
```yaml
strategist:
  role: "AI Strategy Architect"
  goal: "Develop comprehensive AI strategies aligned with business objectives"
  llm_config:
    provider: "openai"
    model: "gpt-4o"
```

### Writer (Content Strategist & Writer)

The writer agent creates high-quality content for AI communications.

**Capabilities:**
- Technical content writing
- AI insight translation
- Multi-audience communication
- Report generation

**Configuration:**
```yaml
writer:
  role: "Content Strategist & Writer"
  goal: "Create high-quality, engaging content"
  llm_config:
    provider: "openai"
    model: "gpt-4o"
```

### Privacy Officer (AI Privacy & Compliance Officer)

The privacy officer ensures AI operations comply with regulations.

**Capabilities:**
- GDPR/CCPA compliance assessment
- Privacy risk identification
- Ethical AI guidelines enforcement
- Compliance reporting

**Configuration:**
```yaml
privacy_officer:
  role: "AI Privacy & Compliance Officer"
  goal: "Ensure AI operations comply with data privacy regulations"
  llm_config:
    provider: "openai"
    model: "gpt-4o"
```

---

## Tasks

### Strategic Analysis Task

```yaml
strategic_analysis_task:
  description: "Conduct comprehensive strategic analysis of AI opportunities"
  agent: "strategist"
  expected_output: "A detailed strategic analysis report"
```

### Content Creation Task

```yaml
content_creation_task:
  description: "Create compelling content to communicate AI strategy"
  agent: "writer"
  expected_output: "High-quality content pieces"
```

### Privacy Assessment Task

```yaml
privacy_assessment_task:
  description: "Assess AI system compliance with data privacy regulations"
  agent: "privacy_officer"
  expected_output: "Privacy assessment report with recommendations"
```

---

## Crew Orchestration

The `XerppyCrew` class orchestrates agents and tasks using the `@CrewBase` decorator pattern.

### Implementation

```python
from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task

from core.ai.llm_factory import LLMFactory


@CrewBase
class XerppyCrew:
    """Xerppy AI Core Crew implementation."""

    agents_config = "core/ai/config/agents.yaml"
    tasks_config = "core/ai/config/tasks.yaml"

    @agent
    def strategist(self) -> Agent:
        """Create strategist agent with dynamic LLM injection."""
        conf = self.agents_config["strategist"]
        llm = LLMFactory.create_llm(
            conf["llm_config"]["provider"],
            conf["llm_config"]["model"]
        )
        return Agent(config=conf, llm=llm)

    @crew
    def crew(self) -> Crew:
        """Create the Xerppy AI Core Crew."""
        return Crew(
            agents=[self.strategist(), self.writer(), self.privacy_officer()],
            tasks=[self.strategic_analysis_task(), ...],
            process=Process.sequential,
            verbose=True
        )
```

### Process Types

| Process | Description |
|---------|-------------|
| `Process.sequential` | Tasks execute in order, one after another |
| `Process.hierarchical` | Manager agent coordinates task distribution |

---

## Usage Examples

### Basic Usage

```python
from core.ai import XerppyCrew

# Initialize the crew
crew = XerppyCrew()

# Run the crew with default tasks
result = crew.crew().kickoff()

print(result)
```

### Custom Task Execution

```python
from crewai import Task
from core.ai import XerppyCrew

crew = XerppyCrew()

# Create a custom task
custom_task = Task(
    description="Analyze the current AI landscape for healthcare",
    agent=crew.strategist(),
    expected_output="Healthcare AI landscape analysis report"
)

# Run with custom task
xerppy_crew = crew.crew()
xerppy_crew.tasks = [custom_task]
result = xerppy_crew.kickoff()
```

### Using Different LLM Providers

```python
# Update agent configuration to use Gemini
# In agents.yaml:
strategist:
  llm_config:
    provider: "gemini"
    model: "gemini-1.5-pro"

# Or programmatically:
from core.ai import LLMFactory
from crewai import Agent

gemini_llm = LLMFactory.create_llm("gemini", "gemini-1.5-pro")

agent = Agent(
    role="AI Strategist",
    goal="Develop AI strategies",
    backstory="Expert in AI transformation",
    llm=gemini_llm
)
```

### Integration with Flask Routes

```python
from flask import jsonify, request
from core.ai import XerppyCrew

@app.route("/api/ai/analyze", methods=["POST"])
def analyze():
    data = request.json
    query = data.get("query", "")

    crew = XerppyCrew()
    result = crew.crew().kickoff(inputs={"query": query})

    return jsonify({
        "status": "success",
        "result": str(result)
    })
```

### Async Execution

```python
import asyncio
from core.ai import XerppyCrew

async def run_crew_async():
    crew = XerppyCrew()
    result = await crew.crew().kickoff_async()
    return result

# Run async
result = asyncio.run(run_crew_async())
```

---

## API Reference

### LLMFactory

```python
class LLMFactory:
    @staticmethod
    def create_llm(provider: str, model: str) -> LLM:
        """
        Create an LLM instance for the specified provider.

        Args:
            provider: LLM provider ('openai', 'gemini', 'huggingface')
            model: Model identifier

        Returns:
            Configured LLM instance

        Raises:
            ValueError: If provider is unsupported or API key is missing
        """
```

### XerppyCrew

```python
@CrewBase
class XerppyCrew:
    """
    Xerppy AI Core Crew implementation using CrewAI v1.9+ Flows architecture.

    Attributes:
        agents_config: Path to agents YAML configuration
        tasks_config: Path to tasks YAML configuration

    Methods:
        strategist() -> Agent: Create strategist agent
        writer() -> Agent: Create writer agent
        privacy_officer() -> Agent: Create privacy officer agent
        strategic_analysis_task() -> Task: Create strategic analysis task
        content_creation_task() -> Task: Create content creation task
        privacy_assessment_task() -> Task: Create privacy assessment task
        crew() -> Crew: Create and return the crew instance
    """
```

---

## Troubleshooting

### Common Issues

#### 1. Missing API Key

**Error:**
```
ValueError: OPENAI_API_KEY environment variable is required
```

**Solution:**
Ensure the required API key is set in your `.env` file:
```env
OPENAI_API_KEY=sk-your-api-key
```

#### 2. Unsupported Provider

**Error:**
```
ValueError: Unsupported LLM provider: anthropic
```

**Solution:**
Use one of the supported providers: `openai`, `gemini`, or `huggingface`.

#### 3. YAML Configuration Not Found

**Error:**
```
FileNotFoundError: agents.yaml not found
```

**Solution:**
Ensure the configuration path is correct relative to the project root:
```python
agents_config = "core/ai/config/agents.yaml"
```

#### 4. CrewAI Version Mismatch

**Error:**
```
ImportError: cannot import name 'CrewBase' from 'crewai.project'
```

**Solution:**
Ensure CrewAI version is 1.9.3 or higher:
```bash
uv pip install "crewai>=1.9.3"
```

### Debugging Tips

1. **Enable Verbose Mode:**
   ```yaml
   # In agents.yaml
   strategist:
     verbose: true
   ```

2. **Check LLM Connectivity:**
   ```python
   from core.ai import LLMFactory

   try:
       llm = LLMFactory.create_llm("openai", "gpt-4o")
       response = llm.call("Hello, world!")
       print(response)
   except Exception as e:
       print(f"LLM connection failed: {e}")
   ```

3. **Inspect Agent Configuration:**
   ```python
   from core.ai import XerppyCrew

   crew = XerppyCrew()
   print(crew.agents_config)
   ```

---

## Best Practices

1. **API Key Security**: Never commit API keys to version control. Use environment variables.

2. **Model Selection**: Choose models based on task complexity:
   - Simple tasks: `gpt-3.5-turbo`, `gemini-1.5-flash`
   - Complex tasks: `gpt-4o`, `gemini-1.5-pro`

3. **Agent Specialization**: Create specialized agents for specific domains rather than generic agents.

4. **Task Granularity**: Break down complex tasks into smaller, focused subtasks.

5. **Error Handling**: Always wrap crew execution in try-except blocks for production use.

6. **Cost Management**: Monitor token usage and implement rate limiting for production deployments.

---

## Additional Resources

- [CrewAI Official Documentation](https://docs.crewai.com/)
- [CrewAI GitHub Repository](https://github.com/joaomdmoura/crewAI)
- [OpenAI API Documentation](https://platform.openai.com/docs)
- [Google Gemini API Documentation](https://ai.google.dev/docs)
- [Hugging Face Inference API](https://huggingface.co/docs/api-inference)

---

## Changelog

### v1.0.0 (2026-02-18)
- Initial implementation with CrewAI v1.9.3+ Flows architecture
- Multi-provider LLM support (OpenAI, Gemini, Hugging Face)
- YAML-based configuration for agents and tasks
- Dynamic LLM injection per agent
- Three default agents: strategist, writer, privacy_officer