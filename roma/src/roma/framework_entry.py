"""
ROMA Framework Entry Point.

Main user-facing API using Hydra ConfigStore with domain value objects.
Provides the same interface as v1 for backward compatibility.
"""

from collections.abc import Iterator
from datetime import UTC
from typing import Any

import hydra
from hydra.utils import instantiate
from omegaconf import DictConfig

from roma.application.orchestration.system_manager import SystemManager
from roma.domain.value_objects.config.roma_config import ROMAConfig


class SentientAgent:
    """Main user-facing API matching v1 functionality."""

    def __init__(self, config: ROMAConfig):
        self.config = config
        self._system_manager = SystemManager(config)
        self._initialized = False

    @classmethod
    def create(
        cls, _config_path: str | None = None, enable_hitl_override: bool | None = None, **kwargs
    ) -> "SentientAgent":
        """Create agent using Hydra ConfigStore with configuration."""
        # TODO: Use Hydra to load config with overrides when needed
        # For now, create default config with profile
        profile_name = kwargs.get("profile_name", "general_agent")
        default_config = ROMAConfig(default_profile=profile_name)

        # Apply HITL override if provided
        if enable_hitl_override is not None:
            default_config.execution.hitl_enabled = enable_hitl_override

        return cls(default_config)

    def execute(self, goal: str, **options) -> dict[str, Any]:
        """Execute any task using ROMA's intelligent agent system."""
        import asyncio

        async def _async_execute():
            # Initialize if needed
            if not self._initialized:
                await self._system_manager.initialize(self.config.profile.name)
                self._initialized = True

            # Execute task through SystemManager
            result = await self._system_manager.execute_task(goal, **options)

            return {
                "execution_id": result["execution_id"],
                "goal": goal,
                "status": result["status"],
                "final_output": result["result"],
                "execution_time": result["execution_time"],
                "node_count": result["node_count"],
                "hitl_enabled": options.get("enable_hitl", self.config.execution.hitl_enabled),
                "framework_result": {
                    "framework": result["framework"],
                    "artifacts": result.get("artifacts", []),
                    "task_id": result.get("task_id"),
                },
            }

        # Run async code in event loop
        try:
            loop = asyncio.get_running_loop()
            # If we're in an async context, create a task in the existing loop
            import concurrent.futures

            with concurrent.futures.ThreadPoolExecutor() as executor:
                future = executor.submit(asyncio.run_coroutine_threadsafe, _async_execute(), loop)
                return future.result().result()
        except RuntimeError:
            # No event loop running, we can use asyncio.run
            return asyncio.run(_async_execute())

    def stream_execution(self, goal: str, **options) -> Iterator[dict[str, Any]]:
        """Stream execution progress."""
        from datetime import datetime

        # Start execution
        start_time = datetime.now(UTC)
        yield {
            "event": "started",
            "goal": goal,
            "timestamp": start_time.isoformat(),
            "status": "initializing",
        }

        try:
            # Execute task and yield progress
            yield {"event": "progress", "message": "Initializing ROMA system...", "progress": 0.2}

            result = self.execute(goal, **options)

            yield {"event": "progress", "message": "Processing task...", "progress": 0.8}

            # Final result
            yield {
                "event": "completed",
                "status": result["status"],
                "result": result["final_output"],
                "execution_id": result["execution_id"],
                "execution_time": result["execution_time"],
                "node_count": result["node_count"],
            }

        except Exception as e:
            yield {"event": "error", "error": str(e), "timestamp": datetime.now(UTC).isoformat()}

    def get_system_info(self) -> dict[str, Any]:
        """Get comprehensive system information."""
        base_info = {
            "name": self.config.app.name,
            "version": self.config.app.version,
            "description": self.config.app.description,
            "environment": self.config.app.environment,
            "profile": self.config.profile.name,
            "cache_enabled": self.config.cache.enabled,
        }

        # Add system manager info if initialized
        if self._initialized:
            system_info = self._system_manager.get_system_info()
            base_info.update(system_info)
        else:
            base_info["status"] = "not_initialized"

        return base_info

    def validate_configuration(self) -> dict[str, Any]:
        """Validate configuration."""
        validation_result = self.config.validate_profile_completeness()
        base_validation = {
            "valid": self.config.is_valid(),
            "issues": validation_result,
            "profile": self.config.profile.name,
        }

        # Add system manager validation if initialized
        if self._initialized:
            system_validation = self._system_manager.validate_configuration()
            base_validation["system_validation"] = system_validation
            base_validation["valid"] = base_validation["valid"] and system_validation["valid"]

        return base_validation


class ProfiledSentientAgent(SentientAgent):
    """Profile-specific agent - SCAFFOLDING"""

    @classmethod
    def create_with_profile(
        cls, profile_name: str = "general_agent", **kwargs
    ) -> "ProfiledSentientAgent":
        """Create with specific profile configuration."""
        config = ROMAConfig(default_profile=profile_name)
        # Apply any overrides from kwargs
        if "enable_hitl" in kwargs:
            config.execution.hitl_enabled = kwargs["enable_hitl"]
        return cls(config)

    def get_profile_info(self) -> dict[str, Any]:
        """Get comprehensive profile information."""
        profile_info = {
            "profile_name": self.config.profile.name,
            "description": self.config.profile.description,
            "version": self.config.profile.version,
            "enabled": self.config.profile.enabled,
            "completeness": self.config.validate_profile_completeness(),
        }

        # Add available profiles if system manager is initialized
        if self._initialized:
            profile_info["available_profiles"] = self._system_manager.get_available_profiles()
            profile_info["current_active"] = self._system_manager.get_current_profile()

        return profile_info


class LightweightSentientAgent(SentientAgent):
    """Lightweight async agent - SCAFFOLDING"""

    @classmethod
    def create_with_profile(
        cls, profile_name: str = "general_agent", **kwargs
    ) -> "LightweightSentientAgent":
        """Create lightweight agent with profile configuration."""
        config = ROMAConfig(default_profile=profile_name)
        # Apply lightweight optimizations
        config.execution.max_concurrent_tasks = kwargs.get("max_concurrent", 5)
        if "enable_hitl" in kwargs:
            config.execution.hitl_enabled = kwargs["enable_hitl"]
        return cls(config)

    async def execute(
        self, goal: str, max_steps: int = 50, save_state: bool = False, **options
    ) -> dict[str, Any]:
        """High-performance async execution with step limits."""
        # Initialize if needed
        if not self._initialized:
            await self._system_manager.initialize(self.config.profile.name)
            self._initialized = True

        # Add execution constraints for lightweight mode
        options["max_steps"] = max_steps
        options["save_state"] = save_state
        options["lightweight"] = True

        # Execute task through SystemManager
        result = await self._system_manager.execute_task(goal, **options)

        return {
            "execution_id": result["execution_id"],
            "goal": goal,
            "status": result["status"],
            "max_steps": max_steps,
            "save_state": save_state,
            "final_output": result["result"],
            "execution_time": result["execution_time"],
            "node_count": result["node_count"],
            "framework_result": {
                "framework": result["framework"],
                "artifacts": result.get("artifacts", []),
                "task_id": result.get("task_id"),
                "lightweight": True,
            },
        }


# Hydra main entry point using ConfigStore with automatic instantiation
@hydra.main(version_base=None, config_path="../../config", config_name="config")
def hydra_main(cfg: DictConfig) -> None:
    """Hydra entry point using automatic object instantiation."""
    try:
        print(f"🚀 ROMA v{cfg.app.version} - Hydra CLI Entry Point")
        print(f"📋 Profile: {cfg.profiles.name}")
        print(f"🌍 Environment: {cfg.app.environment}")

        # Use FULL automatic instantiation with recursive object conversion
        print("\n🔧 Instantiating full ROMA configuration...")

        # Single instantiate call with _convert_="object" for full recursive instantiation
        roma_config = instantiate(cfg, _convert_="object")
        print(f"✅ Full instantiation successful: {type(roma_config).__name__}")

        # Initialize agent
        agent = SentientAgent(roma_config)

        print("✅ ROMA Agent initialized successfully!")
        print(f"📊 System Info: {agent.get_system_info()}")

        # TODO: Add interactive mode or specific execution logic

    except Exception as e:
        print(f"❌ Configuration error: {e}")
        import traceback

        traceback.print_exc()
        raise


# Convenience functions matching v1 API
def quick_research(
    topic: str, enable_hitl: bool | None = None, profile_name: str = "deep_research_agent", **kwargs
) -> str:
    """Quick research function - SCAFFOLDING"""
    agent = ProfiledSentientAgent.create_with_profile(profile_name)
    result = agent.execute(f"Research: {topic}", enable_hitl=enable_hitl, **kwargs)
    return result.get("final_output", "Scaffolding research result")


def quick_analysis(data_description: str, enable_hitl: bool | None = None, **kwargs) -> str:
    """Quick analysis function - SCAFFOLDING"""
    agent = SentientAgent.create()
    result = agent.execute(f"Analyze: {data_description}", enable_hitl=enable_hitl, **kwargs)
    return result.get("final_output", "Scaffolding analysis result")


def create_research_agent(enable_hitl: bool = True, **kwargs) -> ProfiledSentientAgent:
    """Create research agent - SCAFFOLDING"""
    # TODO: Implement HITL integration when available
    return ProfiledSentientAgent.create_with_profile("deep_research_agent", enable_hitl_override=enable_hitl, **kwargs)


def list_available_profiles() -> list[str]:
    """List available profiles from configuration."""
    # Create a temporary agent to discover profiles
    agent = SentientAgent.create()
    if agent._initialized:
        return agent._system_manager.get_available_profiles()
    return []


if __name__ == "__main__":
    hydra_main()
