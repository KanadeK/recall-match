# Release process

## Release criteria

A release is ready only when:

1. `python scripts/release_gate.py` passes from the intended commit.
2. GitHub Actions passes that same commit on Python 3.10.
3. The changelog and version agree.
4. The public example still yields one identifier match, one review candidate, and one item without candidates.
5. No required code/security review finding remains.

The gate follows the current PyPA recommendation to use `python -m build`, producing one wheel and one source distribution. GitHub Actions uses `setup-python`, which GitHub documents as the recommended way to get consistent hosted-runner Python behavior.

Official references:

- https://packaging.python.org/en/latest/tutorials/packaging-projects/#generating-distribution-archives
- https://docs.github.com/actions/automating-builds-and-tests/building-and-testing-python
- https://github.com/actions/checkout/releases
- https://github.com/actions/setup-python/releases

## Publish

```bash
python scripts/release_gate.py
git tag -a v0.1.0 -m "Recall Match v0.1.0"
git push origin v0.1.0
gh release create v0.1.0 dist/*.whl dist/*.tar.gz \
  --title "Recall Match v0.1.0" \
  --notes-file docs/release-notes-v0.1.0.md
```

Do not rebuild artifacts after tagging. Upload the wheel and source distribution that passed the local gate.

## Withdraw or repair

If a released artifact is corrupt, installs the wrong version, or creates unsafe match tiers:

1. Mark the GitHub release as pre-release and add a visible withdrawal note.
2. Keep the original tag immutable; do not silently replace an asset with different bytes.
3. Reproduce the defect from the released wheel and add a failing test.
4. Fix it and publish a patch version through the complete release gate.

Because this release is an offline CLI with no server or data migration, rollback for a user is reinstalling the prior wheel. A removed GitHub asset cannot revoke copies already downloaded, so a corrected patch release and clear notice are required.

