"""
ADK App Configuration with Resumability Support

This module configures the ADK App with resumability enabled, allowing agents
to resume execution after interruptions (network failures, power outages, etc.).

Per ADK Documentation: https://google.github.io/adk-docs/runtime/resume/

Resume Feature:
- Allows agents to pick up where they left off after interruptions
- Tracks completed workflow tasks using Events and Event Actions
- Can resume using invocation_id from the Event history
- Works automatically for standard LLM agents (no code changes needed)

To resume a stopped workflow:
1. Find the invocation_id from the Event history
2. Use the /run_sse endpoint with invocation_id parameter
3. Or use runner.run_async() with invocation_id parameter
"""
try:
    from google.adk.app import App
    from google.adk.runtime import ResumabilityConfig
except ImportError:
    # Fallback for older ADK versions that may not have these imports
    App = None
    ResumabilityConfig = None

from rag import root_agent

# Create the App with resumability enabled (if ADK version supports it)
if App and ResumabilityConfig:
    app = App(
        name='rag',
        root_agent=root_agent,
        # Enable resumability to allow agents to resume after interruptions
        # This requires ADK Python v1.14.0 or higher
        resumability_config=ResumabilityConfig(
            is_resumable=True,
        ),
    )
else:
    # Fallback: For older ADK versions, app will be None
    # The system will use root_agent directly (resumability not available)
    app = None

