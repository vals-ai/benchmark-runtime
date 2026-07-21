# benchmark-runtime

`benchmark-runtime` contains the lab-facing contracts shared by Vals benchmark
orchestrators. It validates benchmark manifests, packages and runs command-based
agents inside an orchestrator-owned sandbox, persists generation and grading
artifacts, resumes interrupted work, and calls the benchmark service for grading
and final scoring.

It does not schedule tasks, create sandboxes, or choose an orchestration
framework. The custom Vals orchestrator and the Inspect adapter depend on this
package and retain ownership of those framework-specific behaviors.

## Development

```bash
make install
make test
make lint
make typecheck
```

