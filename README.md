# fosslint

fosslint checks that the structure of free software projects so that they
follow a given policy.

A policy can include.

* Which license the project should have, and what header should be applied to
  all in-scope source files.
* The README mentions how to collaborate.

# How to Use

Install using pip:

```bash
$> pip3 install --user fosslint
```

`fosslint` can be invoked without arguments to print any violations that are
present in the current project.
If any violations are present, `fosslint` will exit with a non-zero exit status
which is useful if you intend to make it part of your build pipeline.

It is also capable of suggesting a fix for many violations. To do this, run
`fosslint --fix`.

```bash
$> fosslint --fix
/home/udoprog/repo/project/src/main.c:1 - License Header Mismatch:
  " * Copyright (c) 2016 Wrong Entity." != " * Copyright (c) 2016 Right Entity."
--- /home/udoprog/repo/project/src/main.c
+++ /home/udoprog/repo/project/src/main.c.fix
@@ -1,5 +1,5 @@
 /*
- *  Copyright (c) 2016 Wrong Entity
+ *  Copyright (c) 2016 Right Entity
  *
  *  Licensed to the Apache Software Foundation (ASF) under one
  *  or more contributor license agreements.  See the NOTICE file
@@ -9,7 +9,7 @@
  *  "License"); you may not use this file except in compliance
  *  with the License.  You may obtain a copy of the License at
  *
- *  http://www.apache.org/licenses/LICENSE-2.0
+ *    http://www.apache.org/licenses/LICENSE-2.0
  *
  *  Unless required by applicable law or agreed to in writing,
  *  software distributed under the License is distributed on an
Fix Header [y/n]?
```

# Defining policies

Policies are defined in `.fosslint` configuration files that live in the project.

We also look for configuration in the following locations.

* `/etc/fosslint.conf`
* `$HOME/.fosslint`

# Configuration

The configuration file contains sections which match a given file pattern,
after which the rule to apply to that kind of file should be defined.

The anonymous section at the top is for global options.

```config
[global]
expect_license = Apache 2.0
entity = Company
year = 2016

[pattern:/**/*.py]
license_header = Apache 2.0
```

# Policy Configurations (`policy:<name>`)

A policy applies a set of default configurations.

The following is an example use of a policy.

```
[policy:Spotify 1.0]
# configuration
```

## Policies

### `Spotify 1.0`

Follows the Spotify FOSS policy, versioned to allow for mistakes.

There is no official guide for this policy.

* Uses `Apache 2.0` as a license.
* Makes sure license header is present in non-test source files.

# Pattern Configurations (`pattern:<glob>`)

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

## `language = <language>`

If fosslint can't determine which language a file has, or if the wrong one is
detected, this option can override it.

Available languages are:

* `hash` - Generic language where comments are hash-based (`#` prefixed).
* `c-style` - Generic language where comments are c-style (`/*` and `*/`).
* `python` - Python
* `java` - Java

## `license_header = <license>` (also global)

Expect the license header for the given license to be applied to a file.

## `license_header_path = <path>` (also global)

Expect the license header in `<path>` for all matching source files to be
applied.
This path is relative to the project which is applying the configuration.

This file can contain the following variables, which will be replaced if
present:

* `{entity}` the entity which the license belongs to.
* `{year}` the year for which the license was issued.

## `license_header_pad = <string>` (also global)

Indicates that the beginning of the license header should be padded with the
given string.

Typically this is one space (` `) by default, but it depends on the extension.

## `skip_header_lines = <linespec>`

Skip matching any lines in the expected comment header that matches
`<linespec>`.

`<linespec>` is a line number specification supporting ranges, like `0-10,12`
which would match lines 0-10, and 12.

## `skip_header_on_stanza = <string>`

If `<string>` is found in any line of the header, do not verify license header.

## `strip_header = <true|false>` (also global)

If `true`, will cause trailing spaces in header to be removed.

# Ignore Configurations (`ignore:<glob>`)

Any path matched in the ignore section will be ignored by fosslint.

# Global Configuration Keys

## `year = <year>`

Copyright year to apply.

## `auto_year = true`

Automatically determine current year from the local system clock.

## `start_year = <year>`

If copyright year is a range, this is the first component of that range as in
`<start_year>-<year>`.

## `expect_license = <license>`

Expect the given license to be applied to the project.

## `year_range_format = <format>`

The format to apply when rendering a year range, must contain `{start}` and
`{end}` which is replaced with the starting and ending year respectively.

```
year_range_format = {start}-{end}
```

# Licenses

The following section describes all the available licenses, and the options
that can be applied to them.

## `Apache 2.0`

Unless `apache_notice = no` is set, will check that a `/NOTICE` file is present
and contains a copyright notice.

Unless `apache_license = no` is set, will check that a `/LICENSE` file is
present and contains the entirety of the Apache 2.0 license.
