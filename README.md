# Base Agent

This repository is a starter template for building Google ADK agents that:

- run locally with `adk web`
- are packaged as a Python wheel
- can be deployed to Vertex AI Agent Engine
- can then be connected to Gemini Enterprise / Agentspace

It is intentionally small, so you can copy it for a new agent and replace the prompt, tools, and business logic with your own.

## What This Template Contains

The important files are:

- `base_agent/agent.py`: defines the `root_agent` entrypoint used by ADK and deployment.
- `base_agent/prompts.py`: stores the prompt/instructions for the root agent.
- `base_agent/config.py`: loads environment variables and initializes Vertex AI config.
- `deployment/deploy.py`: creates or deletes the Agent Engine deployment.
- `.env.example`: sample environment variables for local use and deployment.
- `pyproject.toml`: Python package metadata and dependencies.

## How ADK Sees This Repo

ADK expects an agents directory where each subfolder is one agent package containing at least:

- `__init__.py`
- `agent.py`

In this repo, the project root is the agents directory, and `base_agent/` is the agent package.

That is why local testing is done from the repository root with:

```powershell
uv run adk web .
```

## Prerequisites

Before you start, make sure you have:

- Python `3.12`
- `uv` installed
- access to a Google Cloud project
- Vertex AI enabled in that project
- a staging GCS bucket name for deployment
- local Google Cloud authentication set up

For local authentication, this template assumes you are using Vertex AI credentials. A common setup is:

```powershell
gcloud auth application-default login
```

You should also make sure your project and bucket permissions are ready before deployment.

## Initial Setup

Create and activate the virtual environment:

```powershell
uv venv
.\.venv\Scripts\Activate.ps1
```

Install dependencies:

```powershell
uv sync
```

If you also want development extras such as `pytest` and `black`, use:

```powershell
uv sync --extra dev
```

## Managing Dependencies With `uv add`

When you extend this template, the simplest way to add packages is with `uv add`.

Examples:

```powershell
uv add google-cloud-bigquery
uv add pydantic-settings
uv add --dev pytest-mock
```

What `uv add` does for you:

- updates `pyproject.toml`
- updates `uv.lock`
- installs the dependency into your local environment

Useful rules of thumb:

- use `uv add PACKAGE_NAME` for runtime dependencies your agent needs in production
- use `uv add --dev PACKAGE_NAME` for local-only tooling such as test and lint packages
- after adding dependencies, rebuild the wheel before deployment so Agent Engine gets the updated package set

For this repo, that rebuild step is:

```powershell
uv build --wheel --out-dir deployment
```

## Environment Variables

Copy `.env.example` to `.env` and fill in your values:

```env
GOOGLE_GENAI_USE_VERTEXAI=1

GOOGLE_CLOUD_PROJECT=YOUR_VALUE_HERE
GOOGLE_CLOUD_LOCATION=YOUR_VALUE_HERE
GOOGLE_CLOUD_STORAGE_BUCKET=YOUR_VALUE_HERE
DISPLAY_NAME=YOUR_VALUE_HERE

ROOT_AGENT_MODEL='gemini-2.5-pro'
```

What these values are used for:

- `GOOGLE_GENAI_USE_VERTEXAI=1`: tells the Google GenAI SDK to use Vertex AI.
- `GOOGLE_CLOUD_PROJECT`: your Google Cloud project ID.
- `GOOGLE_CLOUD_LOCATION`: the region for Vertex AI, for example `us-central1`.
- `GOOGLE_CLOUD_STORAGE_BUCKET`: staging bucket used during Agent Engine deployment.
- `DISPLAY_NAME`: the display name shown for the deployed agent.
- `ROOT_AGENT_MODEL`: the model used by the root ADK agent.

### Passing Custom Environment Variables To The Deployed Agent

Adding a variable to `.env` helps locally, but it is not automatically forwarded to the deployed Agent Engine runtime.

The deployment script only passes variables listed in `env_var_keys` inside `deployment/deploy.py`.

Current code:

```python
env_var_keys = [
    "ROOT_AGENT_MODEL",
]
```

If your deployed agent needs extra values, add them to both places:

1. Add the variable to `.env`
2. Add the variable name to `env_var_keys`

Example:

```env
ROOT_AGENT_MODEL='gemini-2.5-pro'
MY_API_BASE_URL='https://example.internal'
MY_FEATURE_FLAG='true'
```

```python
env_var_keys = [
    "ROOT_AGENT_MODEL",
    "MY_API_BASE_URL",
    "MY_FEATURE_FLAG",
]
```

Important note:

- do not add `GOOGLE_CLOUD_PROJECT` or `GOOGLE_CLOUD_LOCATION` to `env_var_keys` here, because the deployment script intentionally avoids passing those to Agent Engine and lets the backend provide them
- empty values are skipped by the script
- if you change environment variables used by deployment, redeploy the agent so the remote runtime gets the new values

## Creating a New Agent From This Base

For a new project, the usual edits are:

1. Update the prompt in `base_agent/prompts.py`.
2. Add tools and business logic in `base_agent/agent.py`.
3. Rename the package folder `base_agent` if you want a project-specific name.
4. Update the package name/version in `pyproject.toml`.
5. If you change the package name or version, also update `AGENT_WHL_FILE` in `deployment/deploy.py`.

That last step is important because the deployment script currently looks for a specific wheel filename:

```python
AGENT_WHL_FILE = "base_agent-0.1.0-py3-none-any.whl"
```

If the wheel filename does not match your package name/version, deployment will fail with a wheel not found error.

## Local Testing With ADK Web

`adk web` is the easiest way to test the agent locally in a browser.

From the repository root, run:

```powershell
uv run adk web .
```

What happens next:

1. ADK starts a local web server and discovers the `base_agent` package.
2. Open the local URL shown in the terminal.
3. Select the `base_agent` agent in the UI.
4. Start chatting with it to validate prompts, tools, and behavior.

Helpful options while developing:

```powershell
uv run adk web . --reload --reload_agents
```

That enables server reload and agent reload when files change.

### Common Local Testing Notes

- Run the command from the repo root, not from inside `base_agent/`.
- Make sure `.env` is present before running the agent.
- If authentication is missing, model calls to Vertex AI will fail.
- Local ADK sessions and artifacts use local storage by default unless you override it.

## How This Agent Is Wired

The root agent is created in `base_agent/agent.py`:

- `get_root_agent()` builds an `LlmAgent`
- `root_agent = get_root_agent()` exposes the entrypoint ADK uses

Right now, the template starts with:

- one root agent
- no tools yet
- a simple default instruction prompt

That makes it a clean starting point for a new agent project.

## Deploying To Vertex AI Agent Engine

This repo includes a deployment script in `deployment/deploy.py`.

### Deployment Flow

1. Create the virtual environment:

```powershell
uv venv
```

2. Activate it:

```powershell
.\.venv\Scripts\Activate.ps1
```

3. Sync dependencies:

```powershell
uv sync
```

4. Create and fill `.env` using `.env.example`.

5. Build the wheel into the `deployment/` folder:

```powershell
uv build --wheel --out-dir deployment
```

6. Move into the deployment folder:

```powershell
Set-Location .\deployment\
```

7. Run the deployment script:

```powershell
python .\deploy.py --create
```

8. Wait for the deployment to finish. It can take several minutes.

9. Copy the created Agent Engine resource name, which looks like:

```text
projects/PROJECT_ID/locations/us-central1/reasoningEngines/1234567890
```

### What The Deployment Script Does

When you run `python .\deploy.py --create`, the script:

- loads values from `.env`
- checks whether the staging bucket exists
- creates the bucket if needed
- initializes Vertex AI with your project, region, and staging bucket
- packages the local wheel as a dependency for Agent Engine
- creates the remote Agent Engine app

### Required Deployment Inputs

The deployment script expects these values:

- `GOOGLE_CLOUD_PROJECT`
- `GOOGLE_CLOUD_LOCATION`
- `GOOGLE_CLOUD_STORAGE_BUCKET`
- `DISPLAY_NAME`

It also passes `ROOT_AGENT_MODEL` to the remote environment when present.

If you want to pass more runtime configuration to the deployed agent, add those variable names to `env_var_keys` in `deployment/deploy.py` before deploying.

### Deployment Command Overrides

You can override `.env` values with flags:

```powershell
python .\deploy.py --create --project_id YOUR_PROJECT --location us-central1 --bucket YOUR_BUCKET
```

## Deleting A Deployed Agent

To delete an existing Agent Engine deployment:

```powershell
python .\deploy.py --delete --resource_id "projects/PROJECT_ID/locations/us-central1/reasoningEngines/1234567890"
```

## Connecting The Deployed Agent To Gemini Enterprise / Agentspace

After deployment:

1. Copy the resource name returned by the deployment script.
2. Open Gemini Enterprise / Agentspace.
3. Add a custom agent backed by Agent Engine.
4. Paste the Agent Engine resource name into the required field.
5. Save the configuration.
6. Open the `Agents` area and find the agent under `From your organization`.

This is the step that makes the deployed Agent Engine app available to business users in your organization.

## Troubleshooting

### `adk web` does not find the agent

Make sure you are running:

```powershell
uv run adk web .
```

from the repo root, where `base_agent/` is a subdirectory.

### Deployment says the wheel file is missing

Rebuild the wheel:

```powershell
uv build --wheel --out-dir deployment
```

Then make sure the filename matches `AGENT_WHL_FILE` in `deployment/deploy.py`.

### Deployment fails with permission errors

Check:

- Vertex AI permissions
- Storage permissions on the staging bucket
- local Google Cloud authentication

### The local agent runs but model calls fail

Usually this means one of these is missing or incorrect:

- `GOOGLE_GENAI_USE_VERTEXAI=1`
- `GOOGLE_CLOUD_PROJECT`
- `GOOGLE_CLOUD_LOCATION`
- Application Default Credentials

## Suggested Next Steps

Once the template is running, the next improvements are usually:

1. Replace the placeholder instruction in `base_agent/prompts.py`.
2. Add tools to `base_agent/agent.py`.
3. Add tests under `tests/`.
4. Add evaluation flows if you want repeatable quality checks.
