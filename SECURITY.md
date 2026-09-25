# Security Policy

## Supported status

ReproCert is currently **public alpha software**. Security fixes target the current `main` branch and the latest published package/release line when one exists.

## Core execution boundary

A ReproCert claim contains a command to execute. Treat a claim-file change as code-execution capability.

- Never expose secrets to untrusted claim changes.
- Use least-privilege GitHub Actions permissions.
- Do not use `pull_request_target` to execute untrusted contribution code.
- ReproCert executes the declared command with `shell=False`.
- Evidence/source paths are constrained to the claim working directory.
- ReproCert does not intentionally capture environment-variable values.

## Reporting a vulnerability

Do **not** publish credentials, private customer data, or sensitive exploit details in a public issue.

If GitHub private vulnerability reporting is available for this repository, use it. Otherwise, open a non-sensitive issue requesting a private security contact channel without disclosing exploit details.

## Security boundary

A ReproCert PASS result is not a security certification of the executed program, dependency set, runner, or evidence source. See [docs/THREAT_MODEL.md](docs/THREAT_MODEL.md).
