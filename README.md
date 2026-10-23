# API routes and arguments

All routes use `GET`. Unless noted otherwise, boolean arguments accept `true` or `false` and default to `true`. Setting one to `false` excludes that category.

## `/API/sector/member`

| Argument | Description |
| --- | --- |
| `page` | Page number, starting at `1` (30 records per page). |
| `q` | Search member full names. |

## `/API/sector/bill`

| Argument | Description |
| --- | --- |
| `page` | Page number, starting at `1` (30 records per page). |
| `q` | Search English short titles, English long titles, and Irish short titles. |
| `after` | Inclusive start date (`YYYY-MM-DD`); defaults to `1900-01-01`. |
| `before` | Inclusive end date (`YYYY-MM-DD`); defaults to `2300-01-01`. |
| `current`, `withdrawn`, `enacted`, `rejected`, `defeated`, `lapsed`, `repugnant` | Include or exclude bills with each status. |
| `SourcePrivate`, `SourceGovernment`, `SourcePrivateMember` | Include or exclude bills from each source. Names are case-sensitive. |
| `BillTypePublic`, `BillTypePrivate`, `BillTypeHybrid` | Include or exclude each bill type. Names are case-sensitive. |

## `/API/sector/vote`

| Argument | Description |
| --- | --- |
| `page` | Page number, starting at `1` (30 records per page). |
| `q` | Search vote text and names of members voting for, against, or abstaining. |
| `after` | Inclusive start date (`YYYY-MM-DD`); defaults to `1900-01-01`. |
| `before` | Inclusive end date (`YYYY-MM-DD`); defaults to `2300-01-01`. |
| `dail` | Include or exclude Dáil Éireann votes. |
| `seanad` | Include or exclude Seanad Éireann votes. |
| `committee` | Include committee/other-chamber votes; `false` limits results to Dáil and Seanad votes. |
| `lost`, `carried` | Include or exclude votes with each outcome. |
| `null` | Include votes with no outcome (`_`) when `true`; exclude them when `false`. |

## `/API/sector/debate`

| Argument | Description |
| --- | --- |
| `page` | Page number, starting at `1` (30 records per page). |
| `q` | Search debate titles, member names, member codes, house codes, and debate type. |
| `after` | Inclusive start date (`YYYY-MM-DD`); defaults to `1900-01-01`. |
| `before` | Inclusive end date (`YYYY-MM-DD`); defaults to `2300-01-01`. |
| `dail` | Include or exclude Dáil debates. |
| `seanad` | Include or exclude Seanad debates. |

## `/API/sector/lobby`

| Argument | Description |
| --- | --- |
| `page` | Page number, starting at `1` (30 records per page). |
| `q` | Search lobbyist names, relevant matter, details, subject matter, lobbying activities, intended results, and member codes. |
| `after` | Inclusive start date (`YYYY-MM-DD`); defaults to `1900-01-01`. |
| `before` | Inclusive end date (`YYYY-MM-DD`); defaults to `2300-01-01`. |

## `/API/sector/question`

| Argument | Description |
| --- | --- |
| `page` | Page number, starting at `1` (30 records per page). |
| `q` | Search question and answer text. |
| `after` | Inclusive start date (`YYYY-MM-DD`); defaults to `1900-01-01`. |
| `before` | Inclusive end date (`YYYY-MM-DD`); defaults to `2300-01-01`. |
| `oral`, `written` | Include or exclude oral and written questions. |
| `questiontxt` | Search question text. |
| `answertxt` | Search answer text. |

When multiple text arguments are provided, all supplied filters must match.

## `/API/<member_id>`

Replace `<member_id>` with a member code. Returns bills, votes, debates, lobbying records, questions, and member statistics when available. Each record section is paginated independently using the same `page` value.

| Argument | Description |
| --- | --- |
| `page` | Page number for each record section, starting at `1` (30 records per page). |
| `q` | Search serialized records in each section. |
| `after` | Inclusive start date (`YYYY-MM-DD`); defaults to `1900-01-01`. |
| `before` | Inclusive end date (`YYYY-MM-DD`); defaults to `2300-01-01`. |
