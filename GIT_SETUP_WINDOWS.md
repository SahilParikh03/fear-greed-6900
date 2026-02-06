# Git Configuration for Windows

## Prevent Repository Corruption on Windows

To prevent issues with Windows reserved filenames (like `nul`, `con`, `prn`, etc.) that can corrupt your Git repository on Windows systems, run the following command:

```bash
git config --global core.protectNTFS true
```

### What This Does

- **Protects NTFS filesystems**: Prevents Git from creating files with Windows reserved names
- **Prevents corruption**: Stops accidental commits of files named `nul`, `con`, `prn`, `aux`, etc.
- **Cross-platform safety**: Ensures your repository works correctly across Windows, macOS, and Linux

### Additional Protection

The `.gitignore` file has been updated to explicitly block these reserved names:

```
# Windows reserved names (prevent repo corruption on Windows)
nul
nul.*
NUL
NUL.*
```

### Windows Reserved Names

Git will now protect against these reserved names:
- `nul`, `con`, `prn`, `aux`
- `com1` through `com9`
- `lpt1` through `lpt9`

### Verification

After running the command, verify it's set correctly:

```bash
git config --global core.protectNTFS
```

This should output `true`.

### Why This Matters

On Windows, certain filenames are reserved by the operating system. If these files get committed to a Git repository, they can cause the repository to become corrupted and unusable on Windows systems. This setting prevents that from happening.

## Setup Checklist

- [ ] Run `git config --global core.protectNTFS true`
- [ ] Verify the setting with `git config --global core.protectNTFS`
- [ ] Ensure `.gitignore` includes Windows reserved names (already done)
- [ ] Share this document with team members using Windows

---

**Note**: This is a global Git configuration that will apply to all your repositories. If you prefer to set it only for this repository, remove the `--global` flag:

```bash
git config core.protectNTFS true
```
