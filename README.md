# fosslint

fosslint checks that the structure of free software projects so that they
follow a given policy.

A policy can include.

* Which license the project should have, and what header should be applied to
  all in-scope source files.
* The README mentions how to collaborate.

## Defining policies

Policies are defined in `.fosslint` configuration files that live in the project.

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

[pattern:/**/*.py]
expect_license_header = Apache 2.0
```

## Policy Configurations (`policy:<name>`)

A policy applies a set of default configurations.

The following is an example use of a policy.

```
[policy:Spotify 1.0]
# configuration
```

### Policies

#### `Spotify 1.0`

Follows the Spotify FOSS policy, versioned to allow for mistakes.

There is no official guide for this policy.

* Uses `Apache 2.0` as a license.
* Makes sure license header is present in non-test source files.

## Pattern Configurations (`pattern:<glob>`)

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
# configuration
```

Or if you require at least one subdirectory to be present:

```
[pattern:/**/*.py]
# configuration
```

### `expect_license_header = <license>`

Expect the license header for the given license to be applied to a file.

### `custom_license_header_path = <path>`

Expect the license header in `<path>` for all matching source files to be
applied.
This path is relative to the project which is applying the configuration.

This file can contain the following variables, which will be replaced if
present:

* `{entity}` the entity which the license belongs to.
* `{year}` the year for which the license was issued.

### `skip_header_lines = <linespec>`

Skip matching any lines in the expected comment header that matches
`<linespec>`.

`<linespec>` is a line number specification supporting ranges, like `0-10,12`
which would match lines 0-10, and 12.

### `skip_header_on_stanza = <string>`

If `<string>` is found in any line of the header, do not verify license header.

## Ignore Configurations (`ignore:<glob>`)

Any path matched in the ignore section will be ignored by fosslint.

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
