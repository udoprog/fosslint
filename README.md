# fosslint

fosslint checks that the structure of free software projects so that they
follow a given policy.

A policy can include.

* Which license the project should have, and what header should be applied to
  all in-scope source files.
* The README mentions how to collaborate.

## Defining policies

Policies are defined in .fosslint configuration files that live in the project.

We also look for configuration in the following locations.

* `/etc/fosslint.conf`
* `$HOME/.fosslint`

## Configuration

The configuration file contains sections which match a given file pattern,
after which the rule to apply to that kind of file should be defined.

The anonymous section at the top is for global options.

```config
[global]
expect_license = Apache 2.0
entity = Company
year = 2016

[pattern:*.py]
expect_license_header = Apache 2.0
```

## Pattern Configurations (pattern:<glob>)

Pattern configurations apply to the file which matches the given glob.

The `<glob>` pattern only permits strict matches, where the following rules
apply.

* `*` matches anything except directory separators.
* `**` matches anything (including nothing)
* Only full matches are permitted.

So in order to match any subdirectory in the project that is contained in
a path like `src/main`, the following pattern would have to be used:

```
[pattern:**/src/main/**/*.java]
```

Or if you require at least one subdirectory to be present:

```
[pattern:/**/*.py]
```

### `expect_license_header = <license>`

Expect the license header for the given license to be applied to a file.

## Global Configuration Keys

### `year = <year>`

Copyright year to apply.

### `auto_year = true`

Automatically determine current year from the local system clock.

### `base_year = <year>`

If copyright year is a range, this is the first component of that range as in
`<base_year>-<year>`.

### `expect_license = <license>`

Expect the given license to be applied to the project.

## Licenses

The following section describes all the available licenses, and the options
that can be applied to them.

### `Apache 2.0`

Unless `apache_notice = no` is set, will check that a `/NOTICE` file is present
and contains a copyright notice.

Unless `apache_license = no` is set, will check that a `/LICENSE` file is
present and contains the entirety of the Apache 2.0 license.
