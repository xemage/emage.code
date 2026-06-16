# Superpowers plugin addition
_Exported on 6/16/2026 at 14:19:33 GMT+2 from Cursor (3.7.36)_

---

**User**

/add-plugin superpowers

---

**Cursor**

I'll look up how `/add-plugin` works in this workspace and what the superpowers plugin requires.


Local plugin install goes in `~/.cursor/plugins/local/` — I'll clone Superpowers there.


Cloning Superpowers into the local Cursor plugins directory.


**Superpowers** (v5.1.0) is installed locally at `~/.cursor/plugins/local/superpowers`.

Since `/add-plugin` is a Cursor IDE command and wasn’t handled by the marketplace here, the plugin was installed manually by cloning [obra/superpowers](https://github.com/obra/superpowers) into the local plugins directory.

### What was installed

| Component | Contents |
|-----------|----------|
| **Skills** | brainstorming, TDD, systematic-debugging, writing-plans, executing-plans, code review patterns, and more |
| **Hooks** | Session-start hook for context-aware skill activation |
| **Version** | 5.1.0 |

### Next steps

1. **Start a new Agent session** (`Ctrl+L`) so Cursor loads the plugin.
2. **Verify** by asking: *“Do you have superpowers?”*
3. If skills don’t appear, try the native install in a fresh Agent chat:
   ```
   /add-plugin superpowers
   ```
   Or open **Settings → Plugins → Marketplace** and search for “superpowers”.

### Using it

Superpowers skills activate from context — for example:

- *“Let’s design a new feature for user profiles”* → brainstorming
- *“This API endpoint returns 500 errors randomly”* → systematic-debugging
- *“Help me implement authentication middleware”* → writing-plans / TDD

You can also ask explicitly: *“use the brainstorming skill”*.

To update later: `git -C ~/.cursor/plugins/local/superpowers pull`, or run `/plugin-update superpowers` if you install via the marketplace.

