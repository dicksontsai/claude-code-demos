# dependency-demo

Demonstrates a cross-marketplace plugin dependency. This plugin depends on
`greeting-helper` from the
[`plugin-dependency-example`](https://github.com/dicksontsai/plugin-dependency-example)
marketplace and pins it to `~1.0.0`.

See the [plugin dependencies docs](https://code.claude.com/docs/en/plugin-dependencies).

## Try it

Add both marketplaces, then install this plugin. The dependency is installed
automatically.

```
/plugin marketplace add dicksontsai/plugin-dependency-example
/plugin marketplace add dicksontsai/claude-code-demos
/plugin install dependency-demo@dickson-cc-demo-plugins
```

You should now have both `/greet` (from the dependency) and `/greet-loudly`
(from this plugin).
