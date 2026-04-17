# dependency-demo-broken

Intentionally broken example. This plugin requires `greeting-helper ~2.0.0`,
but the [`plugin-dependency-example`](https://github.com/dicksontsai/plugin-dependency-example)
marketplace only has `1.0.0` tagged.

Installing this plugin shows how an unsatisfied version constraint is reported.
The plugin is disabled with a `no-matching-tag` /
`dependency-version-unsatisfied` error visible in `claude plugin list` and
`/doctor`.

See the [plugin dependencies docs](https://code.claude.com/docs/en/plugin-dependencies#resolve-dependency-errors).
