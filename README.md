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

[pattern:*.py]
expect_license_header = Apache 2.0
```

## Global Configuration Keys

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
