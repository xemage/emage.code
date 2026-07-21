// Adapter Registry Entry for SIA Target Agent Harness
//
// This Go code should be added to CWSO/orchestrator/internal/harness/registry.go
// It registers the SIA target adapter with the harness launcher registry.
//
// SECURITY REQUIREMENTS:
// - Launcher MUST use the following docker run flags:
//   docker run --rm --read-only --tmpfs /tmp --tmpfs /run -v workspace:/workspace
// - Do NOT add API keys to ExtraEnv defaults
// - All credentials must be injected at runtime via LaunchRequest.ExtraEnv

package harness

// Adapter ID constant
const IDSIATarget AdapterID = "sia_target"

// Registry entry for SIA Target Agent Harness Adapter
var SIATargetAdapter = Adapter{
	ID:          IDSIATarget,
	DisplayName: "SIA Target Agent (Claude or OpenHands)",
	Image:       "emage/cwso-sia-target:latest",
	Command:     []string{"/usr/local/bin/python", "/app/harness-entrypoint.py"},

	// BaseURLEnv maps provider names to environment variables
	// The launcher injects the cwso-rollout proxy URL into these env vars
	BaseURLEnv: map[string]string{
		"anthropic": "ANTHROPIC_BASE_URL", // For Claude backend
		"openai":    "OPENAI_BASE_URL",    // For OpenAI models via OpenHands
		"gemini":    "LLM_BASE_URL",       // For Gemini models via OpenHands
	},

	// ExtraEnv sets default environment variables for the container
	// These can be overridden by LaunchRequest.ExtraEnv
	ExtraEnv: map[string]string{
		"SIA_BACKEND":      "claude", // Backend: "claude" or "openhands"
		"SIA_MODEL":        "haiku",  // Default model (can be "opus", etc.)
		"SIA_MAX_TURNS":    "10",     // Max agent iterations
		"PYTHONUNBUFFERED": "1",      // Real-time logging
	},

	// SecurityFlags specifies docker run flags required for this adapter
	// These flags enforce sandbox isolation (read-only root, writable /tmp only)
	SecurityFlags: []string{
		"--rm",            // Auto-cleanup on exit
		"--read-only",     // Read-only root filesystem
		"--tmpfs", "/tmp", // Writable /tmp only
		"--tmpfs", "/run", // Writable /run only
	},
}

// Add to registry in init():
// registry[IDSIATarget] = SIATargetAdapter

// Usage Example in Launcher:
//
// func (l *Launcher) LaunchSIATarget(ctx context.Context, req LaunchRequest) (Handle, error) {
//     req.HarnessID = harness.IDSIATarget
//
//     // Inject API key at runtime
//     req.ExtraEnv = map[string]string{
//         "ANTHROPIC_API_KEY": os.Getenv("ANTHROPIC_API_KEY"),
//     }
//
//     // Launcher applies security flags: --read-only --tmpfs /tmp --tmpfs /run
//     return l.Launch(ctx, req)
// }
